"""一次原guard定位f139 max，再以至多16原色逐级解释旧cap与当前基线差异。"""
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
from lutlab import channel_coordinates as cc, interp, io, study_provenance
from run_channel_coordinates import checked, digest, metrics, read
from verify_channel_coordinates import integer_oracle


def load_rep(path):
    data = np.load(path)
    if str(data['format']) != 'channel_coordinates_v1_experimental': raise ValueError('实验格式不同')
    model = cc.ChannelLut(data['grid'], data['nodes'], data['shared_idx'], data['channel_frac'])
    cc.validate(model)
    return model


def key(rgb):
    return rgb.astype(np.int64)@np.array([65536, 256, 1], np.int64)


def error_record(output, reference):
    residual = output.astype(np.int32)-reference.astype(np.int32)
    d2 = int(residual@residual)
    return {'rgb': output.tolist(), 'residual': residual.tolist(), 'squared_error': d2, 'distance': float(np.sqrt(d2))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/cinema-cap-anchor-diagnosis-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖诊断')
    plan = read(args.plan); paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    for spec in plan['suffix_models']+plan['tables']: checked(spec)
    if plan['guard_count'] != 81920 or plan['trajectory_maximum_unique_colours'] != 16:
        raise ValueError('只接受原guard及最多16色轨迹')
    numba.set_num_threads(4)
    selection = read(paths['candidate_selection']); previous = read(paths['candidate_run'])
    identity = dict(previous); identity.pop('identity_sha256')
    if (previous['identity_sha256'] != study_provenance.identity_digest(identity)
            or selection['run_identity'] != previous['identity_sha256']
            or selection['representation_sha256'] != plan['inputs']['candidate']['sha256']
            or selection['failures'] != ['photos.max'] or selection['selected']):
        raise ValueError('冻结候选/失败门禁身份不同')
    guard = np.load(paths['selection_points'])['photos']; metadata = read(paths['selection_inputs'])
    if (guard.shape != (81920, 3) or guard.dtype != np.uint8 or len(metadata['images']) != 20
            or hashlib.sha256(guard.tobytes()).hexdigest() != metadata['samples_sha256']):
        raise ValueError('原20图选择像素不同')
    candidate, initial = load_rep(paths['candidate']), load_rep(paths['initial'])
    for name in ('grid', 'idx', 'channel_frac'):
        np.testing.assert_array_equal(getattr(candidate, name), getattr(initial, name))
    suffix = np.load(paths['suffix'], mmap_mode='r')
    reference = np.load(paths['reference'], mmap_mode='r')
    caps = np.load(paths['caps'], mmap_mode='r')
    baseline = np.memmap(paths['baseline_stream'], np.uint8, 'r', shape=(256**3, 3))
    anchor = np.memmap(paths['cap_anchor_stream'], np.uint8, 'r', shape=(256**3, 3))
    files = [Path(__file__), args.plan, ROOT/'scripts/run_channel_coordinates.py', ROOT/'scripts/verify_channel_coordinates.py',
        *[ROOT/'python/lutlab'/name for name in ('channel_coordinates.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': sources,
        'input_sha256': {name: digest(p) for name, p in paths.items()},
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
        'scope': '原guard一次定位，少量去重原色逐级u64轨迹；无新模型/数据或完整终验'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in files: archive.write(p, p.relative_to(ROOT).as_posix())
    # 原guard只映射f139一次；旧af974和daad从已存完整字节查表。
    guard_keys = key(guard)
    own = cc.predict(candidate, guard)
    prediction = suffix[key(own)]
    truth = reference[guard_keys]
    measured = metrics(prediction, truth)
    for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
        if abs(measured[metric]-selection['candidate_samples']['photos'][metric]) > 1e-12:
            raise ValueError('固定guard定位不能重现f139选择结果')
    e = prediction.astype(np.int32)-truth.astype(np.int32)
    d2 = np.sum(e*e, axis=1, dtype=np.int32)
    worst = int(d2.max()); rows = np.flatnonzero(d2 == worst)
    unique_keys = np.unique(guard_keys[rows])
    occurrence = []
    for value in unique_keys:
        positions = rows[guard_keys[rows] == value]
        all_positions = np.flatnonzero(guard_keys == value)
        by_image = []
        for image in np.unique(all_positions//4096):
            positions_image = all_positions[all_positions//4096 == image]
            by_image.append({'id': metadata['images'][image]['id'], 'guard_pixels': len(positions_image),
                'guard_offsets': (positions_image % 4096).tolist()})
        rgb = [int(value >> 16), int((value >> 8) & 255), int(value & 255)]
        occurrence.append({'rgb': rgb, 'key': int(value), 'guard_frequency': len(all_positions),
            'max_error_occurrences': len(positions), 'images': by_image})
    keys = unique_keys[:16]
    points = np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)
    suffix_models = [io.load_sparse(checked(spec), competition=True) for spec in plan['suffix_models']]
    tables = [io.load_full(checked(spec), mmap=True).reshape(-1, 3) for spec in plan['tables']]
    exact, exact_stages = points.copy(), []
    for table in tables:
        exact = table[key(exact)]
        exact_stages.append(exact.copy())
    np.testing.assert_array_equal(exact, reference[keys])
    variants = {'daad_anchor': cc.from_sparse(io.load_sparse(paths['anchor_initial'], competition=True)),
        'af974_baseline': cc.from_sparse(io.load_sparse(paths['baseline_initial'], competition=True)),
        'aed_proposal': initial, 'f139_candidate': candidate}
    trajectories = {}
    for name, model in variants.items():
        value = integer_oracle(model, points)
        np.testing.assert_array_equal(value, cc.predict(model, points))
        first = value.copy(); stages = [value.copy()]
        for sparse in suffix_models:
            independent = integer_oracle(cc.from_sparse(sparse), value)
            np.testing.assert_array_equal(independent, interp.apply_tetra_q16(sparse, value))
            value = independent; stages.append(value.copy())
        np.testing.assert_array_equal(value, suffix[key(first)])
        if name == 'daad_anchor': np.testing.assert_array_equal(value, anchor[keys])
        if name == 'af974_baseline': np.testing.assert_array_equal(value, baseline[keys])
        if name == 'f139_candidate':
            for p, value_key in enumerate(keys):
                np.testing.assert_array_equal(value[p], prediction[np.flatnonzero(guard_keys == value_key)[0]])
        trajectories[name] = stages
    details = []
    for p, input_key in enumerate(keys):
        variants_per_colour = {}
        for name, stages in trajectories.items():
            variants_per_colour[name] = {'stages': [stage[p].tolist() for stage in stages],
                'prefix_total_error_vs_exact_stages': [error_record(stage[p], exact_stages[i][p]) for i, stage in enumerate(stages)],
                'final_error': error_record(stages[-1][p], exact[p])}
        anchor_d2 = variants_per_colour['daad_anchor']['final_error']['squared_error']
        baseline_d2 = variants_per_colour['af974_baseline']['final_error']['squared_error']
        new_d2 = variants_per_colour['f139_candidate']['final_error']['squared_error']
        cap = int(caps[input_key])
        if cap != max(49, anchor_d2) or new_d2 > cap: raise AssertionError('旧cap公式/真实候选可行性不符')
        details.append({'rgb': points[p].tolist(), 'exact_original_rgb8_stages': [stage[p].tolist() for stage in exact_stages],
            'variants': variants_per_colour, 'old_daad_cap': cap, 'current_af974_error_squared': baseline_d2,
            'candidate_f139_error_squared': new_d2, 'hypothetical_af974_anchored_cap_arithmetic_only': max(49, baseline_d2),
            'would_violate_af974_anchored_cap': new_d2 > max(49, baseline_d2),
            'independent_u64_and_suffix_cache_mismatches': 0})
    if sources != {p.relative_to(ROOT).as_posix(): digest(p) for p in files}: raise ValueError('诊断中来源改变')
    result = {'run_identity': run['identity_sha256'], 'guard_mapped_pixels': len(guard),
        'guard_metrics_reproduced': measured, 'maximum_squared_error': worst,
        'maximum_error_occurrences': len(rows), 'unique_maximum_rgb_count': len(unique_keys),
        'maximum_rgb_occurrences': occurrence, 'trajectory_unique_rgb_count': len(points),
        'trajectory_omitted_count': max(0, len(unique_keys)-16), 'trajectories': details,
        'research_and_independent_oracle_mismatches': 0, 'new_fits': 0, 'new_full_evaluations': 0,
        'interpretation': 'few-colour确定性轨迹区分运行时与旧cap锚点；不由单例推断整体误差来源，不改训练或放宽门槛',
        'limits': plan['limits']}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'max_squared': worst, 'occurrences': len(rows), 'unique_rgb': len(unique_keys),
        'details': details}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
