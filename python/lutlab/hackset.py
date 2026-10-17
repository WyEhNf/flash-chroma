"""构造独立版本的压力输入；默认不拟合、不做全色域精度或性能扫描。"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image

from . import io

ROOT = Path(__file__).resolve().parents[2]
DEFINITION = ROOT / "datasets/problem16-hack-v1"
ASSETS = ROOT / "assets/hack-v1"
DEV_SEED = 2026101601
EVAL_SEED = 2026101691


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def file_sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def generator_sha():
    # Git 在不同系统的换行检出策略不应改变同一份生成器的身份。
    return sha(canonical({name: sha((Path(__file__).parent / name).read_bytes().replace(b"\r\n", b"\n"))
                          for name in ("hackset.py", "io.py")}))


def json_sha(path):
    return sha(canonical(json.loads(Path(path).read_text(encoding="utf-8"))))


def list_sha(path):
    return sha(("\n".join(Path(path).read_text(encoding="utf-8").splitlines()) + "\n").encode("utf-8"))


def publish(path, value):
    """已有不同内容即拒绝，防止把新生成器结果写进旧版本。"""
    path = Path(path)
    payload = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    publish_bytes(path, payload)


def publish_bytes(path, payload):
    path = Path(path)
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"版本化文件内容已变化，请使用新目录：{path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def op(name, **params):
    return {"op": name, **params}


def stage_rgb(stage, rgb):
    """固定整数算子，RGB8 输入与输出；浮点 gamma 由整数平方曲线代替。"""
    x = np.asarray(rgb)
    if x.dtype != np.uint8 or x.shape[-1:] != (3,):
        raise ValueError("算子输入必须为 RGB8")
    v = x.astype(np.int32)
    name = stage["op"]
    if name == "identity":
        return x.copy()
    if name == "invert":
        return x ^ np.array([255 if stage["mask"] & (1 << c) else 0 for c in range(3)], np.uint8)
    if name == "permute":
        return x[..., stage["axes"]].copy()
    if name == "gamma2":
        y = (v * v + 127) // 255
    elif name == "affine":
        n = v @ np.asarray(stage["matrix"], np.int32).T
        d = stage["denominator"]
        y = (2 * n + d) // (2 * d) + np.asarray(stage["bias"], np.int32)
    elif name == "step":
        y = v.copy()
        y[..., 1] += (v[..., 0] >= stage["cut"]) * stage["amplitude"]
    elif name == "pulse":
        y = v.copy()
        mask = (v[..., 0] >= stage["start"]) & (v[..., 0] < stage["start"] + stage["width"])
        y[..., 1] += mask * stage["amplitude"]
    elif name == "quantize":
        n = stage["levels"] - 1
        bins = (2 * v * n + 255) // 510
        y = (2 * bins * 255 + n) // (2 * n)
    elif name == "coupled_step":
        score = v @ np.asarray(stage["weights"], np.int32)
        y = v.copy()
        y[..., 2] += (score >= stage["cut"]) * stage["amplitude"]
    elif name == "compress":
        y = v // stage["divisor"] + stage["offset"]
    elif name == "checker":
        mask = ((v[..., 0] + v[..., 1] + v[..., 2] + stage["phase"]) & 1) * 255
        y = np.stack((mask, 255 - mask, mask), -1)
    elif name == "xor":
        y = np.stack((v[..., 0] ^ v[..., 1], v[..., 1] ^ v[..., 2], v[..., 2] ^ v[..., 0]), -1)
    elif name == "hashed_random":
        u = x.astype(np.uint32)
        key = (u[..., 0] << 16) | (u[..., 1] << 8) | u[..., 2]
        key = key ^ np.uint32(stage["seed"])
        key ^= key >> 16
        key *= np.uint32(0x7FEB352D)
        key ^= key >> 15
        key *= np.uint32(0x846CA68B)
        key ^= key >> 16
        return np.stack((key & 255, (key >> 8) & 255, (key >> 16) & 255), -1).astype(np.uint8)
    else:
        raise ValueError(f"未知压力算子：{name}")
    return np.clip(y, 0, 255).astype(np.uint8)


def chain_rgb(case, rgb):
    for stage in case["stages"]:
        rgb = stage_rgb(stage, rgb)
    return rgb


def isolated(stage):
    # 后两张不同的轴置换表互逆，复合后恰好暴露第二级算子。
    return [op("identity"), stage, op("permute", axes=[1, 2, 0]), op("permute", axes=[2, 0, 1])]


def case_spec(name, family, scope, stages, *, split="development", seed=DEV_SEED, **parameters):
    return {"id": name, "family": family, "scope": scope, "split": split, "seed": seed,
            "parameters": parameters, "stages": stages, "recipe_sha256": sha(canonical(stages)),
            "accuracy_status": "unmeasured", "official": False}


def definition():
    cases = [case_spec("identity-roundtrip", "baseline", "explainable_control",
                       [op("invert", mask=m) for m in (1, 2, 4, 7)])]
    for name, stage in (("channel-permutation", op("permute", axes=[2, 1, 0])),
                        ("invert", op("invert", mask=7)), ("smooth-gamma2", op("gamma2")),
                        ("smooth-ccm", op("affine", matrix=[[260, -4, 0], [0, 248, 8], [4, 0, 252]],
                                          denominator=256, bias=[0, 0, 0]))):
        cases.append(case_spec(name, "baseline", "explainable_control", isolated(stage)))
    cases.append(case_spec("highlight-clip", "clip_step", "isp_analogue",
                           isolated(op("affine", matrix=np.diag([3, 3, 3]).tolist(), denominator=2, bias=[-64] * 3))))
    for offset in (-1, 0, 1):
        cut = 128 + offset
        cases.append(case_spec(f"step-{cut}", "clip_step", "isp_stress",
                               isolated(op("step", cut=cut, amplitude=64)),
                               grid_sizes=[17, 33], nearest_integer_to_grid_node=128, offset=offset))
    cases.append(case_spec("staircase-17", "clip_step", "isp_stress", isolated(op("quantize", levels=17))))
    for width in (1, 2, 4):
        cases.append(case_spec(f"interior-peak-w{width}", "local_pulse", "representation_boundary",
                               isolated(op("pulse", start=122, width=width, amplitude=96)),
                               start=122, width=width, grid_sizes=[17, 33]))
    cases.append(case_spec("interior-valley-w2", "local_pulse", "representation_boundary",
                           isolated(op("pulse", start=122, width=2, amplitude=-96))))
    for name, weights, cut in (("coupled-sum", [1, 1, 0], 255), ("coupled-difference", [1, 0, -1], 0)):
        cases.append(case_spec(name, "cross_channel", "isp_stress",
                               isolated(op("coupled_step", weights=weights, cut=cut, amplitude=80)),
                               route_policy="require_byte_proof_before_separable_dispatch"))
    cases.append(case_spec("compress-amplify", "cascade", "isp_stress", [
        op("compress", divisor=4, offset=96),
        op("affine", matrix=np.diag([4] * 3).tolist(), denominator=1, bias=[-384] * 3),
        op("step", cut=128, amplitude=48), op("permute", axes=[2, 1, 0])]))
    cases.append(case_spec("clip-amplify", "cascade", "isp_stress", [
        op("affine", matrix=np.diag([2] * 3).tolist(), denominator=1, bias=[-64] * 3),
        op("compress", divisor=2, offset=32), op("gamma2"),
        op("affine", matrix=np.diag([3] * 3).tolist(), denominator=2, bias=[-24] * 3)]))
    for name, stage in (("checkerboard", op("checker", phase=0)), ("xor", op("xor")),
                        ("hashed-random", op("hashed_random", seed=DEV_SEED))):
        cases.append(case_spec(name, "high_frequency", "representation_boundary", isolated(stage)))
    # 预声明的另一套参数仅用于后续独立验收；本轮没有拟合或评价它们。
    for name, stage in (("step", op("step", cut=93, amplitude=57)),
                        ("peak", op("pulse", start=186, width=2, amplitude=83)),
                        ("valley", op("pulse", start=58, width=4, amplitude=-71)),
                        ("coupling", op("coupled_step", weights=[1, -1, 1], cut=173, amplitude=69)),
                        ("random", op("hashed_random", seed=EVAL_SEED))):
        cases.append(case_spec(f"reserved-{name}", name, "reserved_validation", isolated(stage),
                               split="reserved_validation", seed=EVAL_SEED))
    return {"schema": 1, "name": "problem16-hack-v1", "generator_sha256": generator_sha(),
            "metric": "rgb_l2_code_value", "dev_seed": DEV_SEED, "reserved_seed": EVAL_SEED,
            "cases": cases, "source_format": {"shape": [256, 256, 256, 3], "dtype": "uint8",
            "order": "RGB; R major, B minor; C contiguous", "bytes": io.FULL_NBYTES},
            "pilot_plan": {"status": "declared_not_executed", "grid": "uniform", "sizes": [17, 33],
                           "methods": ["sample", "ls_tetra_int"], "runtime": "tetra_q16",
                           "stages": 4, "accuracy_threshold": None, "performance_scan": False},
            "reference": "four_sequential_RGB8_lookups; every stage already quantized",
            "legacy_dataset_policy": "append_only; no change to corpus-v1, benchmark100 or casebook"}


def cube_block(start, end):
    axes = np.ogrid[start:end, :256, :256]
    return np.stack(np.broadcast_arrays(*axes), -1).astype(np.uint8)


def source_hashes(catalog, block=8):
    """仅流式构造源字节并哈希；不拟合或测量任何策略的精度。"""
    result = {}
    for case in catalog["cases"]:
        for stage in case["stages"]:
            key = sha(canonical(stage))
            if key in result:
                continue
            digest = hashlib.sha256()
            for start in range(0, 256, block):
                digest.update(stage_rgb(stage, cube_block(start, min(start + block, 256))).tobytes())
            result[key] = {"stage": stage, "sha256": digest.hexdigest(), "bytes": io.FULL_NBYTES}
    return result


def pixel_multiset(pixels):
    flat = pixels.reshape(-1, 3)
    keys = (flat[:, 0].astype(np.uint32) << 16) | (flat[:, 1].astype(np.uint32) << 8) | flat[:, 2]
    order = np.argsort(keys, kind="stable")
    return sha(flat[order].tobytes()), order


def layouts(frame, seed):
    flat = frame.reshape(-1, 3)
    rng = np.random.Generator(np.random.PCG64(seed))
    multiset, order = pixel_multiset(frame)
    return multiset, {"original": frame, "shuffled": flat[rng.permutation(len(flat))].reshape(frame.shape),
                      "grouped": flat[order].reshape(frame.shape)}


def image_record(path, frame, **metadata):
    if frame.shape != (768, 1024, 3) or frame.dtype != np.uint8:
        raise ValueError("压力图片必须为 1024×768 RGB8")
    # PPM 直接保存标准 RGB 字节，避免 PNG 编码库版本影响文件哈希。
    path = Path(path).resolve()
    publish_bytes(path, b"P6\n1024 768\n255\n" + frame.tobytes())
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": file_sha(path),
            "rgb_sha256": sha(frame.tobytes()), "size": [1024, 768], "mode": "RGB",
            "natural_photo": False, **metadata}


def make_images(directory):
    yy, xx = np.indices((768, 1024))
    frames = {
        "threshold-plane": np.stack((112 + xx % 33, yy % 256, np.full_like(xx, 127)), -1).astype(np.uint8),
        "interior-pulse": np.stack((120 + xx % 9, np.full_like(xx, 128), yy % 256), -1).astype(np.uint8),
        "coupled-slice": np.stack((xx % 256, yy % 256, (xx + yy) % 256), -1).astype(np.uint8),
        "parity-alternation": np.stack((xx % 256, yy % 256, (xx ^ yy) % 256), -1).astype(np.uint8),
    }
    records = []
    for number, (name, frame) in enumerate(frames.items()):
        multiset, variants = layouts(frame, DEV_SEED + number)
        for layout, pixels in variants.items():
            records.append(image_record(directory / f"{name}-{layout}.ppm", pixels,
                                         group=name, layout=layout, multiset_sha256=multiset,
                                         seed=DEV_SEED + number))
    for name, colours in (("pulse-flat", [[122, 128, 64]]), ("pulse-alternating", [[121, 128, 64], [122, 128, 64]])):
        frame = np.resize(np.asarray(colours, np.uint8), (768, 1024, 3))
        records.append(image_record(directory / f"{name}.ppm", frame, group=name, layout="diagnostic"))
    return records


def neighbourhood(colours):
    points = np.asarray(colours)
    if points.ndim != 2 or points.shape[1] != 3 or points.dtype.kind not in "iu" or np.any(points < 0) or np.any(points > 255):
        raise ValueError("热点必须为 [0,255] 内的整数 RGB 三元组")
    if not 1 <= len(points) <= 64:
        raise ValueError("一次应保存 1 至 64 个反例颜色")
    offsets = np.asarray(list(itertools.product((-1, 0, 1), repeat=3)), np.int32)
    return np.unique(np.clip(points[:, None, :] + offsets, 0, 255).reshape(-1, 3), axis=0).astype(np.uint8)


def scalar_oracle(models, rgb):
    """独立逐像素整数 oracle，不调用生产插值权重、向量化核或拟合器。"""
    output = []
    for pixel in np.asarray(rgb).reshape(-1, 3):
        colour = [int(v) for v in pixel]
        for model in models:
            indices, fractions = model.tables()
            cell = [int(indices[a, colour[a]]) for a in range(3)]
            f = [int(fractions[a, colour[a]]) for a in range(3)]
            axes = sorted(range(3), key=lambda a: (-f[a], a))
            vertices = [tuple(cell)]
            for axis in axes:
                cell = list(cell)
                cell[axis] += 1
                vertices.append(tuple(cell))
            ordered = [f[a] for a in axes]
            weights = [65536 - ordered[0], ordered[0] - ordered[1], ordered[1] - ordered[2], ordered[2]]
            colour = [(sum(w * int(model.nodes[vertex][c]) for w, vertex in zip(weights, vertices)) + 32768) // 65536
                      for c in range(3)]
        output.append(colour)
    return np.asarray(output, np.uint8).reshape(np.asarray(rgb).shape)


def replay_bundle(catalog, directory):
    """冻结一个采样漏峰候选及恒等控制；不宣称对全部方法不可表达。"""
    records = []
    for name in ("identity-roundtrip", "interior-peak-w1"):
        case = next(c for c in catalog["cases"] if c["id"] == name)
        folder = directory / name
        folder.mkdir(parents=True, exist_ok=True)
        grid = np.rint(io.uniform_grid(17))
        axis = np.rint(grid).astype(np.uint8)
        coordinates = np.stack(np.meshgrid(*axis, indexing="ij"), -1)
        paths, models = [], []
        for index, stage in enumerate(case["stages"], 1):
            model = io.SparseLut(grid, stage_rgb(stage, coordinates))
            path = folder / f"stage{index}.slut"
            # 先写临时内存文件的等价字节，保证发布后不会被重复构造覆盖。
            idx, frac = model.tables()
            payload = (b"SLUT" + struct.pack("<III", 1, 17, 0) + grid.astype("<f4").tobytes()
                       + idx.tobytes() + frac.astype("<u4").tobytes() + model.nodes.tobytes())
            publish_bytes(path, payload)
            models.append(io.load_sparse(path))
            paths.append({"path": path.relative_to(ROOT).as_posix(), "sha256": file_sha(path)})
        probes = neighbourhood([[122, 128, 64], [0, 0, 0], [255, 255, 255]])
        exact = chain_rgb(case, probes)
        oracle = scalar_oracle(models, probes)
        errors = ((exact.astype(np.int32) - oracle.astype(np.int32)) ** 2).sum(-1)
        record = {"case": name, "method": "sample_nearest_ties_to_even", "m": 17,
                  "grid": "rounded_uniform_integer; separate_from_unexecuted_pilot_plan",
                  "models": paths, "colours": probes.tolist(), "exact_rgb8": exact.tolist(),
                  "oracle_rgb8": oracle.tolist(), "squared_rgb_l2": errors.tolist(),
                  "scope": "固定颜色候选；没有运行完整色域，也未证明全局最小或其他拟合方法失败"}
        publish(folder / "replay.json", record)
        records.append({"path": (folder / "replay.json").relative_to(ROOT).as_posix(),
                        "sha256": file_sha(folder / "replay.json"), "case": name,
                        "nonzero_error_colours": int(np.count_nonzero(errors)), "max_squared_rgb_l2": int(errors.max())})
    return records


def build():
    catalog = definition()
    publish(DEFINITION / "catalog.json", catalog)
    hashes = source_hashes(catalog)
    for case in catalog["cases"]:
        values = [hashes[sha(canonical(s))]["sha256"] for s in case["stages"]]
        if len(set(values)) != 4:
            raise ValueError(f"四级源字节必须分别不同：{case['id']}")
    publish(DEFINITION / "sources.json", hashes)
    images = make_images(ASSETS / "images")
    replays = replay_bundle(catalog, ASSETS / "replay")
    natural = ROOT / "assets/photos/manifest.json"
    natural_manifest = json.loads(natural.read_text(encoding="utf-8"))
    natural_list = ROOT / "assets/photos/eval.txt"
    listing = ("\n".join(r["path"] for r in images) + "\n").encode("utf-8")
    publish_bytes(ASSETS / "stress.txt", listing)
    manifest = {"schema": 1, "catalog_sha256": file_sha(DEFINITION / "catalog.json"),
                "acceptance_sha256": file_sha(DEFINITION / "acceptance.json"),
                "sources_sha256": file_sha(DEFINITION / "sources.json"), "generator_sha256": generator_sha(),
                "source_hash_count": len(hashes), "full_lut_files_retained": False,
                "images": images, "stress_list_sha256": file_sha(ASSETS / "stress.txt"), "replays": replays,
                "natural_control": {"manifest": "assets/photos/manifest.json", "manifest_canonical_sha256": json_sha(natural),
                                    "list": "assets/photos/eval.txt", "list_lf_sha256": list_sha(natural_list),
                                    "count": len(natural_manifest["images"]), "used_for_tuning": False,
                                    "claim": "固定对照引用；未在本轮进行拟合精度验收，不宣称从未参与其他研究"},
                "numerical_evaluation": "fixed_replay_colours_only", "full_cube_or_pilot_evaluation": "not_run",
                "performance_evaluation": "not_run"}
    publish(DEFINITION / "manifest.json", manifest)
    return manifest


def inspect():
    """一次集中数据门禁，不执行拟合或计时循环。"""
    catalog = json.loads((DEFINITION / "catalog.json").read_text(encoding="utf-8"))
    manifest = json.loads((DEFINITION / "manifest.json").read_text(encoding="utf-8"))
    if catalog != definition() or file_sha(DEFINITION / "catalog.json") != manifest["catalog_sha256"]:
        raise ValueError("清单与当前生成器不一致，请新建版本")
    if file_sha(DEFINITION / "sources.json") != manifest["sources_sha256"]:
        raise ValueError("源哈希清单变化")
    if file_sha(DEFINITION / "acceptance.json") != manifest["acceptance_sha256"]:
        raise ValueError("冻结的验收口径变化")
    sources = json.loads((DEFINITION / "sources.json").read_text(encoding="utf-8"))
    expected_keys = {sha(canonical(stage)) for case in catalog["cases"] for stage in case["stages"]}
    if set(sources) != expected_keys:
        raise ValueError("源配方覆盖不完整")
    for key, row in sources.items():
        if sha(canonical(row["stage"])) != key or row["bytes"] != io.FULL_NBYTES or len(row["sha256"]) != 64:
            raise ValueError("源格式或配方身份不正确")
    for case in catalog["cases"]:
        if len({sources[sha(canonical(stage))]["sha256"] for stage in case["stages"]}) != 4:
            raise ValueError("四张源 LUT 字节重复")
    groups = {}
    for image in manifest["images"]:
        path = ROOT / image["path"]
        with Image.open(path) as decoded:
            if decoded.mode != "RGB" or decoded.size != (1024, 768):
                raise ValueError("压力图格式错误")
            pixels = np.asarray(decoded)
        if file_sha(path) != image["sha256"] or sha(pixels.tobytes()) != image["rgb_sha256"]:
            raise ValueError("压力图字节变化")
        if "multiset_sha256" in image:
            multiset, _ = pixel_multiset(pixels)
            if multiset != image["multiset_sha256"]:
                raise ValueError("布局改变了像素多重集")
            groups.setdefault(image["group"], set()).add(multiset)
    for group, values in groups.items():
        if len(values) != 1:
            raise ValueError(f"布局组不一致：{group}")
    control = manifest["natural_control"]
    if json_sha(ROOT / control["manifest"]) != control["manifest_canonical_sha256"] or list_sha(ROOT / control["list"]) != control["list_lf_sha256"]:
        raise ValueError("自然对照清单改变，应新建压力数据版本")
    natural = json.loads((ROOT / control["manifest"]).read_text(encoding="utf-8"))
    expected_paths = [row["evaluation"]["path"] for row in natural["images"]]
    if (ROOT / control["list"]).read_text(encoding="utf-8").splitlines() != expected_paths:
        raise ValueError("自然对照列表与来源不一致")
    for item in natural["images"]:
        record = item["evaluation"]
        if file_sha(ROOT / record["path"]) != record["sha256"]:
            raise ValueError("自然对照图片变化")
    if (ASSETS / "stress.txt").read_text(encoding="utf-8").splitlines() != [r["path"] for r in manifest["images"]]:
        raise ValueError("压力图片清单不一致")
    if file_sha(ASSETS / "stress.txt") != manifest["stress_list_sha256"]:
        raise ValueError("压力图片清单哈希不一致")
    for replay in manifest["replays"]:
        path = ROOT / replay["path"]
        if file_sha(path) != replay["sha256"]:
            raise ValueError("回放记录变化")
        record = json.loads(path.read_text(encoding="utf-8"))
        models = []
        for item in record["models"]:
            if file_sha(ROOT / item["path"]) != item["sha256"]:
                raise ValueError("回放模型变化")
            model = io.load_sparse(ROOT / item["path"])
            io.validate_sparse(model, competition=True)
            models.append(model)
        colours = np.asarray(record["colours"], np.uint8)
        case = next(c for c in catalog["cases"] if c["id"] == record["case"])
        if not np.array_equal(chain_rgb(case, colours), record["exact_rgb8"]):
            raise ValueError("完整参考与回放记录不一致")
        if not np.array_equal(scalar_oracle(models, colours), record["oracle_rgb8"]):
            raise ValueError("整数 oracle 与回放记录不一致")
        errors = ((np.asarray(record["exact_rgb8"], np.int32) - np.asarray(record["oracle_rgb8"], np.int32)) ** 2).sum(-1)
        if not np.array_equal(errors, record["squared_rgb_l2"]):
            raise ValueError("回放误差摘要变化")
        if (record["case"] == "identity-roundtrip" and np.any(errors)) or (record["case"] == "interior-peak-w1" and not np.any(errors)):
            raise ValueError("恒等控制或窄峰反例的预期不成立")
    return {"pass": True, "images": len(manifest["images"]), "layout_groups": len(groups),
            "natural_controls": len(natural["images"]), "replays": len(manifest["replays"]),
            "source_bytes_rehashed": False, "numerical_or_performance_scan": False}


def export_case(case_id, directory):
    """显式导出一个 case 的四张合法完整表；不隐式遍历整个实验矩阵。"""
    catalog = json.loads((DEFINITION / "catalog.json").read_text(encoding="utf-8"))
    if catalog != definition():
        raise ValueError("生成器变化，请新建版本")
    case = next((c for c in catalog["cases"] if c["id"] == case_id), None)
    if case is None:
        raise ValueError(f"未知 case：{case_id}")
    hashes = json.loads((DEFINITION / "sources.json").read_text(encoding="utf-8"))
    directory = Path(directory) / case_id
    directory.mkdir(parents=True, exist_ok=True)
    records = []
    for index, stage in enumerate(case["stages"], 1):
        expected = hashes[sha(canonical(stage))]
        path = directory / f"lut{index}.lut256"
        if not path.exists():
            temporary = path.with_suffix(".pending")
            with temporary.open("xb") as stream:
                for start in range(0, 256, 8):
                    stream.write(stage_rgb(stage, cube_block(start, start + 8)).tobytes())
            if file_sha(temporary) != expected["sha256"]:
                raise ValueError("源字节与已冻结哈希不符，保留 pending 文件排查")
            temporary.rename(path)
        if path.stat().st_size != io.FULL_NBYTES or file_sha(path) != expected["sha256"]:
            raise ValueError("已有源文件与清单不符")
        records.append({"path": path.name, "sha256": expected["sha256"], "bytes": io.FULL_NBYTES})
    result = {"case": case_id, "recipe_sha256": case["recipe_sha256"], "stages": records,
              "composition": "four_sequential_RGB8_lookups", "fit_status": "not_run"}
    publish(directory / "manifest.json", result)
    return result


def make_hotspots(path, directory):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("cube", payload).get("hotspots", [])
    colours = [row["rgb"] for row in rows]
    probes = neighbourhood(colours)
    folder = (Path(directory) / file_sha(path)[:20]).resolve()
    # 新反例保持显式目录，可回传现有 validation 的 cube.hotspots。
    if not folder.resolve().is_relative_to(ROOT):
        raise ValueError("反例输出目录必须位于项目内")
    publish_bytes(folder / "origin.json", Path(path).read_bytes())
    palette = np.resize(probes, (768, 1024, 3))
    multiset, variants = layouts(palette, DEV_SEED)
    images = [image_record(folder / f"{name}.ppm", pixels, layout=name, multiset_sha256=multiset)
              for name, pixels in variants.items()]
    result = {"origin_json_sha256": file_sha(path), "origin_report": "origin.json", "original_hotspots": colours,
              "neighbourhood": probes.tolist(), "images": images,
              "claim": "仅回放传入热点及 ±1 邻域；原报告的采样/色域范围仍需核实，不证明全局最坏或最小"}
    publish(folder / "manifest.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build", help="构造压力图、回放及源字节哈希，不运行拟合矩阵")
    commands.add_parser("inspect", help="集中核对已生成的清单、图片、回放及自然对照")
    export = commands.add_parser("export", help="只导出指定 case 的四张完整 RGB8 表")
    export.add_argument("--case", required=True)
    export.add_argument("--output", type=Path, default=ROOT / "data/hack-v1")
    hotspots = commands.add_parser("hotspots", help="从已有 hotspots 报告构造 ±1 邻域和同多重集图片")
    hotspots.add_argument("--input", type=Path, required=True)
    hotspots.add_argument("--output", type=Path, default=ROOT / "data/hack-v1-counterexamples")
    args = parser.parse_args(argv)
    if args.command == "build":
        result = build()
        result = {"images": len(result["images"]), "sources": result["source_hash_count"], "replays": len(result["replays"])}
    elif args.command == "inspect":
        result = inspect()
    elif args.command == "export":
        result = export_case(args.case, args.output)
    else:
        result = make_hotspots(args.input, args.output)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
