"""固定R连续8色、RGB基值加2+2+1差分的唯一离线筛查；不加载候选、不构建、不测性能。"""
from __future__ import annotations
import datetime
import hashlib
import json
import os
import platform
import sys
import traceback
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
N = 1 << 24
BLOCKS = N // 8
MASK = np.uint64(0xffffff)
GATE = {"exception_packet8_fraction_max": 0.05,
        "any_image_exception_packet8_fraction_max": 0.20,
        "exception_pool_bytes_max": 2 << 20}
REASONS = ["base_R_outside_0_255", "base_G_outside_0_255", "base_B_outside_0_255",
           "base_RGB_equals_ffffff", "delta_R_outside_0_3",
           "delta_G_minus_R_outside_0_3", "delta_B_minus_R_outside_0_1"]


def digest(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def packed_rgb(a):
    x = a.astype(np.uint32)
    return x[..., 0] | (x[..., 1] << 8) | (x[..., 2] << 16)


def rgb_bytes(x):
    return np.stack((x & 255, (x >> 8) & 255, (x >> 16) & 255), axis=-1).astype(np.uint8)


def update_range(target, name, values):
    if values.size:
        lo, hi = int(values.min()), int(values.max())
        previous = target.setdefault(name, [lo, hi])
        previous[0], previous[1] = min(previous[0], lo), max(previous[1], hi)


def analyze(protocol):
    assert protocol["script_sha256"] == digest(__file__)
    assert protocol["gate"] == GATE
    assert protocol["encoding"]["delta_bits"] == [2, 2, 1]
    assert protocol["encoding"]["input_block_pixels"] == 8
    assert protocol["attempt_policy"]["maximum_analysis_executions"] == 1
    sources = {}
    for name, spec in protocol["inputs"].items():
        path = ROOT / spec["path"]
        actual = digest(path)
        assert actual == spec["sha256"], (name, actual)
        assert path.stat().st_size == spec["bytes"]
        sources[name] = path
    history = read(OUT / "history.json")
    assert digest(OUT / "history.json") == protocol["history_sha256"]
    assert not history["direct_equivalent_found"]
    for spec in history["sources"]:
        assert digest(ROOT / spec["path"]) == spec["sha256"]

    # cache-gold仅独立确认230项原始输出集合；编码和解码均直接使用RGB，不重新编号221项。
    palette = np.unique(np.fromfile(sources["cache_gold"], dtype="<u4"))
    assert len(palette) == 230 and np.all(palette <= 0xffffff)
    old_palette = np.fromfile(sources["old_palette_crosscheck"], dtype="<u4")
    assert len(old_palette) == 256 and np.array_equal(old_palette[:230], palette)
    assert np.all(old_palette[230:] == 0)
    generation = read(sources["cache_generation"])
    assert generation["generation_completed"]
    assert generation["gold_sha256"] == protocol["inputs"]["cache_gold"]["sha256"]

    cube = np.memmap(sources["cube"], dtype=np.uint8, mode="r", shape=(256, 256, 256, 3))
    linear = np.empty((256, 256, 256), dtype="<u4")
    frequencies = np.zeros(230, dtype=np.int64)
    for r in range(256):
        rgb = packed_rgb(cube[r])
        ids = np.searchsorted(palette, rgb)
        assert ids.max() < 230 and np.array_equal(palette[ids], rgb)
        frequencies += np.bincount(ids.ravel(), minlength=230)
        # cube原次序为[R,G,B]；实际地址为[B,G,R]即R低字节。
        linear[:, :, r] = rgb.T
    linear = linear.ravel()
    members = linear.reshape(BLOCKS, 8)
    words = np.empty(BLOCKS, dtype="<u8")
    pool_storage = np.empty((BLOCKS, 8), dtype="<u4")
    pool_count = 0
    reason_histogram = np.zeros(1 << len(REASONS), dtype=np.int64)
    ranges = {}
    span_histograms = {name: np.zeros(511, dtype=np.int64) for name in ("R", "G_minus_R", "B_minus_R")}
    normal_blocks = 0
    base_white_blocks = 0
    all_white_blocks = 0
    for first in range(0, BLOCKS, 65536):
        stop = min(first + 65536, BLOCKS)
        values = members[first:stop]
        rr = (values & 255).astype(np.int32)
        gg = ((values >> 8) & 255).astype(np.int32)
        bb = ((values >> 16) & 255).astype(np.int32)
        dg, db = gg - rr, bb - rr
        br, bdg, bdb = rr.min(axis=1), dg.min(axis=1), db.min(axis=1)
        bg, bblue = br + bdg, br + bdb
        dr, ddg, ddb = rr - br[:, None], dg - bdg[:, None], db - bdb[:, None]
        white = (br == 255) & (bg == 255) & (bblue == 255)
        reasons = [(br < 0) | (br > 255), (bg < 0) | (bg > 255),
                   (bblue < 0) | (bblue > 255), white,
                   np.any((dr < 0) | (dr > 3), axis=1),
                   np.any((ddg < 0) | (ddg > 3), axis=1),
                   np.any((ddb < 0) | (ddb > 1), axis=1)]
        reason_code = np.zeros(stop - first, dtype=np.uint8)
        for bit, failed in enumerate(reasons):
            reason_code |= failed.astype(np.uint8) << bit
        reason_histogram += np.bincount(reason_code, minlength=len(reason_histogram))
        exceptional = reason_code != 0
        good = ~exceptional
        good_count, bad_count = int(good.sum()), int(exceptional.sum())
        normal_blocks += good_count
        base_white_blocks += int(white.sum())
        all_white_blocks += int(np.all(values == 0xffffff, axis=1).sum())
        for name, array in (("source_R", rr), ("source_G", gg), ("source_B", bb),
                            ("G_minus_R", dg), ("B_minus_R", db), ("base_R", br),
                            ("base_G", bg), ("base_B", bblue), ("base_DG", bdg),
                            ("base_DB", bdb), ("delta_R", dr), ("delta_DG", ddg), ("delta_DB", ddb)):
            update_range(ranges, name, array)
        for name, array in (("normal_base_R", br), ("normal_base_G", bg), ("normal_base_B", bblue)):
            update_range(ranges, name, array[good])
        for name, array in (("R", dr), ("G_minus_R", ddg), ("B_minus_R", ddb)):
            span_histograms[name] += np.bincount(array.max(axis=1), minlength=511)
        encoded = np.zeros(stop - first, dtype=np.uint64)
        if good_count:
            base = br[good].astype(np.uint64) | (bg[good].astype(np.uint64) << 8) | (bblue[good].astype(np.uint64) << 16)
            codes = dr[good].astype(np.uint64) | (ddg[good].astype(np.uint64) << 2) | (ddb[good].astype(np.uint64) << 4)
            for k in range(8):
                base |= codes[:, k] << np.uint64(24 + 5 * k)
            encoded[good] = base
        if bad_count:
            ordinals = np.arange(pool_count, pool_count + bad_count, dtype=np.uint64)
            assert int(ordinals[-1]) < (1 << 40)
            encoded[exceptional] = MASK | (ordinals << 24)
            pool_storage[pool_count:pool_count + bad_count] = values[exceptional]
            pool_count += bad_count
        words[first:stop] = encoded
    pool = pool_storage[:pool_count]
    assert normal_blocks + pool_count == BLOCKS
    assert int(reason_histogram[0]) == normal_blocks and int(reason_histogram[1:].sum()) == pool_count
    sentinels = (words & MASK) == MASK
    assert int(sentinels.sum()) == pool_count
    assert np.array_equal(words[sentinels] >> 24, np.arange(pool_count, dtype=np.uint64))

    def decode(c):
        q, k = c >> 3, c & 7
        w = words[q]
        exceptional = (w & MASK) == MASK
        code5 = (w >> (np.uint64(24) + np.uint64(5) * k.astype(np.uint64))) & np.uint64(31)
        decoded = (w & MASK) + (code5 & 3) * np.uint64(0x010101) + ((code5 & 12) << 6) + ((code5 & 16) << 12)
        if np.any(exceptional):
            decoded[exceptional] = pool[(w[exceptional] >> 24).astype(np.intp), k[exceptional]]
        return decoded.astype(np.uint32), exceptional, code5, w

    full_byte_differences = full_pixel_differences = inverse_differences = line_differences = carry_violations = 0
    full_hash = hashlib.sha256()
    grid_g = np.repeat(np.arange(256, dtype=np.uint32), 256)
    grid_b = np.tile(np.arange(256, dtype=np.uint32), 256)
    for r in range(256):
        c = np.uint32(r) | (grid_g << 8) | (grid_b << 16)
        inverse_differences += int(np.count_nonzero(((c >> 3) << 3 | (c & 7)) != c))
        line_differences += int(np.count_nonzero((((c >> 3) * 8) >> 6) != (c >> 6)))
        decoded, exceptional, d, w = decode(c)
        expected = linear[c]
        full_pixel_differences += int(np.count_nonzero(decoded != expected))
        actual_bytes = rgb_bytes(decoded)
        full_byte_differences += int(np.count_nonzero(actual_bytes != cube[r].reshape(-1, 3)))
        full_hash.update(actual_bytes)
        good = ~exceptional
        for shift, increment in ((0, d & 3), (8, (d & 3) + ((d >> 2) & 3)), (16, (d & 3) + ((d >> 4) & 1))):
            channel = ((w[good] >> shift) & 255) + increment[good]
            carry_violations += int(np.count_nonzero(channel > 255))
            update_range(ranges, "normal_decoded_" + {0: "R", 8: "G", 16: "B"}[shift], channel)
    full_exact = full_pixel_differences == full_byte_differences == inverse_differences == line_differences == carry_violations == 0
    full_exact = full_exact and full_hash.hexdigest() == protocol["inputs"]["cube"]["sha256"]

    manifest = read(sources["manifest"])
    assert len(manifest["images"]) == 100
    photos = np.memmap(sources["photos"], dtype=np.uint8, mode="r", shape=(100, 1024 * 768, 3))
    rows = []
    photo_hash = hashlib.sha256()
    packet_histogram = np.zeros(9, dtype=np.int64)
    photo_byte_differences = photo_pixel_differences = 0
    for i, pixels in enumerate(photos):
        meta = manifest["images"][i]
        input_sha = hashlib.sha256(pixels).hexdigest()
        assert input_sha == meta["evaluation"]["pixel_sha256"]
        c = packed_rgb(pixels)
        decoded, exceptional, _, _ = decode(c)
        expected = linear[c]
        output = rgb_bytes(decoded)
        byte_differences = int(np.count_nonzero(output != rgb_bytes(expected)))
        pixel_differences = int(np.count_nonzero(decoded != expected))
        photo_byte_differences += byte_differences
        photo_pixel_differences += pixel_differences
        photo_hash.update(output)
        hits_per_packet = exceptional.reshape(-1, 8).sum(axis=1)
        histogram = np.bincount(hits_per_packet.astype(np.intp), minlength=9)
        packet_histogram += histogram
        hits = int(np.count_nonzero(hits_per_packet))
        packets = len(hits_per_packet)
        rows.append(dict(image_index=i, image_id=meta["id"], input_sha256=input_sha,
                         decoded_output_sha256=hashlib.sha256(output).hexdigest(), pixels=len(c), packets8=packets,
                         exception_pixels=int(exceptional.sum()), exception_pixel_fraction=float(exceptional.mean()),
                         exception_packets8=hits, exception_packet8_fraction=hits / packets,
                         exception_pixels_per_packet8_histogram=histogram.tolist(),
                         decoded_pixel_differences=pixel_differences, decoded_byte_differences=byte_differences))
    packets = sum(row["packets8"] for row in rows)
    hits = sum(row["exception_packets8"] for row in rows)
    fraction = hits / packets
    worst = max(rows, key=lambda row: row["exception_packet8_fraction"])
    photo_exact = photo_pixel_differences == photo_byte_differences == 0
    photo_exact = photo_exact and photo_hash.hexdigest() == protocol["expected_photo_output_sha256"]
    gate = dict(full_domain_exact=full_exact, photos_exact=photo_exact,
                exception_packet8_fraction=fraction, exception_packet8_fraction_max=0.05,
                exception_packets_pass=fraction <= 0.05,
                any_image_exception_packet8_fraction=worst["exception_packet8_fraction"],
                any_image_exception_packet8_fraction_max=0.20,
                per_image_pass=worst["exception_packet8_fraction"] <= 0.20,
                exception_pool_bytes=pool.nbytes, exception_pool_bytes_max=2 << 20,
                exception_pool_pass=pool.nbytes <= (2 << 20))
    gate["passed"] = all(gate[key] for key in ("full_domain_exact", "photos_exact", "exception_packets_pass", "per_image_pass", "exception_pool_pass"))
    reason_counts = {}
    overlap = []
    codes = np.arange(len(reason_histogram), dtype=np.uint32)
    for bit, name in enumerate(REASONS):
        reason_counts[name] = int(reason_histogram[(codes & (1 << bit)) != 0].sum())
        overlap.append([int(reason_histogram[((codes & (1 << bit)) != 0) & ((codes & (1 << other)) != 0)].sum()) for other in range(len(REASONS))])
    result = dict(purpose=__doc__, analysis_completed=True, script_sha256=digest(__file__), protocol_sha256=digest(OUT / "protocol.json"),
                  history_sha256=digest(OUT / "history.json"), environment=dict(platform=platform.platform(), python=sys.version,
                  executable=sys.executable, machine=platform.machine(), processor=platform.processor(), numpy=np.__version__, byteorder=sys.byteorder),
                  inputs=protocol["inputs"], encoding=protocol["encoding"],
                  palette_crosscheck=dict(entries=230, used_cube_entries=int(np.count_nonzero(frequencies)), values_rgb32=palette.tolist(),
                    cube_frequency=frequencies.tolist(), note="仅核对原230色集合；本编码直接RGB，不使用重编号ID或palette依赖"),
                  full_domain=dict(colors=N, blocks=BLOCKS, normal_blocks=normal_blocks, exception_blocks=pool_count,
                    exception_block_fraction=pool_count / BLOCKS, base_white_blocks=base_white_blocks, all_white_blocks=all_white_blocks,
                    failure_reasons=REASONS, failure_reason_counts_overlapping=reason_counts,
                    failure_reason_bitmask_histogram=reason_histogram.tolist(), failure_reason_pairwise_overlap=overlap,
                    value_ranges=ranges, span_histograms={key: value.tolist() for key, value in span_histograms.items()},
                    inverse_mismatches=inverse_differences, main_table_line_mismatches=line_differences,
                    decoded_pixel_differences=full_pixel_differences, decoded_byte_differences=full_byte_differences,
                    normal_channel_carry_violations=carry_violations, decoded_output_sha256=full_hash.hexdigest(),
                    linear_rgb32_sha256=hashlib.sha256(linear).hexdigest(), main_table_bytes=words.nbytes,
                    main_table_sha256=hashlib.sha256(words).hexdigest(), exception_pool_bytes=pool.nbytes,
                    exception_pool_sha256=hashlib.sha256(pool).hexdigest(), total_payload_bytes=words.nbytes + pool.nbytes,
                    pool_ordinals_contiguous=True, sentinel_count=pool_count),
                  photos=dict(images=100, pixels=235929600 // 3, packets8=packets, exception_packets8=hits,
                    exception_packet8_fraction=fraction, exception_pixels=sum(row["exception_pixels"] for row in rows),
                    exception_pixel_fraction=sum(row["exception_pixels"] for row in rows) / (235929600 // 3),
                    exception_pixels_per_packet8_histogram=packet_histogram.tolist(),
                    worst_image_index=worst["image_index"], worst_image_id=worst["image_id"],
                    worst_image_exception_packet8_fraction=worst["exception_packet8_fraction"],
                    images_over_individual_gate=[row["image_index"] for row in rows if row["exception_packet8_fraction"] > 0.20],
                    decoded_pixel_differences=photo_pixel_differences, decoded_byte_differences=photo_byte_differences,
                    decoded_output_sha256=photo_hash.hexdigest()), per_image=rows, gate=gate,
                  decision="离线门槛通过，仅允许另行考虑实现，不构成性能证据" if gate["passed"] else "固定离线门槛失败，停止此方向，不调整位数、块尺寸或排列重扫",
                  limitations=["主表仍16MiB，逐色表行编号与原byteID相同；没有缓存行减少的收益假设。",
                    "正常路径省去palette依赖，但移位、乘加、异常检查和寄存器压力未通过原生实现验证。",
                    "照片窗口固定为各图像素0起每8个像素；不扫描对齐偏移。",
                    "只读profile从已验cube输出评估可行性；任何未来运行时建表必须来自原模型。",
                    "只统计固定输入，不能推广为其他模型的异常率；未做候选原生、性能或Skylake实机测试。"],
                  native_calls=0, performance_calls=0, compiler_calls=0, new_fits=0)
    save("analysis.json", result)
    return result


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    protocol = read(OUT / "protocol.json")
    assert protocol["script_sha256"] == digest(__file__)
    # 独占建立回执：成功或失败均禁止在同一目录再次执行；失败保留原件。
    save("execution-start.json", dict(started_utc=now(), pid=os.getpid(), argv=sys.argv,
         script_sha256=digest(__file__), protocol_sha256=digest(OUT / "protocol.json"),
         maximum_analysis_executions=1, native_calls=0, performance_calls=0, compiler_calls=0))
    try:
        result = analyze(protocol)
    except BaseException as error:
        failure = dict(analysis_completed=False, error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc())
        save("failure.json", failure)
        save("exit.json", dict(ended_utc=now(), exit_code=1, analysis_completed=False,
             failure_sha256=digest(OUT / "failure.json"), native_calls=0, performance_calls=0, compiler_calls=0))
        raise
    save("exit.json", dict(ended_utc=now(), exit_code=0, analysis_completed=True, gate_passed=result["gate"]["passed"],
         analysis_sha256=digest(OUT / "analysis.json"), script_sha256=digest(__file__),
         protocol_sha256=digest(OUT / "protocol.json"), native_calls=0, performance_calls=0, compiler_calls=0))
    print(json.dumps(dict(gate=result["gate"], analysis_sha256=digest(OUT / "analysis.json"),
          exit_sha256=digest(OUT / "exit.json")), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
