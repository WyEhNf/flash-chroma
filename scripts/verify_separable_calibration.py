"""集中验证通用精确单调入口的结构、冲突/回退及Filmic冻结SHA，不追加来源终验。"""
from pathlib import Path
import hashlib
import json
import os
import sys
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"python"))
import numpy as np
import numba
from lutlab import io, interp, separable_calibration as sc, study_provenance
from lutlab.compatibility import write_json


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def model_for(axes, values):
    grid = io.uniform_grid(17)
    nodes = np.empty((17, 17, 17, 3), np.uint8)
    for channel, axis in enumerate(axes):
        shape = [1, 1, 1]
        shape[axis] = 17
        nodes[..., channel] = values[channel].reshape(shape)
    return io.SparseLut(grid, nodes, *io.axis_tables(grid))


def labels_for(model, axes, fractions=None):
    """独立Python整数公式构造整条来源曲线定义，不调用被测解析求交。"""
    index, old = model.tables()
    fractions = old if fractions is None else fractions
    result = []
    for channel, axis in enumerate(axes):
        selection = [0, 0, 0, channel]
        selection[axis] = slice(None)
        nodes = model.nodes[tuple(selection)]
        values = []
        for code in range(256):
            cell, f = int(index[axis, code]), int(fractions[axis, code])
            values.append(((65536-f)*int(nodes[cell])+f*int(nodes[cell+1])+32768)//65536)
        result.append((axis, np.array(values, np.uint8)))
    return result


def exact_check(old, channels, new):
    assert new is not None
    np.testing.assert_array_equal(old.nodes, new.nodes)
    np.testing.assert_array_equal(old.grid, new.grid)
    np.testing.assert_array_equal(old.tables()[0], new.tables()[0])
    index, fraction = new.tables()
    old_f = old.tables()[1].astype(np.int64)
    f = fraction.astype(np.int64)
    assert np.max(np.abs(f-old_f)) <= 4096
    assert np.all(np.diff(index.astype(np.int64)*65536+f, axis=1) >= 0)
    np.testing.assert_array_equal(f[:, [0, 255]], old_f[:, [0, 255]])
    for (_, expected), (_, actual) in zip(channels, labels_for(new, [a for a, _ in channels])):
        np.testing.assert_array_equal(actual, expected)
    rng = np.random.default_rng(2026101910)
    rgb = rng.integers(0, 256, size=(2048, 3), dtype=np.uint8)
    reference = np.column_stack([values[rgb[:, axis]] for axis, values in channels])
    np.testing.assert_array_equal(interp.apply_tetra_q16(new, rgb), reference)


def require_failure(model, channels, expected_reason):
    candidate, report = sc.exact_monotone(model, channels)
    assert candidate is None and not report["feasible"]
    reasons = [report["reason"]]+[f["reason"] for f in report.get("failures", [])]
    assert expected_reason in reasons, (expected_reason, report)
    return report


def main():
    numba.set_num_threads(4)
    output = ROOT/"artifacts/separable-calibration-contract-v1"
    if output.exists():
        raise ValueError("不覆盖既有集中合同")
    source = ROOT/"python/lutlab/separable_calibration.py"
    identity = {"module_sha256": digest(source), "driver_sha256": digest(__file__),
                "environment": study_provenance.environment_fingerprint(),
                "purpose": "通用精确单调接口集中合同；非其他来源完整域/百图/性能测试"}
    study_provenance.claim_run(output/"run.json",
        {"identity": identity, "identity_sha256": study_provenance.identity_digest(identity)})
    passed = []
    # 下降曲线、常量和轴置换；两个非恒定通道都需要真实调整坐标。
    axes = [2, 0, 1]
    curves = [np.rint(np.linspace(255, 0, 17)).astype(np.uint8),
              np.full(17, 73, np.uint8), np.rint(np.linspace(0, 255, 17)).astype(np.uint8)]
    model = model_for(axes, curves)
    desired = model.tables()[1].astype(np.int64)
    desired[2, 8] += 4096
    desired[1, 8] -= 4096
    channels = labels_for(model, axes, desired)
    candidate, report = sc.exact_monotone(model, channels)
    exact_check(model, channels, candidate)
    assert report["changed_fractions"] > 0
    passed.append("下降/常量/轴置换精确校准")
    shared = model_for([0, 0, 2], [np.arange(17, dtype=np.uint8)]*3)
    channels = labels_for(shared, [0, 0, 2])
    candidate, _ = sc.exact_monotone(shared, channels)
    exact_check(shared, channels, candidate)
    passed.append("共享同轴多通道可兼容")
    channels[0][1][8] = 0
    conflict = require_failure(shared, channels, "shared_axis_interval_conflict")
    passed.append("共享同轴单独可达但区间冲突")
    plain = model_for([0, 1, 2], [np.arange(17, dtype=np.uint8)]*3)
    endpoint_labels = labels_for(plain, [0, 1, 2])
    endpoint_labels[0][1][0] = 1
    require_failure(plain, endpoint_labels, "frozen_endpoint")
    passed.append("冻结端点不能被覆盖标签绕过")
    shift_labels = labels_for(plain, [0, 1, 2])
    shift_labels[0][1][1] = 1
    require_failure(plain, shift_labels, "maximum_shift")
    passed.append("不自动增加最大坐标偏移")
    # 两个相邻区间各自非空，但前者必须>=32768、后者必须<=32767。
    index, fraction = plain.tables()
    modified = fraction.copy()
    modified[0, 100:104] = [32767, 32768, 32768, 32768]
    noncanonical = io.SparseLut(plain.grid.copy(), plain.nodes.copy(), index.copy(), modified)
    assert np.all(np.diff(index.astype(np.int64)*65536+modified.astype(np.int64), axis=1) >= 0)
    labels = labels_for(noncanonical, [0, 1, 2])
    labels[0][1][100], labels[0][1][101] = 7, 6
    global_conflict = require_failure(noncanonical, labels, "monotonicity_conflict")
    assert global_conflict["pointwise_intervals_nonempty"]
    passed.append("逐码均可达但全局单调无解")
    constant_labels = labels_for(model, axes)
    constant_labels[1][1][50] = 74
    require_failure(model, constant_labels, "fixed_nodes_or_cell_unreachable")
    passed.append("常量节点不能伪造不同标签")
    broken_nodes = model.nodes.copy()
    broken_nodes[1, 1, 1, 0] ^= 1
    broken = io.SparseLut(model.grid.copy(), broken_nodes, *model.tables())
    require_failure(broken, labels_for(model, axes), "node_tensor_mismatch")
    passed.append("完整节点张量必须符合通道依赖轴")
    require_failure(model, None, "source_not_verified_axis_separable")
    passed.append("未验证来源明确回退")
    parent = ROOT/"artifacts/filmic-calibration-v1"
    old = json.loads((parent/"preparation.json").read_text(encoding="utf-8"))
    labels_path = parent/"source-curves.npy"
    assert digest(labels_path) == old["source_curves_file_sha256"]
    values = np.load(labels_path)
    expected = {17: "d8186ab6762f3aac8ffaf2d86e87fbc1af220a2de3ecfcd41177f58abfa5b9cb",
                33: "49231a3755bc2897f0d32f9ccb7578e11479d2e22cd0516a520915818f7cced0"}
    hashes = {}
    for size in (17, 33):
        path = parent/f"m{size}/baseline.slut"
        assert digest(path) == old["sizes"][str(size)]["baseline_sha256"]
        original = io.load_sparse(path, competition=True)
        channels = [(axis, values[:, axis]) for axis in range(3)]
        candidate, report = sc.exact_monotone(original, channels)
        exact_check(original, channels, candidate)
        destination = output/f"filmic-m{size}.slut"
        io.save_sparse(destination, candidate)
        assert digest(destination) == expected[size], (size, digest(destination))
        hashes[str(size)] = {"sha256": digest(destination), "report": report}
        passed.append(f"Filmic{size}精确复现既有零误差模型SHA")
    result = {"passed": len(passed), "checks": passed, "filmic": hashes,
              "shared_axis_failure": conflict, "global_monotone_failure": global_conflict,
              "scope": "有限合成契约及Filmic已验模型SHA复现；没有追加其他来源全域/百图"}
    write_json(output/"results.json", result)
    print(json.dumps({"passed": len(passed), "filmic_sha256": {k:v["sha256"] for k,v in hashes.items()},
                      "scope": result["scope"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
