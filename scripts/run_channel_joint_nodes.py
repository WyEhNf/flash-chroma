"""固定3e5分通道几何，执行唯一8色26方向RGB联合节点精化并以原样本一次选型。"""
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
from lutlab import channel_coordinates as cc, channel_joint_nodes as cn, io, study_provenance
from run_channel_coordinates import digest, read, checked, metrics, failures


def incremental_failures(value, old):
    failed = []
    for group in ('cube', 'photos'):
        for metric in ('mean', 'rms', 'p99', 'max'):
            if value[group][metric] > old[group][metric]+1e-12:
                failed.append(group+'.'+metric+'_vs_3e5')
        if value[group]['mean'] > .995*old[group]['mean']:
            failed.append(group+'.mean_reduction_0p5pct_vs_3e5')
    if value['photos']['worst_image_p99'] > old['photos']['worst_image_p99']+1e-12:
        failed.append('photos.worst_image_p99_vs_3e5')
    if value['hotspots']['max'] > old['hotspots']['max']+1e-12:
        failed.append('hotspots.max_vs_3e5')
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/velvia-channel-joint-nodes-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖旧阶段')
    plan = read(args.plan); paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    if (plan['threads'] != 4 or plan['tail_at'] != 6. or plan['tail_weight'] != .02
            or plan['colours'] != 8 or plan['directions'] != 26 or plan['incremental_mean_reduction'] != .005
            or plan['mass'] != {'cube': .48, 'photos': .48, 'boundary': .02, 'hotspots': .02}):
        raise ValueError('只接受冻结8色26方向/目标/选型口径')
    numba.set_num_threads(4)
    contract_path = ROOT/plan['contract']; contract = read(contract_path)
    if (contract.get('pass') is not True or [r['m'] for r in contract['cases']] != [17, 33]
            or any(r['groups'] != 8 or r['uint64_output_mismatches'] or r['cap_count_mismatches']
                or r['fresh_cache_mismatches'] or r['geometry_errors']
                or r['maximum_gain_error'] > 1e-12 or not r['zero_mass_cap_prohibitions']
                for r in contract['cases'])
            or any(digest(ROOT/name) != sha for name, sha in contract['source_sha256'].items())):
        raise ValueError('集中整数合同未通过或源码改变')
    previous = read(paths['prior_run']); selection = read(paths['prior_selection']); samples = read(paths['prior_samples'])
    identity = dict(previous); identity.pop('identity_sha256')
    if (previous['identity_sha256'] != study_provenance.identity_digest(identity)
            or selection['run_identity'] != previous['identity_sha256']
            or selection['representation_sha256'] != plan['inputs']['initial']['sha256']
            or previous['plan']['inputs']['frozen_samples'] != plan['inputs']['frozen_samples']
            or previous['plan']['inputs']['caps'] != plan['inputs']['caps']
            or previous['plan']['inputs']['baseline'] != plan['inputs']['baseline']
            or previous['plan']['inputs']['baseline_stream'] != plan['inputs']['baseline_stream']
            or previous['plan']['inputs']['table'] != plan['inputs']['table']
            or previous['plan']['mass'] != plan['mass'] or not selection['selected']):
        raise ValueError('3e5起点/2dd验收基线/样本质量或旧选型身份不同')
    initial = np.load(paths['initial'])
    if str(initial['format']) != 'channel_coordinates_v1_experimental': raise ValueError('实验NPZ格式不同')
    model = cc.ChannelLut(initial['grid'].copy(), initial['nodes'].copy(), initial['shared_idx'].copy(), initial['channel_frac'].copy())
    cc.validate(model)
    if model.m != 33 or str(initial['baseline_model_sha256']) != plan['inputs']['baseline']['sha256']:
        raise ValueError('初始尺寸/基线不同')
    frozen = np.load(paths['frozen_samples'])
    points, targets, mass = [frozen[name] for name in ('points', 'targets', 'mass')]
    table = io.load_full(paths['table'], mmap=True).reshape(-1, 3)
    if points.shape != (256**3, 3) or not np.array_equal(targets, table): raise ValueError('完整本级原表标签不同')
    for start in range(0, len(points), 1 << 18):
        p = points[start:start+(1 << 18)].astype(np.int64)
        if not np.array_equal(p@np.array([65536, 256, 1], np.int64), np.arange(start, start+len(p))):
            raise ValueError('完整RGB8 canonical顺序不同')
    caps = np.load(paths['caps'], mmap_mode='r')
    if caps.shape != (256**3,) or caps.dtype != np.int32: raise ValueError('cap格式不同')
    old_stream = np.memmap(paths['baseline_stream'], np.uint8, 'r', shape=(256**3, 3))
    for start in range(0, len(table), 1 << 18):
        stop = min(start+(1 << 18), len(table))
        e = old_stream[start:stop].astype(np.int32)-table[start:stop].astype(np.int32)
        if not np.array_equal(caps[start:stop], np.maximum(49, np.sum(e*e, axis=1, dtype=np.int32))):
            raise ValueError('cap不是原2dd锚定公式')
    guard = {key: frozen[key+'_selection'] for key in ('cube', 'photos', 'hotspots')}
    for key, rgb in guard.items():
        if (len(rgb) != samples['selection'][key]['n']
                or hashlib.sha256(rgb.tobytes()).hexdigest() != samples['selection'][key]['sha256']):
            raise ValueError('选择样本改变')
    if [len(guard[k]) for k in ('cube', 'photos', 'hotspots')] != [262144, 81920, 8192]:
        raise ValueError('选择规模不同')
    files = [Path(__file__), args.plan, ROOT/'scripts/verify_channel_joint_nodes.py', ROOT/'scripts/verify_channel_coordinates.py',
        ROOT/'scripts/run_channel_coordinates.py', *[ROOT/'python/lutlab'/name for name in
        ('channel_joint_nodes.py', 'channel_global_nodes.py', 'channel_coordinates.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': sources,
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
        'contract_sha256': digest(contract_path), 'input_sha256': {name: digest(p) for name, p in paths.items()},
        'scope': '单次8色26方向RGB联合节点精化，训练fresh检查；一个最终候选固定样本门禁，无新完整流/百图/native/性能'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files: archive.write(path, path.relative_to(ROOT).as_posix())
    print('开始唯一固定几何8色26方向RGB联合节点精化；复用原mass/caps，不解码照片', flush=True)
    candidate, report = cn.propose(model, points, targets, mass, caps=caps,
        progress=lambda row: print(json.dumps(row, ensure_ascii=False), flush=True))
    (args.output/'optimizer.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    destination = args.output/'channel-joint-nodes.npz'
    np.savez_compressed(destination, format=np.array('channel_coordinates_v1_experimental'), grid=candidate.grid,
        nodes=candidate.nodes, shared_idx=candidate.idx, channel_frac=candidate.channel_frac,
        source_model_sha256=np.array(plan['inputs']['initial']['sha256']),
        baseline_model_sha256=np.array(plan['inputs']['baseline']['sha256']))
    for name in ('grid', 'shared_idx', 'channel_frac'):
        if not np.array_equal(initial[name], np.load(destination)[name]): raise AssertionError('固定坐标改变')
    current = {}
    for key, rgb in guard.items():
        prediction = cc.predict(candidate, rgb)
        truth = table[rgb.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
        current[key] = metrics(prediction, truth)
        if key == 'photos':
            per = [metrics(prediction[s:s+4096], truth[s:s+4096]) for s in range(0, len(rgb), 4096)]
            current[key].update(worst_image_p99=max(row['p99'] for row in per), per_image=per)
    original_failed = failures(current, selection['baseline_samples'])
    extra_failed = incremental_failures(current, selection['candidate_samples'])
    failed = original_failed+extra_failed
    if report['training_cap_violations']: failed.append('training_colour_caps')
    if sources != {p.relative_to(ROOT).as_posix(): digest(p) for p in files}: raise ValueError('实际数值源码改变')
    result = {'run_identity': run['identity_sha256'], 'representation_sha256': digest(destination),
        'baseline_samples': selection['baseline_samples'], 'initial_3e5_samples': selection['candidate_samples'],
        'candidate_samples': current, 'original_gate_failures': original_failed,
        'incremental_gate_failures': extra_failed, 'failures': failed, 'selected': not failed,
        'full_evaluation_performed': False, 'native_validation_performed': False, 'scope': plan['limits']}
    (args.output/'selection.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'samples': {key: {m: current[key][m] for m in ('mean', 'rms', 'p99', 'max')}
        for key in ('cube', 'photos')}, 'selected': not failed, 'failures': failed,
        'representation_sha256': digest(destination)}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
