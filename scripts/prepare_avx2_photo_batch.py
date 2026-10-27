"""把固定照片清单转换为紧密RGB8批次，供独立AVX2微基准使用。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", type=Path, default=ROOT / "assets/photos/eval.txt")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = [ROOT / line.strip() for line in args.list.read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    chunks, rows = [], []
    for path in paths:
        with Image.open(path) as image:
            rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
        payload = np.ascontiguousarray(rgb).tobytes()
        chunks.append(payload)
        rows.append({"path": path.relative_to(ROOT).as_posix(), "width": int(rgb.shape[1]),
                     "height": int(rgb.shape[0]), "bytes": len(payload), "sha256": digest(payload)})
    payload = b"".join(chunks)
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "photos.rgb").write_bytes(payload)
    manifest = {"schema_version": 1, "source_list": args.list.as_posix(), "images": rows,
                "image_count": len(rows), "pixels": len(payload) // 3, "bytes": len(payload),
                "sha256": digest(payload)}
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in ("image_count", "pixels", "bytes", "sha256")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
