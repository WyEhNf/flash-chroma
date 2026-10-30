"""前置冻结后单次构建独立Windows OpenMP线程控制helper；不执行或计时。"""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖构建原件')
    args.output.mkdir(parents=True)
    args.output = args.output.resolve()
    source = ROOT / 'experiments/p16-omp-affinity-control-v1'
    compiler = Path('E:/mingw64/bin/g++.exe')
    runtime = Path('E:/mingw64/bin/libgomp-1.dll')
    paths = [source / 'control.cpp', source / 'plan.md', Path(__file__),
             ROOT / 'scripts/check_omp_affinity_control.py', ROOT / 'experiments/channel-runtime/channel_native.py']
    frozen = {'started_utc': datetime.now(timezone.utc).isoformat(),
        'sources_sha256': {str(p): sha(p) for p in paths},
        'compiler': str(compiler), 'compiler_sha256': sha(compiler),
        'libgomp': str(runtime), 'libgomp_sha256': sha(runtime),
        'scope': '冻结在构建前；helper泛用x64+OpenMP，无AVX/BMI/模型运行或性能。'}
    (args.output / 'frozen.json').write_text(json.dumps(frozen, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    command = [str(compiler), '-O2', '-std=c++17', '-shared', '-fopenmp', '-Wall', '-Wextra', '-pedantic',
        '-fstack-usage', '-MMD', '-MP', str(source / 'control.cpp'), '-o', str(args.output / 'libp16_omp_affinity.dll')]
    completed = subprocess.run(command, cwd=args.output, capture_output=True, text=True)
    (args.output / 'build.log').write_text(completed.stdout + completed.stderr, encoding='utf-8')
    version = subprocess.run([str(compiler), '-v'], capture_output=True, text=True)
    (args.output / 'compiler-version.txt').write_text(version.stdout + version.stderr, encoding='utf-8')
    receipt = {'command': command, 'return_code': completed.returncode,
               'sources_unchanged': all(sha(p) == h for p, h in frozen['sources_sha256'].items()),
               'compiler_sha256': sha(compiler), 'libgomp_sha256': sha(runtime), 'performance_calls': 0}
    if completed.returncode == 0:
        receipt['library_sha256'] = sha(args.output / 'libp16_omp_affinity.dll')
        pe = subprocess.run(['E:/mingw64/bin/objdump.exe', '-p', str(args.output / 'libp16_omp_affinity.dll')],
                            capture_output=True, text=True)
        (args.output / 'pe.txt').write_text(pe.stdout + pe.stderr, encoding='utf-8')
        receipt['pe_exit_code'] = pe.returncode
        receipt['imports_libgomp'] = 'libgomp-1.dll' in pe.stdout
        receipt['imports_thread_mask_api'] = 'SetThreadAffinityMask' in pe.stdout and 'GetThreadGroupAffinity' in pe.stdout
    (args.output / 'build-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False))
    if completed.returncode or not receipt['sources_unchanged']:
        raise RuntimeError('构建或源身份失败，保留首次原件')


if __name__ == '__main__':
    main()
