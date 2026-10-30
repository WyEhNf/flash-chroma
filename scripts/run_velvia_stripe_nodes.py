"""固定相容stripe基，单扫8色26方向节点重拟合，保护原3e5五项最终预算。"""
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
from study_velvia_stripe_diagonals import dense, MASKS, score, improves

METRICS = [0, 2, 1, 3, 6]


def choose(change, bad, colours, colour, measured, budget):
    moves = np.zeros((len(colours), 3), np.int32)
    predicted = np.zeros(7)
    records = []
    for node in np.flatnonzero(colours == colour):
        current = measured+predicted
        best, chosen = score(current[METRICS], budget), -1
        for direction in range(26):
            if bad[direction, node]:
                continue
            trial = current+change[:, direction, node]
            candidate = score(trial[METRICS], budget)
            if improves(candidate, best):
                best, chosen = candidate, direction
        if chosen >= 0:
            moves[node] = cj.DIRECTIONS[chosen]
            predicted += change[:, chosen, node]
            records.append({'node': int(node), 'direction': int(chosen), 'deltas': change[:, chosen, node].tolist(), 'score': best})
    return moves, predicted, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖stripe节点冻结试验')
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass'] or contract['source_sha256']['python/lutlab/oriented_tetra.py'] != digest(ROOT/'python/lutlab/oriented_tetra.py'):
        raise ValueError('独立geometry/支撑合同未通过或源码改变')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    cache = args.cache_root.resolve()
    model_path = cache/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz'
    if digest(model_path) != '3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0':
        raise ValueError('不是当前3e5节点起点')
    stripe_path = ROOT/'artifacts/velvia-stripe-diagonals-v1/results.json'
    stripe = json.loads(stripe_path.read_text(encoding='utf-8'))
    selected = next(r for r in stripe['runs'] if r['initial_global_mask'] == 1)
    bits = np.array(selected['stripe_bits'], np.uint8)
    choices = MASKS[dense(bits)]
    bits.tofile(args.output/'stripes-byte.bin')
    np.packbits(bits.reshape(-1), bitorder='little').tofile(args.output/'stripes-packed.bin')
    choices.tofile(args.output/'cell-orientation.bin')
    model = load_model(model_path)
    table_path = cache/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256'
    reference = io.load_full(table_path, mmap=True).reshape(-1, 3)
    points_path = cache/'artifacts/cinema-axis-calibration-v1/envelope-arrivals.npy'
    mass_path = cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy'
    prior = json.loads((ROOT/'artifacts/protected-tail-velvia-v1/run.json').read_text(encoding='utf-8'))['input_sha256']
    for name, path in [('reference', table_path), ('mass', mass_path), ('points', points_path)]:
        if digest(path) != prior[name]:
            raise ValueError('参考、canonical点或原60图频率与已验起点不同')
    points = np.load(points_path, mmap_mode='r')
    mass = np.asarray(np.load(mass_path, mmap_mode='r'), np.float64); mass /= mass.sum()
    proof = json.loads((ROOT/'artifacts/velvia-cell-feasibility-v1/results.json').read_text(encoding='utf-8'))['baseline_metrics']
    metric_names = ('distance_sum', 'squared_sum', 'training_frequency_mean', 'training_frequency_squared', 'count_above_40')
    budget = np.array([proof[n] for n in metric_names])
    save(args.output/'run.json', {'input_sha256': {str(p): digest(p) for p in (model_path, stripe_path, table_path, points_path, mass_path, args.contract)},
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), ROOT/'python/lutlab/oriented_tetra.py', ROOT/'python/lutlab/channel_tail_nodes.py']},
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4, 'baseline_five_metric_budget': budget.tolist(),
        'five_metric_order': metric_names,
        'policy': '固定global1两扫末的相容stripe场及原3e5轴/节点起点；仅1扫8色0..7、26个±1方向。每色按节点升序，以原3e5五项预算的正超额(max,sum)/训练mean/uniformmean严格改善，cap1522从不放宽；逐批fresh完整复算，不看照片或追加扫数。',
        'scope': '初始stripe均值不合格，仅作可行性目标；最终全域五约束须<=原3e5且后续独立全域/照片/边界验收方可入围。新插值表示，无原生/性能。'})
    indices, weights = ot.design(model, points, choices)
    print(json.dumps({'phase': 'design', 'offline_design_bytes': int(indices.nbytes+weights.nbytes),
        'host_available_memory_bytes': psutil.virtual_memory().available, 'process_rss_bytes': psutil.Process().memory_info().rss}), flush=True)
    acc, _ = cj.accumulate(indices, weights, model.nodes.reshape(-1, 3), reference)
    identity = np.asarray(points)
    initial, squared = tail.measure(ot.predict(model, points, choices), reference, identity, mass, 40, 100)
    np.testing.assert_allclose(initial[METRICS], np.array(selected['metrics']), rtol=0, atol=1e-5)
    caps, colours = np.full(len(points), 1522, np.int32), cj.parity(model.m)
    if np.any(squared > caps):
        raise AssertionError('起点超hard max1522')
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    current, measured, records = model, initial.copy(), []
    for colour in range(8):
        change, bad, invalid = tail.gains(indices, weights, acc, reference, identity, mass,
            current.nodes.reshape(-1, 3), colours, colour, caps, root, 4, 40, 100)
        if invalid:
            raise AssertionError('共享parity几何/cap失败')
        moves, predicted, accepted = choose(change, bad, colours, colour, measured, budget)
        current = tail.apply(current, indices, weights, acc, moves, reference)
        fresh = ot.predict(current, points, choices)
        np.testing.assert_array_equal(fresh, ((acc+io.ONE//2) >> io.Q).astype(np.uint8))
        after, squared = tail.measure(fresh, reference, identity, mass, 40, 100)
        if np.max(np.abs(after-measured-predicted)) > 1e-5 or np.any(squared > caps) or improves(score(measured[METRICS], budget), score(after[METRICS], budget)):
            raise AssertionError('fresh完整支撑/cap或可行性目标回退')
        records.append({'colour': colour, 'changed_nodes': len(accepted), 'before': measured.tolist(), 'after': after.tolist(),
            'score': score(after[METRICS], budget), 'max_squared': int(squared.max()), 'moves': accepted,
            'maximum_gain_error': float(np.max(np.abs(after-measured-predicted))),
            'host_available_memory_bytes': psutil.virtual_memory().available, 'process_rss_bytes': psutil.Process().memory_info().rss})
        measured = after
        save(args.output/'progress.json', records)
        print(json.dumps({k: v for k, v in records[-1].items() if k != 'moves'}, ensure_ascii=False), flush=True)
    np.savez_compressed(args.output/'model.npz', format=np.array('oriented_tetra_v1_experimental'), grid=current.grid,
        nodes=current.nodes, shared_idx=current.idx, channel_frac=current.channel_frac)
    save(args.output/'summary.json', {'before': initial.tolist(), 'after': measured.tolist(), 'budget': budget.tolist(),
        'five_constraints_passed': bool(np.all(measured[METRICS] <= budget+np.array([1e-5, 1e-5, 1e-12, 1e-12, 0]))),
        'five_metric_order': metric_names, 'max_squared': int(squared.max()),
        'model_sha256': digest(args.output/'model.npz'), 'cap_violations': 0, 'fresh_byte_mismatches': 0,
        'serialized_stripe_bytes': 12, 'offline_design_bytes': int(indices.nbytes+weights.nbytes), 'runtime_memory_unmeasured': True})


if __name__ == '__main__':
    main()
