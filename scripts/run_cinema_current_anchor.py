"""af974新cap锚定，九块坐标后八色26方向联合节点一次；仅末态严格选择。"""
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
from lutlab import channel_coordinates as cc, channel_suffix_coordinates as cs, channel_suffix_joint_nodes as sj, io, study_provenance
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
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/cinema-current-anchor-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖旧结果')
    plan = read(args.plan); paths = {key: checked(spec) for key, spec in plan['inputs'].items()}
    if (plan['threads'] != 4 or plan['coordinate_blocks'] != 9 or plan['node_colours'] != 8 or plan['node_directions'] != 26
            or plan['pipeline'] != ['channel_suffix_coordinates.propose:9', 'channel_suffix_joint_nodes.propose:8x26'] or plan['tail_at'] != 6. or plan['tail_weight'] != .02
            or plan['suffix_weight'] != 1. or plan['mass'] != {'own_uniform': .1, 'cube_arrival': .45, 'photo_arrival': .45}
            or plan['derived_cap']['file'] != 'af974-anchored-caps.npy'
            or plan['derived_cap']['source_stream_sha256'] != plan['inputs']['baseline_stream']['sha256']):
        raise ValueError('只接受冻结9块+8色管线/同质量/同双项目标')
    numba.set_num_threads(4)
    contract_paths = {name: checked(spec) for name, spec in plan['contracts'].items()}
    contracts = {name: read(path) for name, path in contract_paths.items()}
    for name, record in contracts.items():
        if record.get('pass') is not True or any(digest(ROOT/path) != sha for path, sha in record['source_sha256'].items()):
            raise ValueError('旧集中合同未通过或原数值模块SHA改变')
    contract = contracts['coordinates']
    if ([(row['m'], row['channel'], row['axis']) for row in contract['cases']]
            != [(m, c, a) for m in (17, 33) for c in range(3) for a in range(3)]
            or any(row['integer_states'] != 65537 or row['maximum_event_loss_error'] > 1e-8
                or row['cap_count_mismatches'] or row['uint64_output_mismatches'] or row['other_channel_cache_mismatches']
                or row['fresh_cache_mismatches'] or not row['dp_monotone_endpoints_and_cap_pass'] for row in contract['cases'])):
        raise ValueError('旧坐标完整状态合同覆盖不同')
    contract = contracts['joint_nodes']
    if ([row['m'] for row in contract['cases']] != [17, 33]
            or any(row['groups'] != 8 or row['maximum_gain_error'] > 1e-10 or row['geometry_errors']
                or row['cap_count_mismatches'] or row['uint64_output_mismatches'] or row['fresh_cache_mismatches']
                or not row['zero_mass_cap_prohibitions'] for row in contract['cases'])):
        raise ValueError('旧非线性后缀联合节点合同覆盖不同')
    previous, selection, full = [read(paths[k]) for k in ('prior_run', 'prior_selection', 'prior_full')]
    if (previous['identity_sha256'] != study_provenance.identity_digest(previous['identity'])
            or previous['identity_sha256'] != plan['prior_run_identity']
            or selection['run_identity'] != plan['prior_run_identity'] or full['run_identity'] != plan['prior_run_identity']
            or selection['winner'] != plan['prior_winner'] or not full['acceptance']['accepted']
            or full['acceptance']['failed'] or full['model_sha256'] != plan['baseline_chain_model_sha256']
            or selection['candidates'][plan['prior_winner']]['model_sha256'] != plan['inputs']['initial']['sha256']
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
    model = io.load_sparse(paths['initial'], competition=True)
    if model.m != 33: raise ValueError('首级不是冻结m33')
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
    if plan['derived_cap']['reference_array_sha256'] != arrays['reference']:
        raise ValueError('新cap的独立四级参考身份不同')
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
    files = [Path(__file__), args.plan, ROOT/'scripts/verify_channel_suffix_coordinates.py', ROOT/'scripts/verify_channel_suffix_joint_nodes.py',
        ROOT/'scripts/verify_channel_coordinates.py', ROOT/'scripts/run_channel_coordinates.py',
        *[ROOT/'python/lutlab'/name for name in ('channel_suffix_coordinates.py', 'channel_suffix_joint_nodes.py', 'channel_joint_nodes.py', 'channel_global_nodes.py', 'channel_coordinates.py',
            'axis_calibration.py', 'exact_axis.py', 'monotone_axis.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    args.output.mkdir(parents=True)
    old_caps = caps
    cap_path = args.output/plan['derived_cap']['file']
    derived = np.lib.format.open_memmap(cap_path, mode='w+', dtype=np.int32, shape=(len(points),))
    tightened, unchanged, maximum_tightening, initial_violations = 0, 0, 0, 0
    for start in range(0, len(points), 1 << 18):
        stop = min(start+(1 << 18), len(points))
        error = baseline_stream[start:stop].astype(np.int32)-reference[start:stop].astype(np.int32)
        square32 = np.sum(error*error, axis=1, dtype=np.int32)
        square64 = np.zeros(stop-start, np.int64)
        for c in range(3):
            delta = baseline_stream[start:stop, c].astype(np.int64)-reference[start:stop, c].astype(np.int64)
            square64 += delta**2
        cap32, cap64 = np.maximum(49, square32), np.maximum(np.int64(49), square64)
        if not np.array_equal(cap32, cap64) or np.any(cap32 > old_caps[start:stop]):
            raise ValueError('新cap双算不符或逐色超过旧cap')
        derived[start:stop] = cap32
        tightened += int(np.count_nonzero(cap32 < old_caps[start:stop]))
        unchanged += int(np.count_nonzero(cap32 == old_caps[start:stop]))
        maximum_tightening = max(maximum_tightening, int(np.max(old_caps[start:stop]-cap32)))
        initial_violations += int(np.count_nonzero(square32 > cap32))
    derived.flush(); del derived
    caps = np.load(cap_path, mmap_mode='r')
    cap_metadata = {'formula': 'max(49,||af974_stream-reference||^2)', 'rows': len(points),
        'source_stream_sha256': plan['inputs']['baseline_stream']['sha256'],
        'reference_array_sha256': arrays['reference'], 'old_caps_file_sha256': plan['inputs']['caps']['sha256'],
        'new_caps_file_sha256': digest(cap_path), 'new_caps_array_sha256': array_sha(caps),
        'int32_vector_vs_independent_channel_int64_mismatches': 0,
        'new_greater_than_old_colours': 0, 'strictly_tightened_colours': tightened,
        'unchanged_colours': unchanged, 'maximum_squared_cap_tightening': maximum_tightening,
        'af974_initial_violations': initial_violations,
        'scope': '全原RGB统一约束，未读取反例/图名单改cap；来源旧字节双算，非额外模型映射'}
    if initial_violations or tightened+unchanged != len(points): raise AssertionError('新cap初始可行/覆盖不符')
    (args.output/'derived-cap.json').write_text(json.dumps(cap_metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': sources,
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
        'contract_sha256': {name: digest(path) for name, path in contract_paths.items()}, 'input_sha256': {key: digest(p) for key, p in paths.items()},
        'old_cache_array_sha256': arrays, 'derived_cap': cap_metadata, 'independent_T1_sha256': objective['source_target_sha256'],
        'derived_S_T1_sha256': terminal_sha, 'baseline_chain_model_sha256': full['model_sha256'],
        'scope': '四张真实创意LUT数值四级链；仅首级9块坐标后8色节点整合/唯一末态固定样本选择，无完整终验/native/百图/性能'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in files: archive.write(p, p.relative_to(ROOT).as_posix())
    print('开始唯一af974重新起步：新锚定cap、9块坐标→8色26方向节点；无中间selection', flush=True)
    coordinates, coordinate_report = cs.propose(model, points, targets, terminal, mass, reference=reference, caps=caps,
        suffix=suffix, baseline_stream=baseline_stream,
        progress=lambda row: print('coordinate '+json.dumps(row, ensure_ascii=False), flush=True))
    checkpoint = args.output/'coordinate-checkpoint.npz'
    np.savez_compressed(checkpoint, format=np.array('channel_coordinates_v1_experimental'), grid=coordinates.grid,
        nodes=coordinates.nodes, shared_idx=coordinates.idx, channel_frac=coordinates.channel_frac,
        source_model_sha256=np.array(plan['inputs']['initial']['sha256']),
        baseline_model_sha256=np.array(plan['inputs']['initial']['sha256']),
        frozen_suffix_model_sha256=np.asarray(full['model_sha256'][1:]))
    (args.output/'coordinates-optimizer.json').write_text(json.dumps(coordinate_report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    candidate, node_report = sj.propose(coordinates, points, targets, terminal, mass, reference=reference, caps=caps,
        suffix=suffix, expected_initial_loss=coordinate_report['after_weighted_objective'],
        progress=lambda row: print('nodes '+json.dumps(row, ensure_ascii=False), flush=True))
    node_report['inherited_kernel_scope_text'] = node_report['scope']
    node_report['scope'] = '本轮af974重新生成的坐标checkpoint下8色26方向一次；旧模块保持原样，未以旧aed起步'
    node_report['actual_initial_coordinate_checkpoint_sha256'] = digest(checkpoint)
    (args.output/'nodes-optimizer.json').write_text(json.dumps(node_report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    report = {'before_weighted_objective': coordinate_report['before_weighted_objective'],
        'after_coordinates_weighted_objective': coordinate_report['after_weighted_objective'],
        'after_weighted_objective': node_report['after_weighted_objective'],
        'training_cap_violations': coordinate_report['training_cap_violations']+node_report['training_cap_violations'],
        'coordinate_fresh_mismatches': coordinate_report['cache_recompute_mismatches'],
        'node_fresh_mismatches': node_report['cache_recompute_mismatches'],
        'coordinate_checkpoint_sha256': digest(checkpoint), 'derived_cap': cap_metadata,
        'scope': '重新从af974整合一次9块+8色；没有中间选择、额外扫数/权重或弱基线'}
    (args.output/'optimizer.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    destination = args.output/'current-anchor-pipeline.npz'
    np.savez_compressed(destination, format=np.array('channel_coordinates_v1_experimental'), grid=candidate.grid,
        nodes=candidate.nodes, shared_idx=candidate.idx, channel_frac=candidate.channel_frac,
        source_model_sha256=np.array(plan['inputs']['initial']['sha256']),
        baseline_model_sha256=np.array(plan['inputs']['initial']['sha256']),
        direct_parent_coordinate_checkpoint_sha256=np.array(digest(checkpoint)),
        frozen_suffix_model_sha256=np.asarray(full['model_sha256'][1:]))
    np.testing.assert_array_equal(candidate.grid, model.grid)
    np.testing.assert_array_equal(candidate.idx, model.tables()[0])
    np.testing.assert_array_equal(candidate.channel_frac, coordinates.channel_frac)
    current = evaluate(guard, reference, model=candidate, suffix=suffix)
    failed = failures(current, old)
    if report['training_cap_violations']: failed.append('training_colour_caps')
    if sources != {p.relative_to(ROOT).as_posix(): digest(p) for p in files}: raise ValueError('拟合过程中冻结数值来源改变')
    result = {'run_identity': run['identity_sha256'], 'representation_sha256': digest(destination),
        'baseline_chain_model_sha256': full['model_sha256'], 'baseline_samples': old, 'candidate_samples': current,
        'derived_cap': cap_metadata, 'coordinate_checkpoint_sha256': digest(checkpoint), 'intermediate_selection_performed': False,
        'failures': failed, 'selected': not failed, 'full_evaluation_performed': False,
        'native_validation_performed': False, 'scope': plan['limits']}
    (args.output/'selection.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'samples': {g: {k: current[g][k] for k in ('mean', 'rms', 'p99', 'max', 'cvar_1pct')}
        for g in ('cube', 'photos')}, 'selected': not failed, 'failures': failed,
        'representation_sha256': digest(destination)}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
