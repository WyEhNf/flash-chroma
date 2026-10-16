"""合并数据的版本化索引；保留原身份、划分与测量资格。"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io as textio
import json
from pathlib import Path

import numpy as np
from PIL import Image

from . import corpus, hackextend as ext, hackset as h

DEFINITION = h.ROOT / "datasets/problem16-unified-v1"
INPUTS = ["datasets/problem16-v1/catalog.json", "datasets/problem16-axis-bins-v1/catalog.json",
          "datasets/problem16-unified-v1/legacy-identities.json", "datasets/problem16-unified-v1/composites.json",
          "report/data/r28/case-inventory.csv",
          "report/data/r28/image-inventory.csv", "datasets/problem16-photos-v1/catalog.json",
          "assets/photos/manifest.json", "assets/photos/eval.txt",
          "datasets/problem16-hack-v1/catalog.json", "datasets/problem16-hack-v1/sources.json",
          "datasets/problem16-hack-v1/manifest.json", "datasets/problem16-hack-v1/acceptance.json",
          "datasets/problem16-hack-v2/catalog.json", "datasets/problem16-hack-v2/sources.json",
          "datasets/problem16-hack-v2/manifest.json"]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def generator_sha():
    return h.sha(h.canonical({"dataset.py": h.sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n")),
                              "hack_v1": h.generator_sha(), "hack_v2": ext.generator_sha(),
                              "corpus.py": h.sha(Path(corpus.__file__).read_bytes().replace(b"\r\n", b"\n"))}))


def input_identity():
    result = {}
    for name in INPUTS:
        path = h.ROOT / name
        result[name] = h.json_sha(path) if path.suffix == ".json" else h.sha(path.read_bytes().replace(b"\r\n", b"\n"))
    return result


def csv_rows(path):
    return list(csv.DictReader(textio.StringIO(Path(path).read_text(encoding="utf-8-sig"))))


def safe_relative(value):
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or "\\" in str(value) or ":" in str(value):
        raise ValueError("统一清单只能使用项目相对路径")
    return path.as_posix()


def collect_cases():
    snapshot = DEFINITION / "legacy-identities.json"
    if not snapshot.exists():
        live = read_json(h.ROOT / "datasets/problem16-v1/casebook/index.json")
        h.publish(snapshot, {"schema": 1, "source_casebook": "datasets/problem16-v1/casebook/index.json",
                  "source_casebook_canonical_sha256_at_capture": h.json_sha(h.ROOT / "datasets/problem16-v1/casebook/index.json"),
                  "cases": {key: {"metadata": row["metadata"], "source_sha256": row["source_sha256"]}
                            for key, row in live["cases"].items()},
                  "scope": "只冻结源身份；不复制观测与冠军，原账本后续新增测量不会使数据定义失效"})
    book = read_json(snapshot)
    inventory = {r["case_id"]: r for r in csv_rows(h.ROOT / "report/data/r28/case-inventory.csv")}
    rows, attached = [], set()
    for namespace, path in (("corpus-v1", "datasets/problem16-v1/catalog.json"),
                            ("axis-bins-v1", "datasets/problem16-axis-bins-v1/catalog.json")):
        for case in read_json(h.ROOT / path)["cases"]:
            original = book["cases"][case["id"]]
            hashes = original["source_sha256"]
            snapshot = inventory.get(case["id"])
            if snapshot and hashes != snapshot["source_sha256"].split("|"):
                raise ValueError("旧源表身份与归档不一致")
            rows.append({"id": namespace + "--" + case["id"], "namespace": namespace,
                         "source_case_id": case["id"], "family": case["family"], "split": case["split"],
                         "seed": case["seed"], "definition_ref": path, "source_sha256": hashes,
                         "composite_sha256": snapshot["composite_sha256"] if snapshot else None,
                         "historical_casebook_key": case["id"], "quality_status": "historical_reference_only"})
            attached.add(case["id"])
    for case_id, original in book["cases"].items():
        if case_id in attached:
            continue
        rows.append({"id": "legacy--" + case_id, "namespace": "legacy", "source_case_id": case_id,
                     "family": original["metadata"]["family"], "split": original["metadata"]["split"],
                     "seed": original["metadata"]["seed"], "definition_ref": "datasets/problem16-unified-v1/legacy-identities.json",
                     "source_sha256": original["source_sha256"], "composite_sha256": None,
                     "historical_casebook_key": case_id, "quality_status": "historical_reference_only"})
    for namespace, folder in (("hack-v1", h.DEFINITION), ("hack-v2", ext.DEFINITION)):
        sources = read_json(folder / "sources.json")
        for case in read_json(folder / "catalog.json")["cases"]:
            rows.append({"id": namespace + "--" + case["id"], "namespace": namespace,
                         "source_case_id": case["id"], "family": case["family"], "split": case["split"],
                         "seed": case["seed"], "definition_ref": (folder / "catalog.json").relative_to(h.ROOT).as_posix(),
                         "source_sha256": [sources[h.sha(h.canonical(s))]["sha256"] for s in case["stages"]],
                         "composite_sha256": None, "historical_casebook_key": None,
                         "quality_status": "unmeasured"})
    for row in rows:
        values = row["source_sha256"]
        if not values or len(values) != 4 or len(set(values)) != 4 or any(len(v) != 64 for v in values):
            raise ValueError("合并源缺少四张不同完整表的身份")
        row["chain_sha256"] = h.sha(h.canonical(values))
    return rows


def composed_hashes():
    """仅为数据去重构造完整真值字节，不涉及稀疏模型精度。"""
    inputs = {name: h.json_sha(folder / "catalog.json")
              for name, folder in (("hack-v1", h.DEFINITION), ("hack-v2", ext.DEFINITION))}
    path = DEFINITION / "composites.json"
    if path.exists():
        record = read_json(path)
        if record["inputs"] != inputs or record["generator_sha256"] != generator_sha():
            raise ValueError("复合真值身份变化，请新建合并版本")
        return record["hashes"]
    hashes = {}
    for namespace, folder, apply in (("hack-v1", h.DEFINITION, h.chain_rgb),
                                      ("hack-v2", ext.DEFINITION, ext.chain_rgb)):
        for case in read_json(folder / "catalog.json")["cases"]:
            digest = hashlib.sha256()
            for start in range(0, 256, 8):
                digest.update(apply(case, h.cube_block(start, start + 8)).tobytes())
            hashes[namespace + "--" + case["id"]] = digest.hexdigest()
    h.publish(path, {"schema": 1, "inputs": inputs, "generator_sha256": generator_sha(), "hashes": hashes,
                     "scope": "完整RGB8源真值的字节身份，用于数据重复检查；不是稀疏拟合评价"})
    return hashes


def collect_images():
    rows = []
    def add(namespace, identifier, path, file_hash, rgb_hash, split, memberships):
        rows.append({"id": namespace + "--" + identifier, "namespace": namespace,
                     "source_image_id": identifier, "path": safe_relative(path), "file_sha256": file_hash,
                     "rgb_sha256": rgb_hash, "split": split, "memberships": memberships,
                     "size": [1024, 768], "mode": "RGB", "natural_photo": namespace in ("natural100", "photos-v1")})
    for row in csv_rows(h.ROOT / "report/data/r28/image-inventory.csv"):
        add("corpus-v1", row["id"], f"data/corpus-v1/images/{row['id']}.ppm", row["sha256"], row["rgb_sha256"],
            row["split"], ["corpus-v1", "corpus-" + row["split"]])
    for namespace, folder in (("hack-v1", h.DEFINITION), ("hack-v2", ext.DEFINITION)):
        for row in read_json(folder / "manifest.json")["images"]:
            add(namespace, Path(row["path"]).stem, row["path"], row["sha256"], row["rgb_sha256"],
                "stress_development", [namespace, "stress"])
            rows[-1].update({k: row[k] for k in ("group", "layout", "multiset_sha256") if k in row})
    for row in read_json(h.ROOT / "assets/photos/manifest.json")["images"]:
        ev = row["evaluation"]
        add("natural100", row["id"], ev["path"], ev["sha256"], ev["pixel_sha256"], "external_reference", ["natural100"])
    for row in read_json(h.ROOT / "datasets/problem16-photos-v1/catalog.json")["images"]:
        add("photos-v1", row["id"], row["path"], row["file_sha256"], row["rgb_sha256"],
            row["split"], ["photos-v1"])
    seen = {}
    for row in rows:
        row["canonical_id"] = seen.setdefault(row["rgb_sha256"], row["id"])
    return rows


def grouped_duplicates(rows, key):
    groups = defaultdict(list)
    for row in rows:
        if row.get(key):
            groups[row[key]].append(row)
    return [{"sha256": digest, "ids": [r["id"] for r in group], "splits": sorted({r["split"] for r in group})}
            for digest, group in groups.items() if len(group) > 1]


def split_conflicts(groups):
    held = {"holdout", "reserved_validation"}
    return [g for g in groups if held.intersection(g["splits"]) and set(g["splits"]) - held]


def build():
    cases, images = collect_cases(), collect_images()
    composites = composed_hashes()
    for row in cases:
        if row["id"] in composites:
            row["composite_sha256"] = composites[row["id"]]
    chains = grouped_duplicates(cases, "chain_sha256")
    targets = grouped_duplicates(cases, "composite_sha256")
    image_duplicates = grouped_duplicates(images, "rgb_sha256")
    conflicts = {"chains": split_conflicts(chains), "final_targets": split_conflicts(targets),
                 "images": split_conflicts(image_duplicates)}
    blocked_cases = {case_id for groups in (conflicts["chains"], conflicts["final_targets"]) for g in groups for case_id in g["ids"]}
    blocked_images = {image_id for g in conflicts["images"] for image_id in g["ids"]}
    for row in cases:
        row["selection_eligibility"] = "quarantined_split_overlap" if row["id"] in blocked_cases else "declared_split_only"
    for row in images:
        row["selection_eligibility"] = "quarantined_split_overlap" if row["id"] in blocked_images else "declared_split_only"
    by_id = {r["id"]: r for r in images}
    cohorts = {name: [r["id"] for r in images if name in r["memberships"]]
               for name in ("corpus-v1", "corpus-development", "corpus-calibration", "corpus-holdout",
                            "hack-v1", "hack-v2", "stress", "natural100", "photos-v1")}
    cohorts["all-inventory"] = [r["id"] for r in images if r["canonical_id"] == r["id"]]
    cohorts["development"] = [r["id"] for r in images if r["split"] in ("development", "stress_development")
                              and r["id"] not in blocked_images]
    legacy = read_json(h.ROOT / "datasets/problem16-v1/catalog.json")
    cohorts["benchmark100-legacy"] = ["corpus-v1--" + r["id"] for family in corpus.IMAGE_FAMILIES
        for intensity, seed in ((0, 0), (1, 1), (2, 2), (3, 3), (3, 2))
        for r in legacy["images"] if r["family"] == family and r["intensity"] == intensity and r["seed"] == seed]
    cohort_records = {}
    for name, ids in cohorts.items():
        paths = [by_id[identifier]["path"] for identifier in ids]
        path = DEFINITION / "cohorts" / f"{name}.txt"
        h.publish_bytes(path, ("\n".join(paths) + "\n").encode("utf-8"))
        cohort_records[name] = {"image_ids": ids, "count": len(ids), "unique_rgb_contents": len({by_id[i]["rgb_sha256"] for i in ids}),
                                "list": path.relative_to(h.ROOT).as_posix(), "list_sha256": h.file_sha(path),
                                "purpose": "inventory_only_includes_holdout" if name == "all-inventory" else "explicit_cohort"}
    record = {"schema": 1, "name": "problem16-unified-v1", "generator_sha256": generator_sha(),
              "inputs": input_identity(), "cases": cases, "images": images, "cohorts": cohort_records,
              "duplicates": {"chains": chains, "final_targets": targets, "image_rgb": image_duplicates},
              "split_conflicts": conflicts,
              "counts": {"cases": len(cases), "cases_by_namespace": dict(Counter(r["namespace"] for r in cases)),
                         "unique_ordered_source_chains": len({r["chain_sha256"] for r in cases}),
                         "cases_without_final_target_hash": sum(r["composite_sha256"] is None for r in cases),
                         "image_aliases": len(images), "unique_image_contents": len(cohorts["all-inventory"])},
              "metric": "rgb_l2_code_value", "accuracy_threshold": None,
              "legacy_casebook_policy": "reference_only; no new observations or automatic transfer of qualification",
              "legacy_matrix_denominator": 7917, "new_case_quality": "unmeasured",
              "limitations": ["完整源表不随Git重复分发；原合成图需显式重建", "只检查已知真值哈希，不声称没有未知最终变换重复",
                              "合并与新源真值哈希不是稀疏拟合精度或性能测试", "all-inventory包含留出图片，不能用作调参队列"]}
    h.publish(DEFINITION / "catalog.json", record)
    return record


def load():
    record = read_json(DEFINITION / "catalog.json")
    if record["inputs"] != input_identity() or record["generator_sha256"] != generator_sha():
        raise ValueError("合并索引依赖已变化，应追加新版本")
    return record


def inspect(verify_files=False):
    record = load()
    for kind in ("cases", "images"):
        ids = [r["id"] for r in record[kind]]
        if len(ids) != len(set(ids)):
            raise ValueError("命名空间标识冲突")
    by_id = {r["id"]: r for r in record["images"]}
    for cohort in record["cohorts"].values():
        path = h.ROOT / cohort["list"]
        if h.file_sha(path) != cohort["list_sha256"] or path.read_text(encoding="utf-8").splitlines() != [by_id[i]["path"] for i in cohort["image_ids"]]:
            raise ValueError("合并图片队列变化")
    missing, checked, checked_paths = [], 0, set()
    if verify_files:
        for row in record["images"]:
            path = h.ROOT / row["path"]
            identity = (row["path"], row["file_sha256"], row["rgb_sha256"])
            if identity in checked_paths:
                continue
            if not path.exists():
                missing.append(row["id"])
                continue
            if h.file_sha(path) != row["file_sha256"]:
                raise ValueError(f"合并图片文件变化：{row['id']}")
            with Image.open(path) as im:
                pixels = np.asarray(im)
                if im.mode != "RGB" or im.size != (1024, 768) or h.sha(pixels.tobytes()) != row["rgb_sha256"]:
                    raise ValueError("合并图片 RGB 内容变化")
                if "multiset_sha256" in row:
                    if h.pixel_multiset(pixels)[0] != row["multiset_sha256"]:
                        raise ValueError("扩展布局的像素多重集变化")
            checked_paths.add(identity)
            checked += 1
        if missing:
            raise FileNotFoundError(f"缺少 {len(missing)} 个图片别名，先显式 restore：{missing[:3]}")
    return {"pass": True, "metadata_verified": True, "image_files_verified": checked,
            "image_files_check_requested": verify_files, "counts": record["counts"],
            "split_conflict_groups": {k: len(v) for k, v in record["split_conflicts"].items()},
            "source_lut_bytes_rehashed": False, "fit_or_performance_scan": False}


def restore_images(cohort=None, image_id=None):
    record = load()
    by_id = {r["id"]: r for r in record["images"]}
    ids = [image_id] if image_id else record["cohorts"][cohort]["image_ids"]
    definitions = {r["id"]: r for r in read_json(h.ROOT / "datasets/problem16-v1/catalog.json")["images"]}
    restored = 0
    for identifier in ids:
        row = by_id[identifier]
        path = h.ROOT / row["path"]
        if path.exists():
            if h.file_sha(path) != row["file_sha256"]:
                raise ValueError("已有图片与冻结版本不同，拒绝覆盖")
            continue
        if row["namespace"] != "corpus-v1":
            raise FileNotFoundError(f"版本库图片缺失，请从Git恢复：{row['path']}")
        pixels = corpus.image(definitions[row["source_image_id"]])
        payload = b"P6\n1024 768\n255\n" + pixels.tobytes()
        if h.sha(payload) != row["file_sha256"] or h.sha(pixels.tobytes()) != row["rgb_sha256"]:
            raise ValueError("重构字节不同；使用原 NumPy 环境或新版本，不更新历史哈希")
        h.publish_bytes(path, payload)
        restored += 1
    return {"requested": len(ids), "restored": restored, "fit_or_performance_scan": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build", help="建立合并索引并检查源链/真值/图像重复")
    audit = commands.add_parser("inspect", help="核对统一清单；图片字节检查需显式启用")
    audit.add_argument("--verify-files", action="store_true")
    show = commands.add_parser("show", help="按保留的命名空间ID读取一个源case")
    show.add_argument("--case", required=True)
    export = commands.add_parser("export", help="按统一ID导出新增压力case的四张完整源表")
    export.add_argument("--case", required=True)
    export.add_argument("--output", type=Path, default=h.ROOT / "data/unified-v1")
    restore = commands.add_parser("restore", help="显式重建选定队列或单张原合成图，逐字节核对")
    selection = restore.add_mutually_exclusive_group(required=True)
    selection.add_argument("--cohort")
    selection.add_argument("--image")
    args = parser.parse_args(argv)
    if args.command == "build":
        result = build()["counts"]
    elif args.command == "inspect":
        result = inspect(args.verify_files)
    elif args.command == "restore":
        result = restore_images(args.cohort, args.image)
    else:
        result = next((r for r in load()["cases"] if r["id"] == args.case), None)
        if result is None:
            parser.error("不存在这个命名空间 case")
        if args.command == "export":
            exporters = {"hack-v1": h.export_case, "hack-v2": ext.export_case}
            if result["namespace"] not in exporters:
                parser.error("这个入口仅导出新增压力case；历史源仍使用原版本生成器或本机内容寻址对象")
            result = {"id": result["id"], "export": exporters[result["namespace"]](
                result["source_case_id"], args.output / result["namespace"])}
        else:
            definitions = read_json(h.ROOT / result["definition_ref"])["cases"]
            original = (definitions[result["source_case_id"]] if isinstance(definitions, dict) else
                        next(c for c in definitions if c["id"] == result["source_case_id"]))
            result = {**result, "original_definition": original}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
