"""只读冻结完整流，定位固定照片选择集的尾部退化，不反馈训练。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numpy as np
from lutlab import error_analysis as ea, io
from run_chain_error_study import digest, encoded, cube_evaluate
from run_joint_box_study import photo_samples
from lutlab.compatibility import write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--plan",type=Path,default=ROOT / "experiments/full-photo-v1.json")
    parser.add_argument("--profiles",nargs="+",default=["control_mixed","grid_mixed"])
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("不覆盖已有反例说明")
    result = json.loads((args.input / "results.json").read_text(encoding="utf-8"))
    partition = json.loads((args.input / "photo-partition.json").read_text(encoding="utf-8"))
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    manifest = {r["id"]:r for r in json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]}
    rows = [manifest[r["id"]] for r in partition["guard"]["images"]]
    points,info = photo_samples(rows,plan)
    if info != partition["guard"]:
        raise ValueError("诊断像素与冻结选择集不同")
    indices = []
    for row in rows:
        seed = int.from_bytes(hashlib.sha256((str(plan["pixel_seed"])+":"+row["id"]).encode()).digest()[:8],"little")
        indices.append(np.random.default_rng(seed).choice(1024*768,plan["pixels_per_image"],replace=False))
    records = []
    for case in result["cases"]:
        cid = case["case"]["id"]
        source = ROOT / case["sources"][0]["path"]
        if digest(source) != case["sources"][0]["table_sha256"]:
            raise ValueError("完整参考表SHA变化")
        table = io.load_full(source,mmap=True)
        truth = table[points[:,0],points[:,1],points[:,2]]
        historical_path = args.input / cid / "historical.rgb"
        if not historical_path.exists():
            # 新时期可能只带版本化模型；恢复本目录缓存，不依赖旧忽略目录。
            model = io.load_sparse(args.input / cid / "historical.slut")
            cube_evaluate([table],ea.Operator([model]),historical_path,128)
        paths = {"historical":historical_path,**{n:args.input / cid / n / "cube.rgb" for n in args.profiles}}
        predictions = {}
        for name,path in paths.items():
            if path.stat().st_size != 256**3*3 or digest(path) != case["bank"][name]["cube"]["prediction_sha256"]:
                raise ValueError("诊断流SHA或长度变化")
            predictions[name] = np.memmap(path,np.uint8,mode="r",shape=(256**3,3))[encoded(points)]
            measured = ea.metrics(predictions[name],truth)
            if any(measured[k] != case["bank"][name]["guard"][k] for k in measured):
                raise AssertionError("冻结流复算的选择指标不同")
        old_d2 = np.sum((predictions["historical"].astype(np.int32)-truth)**2,axis=1)
        for name in args.profiles:
            new_d2 = np.sum((predictions[name].astype(np.int32)-truth)**2,axis=1)
            difference = new_d2-old_d2
            top,seen = [],set()
            for i in np.lexsort((encoded(points),-difference)):
                key = tuple(map(int,points[i]))
                if difference[i] <= 0 or len(top) == 8:
                    break
                if key in seen:
                    continue
                seen.add(key)
                image,sample = divmod(int(i),plan["pixels_per_image"])
                pixel = int(indices[image][sample])
                top.append({"rgb":list(key),"image":rows[image]["id"],"position_xy":[pixel%1024,pixel//1024],
                    "reference":truth[i].tolist(),"before":predictions["historical"][i].tolist(),
                    "after":predictions[name][i].tolist(),"before_squared":int(old_d2[i]),"after_squared":int(new_d2[i])})
            per_image = []
            for k,row in enumerate(rows):
                chunk = slice(k*plan["pixels_per_image"],(k+1)*plan["pixels_per_image"])
                per_image.append({"image":row["id"],"before":ea.metrics(predictions["historical"][chunk],truth[chunk]),
                    "after":ea.metrics(predictions[name][chunk],truth[chunk])})
            records.append({"case":cid,"profile":name,"guard_failed":case["selection_before_photos"]["failures"][name],
                "top_squared_increases":top,"per_image":per_image})
    write_json(args.output,{"input_results_sha256":digest(args.input / "results.json"),"source_sha256":digest(Path(__file__)),
        "guard_samples_sha256":info["samples_sha256"],"records":records,
        "scope":"后验诊断，同一冻结选择像素与完整流；缺少基线缓存时按版本化模型恢复并核对旧SHA，未重拟合或调门槛，不用完整100图反选模型"})
    print("固定选择像素与完整流指标复算一致，已保存尾部反例")


if __name__ == "__main__":
    main()
