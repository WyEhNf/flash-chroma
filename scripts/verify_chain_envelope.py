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
    print(json.dumps({'passed': 2, 'original_input_rows': len(rgb), 'unique_arrivals': len(points),
        'independent_node_changes': checked, 'forbidden': blocked, 'allowed': allowed,
        'batched_moves': int(np.count_nonzero(move)), 'scope': '真实前缀与非均匀逐色上限合同，非完整精度或性能结果'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
