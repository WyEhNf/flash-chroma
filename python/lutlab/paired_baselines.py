"""复用冻结模型，重新测量m17/m33双基线及同尺寸、跨尺寸比较。"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io as text_io
import json
from pathlib import Path
import statistics
import subprocess
import time
from contextlib import redirect_stdout

import numba
import numpy as np
from PIL import Image

from . import io, interp, study_kernels, study_provenance
from .compatibility import KINDS, METRICS, PeakRSS, model_args, quality, write_json

ROOT = Path(__file__).resolve().parents[2]
SEED = 20261017


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT)).replace("\\", "/")


def publish(path, value):
    for attempt in range(6):
        try:
            write_json(path, value)
            return
        except PermissionError:
            if attempt == 5:
                raise
            time.sleep(.1 * (attempt+1))


def percentage_reduction(candidate, reference):
    """零基线没有定义相对降幅，保留空值及绝对差，不伪造百分比。"""
    return 100 * (1-candidate/reference) if reference != 0 else None


def select_pairs(report):
    records = {}
    for row in report["screen"]:
        if row["status"] != "ok":
            raise ValueError("输入包含失败配置，不能默默排除")
        key = (row["profile"], row["m"])
        if key in records:
            raise ValueError("同一LUT的profile/m必须唯一")
        records[key] = row
    profiles = sorted({row["profile"] for row in report["full"]} | {"sample_tetra"})
    for profile in {key[0] for key in records}:
        if any((profile,m) not in records for m in (17,33)):
            raise ValueError("同方法缺少m17或m33，不能跨尺寸配对")
    for profile in profiles:
        for m in (17,33):
            if (profile,m) not in records:
                raise ValueError("完整验证方法缺少配对模型")
    return records, profiles


def compare(rows, kind):
    """只在同一测量范围内按LUT/profile/m关联，禁止首行/模糊基线。"""
    index = {}
    scopes = {row["scope"] for row in rows}
    if len(scopes) != 1:
        raise ValueError("不得混合抽样与完整图片测量")
    for row in rows:
        key = (row["lut"], row["profile"], row["m"])
        if key in index:
            raise ValueError("比较键不唯一")
        index[key] = row
    results = []
    for row in rows:
        if kind == "same_size":
            target = (row["lut"], "sample_tetra", row["m"])
        elif kind == "small_vs_large_baseline":
            if row["m"] != 17:
                continue
            target = (row["lut"], "sample_tetra", 33)
        elif kind == "size_pair":
            if row["m"] != 33:
                continue
            target = (row["lut"], row["profile"], 17)
        else:
            raise ValueError("未知比较类型")
        if target not in index:
            raise ValueError("比较基线缺失："+str(target))
        base = index[target]
        result = {"lut":row["lut"], "source":row["source"], "scope":row["scope"], "comparison":kind,
            "profile":row["profile"], "m":row["m"], "reference_profile":base["profile"], "reference_m":base["m"],
            "mean":row["mean"], "reference_mean":base["mean"], "mean_delta":row["mean"]-base["mean"],
            "mean_reduction_percent":percentage_reduction(row["mean"],base["mean"]),
            "time_unit":row["time_unit"], "time":row["time"], "reference_time":base["time"],
            "time_ratio_candidate_over_reference":row["time"]/base["time"] if base["time"] else None,
            "node_bytes":row["node_bytes"], "reference_node_bytes":base["node_bytes"],
            "node_bytes_ratio":row["node_bytes"]/base["node_bytes"]}
        for name in ("rms","worst_image_p99","max"):
            result[name] = row[name]
            result["reference_"+name] = base[name]
            result[name+"_delta"] = row[name]-base[name]
        results.append(result)
    return results


def write_table(path, rows):
    if not rows:
        return
    with Path(path).open("w",newline="",encoding="utf-8-sig") as stream:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        writer = csv.DictWriter(stream,fields)
        writer.writeheader()
        writer.writerows(rows)


def flat_row(report, row):
    result = {"lut":report["lut"]["path"], "source":report["lut"]["source_id"],
        **{key:row[key] for key in ("profile","m","kernel","scope","node_bytes","serialized_bytes")},
        **row["quality"], "time_unit": "ms_per_image" if row["scope"] == "full_100_images" else "ms_per_409600_queries",
        "time":statistics.median(row["set_ms"])/(100 if row["scope"] == "full_100_images" else 1),
        "set_ms_1":row["set_ms"][0],"set_ms_2":row["set_ms"][1],"set_ms_3":row["set_ms"][2],
        "set_ms_min":min(row["set_ms"]),"set_ms_max":max(row["set_ms"]),
        "host_process_sampled_peak_rss_bytes":row["host_process_sampled_peak_rss_bytes"],
        "model_sha256":row["model_sha256"],"output_sha256":row["output_sha256"]}
    return result


def summarize(out):
    reports = [load_json(path) for path in sorted((out/"luts").glob("*/result.json"))]
    sizes = {}
    for stage in ("screen","full"):
        rows = [flat_row(report,row) for report in reports for row in report[stage]]
        sizes[stage] = len(rows)
        write_table(out/(stage+"-results.csv"),rows)
        if rows:
            for kind in ("same_size","small_vs_large_baseline","size_pair"):
                write_table(out/(stage+"-"+kind+".csv"),compare(rows,kind))
        if stage == "full":
            write_table(out/"baselines.csv",[r for r in rows if r["profile"] == "sample_tetra"])
            images = [{"lut":report["lut"]["path"],"profile":row["profile"],"m":row["m"],**image}
                for report in reports for row in report[stage] for image in row["per_image"]]
            write_table(out/"per-image.csv",images)
    progress = {"luts":len(reports), "screen_rows":sizes["screen"],"full_rows":sizes["full"],
        "baseline_rows":sum(row["profile"]=="sample_tetra" for r in reports for row in r["full"]),
        "screen_complete":sum(r.get("screen_complete",False) for r in reports),
        "full_complete":sum(r.get("full_complete",False) for r in reports)}
    publish(out/"progress.json",progress)
    return progress


def run(args):
    source = args.input.resolve()
    out = args.output.resolve()
    if source == out:
        raise ValueError("不得覆盖历史输入目录")
    original = [load_json(p) for p in sorted((source/"luts").glob("*/result.json"))]
    if args.limit:
        original = original[:args.limit]
    if not original:
        raise ValueError("没有冻结的LUT检查点")
    numba.set_num_threads(4)
    dummy = io.SparseLut(io.uniform_grid(17),np.zeros((17,17,17,3),np.uint8))
    study_kernels.map_pixels(np.zeros((1,3),np.uint8),*model_args(dummy),0)
    environment = study_provenance.environment_fingerprint()
    environment["numba_threading_layer"] = numba.threading_layer()
    environment["numba_threads"] = numba.get_num_threads()
    environment["numpy_cpu_features"] = np.core._multiarray_umath.__cpu_features__
    with redirect_stdout(text_io.StringIO()) as stream:
        np.show_config()
    environment["numpy_build"] = stream.getvalue()
    core_files = [Path(__file__),Path(study_kernels.__file__),Path(io.__file__),Path(interp.__file__),
                  Path(study_provenance.__file__),ROOT/"python/lutlab/compatibility.py"]
    plan = []
    for report in original:
        records, profiles = select_pairs(report)
        identifier = report["lut"]["sha256"][:12]
        plan.append({"lut":report["lut"],"old_result_sha256":digest(source/"luts"/identifier/"result.json"),
            "reference_sha256":report["reference_sha256"],"full_profiles":profiles,
            "models":{row["model"]:row["model_sha256"] for row in records.values()}})
    identity = {"schema":1,"input":relative(source),"old_run_sha256":digest(source/"run.json"),
        "lut_manifest_sha256":digest(ROOT/"assets/LUT/manifest.json"),
        "image_manifest_sha256":digest(ROOT/"assets/photos/manifest.json"),"plan":plan,
        "source_sha256":{relative(p):digest(p) for p in core_files},"environment":environment,
        "screen_pixels_per_image":4096,"sample_seed":20261016,"order_seed":SEED,"reps":3,
        "backend":"Numba LLVM CPU四线程，沿用冻结模型；计时全部新测，拟合未执行"}
    metadata = {"identity":identity,"identity_sha256":study_provenance.identity_digest(identity),
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "selection":"原188条完整结果冻结178个LUT/profile，不按新结果重选；均补齐两尺寸",
        "timing_scope":"预加载输入；含输出分配；不含解码/JIT/统计/拟合；预热后3次；抽样查询与完整100图分列"}
    study_provenance.claim_run(out/"run.json",metadata)
    print("核验全部源/照片/黄金表/模型，不改写旧记录",flush=True)
    checked = set()
    for entry in plan:
        path = ROOT/entry["lut"]["path"]
        if digest(path) != entry["lut"]["sha256"]:
            raise ValueError("原LUT哈希不一致")
        reference = source/"references"/(entry["lut"]["sha256"][:12]+".npy")
        if digest(reference) != entry["reference_sha256"]:
            raise ValueError("黄金表哈希不一致")
        for name,expected in entry["models"].items():
            if name not in checked:
                if digest(source/name) != expected:
                    raise ValueError("冻结模型哈希不一致")
                checked.add(name)
    manifest = load_json(ROOT/"assets/photos/manifest.json")["images"]
    frames = []
    for entry in manifest:
        path = ROOT/entry["evaluation"]["path"]
        if digest(path) != entry["evaluation"]["sha256"]:
            raise ValueError("图片哈希不一致")
        with Image.open(path) as frame:
            if frame.mode != "RGB" or frame.size != (1024,768):
                raise ValueError("图片尺寸/格式不符")
            frames.append(np.asarray(frame).reshape(-1,3))
    images = np.stack(frames)
    positions = np.random.default_rng(20261016).choice(1024*768,4096,replace=False)
    samples = np.ascontiguousarray(images[:,positions])
    study_kernels.image_metrics(samples[:1,:1],np.zeros((256**3,3),np.uint8),*model_args(dummy),0)
    publish(out/"validated-inputs.json",{"models":len(checked),"luts":len(plan),"images":len(manifest),
        "identity_sha256":metadata["identity_sha256"],"status":"ok"})
    stages = ("screen","full") if args.phase == "all" else (args.phase,)
    for stage in stages:
        batch = samples if stage == "screen" else images
        flat = batch.reshape(-1,3)
        for index, previous in enumerate(original):
            identifier = previous["lut"]["sha256"][:12]
            path = out/"luts"/identifier/"result.json"
            report = load_json(path) if path.exists() else {"lut":previous["lut"],"identity_sha256":metadata["identity_sha256"],"screen":[],"full":[]}
            if report["identity_sha256"] != metadata["identity_sha256"]:
                raise ValueError("检查点身份不一致")
            if report.get(stage+"_complete"):
                continue
            records, chosen = select_pairs(previous)
            profiles = sorted({key[0] for key in records}) if stage == "screen" else chosen.copy()
            rng = np.random.default_rng(SEED+index)
            rng.shuffle(profiles)
            targets = []
            for profile in profiles:
                for m in rng.permutation([17,33]):
                    targets.append(records[(profile,int(m))])
            truth = np.load(source/"references"/(identifier+".npy"),mmap_mode="r").reshape(-1,3)
            done = {(row["profile"],row["m"]) for row in report[stage]}
            for old in targets:
                if (old["profile"],old["m"]) in done:
                    continue
                model = io.load_sparse(source/old["model"])
                arguments = model_args(model)
                kind = KINDS[old["kernel"]]
                if kind == 0:
                    np.testing.assert_array_equal(study_kernels.map_pixels(flat[:1024],*arguments,kind),
                                                  interp.apply_tetra_q16(model,flat[:1024]))
                summary = study_kernels.image_metrics(batch,truth,*arguments,kind)
                metrics = quality(summary)
                if stage == "screen" and abs(metrics["mean"]-old["quality"]["mean"]) > 1e-10:
                    raise RuntimeError("新旧固定样本误差不同，不能默默混用模型")
                if stage == "full":
                    prediction = study_kernels.map_pixels(images[0],*arguments,kind).astype(np.int32)
                    rgb = images[0].astype(np.int32)
                    expected = truth[(rgb[:,0]*256+rgb[:,1])*256+rgb[:,2]].astype(np.int32)
                    distances = np.linalg.norm(prediction-expected,axis=1)
                    if abs(distances.mean()-summary[0,0]) > 1e-10 or abs(np.percentile(distances,99)-summary[0,2]) > 1e-10:
                        raise RuntimeError("独立NumPy完整图片统计不一致")
                study_kernels.map_pixels(flat[:1024],*arguments,kind)
                times = []
                with PeakRSS() as memory:
                    for _ in range(3):
                        start = time.perf_counter()
                        mapped = study_kernels.map_pixels(flat,*arguments,kind)
                        times.append((time.perf_counter()-start)*1000)
                row = {key:old[key] for key in ("profile","m","kernel","node_bytes","serialized_bytes","model","model_sha256")}
                row.update(scope="screen_4096_per_image" if stage=="screen" else "full_100_images",
                    quality=metrics,set_ms=times,output_sha256=hashlib.sha256(mapped.tobytes()).hexdigest(),
                    host_process_sampled_peak_rss_bytes=memory.peak,
                    per_image=[{"image":manifest[j]["id"],**{k:float(summary[j,i]) for i,k in enumerate(METRICS)}} for j in range(len(images))] if stage=="full" else [])
                report[stage].append(row)
                publish(path,report)
            report[stage+"_complete"] = True
            publish(path,report)
            # 完整配对后才输出汇总，缺一档时绝不自动换成另一档基线。
            progress = summarize(out)
            print(f"{stage} {index+1}/{len(original)}，抽样{progress['screen_rows']}，完整{progress['full_rows']}，基线{progress['baseline_rows']}",flush=True)
    print(json.dumps(summarize(out),ensure_ascii=False),flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=ROOT/"artifacts/local-lut-study/20261016")
    parser.add_argument("--output",type=Path,default=ROOT/"artifacts/lut-dual-baseline/20261017")
    parser.add_argument("--phase",choices=("all","screen","full"),default="all")
    parser.add_argument("--limit",type=int)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
