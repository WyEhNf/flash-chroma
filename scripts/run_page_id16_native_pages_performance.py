"""只执行预冻结四worker/六RSS一次；任一native或身份失败STOP，AA不补采。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

PLAN = ROOT / 'experiments/page-id16-native-pages-performance-v1.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan = read(PLAN)
    if sys.version.split()[0] != plan['expected_versions']['python']:
        raise AssertionError('正式driver Python版本不匹配，STOP')
    if any(sha(ROOT / name) != value for name, value in plan['source_sha256'].items()) or any(sha(name) != value for name, value in plan['input_sha256'].items()):
        raise AssertionError('formal启动前冻结身份不符，STOP')
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment.update(plan['required_environment'])
    jobs = [('worker' + str(index), ['--worker', str(index)]) for index in range(4)]
    jobs += [('rss-' + role, ['--rss', role]) for role in plan['roles']]
    records = []
    for label, flags in jobs:
        command = [sys.executable, str(ROOT / 'scripts/bench_page_id16_native_pages.py'),
                   '--plan', str(PLAN), *flags, '--output', str(args.output / label)]
        print('开始唯一native-pages正式进程：' + label, flush=True)
        started = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True)
        records.append(dict(label=label, command=command, returncode=result.returncode,
            wall_seconds=time.perf_counter() - started,
            stdout=result.stdout.decode('utf-8', errors='replace'), stderr=result.stderr.decode('utf-8', errors='replace')))
        save(args.output / 'driver.json', dict(plan_sha256=sha(PLAN), passed=False, jobs=records))
        print(dict(label=label, returncode=result.returncode, stdout=records[-1]['stdout'][-1000:],
                   stderr=records[-1]['stderr'][-2000:]), flush=True)
        if result.returncode:
            raise RuntimeError('唯一formal进程失败，停止余下未运行角色：' + label)
    save(args.output / 'driver.json', dict(plan_sha256=sha(PLAN), passed=True, jobs=records))
    print(dict(passed=True, workers=4, calls=1920, rss_processes=6), flush=True)


if __name__ == '__main__':
    main()
