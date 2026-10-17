"""保持历史权威轴表，集中比较原小数网格的完整域与照片混合拟合。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numba
import numpy as np
from lutlab import error_analysis as ea, error_certificate as ec, fit, fullfit, full_photo_fit as fp, full_domain_guard as fg, io, study_provenance
from lutlab.compatibility import environment, write_json
from run_chain_error_study import cube_evaluate,digest,photos_evaluate,source_tables
from run_joint_box_study import native_verify,photo_samples
from run_full_photo_study import stream_hist,choose
from run_tail_repair import read_image


def process(previous,cid,plan,out,cache,executable,archive,grid_archive,training,guard):
    folder = out / cid
    folder.mkdir()
    tables,sources = source_tables(previous["case"],cache)
    if sources[0]["table_sha256"] != previous["sources"][0]["table_sha256"]:
        raise ValueError("完整参考表与父阶段不同")
    table = tables[0]
    bank,models = {},{}
    for name in ("historical","control_full","control_mixed"):
        member = cid+"/"+(name+".slut" if name != "control_mixed" else name+"/model.slut")
        path = folder / (name+".slut")
        path.write_bytes(archive.read(member))
        if digest(path) != previous["bank"][name]["model_sha256"]:
            raise ValueError("父阶段序列化模型SHA不同")
        models[name] = io.load_sparse(path)
        bank[name] = {**previous["bank"][name],"reused_metrics":True}
    old = models["historical"]
    with grid_archive.open(cid+"/historical-grid.npy") as stream:
        old.grid = np.load(stream)
    np.save(folder / "historical-grid.npy",old.grid)
    if not all(np.array_equal(a,b) for a,b in zip(io.axis_tables(old.grid),old.tables())):
        raise ValueError("恢复离线原网格与历史权威轴表不同")
    print(f"[{cid}] 原小数网格完整域有界拟合",flush=True)
    full_info = {}
    nodes,H,b = fit.fit_full_box_tetra(table,old.grid,threads=plan["threads"],diagnostics=full_info)
    idx,frac = old.tables()
    full_model = io.SparseLut(old.grid.copy(),nodes,idx.copy(),frac.copy())
    mix_info = {}
    print(f"[{cid}] 同一原轴表的等质量拟合",flush=True)
    mixed_model = fp.fit_equal_mass(table,full_model,training,H,b,diagnostics=mix_info)
    for name,model,detail in (("fractional_full",full_model,full_info),("fractional_mixed",mixed_model,mix_info)):
        if not all(np.array_equal(a,b) for a,b in zip(model.tables(),old.tables())):
            raise AssertionError("本阶段新模型改变了历史权威轴表")
        part = folder / name
        part.mkdir()
        path = part / "model.slut"
        io.save_sparse(path,model)
        models[name] = io.load_sparse(path)
        bank[name] = {"fit":detail,"model_sha256":digest(path),"axis_tables_unchanged":True,"reused_metrics":False}
        write_json(part / "frozen-model.json",bank[name])
    reference = previous["bank"]["historical"]["full_domain_certificate"]["candidate"]
    guard_truth = ea.source_apply(table,guard)
    triples = np.array([[247,0,72],[247,0,76],[247,0,80]] if cid == "lomo-purple2" else [[255,247,0],[255,251,0],[255,255,0]],np.uint8)
    for name in plan["profiles"]:
        model,part = models[name],folder / name
        print(f"[{cid}/{name}] 完整色域及独立整数/原生验收",flush=True)
        cube = cube_evaluate(tables,ea.Operator([model]),part / "cube.rgb",128)
        if cube["reference_sha256"] != bank["historical"]["cube"]["reference_sha256"]:
            raise AssertionError("原参考完整流变化")
        hist = stream_hist(part / "cube.rgb",table,cube["prediction_sha256"])
        proof = fg.certify(reference,fg.summary(hist),numerator=1,denominator=1)
        if reference["histogram"] == proof["candidate"]["histogram"]:
            proof.update(accepted=True,failed=[],scope="保存直方图相同，四项指标精确相等")
        prediction = ea.Operator([model])(guard)
        per_image = [ea.metrics(prediction[i:i+plan["pixels_per_image"]],guard_truth[i:i+plan["pixels_per_image"]])
            for i in range(0,len(guard),plan["pixels_per_image"])]
        bank[name].update(cube=cube,full_domain_certificate=proof,
            guard={**ea.metrics(prediction,guard_truth),"worst_image_p99":max(r["p99"] for r in per_image)},
            native=native_verify([model],part,cube["prediction_sha256"],executable),
            fixed_triplet_certificate=ec.three_point_bound(model,triples,ea.source_apply(table,triples)))
        print(f"[{cid}/{name}] mean={cube['mean']:.6f} RMS={cube['rms']:.6f} max={cube['max']:.6f}；选择图mean={bank[name]['guard']['mean']:.6f}",flush=True)
    selection = choose(bank)
    write_json(folder / "selection-before-photos.json",selection)
    print(f"[{cid}] 选择冻结为{selection['winner']}，两个新模型完整100图",flush=True)
    photos = photos_evaluate(tables,{name:ea.Operator([models[name]]) for name in plan["profiles"]})
    for name,value in photos.items():
        bank[name]["photos"] = value
    result = {"case":previous["case"],"sources":sources,"bank":bank,"selection_before_photos":selection,
        "scope":plan["limits"]}
    write_json(folder / "result.json",result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=ROOT / "experiments/fractional-fit-v1.json")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--cache",type=Path,default=ROOT / "artifacts/chain-error-cache")
    parser.add_argument("--executable",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("不覆盖已有结果；复现请指定新目录")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    parent,grid_parent = ROOT / plan["parent"],ROOT / plan["grid_parent"]
    history = json.loads((parent / "results.json").read_text(encoding="utf-8"))
    old_env = json.loads((parent / "environment.json").read_text(encoding="utf-8"))
    if old_env["identity"]["image_manifest"] != digest(ROOT / "assets/photos/manifest.json"):
        raise ValueError("照片清单变化，拒绝复用历史指标")
    rows = {r["id"]:r for r in json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]}
    for row in rows.values():read_image(row)
    partition = json.loads((parent / "photo-partition.json").read_text(encoding="utf-8"))
    training,train_info = photo_samples([rows[r["id"]] for r in partition["training"]["images"]],plan)
    guard,guard_info = photo_samples([rows[r["id"]] for r in partition["guard"]["images"]],plan)
    if train_info != partition["training"] or guard_info != partition["guard"]:
        raise ValueError("训练/选择像素与父阶段不同")
    numba.set_num_threads(plan["threads"])
    metadata = environment(argparse.Namespace(sizes=[plan["m"]],screen_pixels=plan["pixels_per_image"],threads=plan["threads"],reps=0,extended=False))
    extra = [Path(__file__),ROOT / "python/lutlab/fullfit.py",ROOT / "python/lutlab/support_certificate.py",
        ROOT / "python/lutlab/full_photo_fit.py",ROOT / "python/lutlab/full_domain_guard.py",ROOT / "python/lutlab/box.py",
        ROOT / "python/lutlab/error_analysis.py",ROOT / "python/lutlab/error_certificate.py",ROOT / "python/lutlab/tail_repair.py",
        ROOT / "scripts/run_chain_error_study.py",ROOT / "scripts/run_joint_box_study.py",
        ROOT / "scripts/run_full_photo_study.py",ROOT / "scripts/run_tail_repair.py"]
    parent_files = {"full-photo/"+n:digest(parent / n) for n in ("results.json","environment.json","photo-partition.json","models-and-selection.zip","archive-index.json")}
    parent_files.update({"tail-grid/"+n:digest(grid_parent / n) for n in ("models-grid-and-costs.zip","archive-index.json")})
    metadata["identity"].update(plan_sha256=digest(args.plan),executable_sha256=digest(args.executable),
        full_fit=fullfit.trainer_fingerprint(),stage_source_sha256={str(p.relative_to(ROOT)):digest(p) for p in extra},parent_files=parent_files)
    metadata["identity_sha256"] = study_provenance.identity_digest(metadata["identity"])
    metadata.update(backend="Numba/原生完整拟合4线程，标量/AVX2验收单线程",timing_scope="不比较性能",deferred=["硬件优化","官方评分","逐图max/p99约束修复"])
    study_provenance.claim_run(args.output / "run.json",metadata)
    write_json(args.output / "photo-partition.json",partition)
    with zipfile.ZipFile(args.output / "measured-source.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name,expected in {**metadata["identity"]["source_sha256"],**metadata["identity"]["stage_source_sha256"]}.items():
            data = (ROOT / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:raise ValueError("源码快照变化")
            z.writestr(name.replace("\\","/"),data)
    with zipfile.ZipFile(parent / "models-and-selection.zip") as archive,zipfile.ZipFile(grid_parent / "models-grid-and-costs.zip") as grid_archive:
        for root,z in ((parent,archive),(grid_parent,grid_archive)):
            index = json.loads((root / "archive-index.json").read_text(encoding="utf-8"))
            if set(index) != set(z.namelist()) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in index.items()):
                raise ValueError("父归档成员或SHA变化")
        cases = [process(next(r for r in history["cases"] if r["case"]["id"] == cid),cid,plan,args.output.resolve(),
            args.cache.resolve(),args.executable.resolve(),archive,grid_archive,training,guard) for cid in plan["cases"]]
    write_json(args.output / "results.json",{"run_identity":metadata["identity_sha256"],"cases":cases})
    print("原轴表配对批次完成；不更换默认",flush=True)


if __name__ == "__main__":main()
