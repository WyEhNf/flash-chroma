"""压力输入的少量确定性回归；不生成完整 LUT，不运行拟合矩阵。"""
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from lutlab import hackset, interp, io, metrics


def test_pulse_and_quantized_cascade_have_independent_expected_values():
    ramp = np.repeat(np.arange(256, dtype=np.uint8)[:, None], 3, axis=1)
    ramp[:, 1] = 128
    for width in (1, 2, 4):
        output = hackset.stage_rgb(hackset.op("pulse", start=122, width=width, amplitude=96), ramp)
        assert np.flatnonzero(output[:, 1] != 128).tolist() == list(range(122, 122 + width))
        assert np.all(output[122:122 + width, 1] == 224)
    case = next(c for c in hackset.definition()["cases"] if c["id"] == "compress-amplify")
    expected = []
    for r, g, b in ramp:
        values = [int(v) // 4 * 4 for v in (r, g, b)]
        values[1] = min(255, values[1] + (48 if values[0] >= 128 else 0))
        expected.append(values[::-1])
    assert np.array_equal(hackset.chain_rgb(case, ramp), expected)
    random = hackset.op("hashed_random", seed=hackset.DEV_SEED)
    assert np.array_equal(hackset.stage_rgb(random, ramp),
                          np.concatenate([hackset.stage_rgb(random, part) for part in np.array_split(ramp, 7)]))
    neighbours = hackset.neighbourhood([[0, 0, 0], [255, 255, 255], [122, 128, 64]])
    assert len(neighbours) == 8 + 8 + 27
    with pytest.raises(ValueError):
        hackset.neighbourhood([[256, 0, 0]])


def test_layouts_preserve_exact_pixel_multiplicity():
    frame = np.resize(np.asarray([[0, 0, 0], [1, 2, 3], [255, 128, 7]], np.uint8), (9, 17, 3))
    digest, variants = hackset.layouts(frame, hackset.DEV_SEED)
    for pixels in variants.values():
        assert hackset.pixel_multiset(pixels)[0] == digest
    assert np.array_equal(variants["shuffled"], hackset.layouts(frame, hackset.DEV_SEED)[1]["shuffled"])


def test_frozen_replays_separate_runtime_correctness_from_sampling_error(tmp_path: Path):
    binary = metrics.resolve_jshc()
    capabilities = json.loads(subprocess.check_output([str(binary), "info"], text=True))
    kernels = [name for name in capabilities["available_kernels"] if name.startswith("tetra_")]
    for name in ("identity-roundtrip", "interior-peak-w1"):
        path = hackset.ASSETS / "replay" / name / "replay.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        models = [io.load_sparse(hackset.ROOT / item["path"]) for item in record["models"]]
        colours = np.asarray(record["colours"], np.uint8)
        oracle = hackset.scalar_oracle(models, colours)
        assert np.array_equal(oracle, record["oracle_rgb8"])
        vectorized = colours
        for model in models:
            vectorized = interp.apply_tetra_q16(model, vectorized)
        assert np.array_equal(vectorized, oracle)
        squared = ((np.asarray(record["exact_rgb8"], np.int32) - oracle.astype(np.int32)) ** 2).sum(-1)
        if name == "identity-roundtrip":
            assert not np.any(squared)
        else:
            assert squared.max() == 96 ** 2
        # 短输入只用于内核回归；不混入 1024×768 压力图片清单。
        source = tmp_path / f"{name}.png"
        io.save_image(source, colours[None, ...])
        for kernel in kernels:
            output = tmp_path / f"{name}-{kernel}.png"
            subprocess.run([str(binary), "apply", "-i", str(source), "-o", str(output), "-k", kernel,
                            *(str(hackset.ROOT / item["path"]) for item in record["models"])], check=True)
            assert np.array_equal(io.load_image(output)[0], oracle), kernel
