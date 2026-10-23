"""静态封存cap1600三预算独立trial及其RMS/CVaR观察，不覆盖旧五预算。"""
from __future__ import annotations
import argparse
import hashlib
import json
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
        raise ValueError('不覆盖独立三预算归档')
    args.output.mkdir(parents=True)
    fit = ROOT/'artifacts/velvia-mean-first-nodes-v1'
    for target, source in [('run.json', fit/'run.json'), ('summary.json', fit/'summary.json'),
        ('contract.json', ROOT/'artifacts/oriented-tail-contract-v2-steps12.json'),
        ('observations.json', ROOT/'artifacts/velvia-mean-first-observations-v1.json'),
        ('memory-before.json', ROOT/'artifacts/velvia-mean-first-memory-before-v1.json')]:
        shutil.copyfile(source, args.output/target)
    for record in (read(fit/'run.json'), read(args.output/'contract.json'), read(args.output/'observations.json')):
        for name, sha in record['source_sha256'].items():
            if digest(ROOT/name) != sha:
                raise ValueError('冻结源码发生改变')
    with zipfile.ZipFile(args.output/'fit-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(fit/'progress.json', 'progress.json')
    with zipfile.ZipFile(args.output/'research-model.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in ('model.npz', 'stripes-byte.bin', 'stripes-packed.bin', 'cell-orientation.bin'):
            archive.write(fit/name, name)
    sources = ['scripts/'+n for n in ('run_velvia_mean_first_nodes.py', 'verify_oriented_tail_nodes.py',
        'observe_velvia_mean_first.py', 'archive_velvia_mean_first.py', 'study_velvia_stripe_diagonals.py',
        'study_velvia_body_diagonals.py', 'accept_velvia_cell_diagonals.py', 'accept_channel_tail_nodes.py',
        'accept_channel_coordinates.py', 'run_channel_tail_nodes.py')]+['python/lutlab/'+n for n in
        ('oriented_tetra.py', 'channel_tail_nodes.py', 'channel_joint_nodes.py', 'channel_coordinates.py', 'io.py', 'study_provenance.py')]
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    progress, summary = read(fit/'progress.json'), read(fit/'summary.json')
    diagnostics = {'uniform_mean_ratio_to_3e5': summary['after'][0]/summary['original_3e5_mean_budget'][0],
        'training_mean_ratio_to_3e5': summary['after'][1]/summary['original_3e5_mean_budget'][1],
        'maximum_gain_error': max(r['maximum_gain_error'] for r in progress),
        'minimum_observed_host_available_memory_bytes': min(r['host_available_memory_bytes'] for r in progress),
        'maximum_observed_process_rss_bytes': max(r['process_rss_bytes'] for r in progress),
        'three_budget_trial_passed': False, 'new_default': False,
        'scope': 'mean仍失败；观察量为完整域研究核，不是独立u64/照片/边界/native/performance终验。'}
    (args.output/'diagnostics.json').write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    manifest = {'source_sha256': {name: digest(ROOT/name) for name in sources}, 'files': {p.name: digest(p) for p in args.output.iterdir()},
        'progress_json_sha256': digest(fit/'progress.json'), 'numeric_or_performance_calls_during_archive': 0, 'purpose': __doc__}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(diagnostics, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
