"""独立三预算trial：cap1600、±1/2，先追回原3e5双mean，不硬约束RMS。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
import psutil
from lutlab import channel_joint_nodes as cj, channel_tail_nodes as tail, oriented_tetra as ot, io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from study_velvia_stripe_diagonals import improves


def mean_score(means, budget):
    ratio = means/budget
    positive = np.maximum(ratio-1., 0.)
    return (float(positive.max()), float(positive.sum()), float(ratio[1]), float(ratio[0]))


def choose(change, bad, colours, colour, measured, mean_budget, count_budget):
    moves = np.zeros((len(colours), 3), np.int32)
    predicted = np.zeros(7)
    records = []
    for node in np.flatnonzero(colours == colour):
        current = measured+predicted
        best, selected = mean_score(current[:2], mean_budget), -1
        for direction in range(52):
            delta = change[:, direction, node]
            if bad[direction, node] or current[6]+delta[6] > count_budget:
                continue
            candidate = mean_score(current[:2]+delta[:2], mean_budget)
            if improves(candidate, best):
                best, selected = candidate, direction
        if selected >= 0:
            amplitude = selected//26+1
            moves[node] = amplitude*cj.DIRECTIONS[selected % 26]
            predicted += change[:, selected, node]
            records.append({'node': int(node), 'direction': int(selected % 26), 'amplitude': amplitude,
                'deltas': change[:, selected, node].tolist(), 'score': best})
    return moves, predicted, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖独立三预算trial')
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass'] or contract.get('steps') != [1, 2]:
        raise ValueError('必须先过新±1/2独立方向合同')
    for name in ('python/lutlab/oriented_tetra.py', 'python/lutlab/channel_tail_nodes.py'):
        if contract['source_sha256'][name] != digest(ROOT/name):
            raise ValueError('合同后修改了权重或gain模块')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    cache = args.cache_root.resolve()
    initial = ROOT/'artifacts/velvia-stripe-nodes-v1'
    model_path = initial/'model.npz'
    if digest(model_path) != 'bcc60aa2d9cc7c17aa9a985c1b3597dd9639b8f50470000246502aefebf51651':
        raise ValueError('不是前一独立失败trial冻结末节点')
    model = load_model(model_path)
    choices = np.fromfile(initial/'cell-orientation.bin', np.uint8)
    for name in ('stripes-byte.bin', 'stripes-packed.bin', 'cell-orientation.bin'):
        (args.output/name).write_bytes((initial/name).read_bytes())
    old = json.loads((initial/'summary.json').read_text(encoding='utf-8'))
    mean_budget = np.array(old['budget'])[[0, 2]]
    count_budget = old['budget'][4]
    table_path = cache/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256'
    points_path = cache/'artifacts/cinema-axis-calibration-v1/envelope-arrivals.npy'
    mass_path = cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy'
    prior = json.loads((ROOT/'artifacts/protected-tail-velvia-v1/run.json').read_text(encoding='utf-8'))['input_sha256']
    for name, path in [('reference', table_path), ('mass', mass_path), ('points', points_path)]:
        if digest(path) != prior[name]:
            raise ValueError('不可更换原参考/输入/60图频率')
    reference = io.load_full(table_path, mmap=True).reshape(-1, 3)
    points = np.load(points_path, mmap_mode='r')
    mass = np.asarray(np.load(mass_path, mmap_mode='r'), np.float64); mass /= mass.sum()
    save(args.output/'run.json', {'input_sha256': {str(p): digest(p) for p in (model_path, initial/'cell-orientation.bin', table_path, points_path, mass_path, args.contract)},
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), ROOT/'python/lutlab/oriented_tetra.py', ROOT/'python/lutlab/channel_tail_nodes.py']},
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
        'original_3e5_mean_budget': mean_budget.tolist(), 'original_3e5_p99_count_budget': count_budget,
        'policy': '独立于cap1522五预算trial，从该trial末节点/固定相容场开始；cap1600，一扫8色26方向×步长{1,2}。每节点全支撑，p99超阈数始终<=原3e5；双mean正超额(max,sum)、训练mean/uniformmean优先。RMS/CVaR只披露不选择，不看百图、不追加扫。',
        'scope': '初始mean不合格，仅追可行性；最终原3e5双mean和p99count全过方能终验。新表示未被现有native支持。'})
    indices, weights = ot.design(model, points, choices)
    acc, _ = cj.accumulate(indices, weights, model.nodes.reshape(-1, 3), reference)
    initial_values, square = tail.measure(ot.predict(model, points, choices), reference, points, mass, 40, 100)
    np.testing.assert_allclose(initial_values, old['after'], rtol=0, atol=1e-5)
    caps, colours = np.full(len(points), 1600, np.int32), cj.parity(model.m)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    current, measured, records = model, initial_values.copy(), []
    for colour in range(8):
        changes, forbiddens = [], []
        for amplitude in (1, 2):
            gain, bad, invalid = tail.gains(indices, weights, acc, reference, points, mass,
                current.nodes.reshape(-1, 3), colours, colour, caps, root, 4, 40, 100, amplitude)
            if invalid:
                raise AssertionError('有向parity或hard cap失败')
            changes.append(gain); forbiddens.append(bad)
        change, forbidden = np.concatenate(changes, axis=1), np.concatenate(forbiddens, axis=0)
        del changes, forbiddens, gain, bad
        moves, predicted, accepted = choose(change, forbidden, colours, colour, measured, mean_budget, count_budget)
        del change, forbidden
        current = tail.apply(current, indices, weights, acc, moves, reference)
        fresh = ot.predict(current, points, choices)
        np.testing.assert_array_equal(fresh, ((acc+io.ONE//2) >> io.Q).astype(np.uint8))
        after, square = tail.measure(fresh, reference, points, mass, 40, 100)
        if np.max(np.abs(after-measured-predicted)) > 1e-5 or np.any(square > caps) or after[6] > count_budget or improves(mean_score(measured[:2], mean_budget), mean_score(after[:2], mean_budget)):
            raise AssertionError('完整fresh/三约束或mean目标回退')
        records.append({'colour': colour, 'before': measured.tolist(), 'after': after.tolist(), 'changed_nodes': len(accepted),
            'moves': accepted, 'max_squared': int(square.max()), 'maximum_gain_error': float(np.max(np.abs(after-measured-predicted))),
            'host_available_memory_bytes': psutil.virtual_memory().available, 'process_rss_bytes': psutil.Process().memory_info().rss})
        measured = after
        save(args.output/'progress.json', records)
        print(json.dumps({k: v for k, v in records[-1].items() if k != 'moves'}, ensure_ascii=False), flush=True)
    np.savez_compressed(args.output/'model.npz', format=np.array('oriented_tetra_v1_experimental'), grid=current.grid,
        nodes=current.nodes, shared_idx=current.idx, channel_frac=current.channel_frac)
    save(args.output/'summary.json', {'before': initial_values.tolist(), 'after': measured.tolist(),
        'original_3e5_mean_budget': mean_budget.tolist(), 'original_3e5_count_budget': count_budget,
        'three_constraints_passed': bool(np.all(measured[:2] <= mean_budget+np.array([1e-5, 1e-12])) and measured[6] <= count_budget),
        'max_squared': int(square.max()), 'model_sha256': digest(args.output/'model.npz'),
        'cap_violations': 0, 'fresh_byte_mismatches': 0, 'runtime_memory_unmeasured': True})


if __name__ == '__main__':
    main()
