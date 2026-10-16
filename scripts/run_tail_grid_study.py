"""固定两例、三网格的一次性完整域误差归因批次。"""
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
from lutlab import axis_grid as ag, error_analysis as ea, error_certificate, fit, fullfit, interp, io, study_provenance
from lutlab.compatibility import environment, write_json
from run_chain_error_study import colours, cube_evaluate, digest, encoded, photos_evaluate, source_tables
from run_joint_box_study import native_verify
from run_tail_repair import read_image


TRIPLETS = {
    "lomo-purple2": [[247,0,72],[247,0,76],[247,0,80]],
    "velvia-vivid": [[255,247,0],[255,251,0],[255,255,0]],
}


def probes(table,model,centres):
    """保存真实参考变化和模型变化，不能把参考本身的阶跃判为不稳定。"""
    points = ea.neighbourhood(np.asarray(centres,np.uint8))
    indices,weights = interp.tetra_weights(points,*model.tables(),model.m)
    before = np.sum(weights[:,:,None]*model.nodes.reshape(-1,3)[indices],axis=1)
    after = interp.apply_tetra_q16(model,points)
    truth = ea.source_apply(table,points)
    return {"centres":centres,"points":points.tolist(),"reference":truth.tolist(),
        "pre_round_output":before.tolist(),"output":after.tolist(),
        "metrics":ea.metrics(after,truth),"scope":"指定热点±1的局部诊断，不替代完整域统计"}


def process(previous,plan,out,cache,executable,parent):
    case = previous["case"]
    folder = out / case["id"]
    folder.mkdir()
    tables,sources = source_tables(case,cache)
    if sources[0]["table_sha256"] != previous["sources"][0]["table_sha256"]:
        raise ValueError("完整参考字节与历史证据不同")
    table = tables[0]
    member = case["id"]+"/baseline-stage1.slut"
    expected = json.loads((parent / "archive-index.json").read_text(encoding="utf-8"))[member]
    with zipfile.ZipFile(parent / "models-and-counterexamples.zip") as archive:
        raw = archive.read(member)
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("历史模型归档成员SHA不同")
    baseline_path = folder / "historical.slut"
    baseline_path.write_bytes(raw)
    old = io.load_sparse(baseline_path)
    old.grid = fit.adaptive_grid(table,plan["m"]) if case["grid"] == "curvature" else io.uniform_grid(plan["m"])
    if not all(np.array_equal(a,b) for a,b in zip(io.axis_tables(old.grid),old.tables())):
        raise ValueError("重建离线旧网格与保存的权威轴表不一致")
    np.save(folder / "historical-grid.npy",old.grid)
    hotspots = [r["rgb"] for r in previous["final"]["baseline"]["cube"]["hotspots"][:plan["curves"]["hotspots"]]]
    grids = {"rounded_control":np.rint(old.grid)}
    line_records,dp_records = [],{"line_sse":[],"line_minimax":[]}
    for axis in range(3):
        curves,record = ag.axis_curves(table,axis,hotspots,anchors=plan["curves"]["anchors"],hot_lines=plan["curves"]["hot_lines"])
        worst,sse = ag.chord_costs(curves,**plan["spacing"])
        np.savez_compressed(folder / f"axis{axis}-costs.npz",curves=curves,worst=worst,sse=sse)
        line_records.append(record)
        for name,objective in (("line_sse","sse"),("line_minimax","minimax")):
            grid,detail = ag.choose_knots(worst,sse,plan["m"],objective=objective,**plan["spacing"])
            grids.setdefault(name,[]).append(grid)
            dp_records[name].append(detail)
    write_json(folder / "grid-design.json",{"curves":line_records,"dynamic_programming":dp_records})
    models,records = {},{}
    triplet = np.asarray(TRIPLETS[case["id"]],np.uint8)
    targets = ea.source_apply(table,triplet)
    for name in plan["profiles"]:
        grid = np.asarray(grids[name],np.float64)
        part = folder / name
        part.mkdir()
        np.save(part / "grid.npy",grid)
        diagnostics = {}
        print(f"[{case['id']}/{name}] 完整域拟合及窄区间矩阵行复核",flush=True)
        nodes,H,b = fit.fit_full_box_tetra(table,grid,threads=plan["threads"],diagnostics=diagnostics)
        if H.diagonal().min() < 1/64 or np.count_nonzero(H.diagonal() == 0):
            raise AssertionError("整数网格完整域支撑/正定下界失败")
        audit = ag.audit_normal_rows(table,grid,H,b)
        model = io.SparseLut(grid,nodes)
        path = part / "model.slut"
        io.save_sparse(path,model)
        loaded = io.load_sparse(path)
        if not np.array_equal(loaded.nodes,nodes) or not all(np.array_equal(a,b) for a,b in zip(loaded.tables(),model.tables())):
            raise AssertionError("模型序列化往返改变权威表或节点")
        models[name] = loaded
        records[name] = {"fit":diagnostics,"normal_row_audit":audit,"model_sha256":digest(path),
            "model_bytes":path.stat().st_size,"minimum_axis_width":np.diff(grid,axis=1).min(axis=1).tolist(),
            "old_triplet_certificate":error_certificate.three_point_bound(model,triplet,targets)}
        write_json(part / "frozen-model.json",records[name])
    # 三方案均已冻结；以下是同一批完整验收，不按结果重拟合。
    for name,model in models.items():
        part = folder / name
        print(f"[{case['id']}/{name}] 完整256³及独立整数/原生复核",flush=True)
        cube = cube_evaluate(tables,ea.Operator([model]),part / "cube.rgb",128)
        if cube["reference_sha256"] != previous["final"]["baseline"]["cube"]["reference_sha256"]:
            raise AssertionError("完整参考流SHA与历史不同")
        records[name].update(cube=cube,native=native_verify([model],part,cube["prediction_sha256"],executable))
        new_worst = cube["hotspots"][0]["rgb"]
        records[name]["probes"] = probes(table,model,TRIPLETS[case["id"]]+[new_worst])
        write_json(part / "result.json",records[name])
        print(f"[{case['id']}/{name}] mean={cube['mean']:.6f}, p99={cube['p99']:.6f}, max={cube['max']:.6f}",flush=True)
    # 边界由完整域已保存输出读取；不再运行拟合或插值。
    ids = np.arange(256**3,dtype=np.int64)
    rgb = colours(ids)
    boundary = np.any((rgb == 0)|(rgb == 255),axis=1)
    points = rgb[boundary]
    truth = ea.source_apply(table,points)
    for name in models:
        pred = np.memmap(folder / name / "cube.rgb",np.uint8,mode="r",shape=(256**3,3))
        records[name]["boundary"] = ea.metrics(pred[boundary],truth)
    del rgb,ids,boundary,points,truth,pred
    print(f"[{case['id']}] 三个冻结模型统一执行100张历史照片",flush=True)
    photos = photos_evaluate(tables,{name:ea.Operator([model]) for name,model in models.items()})
    for name in models:
        records[name]["photos"] = photos[name]
        write_json(folder / name / "result.json",records[name])
    result = {"case":case,"sources":sources,"historical":{"model_sha256":expected,
        "cube":previous["final"]["baseline"]["cube"],"photos":previous["final"]["baseline"]["photos"],
        "old_triplet_certificate":error_certificate.three_point_bound(old,triplet,targets),
        "reused":True},"profiles":records,"scope":plan["limits"]}
    write_json(folder / "result.json",result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=ROOT / "experiments/tail-grid-v1.json")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--cache",type=Path,default=ROOT / "artifacts/chain-error-cache")
    parser.add_argument("--executable",type=Path,required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise ValueError("不覆盖已有运行；复现请使用新输出目录")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    parent = ROOT / plan["parent"]
    history = json.loads((parent / "results.json").read_text(encoding="utf-8"))
    parent_env = json.loads((parent / "environment.json").read_text(encoding="utf-8"))
    if digest(ROOT / "assets/photos/manifest.json") != parent_env["identity"]["image_manifest"]:
        raise ValueError("照片清单变化，不得复用历史逐图指标")
    # 新旧完整照片证据先绑定相同压缩字节和解码像素；后面的评估不承担此检查。
    for row in json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]:
        read_image(row)
    numba.set_num_threads(plan["threads"])
    metadata = environment(argparse.Namespace(sizes=[plan["m"]],screen_pixels=0,threads=plan["threads"],reps=0,extended=False))
    files = [Path(__file__),ROOT / "python/lutlab/axis_grid.py",ROOT / "python/lutlab/error_certificate.py",
        ROOT / "python/lutlab/error_analysis.py",ROOT / "python/lutlab/box.py",ROOT / "python/lutlab/fullfit.py",
        ROOT / "scripts/run_chain_error_study.py",ROOT / "scripts/run_joint_box_study.py",ROOT / "scripts/run_tail_repair.py"]
    metadata["identity"].update(plan_sha256=digest(args.plan),parent_files={p.name:digest(p) for p in
        [parent / name for name in ("results.json","environment.json","models-and-counterexamples.zip","archive-index.json")]},
        executable_sha256=digest(args.executable),full_fit=fullfit.trainer_fingerprint(),
        stage_source_sha256={str(p.relative_to(ROOT)):digest(p) for p in files})
    metadata["identity_sha256"] = study_provenance.identity_digest(metadata["identity"])
    metadata.update(backend="Numba4线程，完整矩原生4线程；验收标量/AVX2单线程",timing_scope="本轮不比较性能",deferred=["硬件优化","官方阈值","未知LUT泛化"])
    study_provenance.claim_run(out / "run.json",metadata)
    with zipfile.ZipFile(out / "measured-source.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for name,expected in {**metadata["identity"]["source_sha256"],**metadata["identity"]["stage_source_sha256"]}.items():
            raw = (ROOT / name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError("源码快照字节与运行身份不同")
            archive.writestr(name.replace("\\","/"),raw)
    results = []
    for case_id in plan["cases"]:
        previous = next(r for r in history["cases"] if r["case"]["id"] == case_id)
        results.append(process(previous,plan,out,args.cache.resolve(),args.executable.resolve(),parent))
    write_json(out / "results.json",{"run_identity":metadata["identity_sha256"],"cases":results})
    print("固定两例三方案批次完成；不提升默认配置",flush=True)


if __name__ == "__main__":
    main()
