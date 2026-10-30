"""串行验证真实四表的偏好选型、框架输出与拒绝路径；不是受控速度优化比较。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time

import psutil

from check_framework_delivery import parse_output


def identity(path):
    path = Path(path)
    with path.open('rb') as stream:
        sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'path': str(path.resolve()), 'bytes': path.stat().st_size, 'sha256': sha}


def write_new(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def validate(exe, data, output, affinity, fit):
    exe, data, output = exe.resolve(), data.resolve(), output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    tracked = [exe, *(exe.parent / name for name in ('main.cpp', 'flash_chroma_framework.hpp', 'source-manifest.json', 'run.ps1')),
               *(data / 'LUT' / f'Test{i}.3DL' for i in range(1, 5)),
               *(data / 'image' / f'{i}.bin' for i in range(1, 5))]
    before = [identity(p) for p in tracked]
    started_utc = datetime.now(timezone.utc).isoformat()
    records = []
    prefix = [str(exe), os.path.relpath(data, exe.parent), '33', 'auto', 'avx2', 'framework', '4', fit]

    def launch(name, command, expected_code, report_file=None, expected_deltas=None):
        started = time.perf_counter()
        with (output / f'{name}.stdout.log').open('xb') as stdout, (output / f'{name}.stderr.log').open('xb') as stderr:
            child = subprocess.Popen(command, cwd=exe.parent, stdout=stdout, stderr=stderr)
            observed = None
            try:
                process = psutil.Process(child.pid)
                process.cpu_affinity([affinity])
                observed = process.cpu_affinity()
                if observed != [affinity]:
                    raise RuntimeError('子进程绑核失败')
            except psutil.NoSuchProcess:
                if expected_code == 0:
                    raise
            code = child.wait()
        record = {'name': name, 'command': command, 'cwd': str(exe.parent), 'returncode': code,
                  'expected_returncode': expected_code, 'affinity': observed,
                  'wall_seconds': time.perf_counter() - started, 'passed': code == expected_code,
                  'stdout': identity(output / f'{name}.stdout.log'), 'stderr': identity(output / f'{name}.stderr.log')}
        text = (output / f'{name}.stdout.log').read_text(encoding='utf-8', errors='replace')
        if report_file is not None:
            report = json.loads(report_file.read_text(encoding='utf-8'))
            lines = [line for line in text.splitlines() if line.startswith('PreferenceReport=')]
            record['report_matches_stdout'] = len(lines) == 1 and json.loads(lines[0].split('=', 1)[1]) == report
            record['report'] = identity(report_file)
            record['selected'] = report['selected']
            record['passed'] &= record['report_matches_stdout'] and report['selected'] == (expected_code == 0)
            if report['selected']:
                index = report['selection']['candidate_index']
                candidate = report['candidates'][index]
                model = report['models'][candidate['model_index']]
                record['chosen'] = {'id': candidate['id'], 'm': model['sizes'], 'mode': candidate['requested_representation'],
                                    'domain_mean': model['domain_mean'], 'domain_max': model['domain_max'],
                                    'runtime_bytes': candidate['runtime_bytes'], 'time_stable': candidate['time_stable'],
                                    'provisional': report['selection']['provisional']}
                record['passed'] &= candidate['correctness_verified'] and candidate['full_domain_verified_pixels'] == 256 ** 3
                record['passed'] &= candidate['runtime_bytes'] <= report['max_runtime_bytes']
                if report['time_requested'] and not report['allow_unstable']:
                    record['passed'] &= candidate['time_verified'] and candidate['time_stable']
                if report['max_domain_mean'] is not None:
                    record['passed'] &= model['domain_mean'] <= report['max_domain_mean']
                if report['max_pixel_error'] is not None:
                    record['passed'] &= model['domain_max'] <= report['max_pixel_error']
        if code == 0:
            record['images'] = parse_output(text, 4)
            if expected_deltas is not None:
                record['delta_matches_selection'] = [r['candidate_delta'] for r in record['images']] == expected_deltas
                record['passed'] &= record['delta_matches_selection']
        records.append(record)
        write_new(output / f'{name}.receipt.json', record)
        print(json.dumps({'case': name, 'returncode': code, 'passed': record['passed'], 'chosen': record.get('chosen')}, ensure_ascii=False), flush=True)
        return record

    cases = [('accuracy', '1,0,0', []), ('compact', '0,0,1', ['--max-runtime-mib', '1']),
             ('speed', '0,1,0', [])]
    for name, weights, extra in cases:
        path = output / f'{name}.selection.json'
        command = prefix + ['--preference', weights, '--candidate-sizes', '17;33', '--candidate-modes', 'sparse,direct_rgb24',
                            '--selection-report', os.path.relpath(path, exe.parent), '--calibration-reps', '5', *extra]
        launch(name, command, 0, path)

    # 同一EXE按选中模型/模式重新走原手动入口，逐图Delta必须完全一致。
    for original in list(records):
        if not original['passed'] or 'chosen' not in original:
            continue
        choice = original['chosen']
        command = prefix.copy()
        command[2] = ','.join(map(str, choice['m']))
        command[3] = choice['mode']
        launch(original['name'] + '-manual', command, 0,
               expected_deltas=[r['candidate_delta'] for r in original['images']])

    path = output / 'no-feasible.selection.json'
    launch('no-feasible', prefix + ['--preference', '1,0,0', '--candidate-sizes', '17', '--candidate-modes', 'sparse',
                                    '--max-runtime-mib', '0', '--selection-report', os.path.relpath(path, exe.parent)], 2, path)
    launch('invalid-before-source-read', [str(exe), 'nonexistent-data', '--preference', 'nan,0,1'], 2)
    after = [identity(p) for p in tracked]
    summary = {'schema': 'framework-preference-validation-v1', 'started_utc': started_utc,
               'environment': {'platform': platform.platform(), 'cpu': os.environ.get('PROCESSOR_IDENTIFIER'),
                               'python': platform.python_version(), 'psutil': psutil.__version__, 'affinity': affinity},
               'scope': '真实原四表与四图的功能/完整域选型/原框架逐图Delta对照；合成输入时间只用于本次选择，不宣称受控优化收益',
               'before': before, 'after': after, 'sources_inputs_exe_unchanged': before == after,
               'records': records, 'passed': before == after and all(r['passed'] for r in records)}
    write_new(output / 'summary.json', summary)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--affinity', type=int, required=True)
    parser.add_argument('--fit', choices=['sample', 'independent_ls', 'chain_ls'], default='chain_ls')
    args = parser.parse_args()
    result = validate(args.exe, args.data, args.output, args.affinity, args.fit)
    print(json.dumps({'passed': result['passed'], 'cases': len(result['records'])}, ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 1)
