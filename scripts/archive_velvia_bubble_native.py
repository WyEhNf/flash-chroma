"""静态保存187原生正确性、密集栈与首轮构建失败，未测速度。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖187正确性归档')
    args.output.mkdir(parents=True)
    v1=ROOT/'artifacts/velvia-bubble-native-v1';v2=ROOT/'artifacts/velvia-bubble-native-v2'
    quality=ROOT/'artifacts/velvia-bubble-native-check-v1';build=ROOT/'artifacts/velvia-bubble-native-build-v1'
    frozen=read(v2/'frozen.json');result=read(quality/'results.json')
    for name,sha in frozen['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('原生构建后改过实际源码')
    if digest(ROOT/'scripts/check_velvia_bubble_native.py')!=result['quality_source_sha256']:raise ValueError('正确性脚本变动')
    for target,source in [('frozen-v1.json',v1/'frozen.json'),('frozen-v2.json',v2/'frozen.json'),
        ('quality-run.json',quality/'run.json'),('results.json',quality/'results.json'),('base.slut',v2/'base.slut'),
        ('channel-frac.bin',v2/'channel-frac.bin'),('compile-commands.json',build/'compile_commands.json'),
        ('configure.log',v2/'configure.log'),('build.log',v2/'build.log')]:shutil.copyfile(source,args.output/target)
    # 第一轮CMake由当前文件的未追加段精确恢复，并与当时冻结SHA核实。
    cmake='experiments/velvia-bubble-runtime/CMakeLists.txt'
    old=(ROOT/cmake).read_bytes().split(b'set_source_files_properties("${BASE}/channel_avx2.cpp"')[0]
    if hashlib.sha256(old).hexdigest()!=read(v1/'frozen.json')['source_sha256'][cmake]:raise ValueError('首轮失败CMake恢复SHA不符')
    (args.output/'failed-CMakeLists.txt').write_bytes(old)
    attempt={'first_build_exit_code':1,'failure':'AVX2内联失败：target specific option mismatch；CMake子目录SOURCE属性未传播至派生target',
        'fix':'父目录显式为原87像素TU设置相同-mavx2/-mbmi等flags；v2重新冻结后构建成功',
        'numeric_model_or_parameter_changes':0,'preserved_first_frozen_sha256':digest(v1/'frozen.json')}
    (args.output/'build-attempts.json').write_text(json.dumps(attempt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(args.output/'stack-usage.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in build.rglob('*.su'):archive.write(path,path.relative_to(build).as_posix())
    dll=build/'libjshc_velvia_bubble.dll'
    if digest(dll)!=result['library_sha256']['187']:raise ValueError('实际187 DLL变更')
    with zipfile.ZipFile(args.output/'library.zip','w',zipfile.ZIP_DEFLATED) as archive:archive.write(dll,dll.name)
    sources=set(frozen['source_sha256'])
    sources.update(['scripts/check_velvia_bubble_native.py','scripts/archive_velvia_bubble_native.py',
        'scripts/run_channel_tail_nodes.py','scripts/outplace_support.py','scripts/suffix_cache_support.py',
        'experiments/channel-runtime/channel_runtime.h','experiments/channel-runtime/channel_native.py',
        'python/lutlab/io.py','python/lutlab/channel_coordinates.py','python/lutlab/study_provenance.py','CMakeLists.txt'])
    for cmd in read(build/'compile_commands.json'):
        path=Path(cmd['file']).resolve()
        if 'jshc_velvia_bubble.dir' in cmd['command'] or 'jshc_core.dir' in cmd['command']:
            sources.add(path.relative_to(ROOT).as_posix())
    for folder in ('cpp/include/jshc','portable/include','experiments/skylake-andn-normal-runtime','experiments/skylake-suffix-cache-runtime'):
        sources.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*.hpp'))
        sources.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*.h'))
    for name in list(sources):
        path=ROOT/name
        if path.suffix in ('.c','.cpp'):
            sources.update(p.relative_to(ROOT).as_posix() for p in path.parent.glob('*.hpp'))
            sources.update(p.relative_to(ROOT).as_posix() for p in path.parent.glob('*.h'))
    sources.add('experiments/skylake-andn-normal-runtime/CMakeLists.txt')
    source_sha={name:digest(ROOT/name) for name in sorted(sources)}
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(sources):archive.write(ROOT/name,name)
    manifest={'source_sha256':source_sha,'files':{p.name:digest(p) for p in args.output.iterdir()},
        'library_sha256':result['library_sha256'],'numeric_or_performance_calls_during_archive':0,
        'scope':'187仅正确性验收，18全域/600照片/密集与拒绝合同；每线程命中数组24576B、block自身GCC栈24864B，不含被调函数及运行时栈；无正式速度或RSS结论'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(manifest['files']),'source_members':len(source_sha),'passed':result['passed'],'performance_calls':0}),flush=True)


if __name__=='__main__':main()
