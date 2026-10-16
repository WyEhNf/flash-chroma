"""在保留 hack-v1 字节的前提下追加三维与串联压力配方。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

import numpy as np

from . import hackset as h, io

DEFINITION = h.ROOT / "datasets/problem16-hack-v2"
ASSETS = h.ROOT / "assets/hack-v2"
DEV_SEED, EVAL_SEED = 2026101602, 2026101692


def generator_sha():
    return h.sha(h.canonical({"hackextend.py": h.sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n")),
                              "hack_v1_generator": h.generator_sha()}))


def stage_rgb(stage, rgb):
    name = stage["op"]
    if name not in ("box_pulse", "oblique_slab", "coupled_wave", "block_parity"):
        return h.stage_rgb(stage, rgb)
    x = np.asarray(rgb)
    if x.dtype != np.uint8 or x.shape[-1:] != (3,):
        raise ValueError("扩展算子必须接收 RGB8")
    v = x.astype(np.int32)
    if name == "box_pulse":
        start = np.asarray(stage["start"], np.int32)
        mask = np.all((v >= start) & (v < start + stage["width"]), axis=-1)
        y = v + mask[..., None] * np.asarray(stage["delta"], np.int32)
    elif name == "oblique_slab":
        score = v @ np.asarray(stage["weights"], np.int32)
        mask = (score >= stage["start"]) & (score < stage["start"] + stage["width"])
        y = v + mask[..., None] * np.asarray(stage["delta"], np.int32)
    elif name == "coupled_wave":
        period = stage["period"]
        score = (v @ np.asarray(stage["weights"], np.int32) + stage["phase"]) % period
        triangle = period // 2 - np.abs(2 * score - period)
        shift = (triangle * stage["amplitude"]) // (period // 2)
        y = v.copy()
        y[..., 1] += shift
    else:
        mask = ((v // stage["period"]).sum(-1) + stage["phase"]) % 2
        y = v + mask[..., None] * np.asarray(stage["delta"], np.int32)
    return np.clip(y, 0, 255).astype(np.uint8)


def chain_rgb(case, rgb):
    for stage in case["stages"]:
        rgb = stage_rgb(stage, rgb)
    return rgb


def definition():
    cases = []
    def add(name, family, stage, *, stages=None, reserved=False, **parameters):
        cases.append(h.case_spec(name, family, "reserved_validation" if reserved else "stress_extension",
            h.isolated(stage) if stages is None else stages,
            split="reserved_validation" if reserved else "development",
            seed=EVAL_SEED if reserved else DEV_SEED, **parameters))
    for m, node in ((17, 4), (33, 23)):
        floor_node = node * 255 // (m - 1)
        for offset in (-1, 0, 1):
            cut = floor_node + offset
            add(f"grid-step-m{m}-cut{cut}", "grid_step_sweep", h.op("step", cut=cut, amplitude=48),
                m=m, node=node, node_numerator=node * 255, node_denominator=m - 1, offset_from_floor=offset)
    for width in (1, 2, 4):
        for sign, title in ((1, "peak"), (-1, "valley")):
            add(f"box-{title}-w{width}", "box_pulse",
                h.op("box_pulse", start=[122, 90, 202], width=width, delta=[64 * sign, -32 * sign, 48 * sign]))
    for width in (1, 2, 4):
        add(f"oblique-slab-w{width}", "oblique_slab",
            h.op("oblique_slab", weights=[1, 1, -1], start=123, width=width, delta=[0, 72, -24]))
    for period in (4, 16, 64):
        add(f"coupled-wave-p{period}", "coupled_wave",
            h.op("coupled_wave", weights=[1, 2, 3], phase=3, period=period, amplitude=24))
    for period in (1, 2, 4, 8):
        add(f"block-parity-p{period}", "block_parity", h.op("block_parity", period=period, phase=0, delta=[32, -16, 24]))
    for number, bias in enumerate(([0, 0, 0], [-1, 0, 1])):
        add(f"rounding-ties-{number}", "rounding_ties",
            h.op("affine", matrix=[[1, 1, 0], [0, 1, 1], [1, 0, 1]], denominator=2, bias=bias))
    for divisor in (2, 8):
        add(f"cascade-zoom-d{divisor}", "cascade_threshold_zoom", None, stages=[
            h.op("compress", divisor=divisor, offset=96), h.op("step", cut=112, amplitude=32),
            h.op("affine", matrix=np.diag([divisor] * 3).tolist(), denominator=1, bias=[-96 * divisor] * 3),
            h.op("permute", axes=[2, 1, 0])])
    for strength in (2, 4):
        add(f"gamut-fold-s{strength}", "gamut_fold",
            h.op("affine", matrix=[[256 + 32 * strength, -32 * strength, 0],
                                   [-16 * strength, 256 + 16 * strength, 0],
                                   [0, -32 * strength, 256 + 32 * strength]], denominator=256, bias=[0, 0, 0]))
    reserved = [
        ("grid-step", "grid_step_sweep", h.op("step", cut=76, amplitude=44)),
        ("box-peak", "box_pulse", h.op("box_pulse", start=[181, 57, 149], width=2, delta=[53, -27, 41])),
        ("slab", "oblique_slab", h.op("oblique_slab", weights=[2, -1, 1], start=180, width=3, delta=[19, 57, -21])),
        ("wave", "coupled_wave", h.op("coupled_wave", weights=[3, 1, 2], phase=7, period=32, amplitude=19)),
        ("parity", "block_parity", h.op("block_parity", period=2, phase=1, delta=[27, -19, 31])),
        ("ties", "rounding_ties", h.op("affine", matrix=[[1, 0, 1], [1, 1, 0], [0, 1, 1]], denominator=2, bias=[1, -1, 0])),
        ("clip", "gamut_fold", h.op("affine", matrix=[[300, -44, 0], [0, 294, -38], [-42, 0, 298]], denominator=256, bias=[0, 0, 0])),
        ("valley", "box_pulse", h.op("box_pulse", start=[67, 173, 38], width=3, delta=[-43, 29, -31])),
    ]
    for name, family, stage in reserved:
        add("reserved-" + name, family, stage, reserved=True)
    return {"schema": 1, "name": "problem16-hack-v2", "generator_sha256": generator_sha(),
            "cases": cases, "metric": "rgb_l2_code_value", "dev_seed": DEV_SEED,
            "reserved_seed": EVAL_SEED, "acceptance_reference": "datasets/problem16-hack-v1/acceptance.json",
            "scope": "追加数据定义与源字节；没有拟合、精度门槛或性能扫描"}


def layouts(frame, seed):
    """按固定 uint32 双射的键排序，实现不依赖 RNG 置换实现的重排。"""
    flat = frame.reshape(-1, 3)
    key = np.arange(len(flat), dtype=np.uint32) ^ np.uint32(seed)
    key ^= key >> 16
    key *= np.uint32(0x7FEB352D)
    key ^= key >> 15
    key *= np.uint32(0x846CA68B)
    key ^= key >> 16
    multiset, grouped = h.pixel_multiset(frame)
    return multiset, {"original": frame, "shuffled": flat[np.argsort(key)].reshape(frame.shape),
                      "grouped": flat[grouped].reshape(frame.shape)}


def make_images():
    yy, xx = np.indices((768, 1024))
    frames = {f"box-slice-b{blue}": np.stack((120 + xx % 9, 88 + yy % 9, np.full_like(xx, blue)), -1).astype(np.uint8)
              for blue in (201, 202, 203)}
    frames.update({
        "oblique-plane": np.stack((xx % 256, yy % 256, np.full_like(xx, 128)), -1).astype(np.uint8),
        "periodic-coupling": np.stack((xx % 256, yy % 256, (2 * xx + yy) % 256), -1).astype(np.uint8),
        "gamut-clip": np.stack((xx % 256, yy % 256, 255 - xx % 256), -1).astype(np.uint8),
        "dark-rounding": np.stack((xx % 24, yy % 24, (xx + yy) % 24), -1).astype(np.uint8),
    })
    images = []
    for number, (name, frame) in enumerate(frames.items()):
        multiset, variants = layouts(frame, DEV_SEED + number)
        for layout, pixels in variants.items():
            images.append(h.image_record(ASSETS / "images" / f"{name}-{layout}.ppm", pixels,
                group=name, layout=layout, multiset_sha256=multiset, seed=DEV_SEED + number))
    return images


def make_replay(catalog):
    case = next(c for c in catalog["cases"] if c["id"] == "coupled-wave-p64")
    folder = ASSETS / "replay/coupled-wave-p64"
    grid = np.rint(io.uniform_grid(17))
    coordinates = np.stack(np.meshgrid(*grid.astype(np.uint8), indexing="ij"), -1)
    models, paths = [], []
    for number, stage in enumerate(case["stages"], 1):
        model = io.SparseLut(grid, stage_rgb(stage, coordinates))
        idx, frac = model.tables()
        payload = (b"SLUT" + struct.pack("<III", 1, 17, 0) + grid.astype("<f4").tobytes()
                   + idx.tobytes() + frac.astype("<u4").tobytes() + model.nodes.tobytes())
        path = folder / f"stage{number}.slut"
        h.publish_bytes(path, payload)
        models.append(io.load_sparse(path))
        paths.append({"path": path.relative_to(h.ROOT).as_posix(), "sha256": h.file_sha(path)})
    colours = h.neighbourhood([[0, 0, 0], [255, 255, 255], [122, 90, 202], [127, 128, 129],
                              [16, 32, 48], [64, 96, 128], [123, 123, 123]])
    exact, oracle = chain_rgb(case, colours), h.scalar_oracle(models, colours)
    record = {"case": case["id"], "grid": "rounded_uniform_integer", "m": 17,
              "method": "sample_nearest_ties_to_even", "models": paths, "colours": colours.tolist(),
              "exact_rgb8": exact.tolist(), "oracle_rgb8": oracle.tolist(),
              "squared_rgb_l2": ((exact.astype(np.int32) - oracle.astype(np.int32)) ** 2).sum(-1).tolist(),
              "required_second_stage_path": "tetra", "scope": "固定探针的耦合回放，不是全色域精度验收"}
    h.publish(folder / "replay.json", record)
    return {"path": (folder / "replay.json").relative_to(h.ROOT).as_posix(),
            "sha256": h.file_sha(folder / "replay.json"), "colours": len(colours)}


def build():
    catalog = definition()
    sources = {}
    previous = json.loads((h.DEFINITION / "sources.json").read_text(encoding="utf-8"))
    for case in catalog["cases"]:
        for stage in case["stages"]:
            key = h.sha(h.canonical(stage))
            if key in sources:
                continue
            if key in previous:
                sources[key] = previous[key]
                continue
            digest = hashlib.sha256()
            for start in range(0, 256, 8):
                digest.update(stage_rgb(stage, h.cube_block(start, start + 8)).tobytes())
            sources[key] = {"stage": stage, "sha256": digest.hexdigest(), "bytes": io.FULL_NBYTES}
    for case in catalog["cases"]:
        if len({sources[h.sha(h.canonical(s))]["sha256"] for s in case["stages"]}) != 4:
            raise ValueError("新增 case 的四张源 LUT 不应字节相同")
    images = make_images()
    replay = make_replay(catalog)
    h.publish(DEFINITION / "catalog.json", catalog)
    h.publish(DEFINITION / "sources.json", sources)
    h.publish_bytes(ASSETS / "stress.txt", ("\n".join(r["path"] for r in images) + "\n").encode("utf-8"))
    record = {"schema": 1, "catalog_sha256": h.file_sha(DEFINITION / "catalog.json"),
              "sources_sha256": h.file_sha(DEFINITION / "sources.json"), "generator_sha256": generator_sha(),
              "acceptance_canonical_sha256": h.json_sha(h.DEFINITION / "acceptance.json"),
              "sources": len(sources), "images": images, "replay": replay,
              "stress_list_sha256": h.file_sha(ASSETS / "stress.txt"),
              "full_cube_fit_accuracy": "not_run", "performance_scan": "not_run"}
    h.publish(DEFINITION / "manifest.json", record)
    return record


def export_case(case_id, directory):
    catalog = json.loads((DEFINITION / "catalog.json").read_text(encoding="utf-8"))
    if catalog != definition():
        raise ValueError("扩展生成器已变化，请使用新版本")
    case = next((c for c in catalog["cases"] if c["id"] == case_id), None)
    if case is None:
        raise ValueError("未知扩展 case")
    sources = json.loads((DEFINITION / "sources.json").read_text(encoding="utf-8"))
    folder = Path(directory) / case_id
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for number, stage in enumerate(case["stages"], 1):
        path = folder / f"lut{number}.lut256"
        expected = sources[h.sha(h.canonical(stage))]
        if not path.exists():
            temporary = path.with_suffix(".pending")
            with temporary.open("xb") as stream:
                for start in range(0, 256, 8):
                    stream.write(stage_rgb(stage, h.cube_block(start, start + 8)).tobytes())
            if h.file_sha(temporary) != expected["sha256"]:
                raise ValueError("新增源表哈希不符；保留 pending 文件")
            temporary.rename(path)
        if path.stat().st_size != io.FULL_NBYTES or h.file_sha(path) != expected["sha256"]:
            raise ValueError("源字节与冻结版本不同")
        records.append({"path": path.name, "sha256": expected["sha256"], "bytes": io.FULL_NBYTES})
    result = {"case": case_id, "stages": records, "fit_status": "not_run"}
    h.publish(folder / "manifest.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build", help="追加源哈希与压力图片，不运行拟合")
    export = commands.add_parser("export", help="显式导出单个 case 的四张完整源表")
    export.add_argument("--case", required=True)
    export.add_argument("--output", type=Path, default=h.ROOT / "data/hack-v2")
    args = parser.parse_args(argv)
    if args.command == "build":
        result = build()
        result = {"cases": len(definition()["cases"]), "sources": result["sources"], "images": len(result["images"])}
    else:
        result = export_case(args.case, args.output)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
