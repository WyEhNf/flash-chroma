"""固定四个拟合配置，分开验证混合目标、完整域保护与完整照片结果。"""
from __future__ import annotations
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
from lutlab import error_analysis as ea, full_domain_guard as fg, full_photo_fit as fp, fullfit, io, study_provenance
from lutlab.compatibility import environment, write_json
from run_chain_error_study import cube_evaluate, digest, photos_evaluate, source_tables
from run_joint_box_study import native_verify, photo_samples
from run_tail_repair import read_image


def stream_hist(path,table,expected):
    if path.stat().st_size != 256**3*3 or digest(path) != expected:
        raise ValueError("完整流长度或SHA不同，拒绝证书绑定")
    stream = np.memmap(path,np.uint8,mode="r",shape=(256**3,3))
    target = table.reshape(-1,3)
    hist = np.zeros(len(ea.ROOT_DISTANCE),np.int64)
    for start in range(0,len(stream),1 << 18):
        hist += ea.histogram(stream[start:start+(1 << 18)],target[start:start+(1 << 18)])[0]
    return hist


def certify(reference,hist):
    if np.array_equal(reference,hist):
        return {"accepted":True,"failed":[],"mean_ratio":[1,1],"candidate":fg.summary(hist),
            "scope":"误差直方图逐项相同，四项指标精确相等"}
    return fg.certify(fg.summary(reference),fg.summary(hist),numerator=1,denominator=1)


def choose(bank):
    baseline = bank["historical"]
    eligible,details = [],{}
    for name,value in bank.items():
        failures = ["full."+k for k in value["full_domain_certificate"]["failed"]]
        failures += ["photo."+k for k in ("mean","rms","p99","max","worst_image_p99")
            if value["guard"][k] > baseline["guard"][k]+1e-12]
        details[name] = failures
        if not failures:
            ratios = [value["cube"]["mean"]/baseline["cube"]["mean"],value["guard"]["mean"]/baseline["guard"]["mean"]]
            eligible.append(((max(ratios),sum(ratios),name),name))
    return {"winner":min(eligible)[1],"failures":details,"eligible":[n for _,n in sorted(eligible)],
        "scope":"完整域+20图选择样本门禁，完整100图尚未执行；不是最终逐图非退化保证"}


def process(prior,spec,plan,out,cache,executable,archive,training,guard):
    cid = spec["id"]
    folder = out / cid
    folder.mkdir()
    table_list,sources = source_tables(prior["case"],cache)
    table = table_list[0]
    if sources[0]["table_sha256"] != prior["sources"][0]["table_sha256"]:
        raise ValueError("本级完整参考表与父阶段不同")
    models,bank = {},{}
    old_names = {"historical":"historical","control_full":"rounded_control","grid_full":spec["grid"]}
    for name,old_name in old_names.items():
        member = cid+"/historical.slut" if name == "historical" else cid+"/"+old_name+"/model.slut"
        model_path = folder / (name+".slut")
        model_path.write_bytes(archive.read(member))
        model = io.load_sparse(model_path)
        grid_member = cid+"/historical-grid.npy" if name == "historical" else cid+"/"+old_name+"/grid.npy"
        with archive.open(grid_member) as stream:
            model.grid = np.load(stream)
        if not all(np.array_equal(a,b) for a,b in zip(io.axis_tables(model.grid),model.tables())):
            raise ValueError("离线网格与序列化权威表不同")
        models[name] = model
        previous = prior["historical"] if name == "historical" else prior["profiles"][old_name]
        bank[name] = {"cube":previous["cube"],"photos":previous["photos"],"reused_metrics":True,
            "model_sha256":digest(model_path)}
    for old_name,name in (("control_full","control_mixed"),("grid_full","grid_mixed")):
        model = models[old_name]
        print(f"[{cid}/{name}] 组装完整矩并拟合等质量目标",flush=True)
        H,b,assembly = fullfit.normal_equations(table,model.grid,plan["threads"])
        old_profile = old_names[old_name]
        if assembly["integer_system_sha256"] != prior["profiles"][old_profile]["fit"]["integer_system_sha256"]:
            raise AssertionError("原生完整矩与已验证的同网格/同参考矩不一致")
        info = {"full_assembly":assembly,"parent_normal_system_identical":True}
        candidate = fp.fit_equal_mass(table,model,training,H,b,diagnostics=info)
        part = folder / name
        part.mkdir()
        path = part / "model.slut"
        io.save_sparse(path,candidate)
        models[name] = io.load_sparse(path)
        bank[name] = {"fit":info,"model_sha256":digest(path),"reused_metrics":False}
        write_json(part / "frozen-model.json",bank[name])
    # 两个新模型均已冻结；以下集中执行完整域，并冻结五选一，不读取新完整照片结果。
    reference_path = folder / "historical.rgb"
    rebuilt = cube_evaluate(table_list,ea.Operator([models["historical"]]),reference_path,128)
    if rebuilt != bank["historical"]["cube"]:
        raise AssertionError("重建历史完整流/指标与版本化证据不一致")
    reference = stream_hist(reference_path,table,rebuilt["prediction_sha256"])
    write_json(folder / "full-domain-reference.json",fg.summary(reference))
    guard_truth = ea.source_apply(table,guard)
    for name,model in models.items():
        if name.endswith("mixed"):
            part = folder / name
            print(f"[{cid}/{name}] 完整256³及整数/原生验收",flush=True)
            bank[name]["cube"] = cube_evaluate(table_list,ea.Operator([model]),part / "cube.rgb",128)
            if bank[name]["cube"]["reference_sha256"] != rebuilt["reference_sha256"]:
                raise AssertionError("新候选完整参考流变化")
            bank[name]["native"] = native_verify([model],part,bank[name]["cube"]["prediction_sha256"],executable)
            path = part / "cube.rgb"
        elif name == "historical":
            path = reference_path
        else:
            path = ROOT / "artifacts/tail-grid-v1" / cid / old_names[name] / "cube.rgb"
            if not path.exists():
                path = folder / (name+".rgb")
                stats = cube_evaluate(table_list,ea.Operator([model]),path,128)
                if stats != bank[name]["cube"]:
                    raise AssertionError("恢复的父阶段完整流不同")
        hist = stream_hist(path,table,bank[name]["cube"]["prediction_sha256"])
        bank[name]["full_domain_certificate"] = certify(reference,hist)
        prediction = ea.Operator([model])(guard)
        per_image = [ea.metrics(prediction[i:i+plan["pixels_per_image"]],guard_truth[i:i+plan["pixels_per_image"]])
            for i in range(0,len(guard),plan["pixels_per_image"])]
        bank[name]["guard"] = {**ea.metrics(prediction,guard_truth),"worst_image_p99":max(r["p99"] for r in per_image)}
        print(f"[{cid}/{name}] full mean={bank[name]['cube']['mean']:.6f} max={bank[name]['cube']['max']:.6f}; guard photo mean={bank[name]['guard']['mean']:.6f}",flush=True)
    selection = choose(bank)
    write_json(folder / "selection-before-photos.json",selection)
    print(f"[{cid}] 五选一冻结为 {selection['winner']}；随后执行两个新模型完整100图",flush=True)
    photos = photos_evaluate(table_list,{name:ea.Operator([models[name]]) for name in ("control_mixed","grid_mixed")})
    for name,value in photos.items():
        bank[name]["photos"] = value
    result = {"case":prior["case"],"declared_grid":spec["grid"],"sources":sources,"bank":bank,
        "selection_before_photos":selection,"scope":plan["limits"]}
    write_json(folder / "result.json",result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=ROOT / "experiments/full-photo-v1.json")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--cache",type=Path,default=ROOT / "artifacts/chain-error-cache")
    parser.add_argument("--executable",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("不覆盖已有结果；复现请指定新目录")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    parent = ROOT / plan["parent"]
    prior = json.loads((parent / "results.json").read_text(encoding="utf-8"))
    old_env = json.loads((parent / "environment.json").read_text(encoding="utf-8"))
    if old_env["identity"]["image_manifest"] != digest(ROOT / "assets/photos/manifest.json"):
        raise ValueError("照片清单变化，拒绝复用历史指标")
    rows = {r["id"]:r for r in json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]}
    for row in rows.values():
        read_image(row)
    partition = json.loads((ROOT / plan["partition"]).read_text(encoding="utf-8"))
    training,train_info = photo_samples([rows[r["id"]] for r in partition["training"]["images"]],plan)
    guard,guard_info = photo_samples([rows[r["id"]] for r in partition["guard"]["images"]],plan)
    if train_info != partition["training"] or guard_info != partition["guard"]:
        raise ValueError("本轮训练/选择像素与冻结分组不同")
    numba.set_num_threads(plan["threads"])
    metadata = environment(argparse.Namespace(sizes=[plan["m"]],screen_pixels=plan["pixels_per_image"],threads=plan["threads"],reps=0,extended=False))
    extra = [Path(__file__),ROOT / "python/lutlab/full_photo_fit.py",ROOT / "python/lutlab/full_domain_guard.py",
        ROOT / "python/lutlab/fullfit.py",ROOT / "python/lutlab/box.py",ROOT / "python/lutlab/error_analysis.py",
        ROOT / "python/lutlab/tail_repair.py",ROOT / "scripts/run_chain_error_study.py",
        ROOT / "scripts/run_joint_box_study.py",ROOT / "scripts/run_tail_repair.py"]
    metadata["identity"].update(plan_sha256=digest(args.plan),partition_sha256=digest(ROOT / plan["partition"]),
        executable_sha256=digest(args.executable),full_fit=fullfit.trainer_fingerprint(),
        stage_source_sha256={str(p.relative_to(ROOT)):digest(p) for p in extra},parent_files={n:digest(parent / n)
            for n in ("results.json","environment.json","models-grid-and-costs.zip","archive-index.json")})
    metadata["identity_sha256"] = study_provenance.identity_digest(metadata["identity"])
    metadata.update(backend="Numba4线程/原生完整拟合4线程，标量/AVX2验收单线程",timing_scope="仅精度研究，不比较性能",deferred=["硬件优化","官方测试/评分","未知LUT泛化"])
    study_provenance.claim_run(args.output / "run.json",metadata)
    write_json(args.output / "photo-partition.json",partition)
    with zipfile.ZipFile(args.output / "measured-source.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for name,expected in {**metadata["identity"]["source_sha256"],**metadata["identity"]["stage_source_sha256"]}.items():
            data = (ROOT / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("实测源码快照哈希不同")
            archive.writestr(name.replace("\\","/"),data)
    with zipfile.ZipFile(parent / "models-grid-and-costs.zip") as archive:
        index = json.loads((parent / "archive-index.json").read_text(encoding="utf-8"))
        if set(index) != set(archive.namelist()) or any(hashlib.sha256(archive.read(n)).hexdigest() != h for n,h in index.items()):
            raise ValueError("父模型归档成员变化")
        cases = [process(next(r for r in prior["cases"] if r["case"]["id"] == spec["id"]),spec,plan,
            args.output.resolve(),args.cache.resolve(),args.executable.resolve(),archive,training,guard) for spec in plan["cases"]]
    write_json(args.output / "results.json",{"run_identity":metadata["identity_sha256"],"cases":cases})
    print("等质量目标阶段完成；选择与完整100图相分离，不提升默认",flush=True)


if __name__ == "__main__":
    main()
