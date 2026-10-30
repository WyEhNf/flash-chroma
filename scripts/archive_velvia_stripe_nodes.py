"""静态封存stripe节点一轮失败、独立合同与真实离线内存记录。"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖原冻结失败')
    args.output.mkdir(parents=True)
    fit = ROOT/'artifacts/velvia-stripe-nodes-v1'
    for target, source in [('run.json', fit/'run.json'), ('summary.json', fit/'summary.json'),
        ('contract.json', ROOT/'artifacts/oriented-tail-contract-v1.json'),
        ('memory-before.json', ROOT/'artifacts/velvia-stripe-node-memory-before-v1.json')]:
        shutil.copyfile(source, args.output/target)
    run, summary, progress = read(fit/'run.json'), read(fit/'summary.json'), read(fit/'progress.json')
    for name, sha in run['source_sha256'].items():
        if digest(ROOT/name) != sha:
            raise ValueError('冻结拟合源码发生改变')
    with zipfile.ZipFile(args.output/'fit-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(fit/'progress.json', 'progress.json')
    with zipfile.ZipFile(args.output/'research-model.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in ('model.npz', 'stripes-byte.bin', 'stripes-packed.bin', 'cell-orientation.bin'):
            archive.write(fit/name, name)
    budget, before, after = summary['budget'], summary['before'], summary['after']
    def metrics(values):
        return {'mean': values[0]/256**3, 'rms': math.sqrt(values[2]/256**3),
            'training_mean': values[1], 'training_rms': math.sqrt(values[3]), 'count_above_40': values[6]}
    observed = {'original_3e5': {'mean': budget[0]/256**3, 'rms': math.sqrt(budget[1]/256**3),
        'training_mean': budget[2], 'training_rms': math.sqrt(budget[3]), 'count_above_40': budget[4]},
        'stripe_before': metrics(before), 'stripe_after': metrics(after),
        'five_metric_ratios_after': dict(zip(summary['five_metric_order'], [after[n]/budget[k] for k, n in enumerate((0, 2, 1, 3, 6))])),
        'minimum_observed_available_memory_bytes': min(r['host_available_memory_bytes'] for r in progress),
        'maximum_observed_process_rss_bytes': max(r['process_rss_bytes'] for r in progress),
        'maximum_full_gain_error': max(r['maximum_gain_error'] for r in progress),
        'model_sha256': summary['model_sha256'], 'original_frozen_trial_passed': False,
        'scope': 'mean预算失败而停止，没有照片/完整独立u64新流/后拟合面采样/native/performance。max1448只由全域研究fresh核确认，不作为正式尾部升级。'}
    (args.output/'diagnostics.json').write_text(json.dumps(observed, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    sources = ['scripts/'+n for n in ('run_velvia_stripe_nodes.py', 'verify_oriented_tail_nodes.py',
        'archive_velvia_stripe_nodes.py', 'study_velvia_stripe_diagonals.py', 'study_velvia_body_diagonals.py',
        'accept_velvia_cell_diagonals.py', 'run_channel_tail_nodes.py')]+['python/lutlab/'+n for n in
        ('oriented_tetra.py', 'channel_tail_nodes.py', 'channel_joint_nodes.py', 'channel_coordinates.py', 'io.py', 'study_provenance.py')]
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    manifest = {'source_sha256': {name: digest(ROOT/name) for name in sources},
        'files': {p.name: digest(p) for p in args.output.iterdir()}, 'progress_json_sha256': digest(fit/'progress.json'),
        'purpose': __doc__, 'numeric_or_performance_calls_during_archive': 0, 'new_default': False}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(observed, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
