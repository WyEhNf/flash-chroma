"""固定max_first全链，枚举热点物理首级节点的完整正支撑与52个单节点方向。"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import time
from contextlib import ExitStack
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'python'), str(ROOT/'experiments/channel-runtime')]
import numba
import numpy as np
from channel_native import Library
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from verify_channel_coordinates import integer_oracle


TOTAL = 256**3
TRAINING_PIXELS = 60*1024*768
BLOCK = 65536


def train_counts(raw, total_mass):
    value = np.asarray(raw, np.float64)*(TRAINING_PIXELS/total_mass)
    counts = np.rint(value).astype(np.int64)
    residual = float(np.max(np.abs(value-counts), initial=0))
    if residual > 1e-6 or np.any(counts < 0):
        raise AssertionError('原60图逐RGB8整数频数恢复失败')
    return counts, residual


def squared(a, b):
    delta = a.astype(np.int32)-b.astype(np.int32)
    return np.sum(delta*delta, axis=1, dtype=np.int32)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('不覆盖首级有限证书')
    plan_path = ROOT/'experiments/p16-cinema-first-hotspot-v1.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass']: raise ValueError('有限独立合同未通过')
    for name, sha in contract['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('有限合同源已变：'+name)
    directory = ROOT/'artifacts/cinema-second-nodes-v1/max_first/candidate'
    cache = args.cache_root.resolve(); calibration = cache/'artifacts/cinema-axis-calibration-v1'
    paths = {'first': directory/'model.npz', 'first_slut': directory/'candidate-base.slut',
             'sidecar': directory/'channel-frac.bin', 'stage2': directory/'stage2.slut',
             'stage3': cache/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut',
             'stage4': directory/'stage4.slut',
             'cube': ROOT/'artifacts/cinema-second-accept-max_first-v1/candidate.rgb',
             'points': calibration/'envelope-arrivals.npy', 'reference': calibration/'envelope-reference.npy',
             'mass': calibration/'photo-arrival-frequency.npy',
             'library': Path('F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll')}
    expected = {'first': '0ea0a380b83e3581668654f45a7aa5682515b2dfb6ef7c8aeb96f82f60afa030',
                'first_slut': '73dc15fea4db5fb10a481336e18256cff040ca291a9713dc1c383ad84739b5ad',
                'sidecar': '85b045f0247aca016f986b61237302d4f812705d71a390226b8df04189dd7fff',
                'stage2': '904e30a1c0f805175b0b9518949e4e96c9ff2a7e7980978ed8e90fd1282bd924',
                'stage3': '95cb685e2298c49744cf91502bc06a3f8f20e97d1e654872ba1cfd59a48e7234',
                'stage4': '5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386',
                'cube': '143e5cc05f4f2635608cd7720b4013a10998d3f7acc8cf35275b38dcfba0792e',
                'points': 'fac03692667ab8d5220a4a09035b420d96037094c101b91011de303209ccaaea',
                'reference': 'ec79ca618022293b2d2f5c832f1a8647c88e4994ce820664310e09c0f4bf5690',
                'mass': '1eff7aab15715845bbc3efda68043a62a5c2dd9162f33717cee8bea5d36b756e',
                'library': '58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158'}
    hashes = {name: digest(path) for name, path in paths.items()}
    if hashes != expected: raise ValueError('输入不等于冻结max_first与原60图频数')
    sources = [Path(__file__), plan_path, ROOT/'scripts/check_cinema_first_hotspot.py',
               ROOT/'python/lutlab/channel_hotspot_support.py', ROOT/'scripts/run_channel_tail_nodes.py',
               ROOT/'scripts/verify_channel_coordinates.py', ROOT/'experiments/channel-runtime/channel_native.py',
               *[ROOT/'python/lutlab'/name for name in ('channel_coordinates.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    args.output.mkdir(parents=True)
    numba.set_num_threads(4); started = time.perf_counter()
    save(args.output/'run.json', {'inputs': {k: {'path': str(paths[k].resolve()), 'sha256': v} for k, v in hashes.items()},
         'sources_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
         'contract': {'path': str(args.contract.resolve()), 'sha256': digest(args.contract)}, 'plan': plan,
         'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
         'test_type': '完整支撑与固定52方向有限可行性；共享主机质量执行，不计性能'})
    first = load_model(paths['first'])
    rest = [cc.from_sparse(io.load_sparse(paths[name], competition=True)) for name in ('stage2', 'stage3', 'stage4')]
    points = np.load(paths['points'], mmap_mode='r'); gold = np.load(paths['reference'], mmap_mode='r')
    mass = np.load(paths['mass'], mmap_mode='r'); total_mass = float(mass.sum(dtype=np.float64))
    baseline = np.memmap(paths['cube'], np.uint8, 'r', shape=(TOTAL, 3))
    if any(v.shape != (TOTAL, 3) or v.dtype != np.uint8 for v in (points, gold)) or mass.shape != (TOTAL,):
        raise ValueError('冻结完整域形状或类型不符')
    baseline_hist = np.zeros(51, np.int64); training_hist = np.zeros(51, np.int64)
    hotspots, training_total, training_residual = [], 0, 0.
    for start in range(0, TOTAL, BLOCK):
        stop = start+BLOCK; np.testing.assert_array_equal(hs.key(points[start:stop]), np.arange(start, stop, dtype=np.uint32))
        sq = squared(baseline[start:stop], gold[start:stop])
        if int(sq.max()) > 50: raise AssertionError('起点max平方误差超过50')
        counts, residual = train_counts(mass[start:stop], total_mass)
        training_total += int(counts.sum()); training_residual = max(training_residual, residual)
        baseline_hist += hs.histogram(sq); training_hist += hs.histogram(sq, counts)
        hotspots.extend((np.flatnonzero(sq == 50)+start).tolist())
    if training_total != TRAINING_PIXELS or len(hotspots) != plan['expected_hotspot_inputs']:
        raise AssertionError('原60图整数频数总数或全部116热点不符')
    hotspots = np.array(hotspots, np.uint32)
    i, w, _ = hs.basis(first, points[hotspots]); selected = np.unique(i[w > 0])
    if len(selected) > plan['resources']['maximum_selected_nodes']: raise MemoryError('热点物理节点超过预注册上界')
    box_rows = []
    for node in selected:
        coordinate = np.unravel_index(int(node), (first.m,)*3)
        lengths = [int(np.count_nonzero((first.idx[a] == coordinate[a]) |
                       (first.idx[a].astype(np.int64) == coordinate[a]-1))) for a in range(3)]
        box_rows.append(int(np.prod(lengths)))
    if max(box_rows, default=0) > plan['resources']['maximum_single_box_rows']:
        raise MemoryError('预分配前完整节点编码盒已超资源上界')
    save(args.output/'profile-initial.json', {'hotspot_rows': len(hotspots), 'physical_nodes': selected.tolist(),
         'selected_nodes': len(selected), 'maximum_single_box_rows': plan['resources']['maximum_single_box_rows'],
         'actual_maximum_single_box_rows': max(box_rows, default=0),
         'conservative_single_box_temporary_bytes': max(box_rows, default=0)*512,
         'suffix_payload_bytes': 50331648, 'full_domain_mask_bytes': TOTAL,
         'full_design_allocated': False, 'training_pixels': training_total, 'training_count_residual_max': training_residual,
         'baseline_uniform': hs.metrics(baseline_hist), 'baseline_training': hs.metrics(training_hist)})
    print({'phase': '固定输入与全部热点', 'hotspots': len(hotspots), 'nodes': len(selected),
           'max_box_rows': max(box_rows, default=0), 'box_temporary_bound': max(box_rows, default=0)*512}, flush=True)
    # 后缀由当前三张表完整计算，独立u64重放全部16M输入。
    suffix = np.lib.format.open_memmap(args.output/'suffix.npy', mode='w+', dtype=np.uint8, shape=(TOTAL, 3))
    with ExitStack() as stack:
        if hasattr(os, 'add_dll_directory'):
            stack.enter_context(os.add_dll_directory('E:/mingw64/bin'))
            stack.enter_context(os.add_dll_directory(str(paths['library'].parent)))
        library = Library(paths['library'], hashes['library'])
        with library.chain([paths[name] for name in ('stage2', 'stage3', 'stage4')]) as chain:
            suffix_model_bytes = chain.model_bytes
            for start in range(0, TOTAL, BLOCK):
                stop = start+BLOCK; source = np.asarray(points[start:stop])
                actual = chain.apply(source.copy(), kernel='avx2', threads=4)
                expected_rgb = source
                for model in rest: expected_rgb = integer_oracle(model, expected_rgb)
                np.testing.assert_array_equal(actual, expected_rgb); suffix[start:stop] = actual
    suffix.flush()
    selected_mask = np.zeros(first.m**3, bool); selected_mask[selected] = True
    independent_counts = np.zeros(first.m**3, np.int64); global_union_parts, union_rows = [], 0
    for start in range(0, TOTAL, BLOCK):
        stop = start+BLOCK; source = points[start:stop]
        ids, weight = hs.corners(first, source)
        positive = np.any(weight > 0, axis=2) & selected_mask[ids]
        independent_counts += np.bincount(ids[positive], minlength=first.m**3)
        hit = np.any(positive, axis=1); part = (np.flatnonzero(hit)+start).astype(np.uint32)
        union_rows += len(part)
        if union_rows > plan['resources']['maximum_union_rows']: raise MemoryError('完整正支撑并集超过冻结资源界')
        global_union_parts.append(part)
        acc = np.sum(weight.astype(np.int64)*first.nodes.reshape(-1, 3)[ids], axis=1, dtype=np.int64)
        output = ((acc+32768)>>16).astype(np.uint8)
        np.testing.assert_array_equal(suffix[hs.key(output)], baseline[start:stop])
    independent_union = np.concatenate(global_union_parts); del global_union_parts
    local_union = np.zeros(TOTAL, bool); support_counts, support_keys = [], []
    for node in selected:
        source, _, _ = hs.support(first, int(node), plan['resources']['maximum_single_box_rows'])
        keys = hs.key(source)
        if len(keys) != independent_counts[node]: raise AssertionError('完整域独立正支撑计数不符')
        local_union[keys] = True; support_keys.append(keys)
        support_counts.append({'physical_node': int(node), 'complete_support_rows': len(keys),
                               'hotspot_rows': int(np.isin(hotspots, keys).sum())})
    np.testing.assert_array_equal(np.flatnonzero(local_union).astype(np.uint32), independent_union)
    del local_union
    np.savez_compressed(args.output/'support-index.npz', hotspot_keys=hotspots, selected_nodes=selected,
                        union_keys=independent_union, support_keys=np.concatenate(support_keys),
                        offsets=np.r_[0, np.cumsum([len(k) for k in support_keys], dtype=np.int64)])
    del support_keys
    before_uniform, before_training = hs.metrics(baseline_hist), hs.metrics(training_hist)
    measured_metrics = ('mean', 'rms', 'p99', 'cvar_1pct')
    records, eligible = [], []
    for position, node in enumerate(selected):
        source, acc, weight = hs.support(first, int(node), plan['resources']['maximum_single_box_rows'])
        keys = hs.key(source); counts, _ = train_counts(mass[keys], total_mass)
        old_sq = squared(baseline[keys], gold[keys])
        remainder = baseline_hist-hs.histogram(old_sq); training_remainder = training_hist-hs.histogram(old_sq, counts)
        if np.any(remainder < 0) or np.any(training_remainder < 0): raise AssertionError('未触及直方图出现负计数')
        for delta in hs.DIRECTIONS:
            moved = first.nodes.reshape(-1, 3)[node].astype(np.int32)+delta
            record = {'physical_node': int(node), 'delta': delta.tolist(), 'support_rows': len(keys),
                      'hotspot_rows': support_counts[position]['hotspot_rows']}
            if np.any(moved < 0) or np.any(moved > 255):
                records.append({**record, 'rejected': '节点RGB8越界'}); continue
            first_output = ((acc+weight.astype(np.int64)*delta+32768)>>16).astype(np.uint8)
            output = suffix[hs.key(first_output)]; square = squared(output, gold[keys])
            local_max = int(square.max(initial=0))
            if local_max > 50:
                records.append({**record, 'rejected': '完整正支撑超过原cap50', 'local_max_squared': local_max,
                                'cap_violating_rows': int(np.count_nonzero(square > 50))}); continue
            new_hist = remainder+hs.histogram(square); new_train_hist = training_remainder+hs.histogram(square, counts)
            after_uniform, after_training = hs.metrics(new_hist), hs.metrics(new_train_hist)
            failures = [label+'_'+metric for label, after, before in
                        (('uniform', after_uniform, before_uniform), ('training', after_training, before_training))
                        for metric in measured_metrics if after[metric] > before[metric]+1e-12]
            if after_uniform['max_squared'] >= 50: failures.append('strict_max49')
            record.update(uniform=after_uniform, training=after_training, failures=failures,
                          max50_rows=int(new_hist[50]), changed_rows=int(np.count_nonzero(square != old_sq)))
            records.append(record)
            if not failures:
                # 本证书不联合应用；原始52方向全部保留，不拿百图择优。
                eligible.append(record)
        print({'phase': '有限单节点证书', 'node': int(node), 'completed': position+1,
               'total': len(selected), 'eligible': len(eligible), 'seconds': time.perf_counter()-started}, flush=True)
    save(args.output/'directions.json', records)
    cap_pass = [r for r in records if 'uniform' in r]
    summaries = {'baseline_uniform': before_uniform, 'baseline_training': before_training,
                 'hotspot_rows': len(hotspots), 'selected_nodes': len(selected), 'union_rows': len(independent_union),
                 'support': support_counts, 'directions_per_node': 52, 'total_directions': len(records),
                 'cap_pass_directions': len(cap_pass), 'eligible_directions': eligible,
                 'best_max50_count_cap_pass': min((r['max50_rows'] for r in cap_pass), default=len(hotspots)),
                 'maximum_hotspots_covered_by_single_node': max((r['hotspot_rows'] for r in support_counts), default=0),
                 'suffix_sha256': digest(args.output/'suffix.npy'), 'suffix_payload_bytes': suffix.nbytes,
                 'suffix_native_model_bytes': suffix_model_bytes, 'independent_full_domain_rows': TOTAL,
                 'support_count_and_union_mismatches': 0, 'full_domain_baseline_replay_mismatches': 0,
                 'full_design_allocated': False, 'seconds': time.perf_counter()-started,
                 'eligible_for_independent_final_checks': bool(eligible),
                 'scope': '每个热点物理节点单独52方向完整支撑证书；未找到不证明联合修改或其他几何无解；无新照片/native/性能验收'}
    save(args.output/'summary.json', summaries); print({k: v for k, v in summaries.items() if k not in ('support', 'eligible_directions')}, flush=True)


if __name__ == '__main__': main()
