"""读取冻结频数与后缀，诊断训练照片上的精确首级替换，不拟合或重映射模型。"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import error_analysis as ea, io, study_provenance
from lutlab.compatibility import write_json
from run_chain_error_study import digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖已有诊断')
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    run, training = read(args.run/'run.json'), read(args.run/'training.json')
    plan = run['identity']['plan']
    if plan['optimized_stage'] != 1:
        raise ValueError('本诊断只适用于首级原色频数')
    arrays = {}
    input_sha = {}
    for name in ('photo-arrival-frequency.npy', 'envelope-suffix.npy', 'envelope-reference.npy', 'envelope-caps.npy'):
        path = args.run/name; sha = digest(path)
        if sha != training['artifact_sha256'][name]:
            raise ValueError('冻结训练数组SHA不同')
        arrays[name] = np.load(path, mmap_mode='r'); input_sha[name] = sha
    baseline_path = ROOT/plan['baseline_evidence']['cube']['path']
    table_path = ROOT/plan['tables'][0]['path']
    if digest(baseline_path) != plan['baseline_evidence']['cube']['sha256'] or digest(table_path) != plan['tables'][0]['sha256']:
        raise ValueError('基线流或第一原表SHA不同')
    frequency = arrays['photo-arrival-frequency.npy']
    ids = np.flatnonzero(frequency)
    weights = frequency[ids].astype(np.int64)
    table = io.load_full(table_path, mmap=True).reshape(-1, 3)
    target = table[ids].astype(np.int64)
    exact = arrays['envelope-suffix.npy'][target@np.array([65536, 256, 1], np.int64)]
    truth = arrays['envelope-reference.npy'][ids]
    baseline = np.memmap(baseline_path, np.uint8, 'r', shape=(256**3, 3))[ids]
    squared, metrics = {}, {}
    for name, pred in (('baseline', baseline), ('exact_stage1', exact)):
        error = pred.astype(np.int32)-truth.astype(np.int32)
        squared[name] = np.sum(error*error, axis=1, dtype=np.int32)
        hist = np.bincount(squared[name], weights=weights, minlength=3*255**2+1).astype(np.int64)
        metrics[name] = ea.hist_metrics(hist)
    old, new = squared['baseline'], squared['exact_stage1']
    violations = int(weights[new > arrays['envelope-caps.npy'][ids]].sum(dtype=np.int64))
    partition = read(ROOT/plan['partition']['path'])
    training_ids = {r['id'] for r in partition['training']['images']}
    historical = read(args.run/'historical-full-results.json')
    historic_mean = float(np.mean([r['mean'] for r in historical['photos']['per_image'] if r['image'] in training_ids]))
    result = {'parent_run_identity': run['identity_sha256'], 'source_sha256': digest(Path(__file__)),
        'environment': study_provenance.environment_fingerprint(), 'input_sha256': input_sha,
        'baseline_cube_sha256': digest(baseline_path), 'table1_sha256': digest(table_path),
        'training_images': len(training_ids), 'training_pixels': int(weights.sum()), 'unique_colours': len(ids),
        'metrics': metrics, 'historical_baseline_mean_difference': metrics['baseline']['mean']-historic_mean,
        'changes': {name: int(weights[mask].sum()) for name, mask in (
            ('better', new < old), ('equal', new == old), ('worse', new > old))},
        'weighted_envelope_violations': violations,
        'scope': '纯缓存读取与频数汇总，不调用模型映射/拟合；精确首级替换是诊断，非合法稀疏候选或误差下界，不外推选择图/百图验收'}
    write_json(args.output, result)
    print(json.dumps({'metrics': metrics, 'changes': result['changes'], 'violations': violations,
                     'historical_mean_difference': result['historical_baseline_mean_difference']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
