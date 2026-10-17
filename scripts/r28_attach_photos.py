"""Attach the five versioned Kodak references without changing corpus-v1.

Checks original/evaluation bytes, RGB8 decoding, deterministic resizing and
content uniqueness. This registers image coverage, not model qualification or
an unseen source-family holdout. Original photographs and attribution stay in
assets/photos/kodak; only metadata and an explicit image cohort are added here.
"""
from __future__ import annotations

from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
import numpy as np
from PIL import Image
from lutlab import corpus,data,io
from lutlab.entry import _write_report


def main():
    source=ROOT/"assets/photos/kodak/manifest.json";manifest=json.loads(source.read_text(encoding="utf-8"))
    synthetic=json.loads((ROOT/"data/corpus-v1/images.json").read_text(encoding="utf-8"))
    seen={r["rgb_sha256"] for r in synthetic["records"]};records=[]
    for row in manifest["images"]:
        original=ROOT/row["original"]["path"];evaluation=ROOT/row["evaluation"]["path"]
        for kind,path in (("original",original),("evaluation",evaluation)):
            if path.stat().st_size!=row[kind]["bytes"] or corpus.digest_file(path)!=row[kind]["sha256"]:
                raise RuntimeError("upstream photographic bytes differ from provenance")
        rgb=io.load_image(evaluation);original_rgb=io.load_image(original)
        if rgb.shape!=(768,1024,3) or original_rgb.shape!=(512,768,3):raise RuntimeError("photograph dimensions differ")
        with Image.open(original) as image:
            if not np.array_equal(np.asarray(data._to_frame(image)),rgb):raise RuntimeError("evaluation image differs from recorded transformation")
        digest=hashlib.sha256(rgb.tobytes()).hexdigest()
        if digest in seen:raise RuntimeError("duplicate photographic RGB content")
        seen.add(digest);lo,hi=rgb.min(axis=-1),rgb.max(axis=-1)
        keys=(rgb[...,0].astype(np.uint32)<<16)|(rgb[...,1].astype(np.uint32)<<8)|rgb[...,2]
        records.append({"id":"kodak-"+row["id"],"source_family":"Kodak","scene":row["suggested_scene"],
            "natural_photo":True,"synthetic_augmentation":False,"intensity":"ordinary_exposure_as_supplied",
            "split":"external_reference_known_family","source_page":row["source_page"],"photographer":row["photographer"],
            "original":row["original"],"path":row["evaluation"]["path"],"file_sha256":row["evaluation"]["sha256"],"rgb_sha256":digest,
            "features":{"unique_rgb":int(np.unique(keys).size),"channel_min":rgb.min(axis=(0,1)).tolist(),
                "channel_max":rgb.max(axis=(0,1)).tolist(),"near_neutral_pixels":int(np.count_nonzero(hi-lo<=2)),
                "boundary_pixels":int(np.count_nonzero((lo==0)|(hi==255))),"shadow_pixels":int(np.count_nonzero(hi<=16)),
                "highlight_pixels":int(np.count_nonzero(lo>=239))}})
    folder=ROOT/"datasets/problem16-photos-v1";folder.mkdir(exist_ok=True)
    cohort="".join(r["path"]+"\n" for r in records)
    definition={"schema":1,"source_manifest_sha256":corpus.digest_file(source),"rights_note":manifest["rights_note"],
        "transform":manifest["transform"],"scope":__doc__,"images":records,
        "cohort_sha256":hashlib.sha256(cohort.encode()).hexdigest(),"image_count":5,
        "model_qualification_status":"not_executed_on_this_cohort","independent_family_holdout":False}
    catalog=folder/"catalog.json"
    if catalog.exists() and json.loads(catalog.read_text(encoding="utf-8"))!=definition:raise RuntimeError("photo catalog is immutable; create a new version")
    _write_report(catalog,definition);(folder/"reference5.txt").write_text(cohort,encoding="utf-8")
    _write_report(ROOT/"artifacts/r28-photos/inspection.json",{"finished_utc":datetime.now(timezone.utc).isoformat(),
        "source_sha256":{n:corpus.digest_file(ROOT/n) for n in ("scripts/r28_attach_photos.py","python/lutlab/data.py","python/lutlab/io.py")},
        "catalog_sha256":corpus.digest_file(catalog),"verified_images":5,"distinct_from_synthetic_v1":True,
        "model_tests_rerun":False,"pass":True})
    print(json.dumps({"verified_photographs":5,"combined_v1_images":325,"model_qualification_status":"not_executed_on_this_cohort"}))


if __name__=="__main__":main()
