"""静态保存解析最小κ与唯一一次612支撑验证，不扩成全域候选。"""
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
        raise ValueError('不覆盖解析κ阶段')
    args.output.mkdir(parents=True)
    measured = ROOT/'artifacts/velvia-bubble-slope-v1'
    run = json.loads((measured/'run.json').read_text(encoding='utf-8'))
    for name, sha in run['source_sha256'].items():
        if digest(ROOT/name) != sha:
            raise ValueError('推导后修改了实际源码')
    for name in ('run.json', 'interval-contract.json', 'derived-threshold.json', 'results.json'):
        shutil.copyfile(measured/name, args.output/name)
    sources = ['scripts/'+name for name in ('probe_velvia_bubble_slope.py', 'probe_velvia_bubble.py', 'archive_velvia_bubble_slope.py',
        'run_channel_tail_nodes.py', 'accept_channel_tail_nodes.py', 'accept_channel_coordinates.py')]+['python/lutlab/'+name for name in
        ('channel_coordinates.py', 'io.py', 'study_provenance.py')]
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    manifest = {'source_sha256': {name: digest(ROOT/name) for name in sources}, 'files': {p.name: digest(p) for p in args.output.iterdir()},
        'purpose': __doc__, 'numeric_or_performance_calls_during_archive': 0,
        'scope': 'κ3由训练max点解析舍入区间推出，阈值/方向先落盘再验证612一次；无全域/照片/真实面邻接/native/performance。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files': len(manifest['files']), 'new_default': False}), flush=True)


if __name__ == '__main__':
    main()
