"""唯一完整域/逐图子进程，原样stdout/stderr；质量首失败不修后重采。"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from study_memory_rom import ROOT, read, save, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan_path = ROOT / 'experiments/page-id16-native-pages-full-v1.json'
    plan = read(plan_path)
    if any(sha(ROOT / name) != expected for name, expected in plan['source_sha256'].items()) or any(sha(name) != expected for name, expected in plan['input_sha256'].items()):
        raise AssertionError('完整质量启动身份不同，STOP')
    args.output.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment.update(OMP_NUM_THREADS='4', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       NUMEXPR_NUM_THREADS='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    command = [sys.executable, str(ROOT / 'scripts/verify_page_id16_native_pages_full.py'),
               '--output', str(args.output / 'quality')]
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True)
    (args.output / 'stdout.txt').write_bytes(result.stdout)
    (args.output / 'stderr.txt').write_bytes(result.stderr)
    save(args.output / 'run.json', dict(plan_sha256=sha(plan_path), command=command,
        returncode=result.returncode, environment={name: environment[name] for name in
        ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS',
         'PYTHONUTF8', 'PYTHONIOENCODING')}, scope='唯一完整域/照片质量，不做性能/跨平台，不覆盖失败输出。'))
    print(result.stdout.decode('utf-8', errors='replace'), end='', flush=True)
    if result.returncode:
        print(result.stderr.decode('utf-8', errors='replace'), file=sys.stderr, end='', flush=True)
        raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
