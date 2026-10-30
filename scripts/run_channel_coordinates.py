"""独立执行一个9块分输出坐标DP，仅保存实验NPZ，最终一次原样本门禁。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_coordinates as cc, io, study_provenance


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']:
        raise ValueError(f'冻结输入SHA不同：{path}')
    return path


def metrics(prediction, target):
    e = prediction.astype(np.int32)-target.astype(np.int32)
    squared = np.sum(e*e, axis=1, dtype=np.int32)
    distance = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    hist = np.bincount(squared, minlength=len(distance)).astype(np.int64)
    count, rank = len(squared), .99*(len(squared)-1)
    lo, hi = np.searchsorted(np.cumsum(hist), [int(np.floor(rank)), int(np.ceil(rank))], side='right')
    remaining = tail_count = max(1, int(np.ceil(count*.01)))
    tail = 0.
    for d in np.flatnonzero(hist)[::-1]:
        take = min(remaining, int(hist[d])); tail += take*distance[d]; remaining -= take
        if remaining == 0: break
    return {'n': count, 'mean': float(hist@distance/count),
        'rms': float(np.sqrt(hist@np.arange(len(hist), dtype=np.int64)/count)),
        'p99': float(distance[lo]+(rank-np.floor(rank))*(distance[hi]-distance[lo])),
        'max': float(distance[np.flatnonzero(hist)[-1]]), 'cvar_1pct': tail/tail_count,
        **{f'fraction_ge_{t}': float(hist[t*t:].sum()/count) for t in (1, 2, 3, 5)}}


def failures(value, old):
    failed = []
    for group in ('cube', 'photos'):
        for metric in ('mean', 'rms', 'p99', 'max'):
            if value[group][metric] > old[group][metric]+1e-12: failed.append(group+'.'+metric)
        if value[group]['mean'] > .97*old[group]['mean']: failed.append(group+'.mean_reduction_3pct')
    if value['photos']['worst_image_p99'] > old['photos']['worst_image_p99']+1e-12:
        failed.append('photos.worst_image_p99')
    if not any(value[group]['p99'] < old[group]['p99']-1e-12 for group in ('cube', 'photos')):
        failed.append('p99_strict_improvement')
    if value['hotspots']['max'] > old['hotspots']['max']+1e-12: failed.append('hotspots.max')
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/velvia-channel-coordinates-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖旧运行')
    plan = read(args.plan); paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    if plan['threads'] != 4 or plan['tail_at'] != 6 or plan['tail_weight'] != .02:
        raise ValueError('只接受冻结9块目标和4线程')
    numba.set_num_threads(4)
    contract_path = ROOT/plan['contract']; contract = read(contract_path)
    if (contract.get('pass') is not True or len(contract['cases']) != 9 or contract['grid_sizes_checked'] != [17, 33]
            or any(r['integer_states'] != 65537 or r['cap_count_mismatches'] or r['integer_forward_mismatches']
                or r['other_channel_cache_mismatches'] or not r['dp_monotone_endpoints_and_cap_pass'] for r in contract['cases'])
            or any(digest(ROOT/name) != sha for name, sha in contract['source_sha256'].items())):
        raise ValueError('集中合同未通过或数值来源已改变')
    previous, selection, samples, optimizer = [read(paths[name]) for name in
        ('prior_run', 'prior_selection', 'prior_samples', 'prior_optimizer')]
    prior_plan = previous['identity']['plan']
    if (previous['identity_sha256'] != study_provenance.identity_digest(previous['identity'])
            or selection['run_identity'] != previous['identity_sha256']
            or selection['candidates']['alternating_integer_iter003']['model_sha256'] != plan['inputs']['initial']['sha256']
            or prior_plan['baseline_sha256'] != plan['inputs']['baseline']['sha256']
            or prior_plan['baseline_cube_sha256'] != plan['inputs']['baseline_stream']['sha256']
            or prior_plan['table_sha256'] != plan['inputs']['table']['sha256']
            or prior_plan['mass'] != plan['mass'] or prior_plan['tail_at'] != 6 or prior_plan['tail_weight'] != .02
            or optimizer['chain_envelope']['caps_file_sha256'] != plan['inputs']['caps']['sha256']):
        raise ValueError('优化起点/验收基线/质量或cap身份不同')
    model = io.load_sparse(paths['initial'], competition=True)
    frozen = np.load(paths['frozen_samples'])
    points, targets, mass = [frozen[name] for name in ('points', 'targets', 'mass')]
    table = io.load_full(paths['table'], mmap=True).reshape(-1, 3)
    if not np.array_equal(targets, table): raise ValueError('冻结标签不是本级原完整表')
    caps = np.load(paths['caps'], mmap_mode='r')
    if caps.shape != (256**3,) or caps.dtype != np.int32: raise ValueError('cap形状或类型不同')
    old_stream = np.memmap(paths['baseline_stream'], np.uint8, 'r', shape=(256**3, 3))
    for start in range(0, len(table), 1 << 18):
        stop = min(start+(1 << 18), len(table))
        e = old_stream[start:stop].astype(np.int32)-table[start:stop].astype(np.int32)
        if not np.array_equal(caps[start:stop], np.maximum(49, np.sum(e*e, axis=1, dtype=np.int32))):
            raise ValueError('逐色cap不是旧2dd锚定公式')
    guard = {key: frozen[key+'_selection'] for key in ('cube', 'photos', 'hotspots')}
    for key, values in guard.items():
        if len(values) != samples['selection'][key]['n'] or hashlib.sha256(values.tobytes()).hexdigest() != samples['selection'][key]['sha256']:
            raise ValueError('选择像素与旧固定样本不同')
    if [len(guard[key]) for key in ('cube', 'photos', 'hotspots')] != [262144, 20*4096, 8192]:
        raise ValueError('选择规模不是冻结262144/20*4096/8192')
    files = [Path(__file__), args.plan, ROOT/'scripts/verify_channel_coordinates.py',
        *[ROOT/'python/lutlab'/name for name in ('channel_coordinates.py', 'axis_calibration.py', 'exact_axis.py',
            'monotone_axis.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': sources,
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
        'contract_sha256': digest(contract_path), 'input_sha256': {name: digest(path) for name, path in paths.items()},
        'scope': '一个固定9块拟合，最终一次旧样本选型；没有原生、新全域流/百图/性能'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files: archive.write(path, path.relative_to(ROOT).as_posix())
    print('开始唯一分通道坐标9块拟合；复用原样本/质量/cap，无照片解码', flush=True)
    candidate, report = cc.propose(model, points, targets, mass, caps=caps, parts=4,
        progress=lambda r: print(f"channel={r['channel']} axis={r['axis']} loss={r['after_weighted_objective']:.9f} changed={r['changed_coordinates']} shift={r['maximum_fraction_shift']} time={r['seconds']:.1f}s", flush=True))
    (args.output/'optimizer.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    destination = args.output/'channel-coordinates.npz'
    np.savez_compressed(destination, format=np.array('channel_coordinates_v1_experimental'),
        grid=candidate.grid, nodes=candidate.nodes, shared_idx=candidate.idx, channel_frac=candidate.channel_frac,
        source_model_sha256=np.array(plan['inputs']['initial']['sha256']),
        baseline_model_sha256=np.array(plan['inputs']['baseline']['sha256']))
    current = {}
    for key, rgb in guard.items():
        prediction = cc.predict(candidate, rgb)
        truth = table[rgb.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
        current[key] = metrics(prediction, truth)
        if key == 'photos':
            per = [metrics(prediction[start:start+4096], truth[start:start+4096]) for start in range(0, len(rgb), 4096)]
            current[key].update(worst_image_p99=max(row['p99'] for row in per), per_image=per)
    failed = failures(current, selection['baseline_samples'])
    if report['training_cap_violations']: failed.append('training_colour_caps')
    if sources != {path.relative_to(ROOT).as_posix(): digest(path) for path in files}:
        raise ValueError('拟合过程中冻结源码改变')
    result = {'run_identity': run['identity_sha256'], 'representation_sha256': digest(destination),
        'baseline_samples': selection['baseline_samples'], 'candidate_samples': current,
        'failures': failed, 'selected': not failed, 'full_evaluation_performed': False,
        'native_validation_performed': False, 'scope': plan['limits']}
    (args.output/'selection.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'samples': {key: {m: current[key][m] for m in ('mean', 'rms', 'p99', 'max')} for key in ('cube', 'photos')},
        'selected': not failed, 'failures': failed, 'representation_sha256': digest(destination)}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
