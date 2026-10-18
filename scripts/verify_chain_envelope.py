"""独立整数oracle核对整链逐色上限的禁止位与同色批量安全性。"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
import numba
import numpy as np
from lutlab import chain_envelope, error_analysis as ea, fit, interp, io, rounded_grid
from run_cinema_rounded import load_inputs, read


def nonlinear_suffix(rgb):
    """独立解析后缀：包含硬阈值和跨通道异或，显式放大1LSB差异。"""
    out = np.empty_like(rgb)
    out[:, 0] = 255-rgb[:, 0]
    out[:, 1] = np.where(rgb[:, 1] >= 128, 255, 0)
    out[:, 2] = rgb[:, 0] ^ rgb[:, 1] ^ rgb[:, 2]
    return out


def main():
    numba.set_num_threads(4)
    models, tables, _ = load_inputs(read(ROOT / 'experiments/cinema-rounded-v1.json'))
    pool = fit.stratified_points(2026101802)
    rgb = pool[np.random.default_rng(2026101902).choice(len(pool), 2048, replace=False)]
    # 同一到达色的多个原始来源各保留参考；重复行不能用平均目标代替。
    rgb = np.concatenate([rgb, rgb[:137]])
    arrivals = rgb.copy()
    for model in models[:3]:
        arrivals = interp.apply_tetra_q16(model, arrivals)
    points, lookup = np.unique(arrivals, axis=0, return_inverse=True)
    target = ea.exact_chain(tables, rgb)
    first_references = {}
    distinct_reference_collision = False
    for z, reference in zip(arrivals, target):
        key = tuple(map(int, z))
        if key in first_references and first_references[key] != tuple(map(int, reference)):
            distinct_reference_collision = True
        first_references[key] = tuple(map(int, reference))
    if not distinct_reference_collision:
        raise AssertionError('合同必须包含共享到达色但精确参考不同的原始输入')
    own = ea.source_apply(tables[3], points)
    model = models[3]
    indices, weights, acc, squared, colours = rounded_grid.prepare(model, points, own)
    output = interp.apply_tetra_q16(model, arrivals)
    error = output.astype(np.int32)-target.astype(np.int32)
    caps = np.sum(error*error, axis=1, dtype=np.int32)+np.arange(len(rgb), dtype=np.int32)%3
    envelope = chain_envelope.ChainEnvelope(lookup, target, caps, expected_arrivals=arrivals)
    envelope.validate(points, acc)
    checked, blocked, allowed = 0, 0, 0
    for colour in range(8):
        for channel in range(3):
            forbidden = envelope.forbidden(indices, weights, acc, colours, colour, channel, 4)
            support = np.unique(indices[weights > 0])
            selected = support[colours[support] == colour][:3]
            for node in selected:
                for direction, delta in enumerate((1, -1)):
                    if not 0 <= int(model.nodes.reshape(-1, 3)[node, channel])+delta <= 255:
                        continue
                    nodes = model.nodes.copy()
                    nodes.reshape(-1, 3)[node, channel] = int(nodes.reshape(-1, 3)[node, channel])+delta
                    candidate = io.SparseLut(model.grid.copy(), nodes, *model.tables())
                    changed = interp.apply_tetra_q16(candidate, arrivals).astype(np.int32)-target.astype(np.int32)
                    expected = bool(np.any(np.sum(changed*changed, axis=1, dtype=np.int32) > caps))
                    if bool(forbidden[direction, node]) != expected:
                        raise AssertionError('包络禁止位与独立整链整数输出不一致')
                    checked += 1
                    blocked += int(expected)
                    allowed += int(not expected)
    if not blocked or not allowed:
        raise AssertionError('合同必须实际覆盖禁止与允许两类改动')
    # 同色正支撑互斥，多个允许改动合并后仍须逐原始颜色满足上限。
    colour, channel = 3, 1
    forbidden = envelope.forbidden(indices, weights, acc, colours, colour, channel, 4)
    nodes = model.nodes.reshape(-1, 3).copy()
    move = np.zeros(len(nodes), np.int32)
    for node in np.unique(indices[weights > 0]):
        if colours[node] != colour:
            continue
        if nodes[node, channel] < 255 and not forbidden[0, node]:
            move[node] = 1
        elif nodes[node, channel] > 0 and not forbidden[1, node]:
            move[node] = -1
    rounded_grid._apply(indices, weights, acc, squared, own, colours, colour, channel, move)
    nodes[:, channel] = nodes[:, channel].astype(np.int32)+move
    candidate = io.SparseLut(model.grid.copy(), nodes.reshape(model.nodes.shape), *model.tables())
    changed = interp.apply_tetra_q16(candidate, arrivals).astype(np.int32)-target.astype(np.int32)
    if np.any(np.sum(changed*changed, axis=1, dtype=np.int32) > caps):
        raise AssertionError('同色允许改动批量合并后违反包络')
    np.testing.assert_array_equal(((acc+io.ONE//2)>>io.Q).astype(np.uint8), interp.apply_tetra_q16(candidate, points))
    envelope.validate(points, acc)
    # 先重置主缓存，再验证带量化/跨通道后缀的约束，解析公式不读缓存。
    indices, weights, acc, squared, colours = rounded_grid.prepare(model, points, own)
    cache = np.empty((256**3, 3), np.uint8)
    for start in range(0, len(cache), 1 << 18):
        ids = np.arange(start, start+(1 << 18), dtype=np.int64)
        rgb_block = np.column_stack(((ids >> 16) & 255, (ids >> 8) & 255, ids & 255)).astype(np.uint8)
        cache[start:start+len(ids)] = nonlinear_suffix(rgb_block)
    baseline_suffix = nonlinear_suffix(output)
    suffix_targets = np.clip(baseline_suffix.astype(np.int32)+np.array([1, -1, 2]), 0, 255).astype(np.uint8)
    error = baseline_suffix.astype(np.int32)-suffix_targets.astype(np.int32)
    suffix_caps = np.sum(error*error, axis=1, dtype=np.int32)+np.arange(len(rgb), dtype=np.int32)%3
    suffix_guard = chain_envelope.ChainEnvelope(lookup, suffix_targets, suffix_caps,
        expected_arrivals=arrivals, suffix=cache)
    suffix_guard.validate(points, acc)
    suffix_checked = 0
    for colour in range(8):
        for channel in range(3):
            forbidden = suffix_guard.forbidden(indices, weights, acc, colours, colour, channel, 4)
            support = np.unique(indices[weights > 0])
            for node in support[colours[support] == colour][:2]:
                for direction, delta in enumerate((1, -1)):
                    if not 0 <= int(model.nodes.reshape(-1, 3)[node, channel])+delta <= 255:
                        continue
                    changed_nodes = model.nodes.copy()
                    changed_nodes.reshape(-1, 3)[node, channel] = int(changed_nodes.reshape(-1, 3)[node, channel])+delta
                    changed_model = io.SparseLut(model.grid.copy(), changed_nodes, *model.tables())
                    prediction = nonlinear_suffix(interp.apply_tetra_q16(changed_model, arrivals))
                    error = prediction.astype(np.int32)-suffix_targets.astype(np.int32)
                    expected = bool(np.any(np.sum(error*error, axis=1, dtype=np.int32) > suffix_caps))
                    if bool(forbidden[direction, node]) != expected:
                        raise AssertionError('非线性固定后缀约束与独立整数/解析后缀不一致')
                    suffix_checked += 1
    # 非法候选方向需在访问完整后缀缓存前拒绝，避免Numba越界读取。
    extremes = np.array([[0, 0, 0], [255*io.ONE, 255*io.ONE, 255*io.ONE]], np.int32)
    if chain_envelope._output(extremes, 0, 0, -io.ONE, cache) != (-1, 0, 0):
        raise AssertionError('负码值应在后缀缓存索引前返回')
    if chain_envelope._output(extremes, 1, 0, io.ONE, cache) != (256, 255, 255):
        raise AssertionError('上溢码值应在后缀缓存索引前返回')
    print(json.dumps({'passed': 4, 'original_input_rows': len(rgb), 'unique_arrivals': len(points),
        'independent_node_changes': checked, 'forbidden': blocked, 'allowed': allowed,
        'suffix_node_changes': suffix_checked, 'batched_moves': int(np.count_nonzero(move)),
        'scope': '原包络/批量、非线性后缀及索引越界合同，非完整精度或性能结果'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
