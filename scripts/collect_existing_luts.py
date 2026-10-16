"""从固定版本的五个上游压缩包收集LUT，保留原始字节与授权，并检查结构。"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
from io import BytesIO, StringIO
import json
from pathlib import Path, PurePosixPath
import platform
import urllib.parse
import urllib.request
import zipfile

import numpy as np
import tifffile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/LUT"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect_lut(path: str, data: bytes) -> tuple[dict, str]:
    """只验证表示结构；不推断未知色彩空间，不修改数值。"""
    extension = Path(path).suffix.lower()
    if extension == ".cube":
        size, domain_min, domain_max = None, [0., 0., 0.], [1., 1., 1.]
        rows, copyrights = [], []
        for original in data.decode("utf-8-sig").splitlines():
            if "copyright" in original.lower():
                copyrights.append(original)
            line = original.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            if parts[0] == "TITLE":
                continue
            if parts[0] == "LUT_3D_SIZE":
                if size is not None or len(parts) != 2:
                    raise ValueError(f"重复或非法LUT尺寸：{path}")
                size = int(parts[1])
                continue
            if parts[0] in ("DOMAIN_MIN", "DOMAIN_MAX"):
                values = list(map(float, parts[1:]))
                if len(values) != 3:
                    raise ValueError(f"输入域维数错误：{path}")
                if parts[0] == "DOMAIN_MIN":
                    domain_min = values
                else:
                    domain_max = values
                continue
            if len(parts) != 3:
                raise ValueError(f"不支持的CUBE记录：{path}")
            rows.append(list(map(float, parts)))
        table = np.asarray(rows, dtype="<f8")
        if size is None or not 2 <= size <= 256 or table.shape != (size ** 3, 3):
            raise ValueError(f"CUBE行数与尺寸不符：{path}")
        low, high = np.asarray(domain_min), np.asarray(domain_max)
        if not np.all(np.isfinite([low, high])) or not np.all(high > low):
            raise ValueError(f"CUBE输入域错误：{path}")
        meta = {"format": "cube", "grid_size": size, "nodes": size ** 3,
                "domain_min": domain_min, "domain_max": domain_max,
                "output_min": table.min(axis=0).tolist(), "output_max": table.max(axis=0).tolist(),
                "embedded_copyright": copyrights}
        geometry = {k: meta[k] for k in ("format", "grid_size", "domain_min", "domain_max")}
    elif extension == ".3dl":
        lines = [line.split("#", 1)[0].strip() for line in data.decode("utf-8-sig").splitlines()]
        lines = [line for line in lines if line]
        grid = list(map(int, lines[0].split()))
        table = np.loadtxt(StringIO("\n".join(lines[1:])), dtype="<f8")
        size = len(grid)
        if size < 2 or not np.all(np.diff(grid) > 0) or table.shape != (size ** 3, 3):
            raise ValueError(f"3DL网格或行数错误：{path}")
        if np.any(table < 0) or not np.all(table == np.floor(table)):
            raise ValueError(f"3DL必须使用非负整数输出：{path}")
        meta = {"format": "3dl", "grid_size": size, "nodes": size ** 3, "input_grid": grid,
                "output_min": table.min(axis=0).tolist(), "output_max": table.max(axis=0).tolist()}
        geometry = {k: meta[k] for k in ("format", "grid_size", "input_grid")}
    elif extension in (".tif", ".tiff"):
        with tifffile.TiffFile(BytesIO(data)) as image:
            if len(image.pages) != 1 or image.pages[0].photometric.name != "RGB":
                raise ValueError(f"不是单页RGB HaldCLUT：{path}")
            table = image.asarray()
        if table.ndim != 3 or table.shape[2] != 3 or table.shape[0] != table.shape[1]:
            raise ValueError(f"HaldCLUT形状错误：{path}")
        level = round(table.shape[0] ** (1 / 3))
        if level < 2 or level ** 3 != table.shape[0] or table.dtype not in (np.uint8, np.uint16):
            raise ValueError(f"HaldCLUT级数或位深错误：{path}")
        meta = {"format": "hald_tiff", "image_size": [table.shape[1], table.shape[0]],
                "hald_level": level, "grid_size": level ** 2, "nodes": level ** 6,
                "dtype": table.dtype.name, "output_min": table.min(axis=(0, 1)).tolist(),
                "output_max": table.max(axis=(0, 1)).tolist()}
        geometry = {k: meta[k] for k in ("format", "grid_size", "dtype")}
    else:
        raise ValueError(f"不支持的LUT格式：{path}")
    if not np.all(np.isfinite(table)):
        raise ValueError(f"存在非有限输出：{path}")
    numeric_hash = sha(json.dumps(geometry, sort_keys=True).encode() + table.astype("<f8").tobytes())
    return meta, numeric_hash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True, help="已下载源包的版本清单")
    parser.add_argument("--download", action="store_true", help="缺少源包时按固定版本地址下载，再核对哈希")
    args = parser.parse_args()
    source_records = json.loads(args.sources.read_text(encoding="utf-8"))
    assets, sources = [], []
    for source in source_records:
        archive_path = ROOT / source["archive"]
        if not archive_path.exists():
            if not args.download:
                raise FileNotFoundError(f"缺少源包：{archive_path}；可使用--download下载")
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(source["archive_url"], archive_path)
        if sha(archive_path.read_bytes()) != source["archive_sha256"]:
            raise ValueError(f"源压缩包哈希不匹配：{source['id']}")
        relative_base = PurePosixPath("assets/LUT/sources") / source["id"]
        source_meta = {k: source[k] for k in ("id", "repo", "license", "commit", "archive_url",
                                             "archive_bytes", "archive_sha256")}
        source_meta["license_files"] = []
        with zipfile.ZipFile(archive_path) as archive:
            prefix = archive.namelist()[0].split("/", 1)[0] + "/"
            for name in source["license_files"]:
                payload = archive.read(prefix + name)
                destination = ROOT / str(relative_base / name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(payload)
                source_meta["license_files"].append({"path": destination.relative_to(ROOT).as_posix(),
                                                     "sha256": sha(payload)})
            if prefix + "README.md" in archive.namelist():
                payload = archive.read(prefix + "README.md")
                destination = ROOT / str(relative_base / "UPSTREAM_README.md")
                destination.write_bytes(payload)
                source_meta["upstream_readme"] = {"path": destination.relative_to(ROOT).as_posix(),
                                                   "sha256": sha(payload)}
            for name in sorted(source["assets"]):
                relative = relative_base / name
                destination = ROOT / str(relative)
                if not destination.resolve().is_relative_to(OUTPUT.resolve()):
                    raise ValueError("源文件路径超出assets/LUT")
                payload = archive.read(prefix + name)
                metadata, numeric_hash = inspect_lut(name, payload)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(payload)
                repo_url = f"https://github.com/{source['repo']}"
                assets.append({"path": relative.as_posix(), "source_id": source["id"],
                               "source_path": name, "source_commit": source["commit"],
                               "source_url": f"{repo_url}/blob/{source['commit']}/{urllib.parse.quote(name)}",
                               "license": source["license"], "bytes": len(payload),
                               "sha256": sha(payload), "numeric_sha256": numeric_hash, **metadata})
        sources.append(source_meta)
    groups = defaultdict(list)
    for asset in assets:
        groups[asset["numeric_sha256"]].append(asset["path"])
    manifest = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
                "count": len(assets), "source_counts": dict(Counter(a["source_id"] for a in assets)),
                "format_counts": dict(Counter(a["format"] for a in assets)),
                "numeric_unique_within_format": len(groups),
                "duplicate_groups": [paths for paths in groups.values() if len(paths) > 1],
                "numeric_hash_scope": "同格式、同网格及输入域的节点数值一致性；不证明不同格式或插值方式的函数等价",
                "generator": {"path": "scripts/collect_existing_luts.py", "python": platform.python_version(),
                              "sha256": sha(Path(__file__).read_bytes()),
                              "numpy": np.__version__, "tifffile": tifffile.__version__},
                "sources": sources, "assets": assets}
    (OUTPUT / "source-lock.json").write_text(json.dumps(source_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "luts.txt").write_text("".join(a["path"] + "\n" for a in assets), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("count", "source_counts", "format_counts",
                                              "numeric_unique_within_format", "duplicate_groups")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
