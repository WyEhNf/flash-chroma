"""静态整理首阶段两候选的完整准确性、拟合记录和模型，不执行新映射或计时。"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import shutil
import zipfile
from run_channel_tail_nodes import digest, save, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖静态证据')
    args.output.mkdir(parents=True)
    fit = ROOT/'artifacts/channel-tail-nodes-v1'
    accept = ROOT/'artifacts/channel-tail-accept-v2'
    result = json.loads((accept/'results.json').read_text(encoding='utf-8'))
    prior = json.loads((args.cache_root/'artifacts/cinema-current-anchor-accept-v1/results.json').read_text(encoding='utf-8'))
    for mode, value in result['variants'].items():
        if not value['passed_aggregate'] or value['full_native_byte_mismatches'] or value['photo_native_byte_mismatches']:
            raise ValueError('验收未通过')
        if value['model_sha256'] != digest(fit/mode/'model.npz'):
            raise ValueError('候选身份改变')
        if len(set(value['sha256'][k] for k in ('oracle', 'scalar', 'avx2'))) != 1:
            raise ValueError('实际四级输出不同')
    for name, source in [('results.json', accept/'results.json'), ('contract.json', ROOT/'artifacts/channel-tail-contract-v1/results.json'),
                         ('run.json', fit/'run.json'), ('baseline-training.json', fit/'baseline.json')]:
        shutil.copyfile(source, args.output/name)
    with (args.output/'accuracy.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream); writer.writerow(['范围', '模型', 'mean', 'rms', 'p99', 'max', 'cvar_1pct'])
        for group in ('cube', 'photos'):
            old = prior['cube'] if group == 'cube' else prior['photos']['merged']
            writer.writerow([group, 'a399', *[old[k] for k in ('mean', 'rms', 'p99', 'max', 'cvar_1pct')]])
            for mode, value in result['variants'].items():
                writer.writerow([group, mode, *[value[group][k] for k in ('mean', 'rms', 'p99', 'max', 'cvar_1pct')]])
    with zipfile.ZipFile(args.output/'models.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for mode in result['variants']:
            for name in ('model.npz', 'candidate-base.slut', 'channel-frac.bin'):
                archive.write(fit/mode/name, mode+'/'+name)
    with zipfile.ZipFile(args.output/'fit-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for mode in result['variants']:
            for name in ('progress.json', 'summary.json'):
                archive.write(fit/mode/name, mode+'/'+name)
    sources = ['python/lutlab/'+n for n in ('channel_tail_nodes.py', 'channel_coordinates.py', 'channel_global_nodes.py',
        'channel_joint_nodes.py', 'io.py', 'interp.py', 'study_provenance.py')]
    sources += ['scripts/'+n for n in ('run_channel_tail_nodes.py', 'accept_channel_tail_nodes.py', 'verify_channel_tail_nodes.py',
        'verify_channel_coordinates.py', 'accept_channel_coordinates.py', 'archive_channel_tail_nodes.py')]
    sources += ['experiments/channel-runtime/channel_native.py']
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    save(args.output/'manifest.json', {'parent_commit': '16ae431', 'incumbent': 'severe_first',
        'source_sha256': {n: digest(ROOT/n) for n in sources},
        'files': {p.name: digest(p) for p in args.output.iterdir() if p.is_file()},
        'baseline_photos': prior['photos']['merged'],
        'failed_attempt': 'artifacts/channel-tail-accept-v1：首候选完整映射后，汇总误读photos.p99（应为photos.merged.p99）发生KeyError；无结果JSON，不作正式通过。修复后v2两候选完整重跑。',
        'performance_calls': 0, 'default_promoted': False,
        'runtime': '复用原packed v3、GCC15.2 Release AVX2/OpenMP；完整scalar1/AVX2请求4均逐字节一致；不以此证明性能不变。',
        'scope': 'RGB8欧氏距离；历史100图回顾性终验；完整域参与整链目标训练。无官方阈值、许可或成绩；冻结模型未推广其它LUT。'})


if __name__ == '__main__':
    main()
