"""独立finite V2保留原失败，只修声明的fixture与记录器；不自动其它质量。"""
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
    plan_path = ROOT / 'experiments/page-id16-native-pages-finite-v2.json'
    plan = read(plan_path)
    if any(sha(ROOT / name) != expected for name, expected in plan['source_sha256'].items()) or any(sha(name) != expected for name, expected in plan['input_sha256'].items()):
        raise AssertionError('启动前冻结身份不一致，STOP')
    args.output.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment.update(OMP_NUM_THREADS='4', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       NUMEXPR_NUM_THREADS='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    command = [sys.executable, str(ROOT / 'scripts/verify_page_id16_native_pages_finite_v2.py'),
               '--output', str(args.output / 'finite')]
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True)
    (args.output / 'stdout.txt').write_bytes(result.stdout)
    (args.output / 'stderr.txt').write_bytes(result.stderr)
    save(args.output / 'run.json', dict(plan_sha256=sha(plan_path), command=command,
        returncode=result.returncode, environment={name: environment[name] for name in
        ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS',
        'PYTHONUTF8', 'PYTHONIOENCODING')}, scope='独立机械V2，原v1 STOP不改；不计时，不覆盖重采。'))
    print(result.stdout.decode('utf-8', errors='replace'), end='', flush=True)
    if result.returncode:
        print(result.stderr.decode('utf-8', errors='replace'), file=sys.stderr, end='', flush=True)
        raise SystemExit(result.returncode)
    print(dict(finite_returncode=0, plan_sha256=sha(plan_path)), flush=True)


if __name__ == '__main__':
    main()
