"""固定aed首级分输出几何，节点26方向8色一次；对已验af974链严格选型。"""
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
from lutlab import channel_coordinates as cc, channel_suffix_joint_nodes as sj, io, study_provenance
from run_channel_coordinates import digest, read, checked, metrics


def array_sha(array):
    return hashlib.sha256(memoryview(np.ascontiguousarray(array))).hexdigest()


def failures(value, old):
    failed = []
    for group in ('cube', 'photos'):
        for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
            if value[group][metric] > old[group][metric]+1e-12: failed.append(group+'.'+metric)
        if value[group]['mean'] > .97*old[group]['mean']: failed.append(group+'.mean_reduction_3pct')
    if value['photos']['worst_image_p99'] > old['photos']['worst_image_p99']+1e-12:
        failed.append('photos.worst_image_p99')
    if not any(value[g]['p99'] < old[g]['p99']-1e-12 for g in ('cube', 'photos')):
        failed.append('p99_strict_improvement')
    return failed


def evaluate(guard, reference, stream=None, model=None, suffix=None):
    result = {}
    for group, rgb in guard.items():
        keys = rgb.astype(np.int64)@np.array([65536, 256, 1], np.int64)
        if stream is not None:
            prediction = stream[keys]
        else:
            own = cc.predict(model, rgb)
            prediction = suffix[own.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
        target = reference[keys]
        result[group] = metrics(prediction, target)
        if group == 'photos':
            per = [metrics(prediction[s:s+4096], target[s:s+4096]) for s in range(0, len(rgb), 4096)]
            result[group].update(per_image=per, worst_image_p99=max(row['p99'] for row in per),
                mean_image_cvar_1pct=float(np.mean([row['cvar_1pct'] for row in per])))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/cinema-channel-suffix-joint-nodes-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖旧结果')
    plan = read(args.plan); paths = {key: checked(spec) for key, spec in plan['inputs'].items()}
    if (plan['threads'] != 4 or plan['colours'] != 8 or plan['directions'] != 26 or plan['tail_at'] != 6. or plan['tail_weight'] != .02
            or plan['suffix_weight'] != 1. or plan['mass'] != {'own_uniform': .1, 'cube_arrival': .45, 'photo_arrival': .45}):
        raise ValueError('只接受冻结8色26方向/同质量/同双项目标')
    numba.set_num_threads(4)
    contract_path = ROOT/plan['contract']; contract = read(contract_path)
    if (contract.get('pass') is not True or [row['m'] for row in contract['cases']] != [17, 33]
            or any(row['groups'] != 8 or row['maximum_gain_error'] > 1e-10 or row['geometry_errors']
                or row['cap_count_mismatches'] or row['uint64_output_mismatches'] or row['fresh_cache_mismatches']
                or not row['zero_mass_cap_prohibitions'] for row in contract['cases'])
            or any(digest(ROOT/name) != sha for name, sha in contract['source_sha256'].items())):
        raise ValueError('集中联合双项loss/非线性后缀/u64合同未通过或来源改变')
    previous, selection, full = [read(paths[k]) for k in ('prior_run', 'prior_selection', 'prior_full')]
    if (previous['identity_sha256'] != study_provenance.identity_digest(previous['identity'])
            or previous['identity_sha256'] != plan['prior_run_identity']
            or selection['run_identity'] != plan['prior_run_identity'] or full['run_identity'] != plan['prior_run_identity']
            or selection['winner'] != plan['prior_winner'] or not full['acceptance']['accepted']
            or full['acceptance']['failed'] or full['model_sha256'] != plan['baseline_chain_model_sha256']
            or selection['candidates'][plan['prior_winner']]['model_sha256'] != plan['inputs']['baseline_initial']['sha256']
            or full['cube']['prediction_sha256'] != plan['inputs']['baseline_stream']['sha256']
            or any(row['byte_mismatches'] or row['sha256'] != full['cube']['prediction_sha256'] for row in full['native'])):
        raise ValueError('已有最佳链的run/winner/full/native身份或状态不同')
    suffix_specs = plan['suffix_models']
    for spec in suffix_specs: checked(spec)
    if ([row['sha256'] for row in suffix_specs] != full['model_sha256'][1:]
            or suffix_specs != previous['identity']['plan']['baseline_models'][1:]
            or plan['tables'] != previous['identity']['plan']['tables']):
        raise ValueError('后三模型/四张独立原表与历史冻结合同不同')
    for spec in plan['tables']: checked(spec)
    baseline_model = io.load_sparse(paths['baseline_initial'], competition=True)
    initial = np.load(paths['initial'])
    if str(initial['format']) != 'channel_coordinates_v1_experimental': raise ValueError('aed输入格式不同')
    model = cc.ChannelLut(initial['grid'], initial['nodes'], initial['shared_idx'], initial['channel_frac'])
    cc.validate(model)
    if (model.m != 33 or str(initial['source_model_sha256']) != plan['inputs']['baseline_initial']['sha256']
            or str(initial['baseline_model_sha256']) != plan['inputs']['baseline_initial']['sha256']
            or initial['frozen_suffix_model_sha256'].tolist() != full['model_sha256'][1:]
            or not np.array_equal(model.nodes, baseline_model.nodes) or not np.array_equal(model.grid, baseline_model.grid)
            or not np.array_equal(model.idx, baseline_model.tables()[0])):
        raise ValueError('aed坐标起点/原节点/基线/后三模型身份不同')
    proposal_run, proposal_selection, proposal_optimizer = [read(paths[key]) for key in
        ('proposal_run', 'proposal_selection', 'proposal_optimizer')]
    proposal_identity = dict(proposal_run); proposal_identity.pop('identity_sha256')
    if (proposal_run['identity_sha256'] != study_provenance.identity_digest(proposal_identity)
            or proposal_selection['run_identity'] != proposal_run['identity_sha256']
            or proposal_selection['representation_sha256'] != plan['inputs']['initial']['sha256']
            or proposal_selection['baseline_chain_model_sha256'] != full['model_sha256']
            or proposal_run['plan']['inputs']['initial'] != plan['inputs']['baseline_initial']
            or proposal_optimizer['training_cap_violations'] or proposal_optimizer['cache_recompute_mismatches']
            or any(proposal_run['plan']['inputs'][key] != plan['inputs'][key] for key in
                ('points', 'mass', 'reference', 'caps', 'suffix', 'training', 'envelope_metadata', 'suffix_objective_metadata',
                 'selection_points', 'selection_inputs', 'baseline_stream', 'cap_anchor_stream'))):
        raise ValueError('aed提议起点/两标签/质量/cap与上一冻结研究不符；不能当已全验基线')
    points = np.load(paths['points'], mmap_mode='r')
    mass = np.load(paths['mass'], mmap_mode='r')
    reference = np.load(paths['reference'], mmap_mode='r')
    caps = np.load(paths['caps'], mmap_mode='r')
    suffix = np.load(paths['suffix'], mmap_mode='r')
    if (points.shape != (256**3, 3) or points.dtype != np.uint8 or reference.shape != points.shape
            or reference.dtype != np.uint8 or suffix.shape != points.shape or suffix.dtype != np.uint8
            or mass.shape != (len(points),) or mass.dtype != np.float64 or caps.shape != (len(points),) or caps.dtype != np.int32):
        raise ValueError('冻结缓存形状/类型不同')
    training, envelope, objective = [read(paths[k]) for k in ('training', 'envelope_metadata', 'suffix_objective_metadata')]
    arrays = {'points': array_sha(points), 'mass': array_sha(mass), 'reference': array_sha(reference),
        'caps': array_sha(caps), 'suffix': array_sha(suffix)}
    if (training['prefix_model_sha256'] != [] or training['rows'] != len(points)
            or training['points_sha256'] != arrays['points'] or training['mass_sha256'] != arrays['mass']
            or training['allocation'] != plan['mass'] or abs(float(mass.sum())-1.) > 1e-10
            or envelope['arrivals_sha256'] != arrays['points'] or envelope['caps_sha256'] != arrays['caps']
            or envelope['reference_sha256'] != arrays['reference'] or envelope['suffix_cache_sha256'] != arrays['suffix']
            or envelope['suffix_model_sha256'] != full['model_sha256'][1:]
            or envelope['reference_sha256'] != full['cube']['reference_sha256']
            or envelope['baseline_cube_sha256'] != plan['inputs']['cap_anchor_stream']['sha256']):
        raise ValueError('训练原色/质量/整链参考/包络/后三模型缓存身份不同')
    names = {'points': 'envelope-arrivals.npy', 'mass': 'training-mass.npy', 'reference': 'envelope-reference.npy',
        'caps': 'envelope-caps.npy', 'suffix': 'envelope-suffix.npy', 'envelope_metadata': 'envelope.json'}
    if any(training['artifact_sha256'][name] != plan['inputs'][key]['sha256'] for key, name in names.items()):
        raise ValueError('训练记录文件SHA与当前缓存不同')
    targets = io.load_full(checked(plan['tables'][0]), mmap=True).reshape(-1, 3)
    if (objective['weight'] != 1. or objective['source_target_sha256'] != plan['tables'][0]['sha256']
            or training['targets_sha256'] != objective['source_target_sha256']):
        raise ValueError('拟合标签根不是独立T1原表')
    terminal = np.empty_like(points)
    baseline_stream = np.memmap(paths['baseline_stream'], np.uint8, 'r', shape=points.shape)
    anchor_stream = np.memmap(paths['cap_anchor_stream'], np.uint8, 'r', shape=points.shape)
    for start in range(0, len(points), 1 << 18):
        stop = min(start+(1 << 18), len(points))
        terminal[start:stop] = suffix[targets[start:stop].astype(np.int64)@np.array([65536, 256, 1], np.int64)]
        error = anchor_stream[start:stop].astype(np.int32)-reference[start:stop].astype(np.int32)
        if not np.array_equal(caps[start:stop], np.maximum(49, np.sum(error*error, axis=1, dtype=np.int32))):
            raise ValueError('旧逐色cap锚点公式不同')
        error = baseline_stream[start:stop].astype(np.int32)-reference[start:stop].astype(np.int32)
        if np.any(np.sum(error*error, axis=1, dtype=np.int32) > caps[start:stop]):
            raise ValueError('当前已验最佳链违反复用的旧cap')
    terminal_sha = array_sha(terminal)
    if terminal_sha != objective['derived_target_sha256']: raise ValueError('终态标签不是S(T1)派生字节')
    frozen = np.load(paths['selection_points']); guard = {g: frozen[g] for g in ('cube', 'photos')}
    metadata = read(paths['selection_inputs'])
    if (len(guard['cube']) != 262144 or len(guard['photos']) != 20*4096 or len(metadata['images']) != 20
            or array_sha(guard['cube']) != plan['selection_arrays']['cube']
            or array_sha(guard['photos']) != plan['selection_arrays']['photos']
            or array_sha(guard['photos']) != metadata['samples_sha256']):
        raise ValueError('原固定选择像素/图身份不同')
    old = evaluate(guard, reference, stream=baseline_stream)
    historical = selection['candidates'][plan['prior_winner']]['samples']
    for group in ('cube', 'photos'):
        for key in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
            if abs(old[group][key]-historical[group][key]) > 1e-12: raise ValueError('旧流查表样本不符旧最佳指标')
    files = [Path(__file__), args.plan, ROOT/'scripts/verify_channel_suffix_joint_nodes.py',
        ROOT/'scripts/verify_channel_coordinates.py', ROOT/'scripts/run_channel_coordinates.py',
        *[ROOT/'python/lutlab'/name for name in ('channel_suffix_joint_nodes.py', 'channel_joint_nodes.py', 'channel_global_nodes.py', 'channel_suffix_coordinates.py', 'channel_coordinates.py',
            'axis_calibration.py', 'exact_axis.py', 'monotone_axis.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': sources,
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
        'contract_sha256': digest(contract_path), 'input_sha256': {key: digest(p) for key, p in paths.items()},
        'cache_array_sha256': arrays, 'independent_T1_sha256': objective['source_target_sha256'],
        'derived_S_T1_sha256': terminal_sha, 'baseline_chain_model_sha256': full['model_sha256'],
        'scope': '四张真实创意LUT数值四级链；仅首级8色26方向提议/一个固定样本选择，无完整终验/native/百图/性能'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in files: archive.write(p, p.relative_to(ROOT).as_posix())
    print('开始唯一Cinema aed几何固定节点26方向8色；af974验收基线，旧质量/标签/cap不变', flush=True)
    candidate, report = sj.propose(model, points, targets, terminal, mass, reference=reference, caps=caps,
        suffix=suffix, expected_initial_loss=proposal_optimizer['after_weighted_objective'], progress=lambda row: print(json.dumps(row, ensure_ascii=False), flush=True))
    (args.output/'optimizer.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    destination = args.output/'channel-suffix-joint-nodes.npz'
    np.savez_compressed(destination, format=np.array('channel_coordinates_v1_experimental'), grid=candidate.grid,
        nodes=candidate.nodes, shared_idx=candidate.idx, channel_frac=candidate.channel_frac,
        source_model_sha256=np.array(plan['inputs']['initial']['sha256']),
        baseline_model_sha256=np.array(plan['inputs']['baseline_initial']['sha256']),
        frozen_suffix_model_sha256=np.asarray(full['model_sha256'][1:]))
    for name, value in (('grid', candidate.grid), ('shared_idx', candidate.idx), ('channel_frac', candidate.channel_frac)):
        np.testing.assert_array_equal(initial[name], value)
    current = evaluate(guard, reference, model=candidate, suffix=suffix)
    failed = failures(current, old)
    if report['training_cap_violations']: failed.append('training_colour_caps')
    if sources != {p.relative_to(ROOT).as_posix(): digest(p) for p in files}: raise ValueError('拟合过程中冻结数值来源改变')
    result = {'run_identity': run['identity_sha256'], 'representation_sha256': digest(destination),
        'baseline_chain_model_sha256': full['model_sha256'], 'baseline_samples': old,
        'proposal_initial_aed_samples': proposal_selection['candidate_samples'], 'candidate_samples': current,
        'failures': failed, 'selected': not failed, 'full_evaluation_performed': False,
        'native_validation_performed': False, 'scope': plan['limits']}
    (args.output/'selection.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'samples': {g: {k: current[g][k] for k in ('mean', 'rms', 'p99', 'max', 'cvar_1pct')}
        for g in ('cube', 'photos')}, 'selected': not failed, 'failures': failed,
        'representation_sha256': digest(destination)}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
