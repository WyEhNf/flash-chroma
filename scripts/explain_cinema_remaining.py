"""对已完整验收的Cinema链做固定小样本归因，不拟合、不运行完整验收。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import error_analysis as ea, interp, io, study_provenance
from lutlab.compatibility import write_json
from run_chain_error_study import colours, digest
from run_cinema_rounded import checked, read


def diagnose(tables, models, points):
    truth = ea.exact_chain(tables, points)
    prediction = ea.Operator(models)(points)
    squared = ea.histogram(prediction, truth)[1]
    cutoff = float(np.percentile(squared, 99))
    tail = squared >= cutoff
    result = ea.stage_attribution(tables, models, points)
    result['fixed_baseline_tail'] = {'squared_cutoff': cutoff, 'rows': int(tail.sum()),
        'baseline': ea.metrics(prediction[tail], truth[tail]),
        'scope': '固定原基线p99及以上集合，反事实后不重新选尾部；只用于解释'}
    prefix = points.copy()
    for k, row in enumerate(result['stages']):
        own = ea.source_apply(tables[k], prefix)
        replacement = ea.Operator(models[k+1:])(own)
        after = ea.histogram(replacement, truth)[1]
        row['replacement_change_counts'] = {name: int(np.count_nonzero(mask)) for name, mask in (
            ('better', after < squared), ('equal', after == squared), ('worse', after > squared))}
        row['replacement_on_fixed_baseline_tail'] = ea.metrics(replacement[tail], truth[tail])
        prefix = ea.Operator([models[k]])(prefix)
    worst = np.argsort(squared, kind='stable')[-8:][::-1]
    result['worst_traces'] = ea.hotspot_traces(tables, models, points[worst], 0)
    return result, prediction


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖已有归因')
    numba.set_num_threads(4)
    run = read(args.run/'run.json')
    selection = read(args.run/'selection.json')
    full = read(args.run/'full-results.json')
    training = read(args.run/'training.json')
    plan = run['identity']['plan']
    if (run['identity_sha256'] != study_provenance.identity_digest(run['identity'])
            or full['run_identity'] != run['identity_sha256']
            or selection['run_identity'] != run['identity_sha256']
            or not full['acceptance']['accepted'] or not selection['winner']):
        raise ValueError('只诊断身份绑定一致、完整验收通过的模型')
    winner = args.run/selection['winner']
    paths = [winner/f'selected-stage{k}.slut' for k in range(1, 5)]
    if [digest(path) for path in paths] != full['model_sha256']:
        raise ValueError('最终四模型不同于完整验收')
    models = [io.load_sparse(path, competition=True) for path in paths]
    tables = []
    for spec in plan['tables']:
        checked({'path': spec['source'], 'sha256': spec['source_sha256']})
        tables.append(io.load_full(checked(spec), mmap=True))
    stream_path = winner/'cube.rgb'
    if digest(stream_path) != full['cube']['prediction_sha256']:
        raise ValueError('已验收完整流SHA不同')
    stream = np.memmap(stream_path, np.uint8, 'r', shape=(256**3, 3))
    frequency_path = args.run/'photo-arrival-frequency.npy'
    if plan['optimized_stage'] != 1 or digest(frequency_path) != training['artifact_sha256'][frequency_path.name]:
        raise ValueError('需要已冻结首级原色频数')
    frequency = np.load(frequency_path, mmap_mode='r')
    if int(frequency.sum(dtype=np.uint64)) != 60*1024*768:
        raise ValueError('训练像素总量不同')
    # 不借用百图验收反馈；只使用原60张训练图原色频数和独立均匀探针。
    cube_ids = np.random.default_rng(2026101903).choice(256**3, 16384, replace=False)
    photo_ids = np.searchsorted(np.cumsum(frequency, dtype=np.uint64),
        np.random.default_rng(2026101907).integers(0, int(frequency.sum(dtype=np.uint64)), 16384), side='right')
    result = {'parent_run_identity': run['identity_sha256'], 'source_sha256': digest(Path(__file__)),
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
        'input_sha256': {path.name: digest(path) for path in
            (args.run/'run.json', args.run/'selection.json', args.run/'full-results.json', frequency_path)},
        'model_sha256': full['model_sha256'], 'table_sha256': [s['sha256'] for s in plan['tables']],
        'scope': '两组各16384点的因果反事实；RGB8逐级舍入；精确替换非可部署模型，不是误差下界，不能相加为贡献或充当完整验收'}
    for name, ids, seed in (('uniform_probe', cube_ids, 2026101903), ('training_photo_probe', photo_ids, 2026101907)):
        points = colours(ids)
        details, prediction = diagnose(tables, models, points)
        if not np.array_equal(prediction, stream[ids]):
            raise AssertionError('探针基线不同于已验收完整流')
        oracle = points[:4096].copy()
        for model in models:
            oracle = interp.apply_tetra_q16(model, oracle)
        if not np.array_equal(oracle, prediction[:4096]):
            raise AssertionError('小样本解释算子不同于整数oracle')
        details.update(seed=seed, points_sha256=hashlib.sha256(points.tobytes()).hexdigest(),
                       baseline_stream_byte_mismatches=0, integer_oracle_rows=4096)
        result[name] = details
    write_json(args.output, result)
    print(json.dumps({name: {'baseline': result[name]['baseline'],
        'stages': [{k: row[k] for k in ('stage', 'replacement_gain_mean', 'replacement_gain_cvar',
                                      'replace_this_stage_exact')} for row in result[name]['stages']]}
        for name in ('uniform_probe', 'training_photo_probe')}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
