"""静态归档max未降的负结果、末级局部证书和最快后端资格，不执行数值映射。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖证据')
    args.output.mkdir(parents=True)
    folder = ROOT/'artifacts/channel-max-nodes-v1'
    names = {'max-run.json': folder/'run.json', 'max-summary.json': folder/'summary.json',
        'max-contract.json': ROOT/'artifacts/channel-max-contract-v1/results.json',
        'last-stage-probe.json': ROOT/'artifacts/cinema-last-stage-probe-v1/results.json',
        'runtime-eligibility.json': ROOT/'artifacts/tail-runtime-eligibility-v1/results.json'}
    for name, source in names.items():
        shutil.copyfile(source, args.output/name)
    with zipfile.ZipFile(args.output/'negative-fit.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(folder/'progress.json', 'progress.json')
        for name in ('model.npz', 'candidate-base.slut', 'channel-frac.bin'):
            archive.write(folder/'max_bank'/name, 'max_bank/'+name)
    sources = ['python/lutlab/channel_max_nodes.py', 'python/lutlab/channel_tail_nodes.py']+['scripts/'+n for n in
        ('run_channel_max_nodes.py', 'verify_channel_max_nodes.py', 'probe_cinema_last_stage.py', 'inspect_tail_runtime_eligibility.py', 'archive_channel_max_nodes.py')]
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    record = {'source_sha256': {n: digest(ROOT/n) for n in sources}, 'files': {p.name: digest(p) for p in args.output.iterdir()},
        'strict_max_gate_pass': False, 'new_default': False, 'full_accuracy_or_native_acceptance': False,
        'scope': '保留两扫max未降负结果；末级热点可行性与构造资格不冒充全域精度/吞吐。'}
    (args.output/'manifest.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
