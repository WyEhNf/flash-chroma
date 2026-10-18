"""完成后独立核对双尺寸覆盖、配对统计、原始计时和来源哈希。"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import struct

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def verify(path,expected):
    if digest(path)!=expected:
        raise ValueError("哈希不一致："+str(path))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=ROOT/"artifacts/lut-dual-baseline/20261017")
    args=parser.parse_args()
    out=args.input.resolve()
    meta=load(out/"run.json")
    identity=meta["identity"]
    assert hashlib.sha256(json.dumps(identity,sort_keys=True,allow_nan=False).encode()).hexdigest()==meta["identity_sha256"]
    for name,expected in identity["source_sha256"].items():
        verify(ROOT/name,expected)
    source=ROOT/identity["input"]
    verify(source/"run.json",identity["old_run_sha256"])
    verify(ROOT/"assets/LUT/manifest.json",identity["lut_manifest_sha256"])
    verify(ROOT/"assets/photos/manifest.json",identity["image_manifest_sha256"])
    models=set()
    for entry in identity["plan"]:
        lut=entry["lut"]
        identifier=lut["sha256"][:12]
        verify(ROOT/lut["path"],lut["sha256"])
        verify(source/"luts"/identifier/"result.json",entry["old_result_sha256"])
        verify(source/"references"/(identifier+".npy"),entry["reference_sha256"])
        for name,expected in entry["models"].items():
            if name not in models:
                verify(source/name,expected)
                models.add(name)
    photos=load(ROOT/"assets/photos/manifest.json")["images"]
    for image in photos:
        verify(ROOT/image["evaluation"]["path"],image["evaluation"]["sha256"])
    reports=[load(p) for p in sorted((out/"luts").glob("*/result.json"))]
    assert len(reports)==68 and len(models)==1788 and len(photos)==100
    count={"screen":0,"full":0}
    historical_quality_checks=historical_output_checks=0
    all_rows={"screen":{},"full":{}}
    for report in reports:
        assert report["screen_complete"] and report["full_complete"]
        assert report["identity_sha256"]==meta["identity_sha256"]
        historical=load(source/"luts"/report["lut"]["sha256"][:12]/"result.json")
        for stage in ("screen","full"):
            rows={(r["profile"],r["m"]):r for r in report[stage]}
            assert len(rows)==len(report[stage])
            assert ("sample_tetra",17) in rows and ("sample_tetra",33) in rows
            for previous in historical[stage]:
                current=rows[(previous["profile"],previous["m"])]
                for metric,value in previous["quality"].items():
                    assert abs(current["quality"][metric]-value)<1e-10,(stage,metric)
                    historical_quality_checks+=1
                if stage=="full":
                    assert current["output_sha256"]==previous["output_sha256"]
                    historical_output_checks+=1
            for (profile,m),row in rows.items():
                assert (profile,50-m) in rows
                assert len(row["set_ms"])==3 and all(t>0 for t in row["set_ms"])
                assert row["node_bytes"]==3*m**3
                verify(source/row["model"],row["model_sha256"])
                with (source/row["model"]).open("rb") as stream:
                    header=stream.read(16)
                assert header[:4]==b"SLUT" and struct.unpack("<III",header[4:])==(1,m,0)
                assert (source/row["model"]).stat().st_size==row["serialized_bytes"]
                key=(report["lut"]["path"],profile,m)
                all_rows[stage][key]=row
                if stage=="full":
                    assert len(row["per_image"])==100
                    assert [r["image"] for r in row["per_image"]]==[p["id"] for p in photos]
                    q=row["quality"]
                    assert abs(sum(r["mean"] for r in row["per_image"])/100-q["mean"])<1e-10
                    assert abs(math.sqrt(sum(r["rms"]**2 for r in row["per_image"])/100)-q["rms"])<1e-10
                    assert max(r["p99"] for r in row["per_image"])==q["worst_image_p99"]
                    assert max(r["max"] for r in row["per_image"])==q["max"]
            count[stage]+=len(rows)
    assert count=={"screen":2740,"full":356}
    counts={}
    required={"screen-results.csv":2740,"full-results.csv":356,"baselines.csv":136,
        "screen-same_size.csv":2740,"screen-small_vs_large_baseline.csv":1370,"screen-size_pair.csv":1370,
        "full-same_size.csv":356,"full-small_vs_large_baseline.csv":178,"full-size_pair.csv":178,
        "per-image.csv":35600,"baseline-pairs.csv":68}
    for name,expected in required.items():
        with (out/name).open(encoding="utf-8-sig",newline="") as stream:
            rows=list(csv.DictReader(stream))
        counts[name]=len(rows)
        assert len(rows)==expected,name
        if "same_size" in name or "size_pair" in name or "small_vs_large" in name:
            stage="screen" if name.startswith("screen") else "full"
            for row in rows:
                left=all_rows[stage][(row["lut"],row["profile"],int(row["m"]))]
                right=all_rows[stage][(row["lut"],row["reference_profile"],int(row["reference_m"]))]
                assert row["scope"]==left["scope"]==right["scope"]
                assert float(row["mean_delta"])==left["quality"]["mean"]-right["quality"]["mean"]
                divisor=100 if stage=="full" else 1
                assert float(row["time"])==statistics.median(left["set_ms"])/divisor
                assert float(row["reference_time"])==statistics.median(right["set_ms"])/divisor
                assert float(row["node_bytes_ratio"])==left["node_bytes"]/right["node_bytes"]
                reference=right["quality"]["mean"]
                if reference:
                    assert abs(float(row["mean_reduction_percent"])-100*(1-left["quality"]["mean"]/reference))<1e-10
                else:
                    assert row["mean_reduction_percent"]==""
    result={"status":"ok","luts":68,"images":100,"models":len(models),"measurements":count,
        "csv_rows":counts,"historical_quality_values_checked":historical_quality_checks,
        "historical_full_output_sha256_checked":historical_output_checks,
        "identity_sha256":meta["identity_sha256"],"audit_source_sha256":digest(Path(__file__))}
    (out/"audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
