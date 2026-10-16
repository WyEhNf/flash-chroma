"""从冻结模型重算抽样逐图指标，覆盖每个LUT×照片×已测配置。"""
import argparse
import csv
import json
from pathlib import Path
import sys

import numba
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import io, study_kernels
from lutlab.compatibility import digest, KINDS, model_args

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, required=True)
args = parser.parse_args()
out = args.input.resolve()
meta = json.loads((out / "run.json").read_text(encoding="utf-8"))
numba.set_num_threads(4)
count = meta["identity"]["screen_pixels_per_image"]
positions = np.random.default_rng(20261016).choice(1024*768,count,replace=False)
image_rows = json.loads((ROOT / "assets/photos/manifest.json").read_text(encoding="utf-8"))["images"]
frames = []
for image in image_rows:
    path = ROOT / image["evaluation"]["path"]
    if digest(path) != image["evaluation"]["sha256"]:
        raise ValueError("图片哈希不一致")
    with Image.open(path) as frame:
        frames.append(np.asarray(frame).reshape(-1,3)[positions])
images = np.stack(frames)
flat = images.reshape(-1,3)
codes = (flat[:,0].astype(np.int32)*256+flat[:,1])*256+flat[:,2]
fields = ["lut","source","profile","m","kernel","image","scope","pixels",
          "mean","rms","p99","max","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5"]
with (out / "screen-per-image.csv").open("w",newline="",encoding="utf-8-sig") as stream:
    writer = csv.DictWriter(stream, fields)
    writer.writeheader()
    total = 0
    for index,path in enumerate(sorted((out / "luts").glob("*/result.json"))):
        report = json.loads(path.read_text(encoding="utf-8"))
        table = np.load(out / "references" / (report["lut"]["sha256"][:12]+".npy"),mmap_mode="r").reshape(-1,3)
        truth = table[codes].astype(np.int32)
        for row in report["screen"]:
            if row["status"] != "ok":
                continue
            model_path = out / row["model"]
            if digest(model_path) != row["model_sha256"]:
                raise ValueError("模型哈希变化")
            model = io.load_sparse(model_path)
            prediction = study_kernels.map_pixels(flat,*model_args(model),KINDS[row["kernel"]])
            delta = prediction.astype(np.int32)-truth
            d2 = np.sum(delta*delta,axis=1).reshape(len(images),count)
            distances = np.sqrt(d2)
            mean = distances.mean(axis=1)
            if abs(float(mean.mean())-row["quality"]["mean"]) > 1e-10:
                raise RuntimeError("抽样重算与冻结结果不一致")
            rms = np.sqrt(d2.mean(axis=1))
            p99 = np.percentile(distances,99,axis=1)
            maximum = distances.max(axis=1)
            fractions = [(distances>=threshold).mean(axis=1) for threshold in (1,2,3,5)]
            for j,image in enumerate(image_rows):
                writer.writerow({"lut":report["lut"]["path"],"source":report["lut"]["source_id"],
                    "profile":row["profile"],"m":row["m"],"kernel":row["kernel"],"image":image["id"],
                    "scope":"screen_sample","pixels":count,"mean":mean[j],"rms":rms[j],"p99":p99[j],"max":maximum[j],
                    **{f"fraction_ge_{threshold}":fractions[k][j] for k,threshold in enumerate((1,2,3,5))}})
                total += 1
        print(f"逐图抽样重算{index+1}/68 LUT，已写{total}行",flush=True)
