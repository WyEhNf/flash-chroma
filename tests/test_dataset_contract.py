"""数据扩展与合并的少量集中回归；常规 CI 不物化完整源表。"""
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from lutlab import corpus, dataset, hackextend as ext, hackset as h, io, metrics


def test_3d_support_oblique_band_and_integer_wave():
    points = np.array([[121, 90, 202], [122, 90, 202], [122, 91, 202], [122, 90, 203],
                       [123, 90, 202], [0, 0, 0], [255, 255, 255]], np.uint8)
    stage = h.op("box_pulse", start=[122, 90, 202], width=1, delta=[64, -32, 48])
    expected = points.copy()
    expected[1] = [186, 58, 250]
    assert np.array_equal(ext.stage_rgb(stage, points), expected)
    slab = h.op("oblique_slab", weights=[1, 1, -1], start=123, width=2, delta=[0, 72, -24])
    wave = h.op("coupled_wave", weights=[1, 2, 3], phase=3, period=64, amplitude=24)
    for stage in (slab, wave):
        expected = []
        for r, g, b in points.tolist():
            if stage is slab:
                active = 123 <= r + g - b < 125
                expected.append([r, min(255, g + 72) if active else g, max(0, b - 24) if active else b])
            else:
                t = (r + 2 * g + 3 * b + 3) % 64
                triangle = 2 * t - 32 if t <= 32 else 96 - 2 * t
                expected.append([r, min(255, max(0, g + triangle * 24 // 32)), b])
        assert np.array_equal(ext.stage_rgb(stage, points), expected)
        assert np.array_equal(ext.stage_rgb(stage, points),
                              np.concatenate([ext.stage_rgb(stage, p) for p in np.array_split(points, 3)]))
    frame = np.resize(points, (9, 17, 3))
    multiset, layouts = ext.layouts(frame, ext.DEV_SEED)
    assert all(h.pixel_multiset(p)[0] == multiset for p in layouts.values())


def test_merge_preserves_partitions_identity_and_legacy_observation_scope(tmp_path, monkeypatch):
    record = dataset.load()
    legacy = json.loads((h.ROOT / "datasets/problem16-v1/catalog.json").read_text(encoding="utf-8"))
    assert dataset.csv_rows(h.ROOT / "report/data/r28/case-inventory.csv")[0]["case_id"] == legacy["cases"][0]["id"]
    indexed = {c["id"]: c for c in record["cases"]}
    for old in legacy["cases"]:
        row = indexed["corpus-v1--" + old["id"]]
        assert row["source_case_id"] == old["id"] and row["split"] == old["split"]
        assert len(set(row["source_sha256"])) == 4
    assert all(r["quality_status"] == "unmeasured" and r["historical_casebook_key"] is None
               for r in record["cases"] if r["namespace"].startswith("hack-"))
    assert record["legacy_matrix_denominator"] == 7917
    images = {r["id"]: r for r in record["images"]}
    assert record["cohorts"]["benchmark100-legacy"]["count"] == 100
    assert record["cohorts"]["natural100"]["unique_rgb_contents"] == 100
    assert all(images[i]["split"] in ("development", "stress_development")
               and images[i]["selection_eligibility"] != "quarantined_split_overlap"
               for i in record["cohorts"]["development"]["image_ids"])
    assert dataset.inspect()["metadata_verified"]
    # 从冻结配方重构一张旧图，不修改旧队列或写入 CI 大数据目录。
    spec = next(r for r in legacy["images"] if r["id"] == "neutral_ramp-i0-s0")
    rebuilt = corpus.image(spec)
    image = images["corpus-v1--" + spec["id"]]
    assert h.sha(rebuilt.tobytes()) == image["rgb_sha256"]
    assert h.sha(b"P6\n1024 768\n255\n" + rebuilt.tobytes()) == image["file_sha256"]
    # 在隔离目录验证实际恢复入口与拒绝覆写损坏文件，不重建整批320张图。
    catalog_path = tmp_path / "datasets/problem16-v1/catalog.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps({"images": [spec]}), encoding="utf-8")
    monkeypatch.setattr(dataset, "load", lambda: record)
    monkeypatch.setattr(h, "ROOT", tmp_path)
    assert dataset.restore_images(image_id=image["id"])["restored"] == 1
    assert dataset.restore_images(image_id=image["id"])["restored"] == 0
    (tmp_path / image["path"]).write_bytes(b"bad")
    with pytest.raises(ValueError, match="拒绝覆盖"):
        dataset.restore_images(image_id=image["id"])


def test_coupled_replay_requires_generic_path_and_matches_native_oracle(tmp_path: Path):
    replay = json.loads((ext.ASSETS / "replay/coupled-wave-p64/replay.json").read_text(encoding="utf-8"))
    models = [h.ROOT / row["path"] for row in replay["models"]]
    colours = np.asarray(replay["colours"], np.uint8)
    expected = h.scalar_oracle([io.load_sparse(p) for p in models], colours)
    assert np.array_equal(expected, replay["oracle_rgb8"])
    binary = metrics.resolve_jshc()
    kernels = json.loads(subprocess.check_output([str(binary), "info"]))["available_kernels"]
    source = tmp_path / "coupling.png"
    io.save_image(source, colours[None, ...])
    for kernel in (k for k in kernels if k.startswith("tetra_")):
        output = tmp_path / (kernel + ".png")
        subprocess.run([str(binary), "apply", "-k", kernel, "-i", str(source), "-o", str(output),
                        *(str(p) for p in models)], check=True)
        assert np.array_equal(io.load_image(output)[0], expected), kernel
        if kernel in ("tetra_c99", "tetra_structured_avx2"):
            plan = json.loads(subprocess.check_output([str(binary), "plan", "-k", kernel, *(str(p) for p in models)]))
            assert plan["stages"][1]["path"] == "tetra"
