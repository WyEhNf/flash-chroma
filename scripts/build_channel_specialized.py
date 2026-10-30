"""只构建冻结的固定四级专门化候选；不修改已验v3、CMake或静态核心。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/channel-runtime-specialized-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); out = args.output.resolve(); plan = read(args.plan)
    if out.exists(): raise ValueError('不覆盖唯一冻结构建')
    for spec in plan['build_inputs'].values():
        if digest(ROOT/spec['path']) != spec['sha256']: raise ValueError('构建输入SHA不同：'+spec['path'])
    sources = plan['source_sha256']
    if any(digest(ROOT/name) != sha for name, sha in sources.items()): raise ValueError('冻结源码不同')
    compiler = Path(plan['compiler']['path'])
    if digest(compiler) != plan['compiler']['sha256']: raise ValueError('编译器字节不同')
    core = ROOT/plan['build_inputs']['static_core']['path']
    deps = ROOT/plan['build_inputs']['v3_library']['path']; previous = read(ROOT/plan['build_inputs']['v3_build']['path'])
    out.mkdir(parents=True)
    common = [str(compiler), '-DJSHC_CC_HAVE_AVX2=1', '-Djshc_channel_research_EXPORTS',
        '-I'+str(ROOT/'experiments/channel-runtime'), '-I'+str(ROOT/'cpp/include'),
        '-O3', '-DNDEBUG', '-std=c++17', '-fopenmp']
    commands = [common+['-c', str(ROOT/'experiments/channel-runtime/channel_runtime.cpp'), '-o', str(out/'runtime.o')],
        common+['-mavx2', '-c', str(ROOT/'experiments/channel-runtime-specialized/channel_avx2.cpp'), '-o', str(out/'avx2.o')],
        [str(compiler), '-O3', '-DNDEBUG', '-fopenmp', '-shared', '-o', str(out/'jshc_channel_specialized.dll'),
            str(out/'runtime.o'), str(out/'avx2.o'), str(core), '-lwinpthread']]
    logs = []
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        logs.append({'command': command, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            (out/'failed-build.json').write_text(json.dumps(logs, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            raise RuntimeError(result.stderr)
    dependencies = ['libgcc_s_seh-1.dll', 'libgomp-1.dll', 'libstdc++-6.dll', 'libwinpthread-1.dll']
    for name in dependencies:
        source = deps.parent/name
        if digest(source) != previous['files'][name]: raise ValueError('v3依赖SHA不同：'+name)
        shutil.copyfile(source, out/name)
    if (any(digest(ROOT/name) != sha for name, sha in sources.items())
            or digest(core) != plan['build_inputs']['static_core']['sha256']): raise ValueError('构建期间输入变化')
    with zipfile.ZipFile(out/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources: archive.write(ROOT/name, name)
        archive.write(args.plan, args.plan.resolve().relative_to(ROOT).as_posix())
    files = {name: digest(out/name) for name in ['jshc_channel_specialized.dll', *dependencies]}
    record = {'purpose': __doc__, 'plan_sha256': digest(args.plan),
        'compiler': subprocess.check_output([str(compiler), '--version'], text=True, encoding='utf-8'),
        'compiler_sha256': digest(compiler), 'source_sha256': sources,
        'static_core_path': str(core), 'static_core_sha256': digest(core), 'commands': logs,
        'files': files, 'binary_sha256': files, 'abi': 1, 'revision': 2,
        'scope': '唯一独立AVX2 TU；标量壳不含-mavx2，原CPUID/OS派发、读写/尾部/内存布局不变。未做完整域/百图/性能。'}
    (out/'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'library_sha256': files['jshc_channel_specialized.dll'], 'build_sha256': digest(out/'build.json')}, ensure_ascii=False))


if __name__ == '__main__': main()
