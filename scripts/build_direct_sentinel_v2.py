"""单次冻结并构建290与独立有限合同；实际依赖反查冻结，不执行像素合同。"""
from __future__ import annotations
import ast
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'artifacts/p16-direct-sentinel-v2-build-v1'
FROZEN=ROOT/'artifacts/p16-direct-sentinel-v2-build-frozen-v1'
CMAKE=Path('C:/Program Files (x86)/CMake/bin/cmake.exe')
BIN=Path('E:/mingw64/bin')

def sha(path: Path) -> str:
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def save(path: Path,value) -> None:
    if path.exists():raise FileExistsError(f'不覆盖证据：{path}')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main() -> None:
    if BUILD.exists() or FROZEN.exists():raise FileExistsError('不覆盖既有构建或冻结')
    source_freeze=ROOT/'artifacts/p16-direct-sentinel-v2-source-v1/freeze.json'
    source=json.loads(source_freeze.read_text(encoding='utf-8'))
    generated_path=ROOT/'artifacts/p16-direct-sentinel-v2-generated-v1.json'
    generated=json.loads(generated_path.read_text(encoding='utf-8'))
    for name,row in source['sources'].items():
        if sha(ROOT/name)!=row['sha256']:raise ValueError('原生成冻结源变更：'+name)
    for name,expected in generated['outputs'].items():
        if sha(ROOT/'experiments/p16-direct-sentinel-runtime-v2'/name)!=expected:raise ValueError('生成源变更：'+name)
    paths={ROOT/'CMakeLists.txt',ROOT/'AGENTS.md',Path(__file__),ROOT/'experiments/p16-direct-sentinel-plan-v1.md',ROOT/'scripts/generate_direct_sentinel.py',ROOT/'scripts/prepare_direct_sentinel_sources.py'}
    for folder in ('cpp','portable','experiments/p16-direct-sentinel-runtime-v2','experiments/skylake-andn-normal-runtime','experiments/skylake-domain-isolated-runtime','experiments/skylake-exception-runtime','experiments/skylake-suffix-cache-runtime','experiments/channel-runtime'):
        paths.update(path for path in (ROOT/folder).rglob('*') if path.is_file() and (path.suffix in ('.c','.cpp','.h','.hpp') or path.name=='CMakeLists.txt'))
    for path in paths:
        if path.suffix=='.py':ast.parse(path.read_bytes().decode('utf-8-sig'),filename=str(path))
    env=os.environ.copy();env['PATH']=str(BIN)+os.pathsep+env['PATH']
    tools={name:BIN/name for name in ('gcc.exe','g++.exe','mingw32-make.exe','libgomp-1.dll','libstdc++-6.dll','libgcc_s_seh-1.dll')}
    tools['cmake.exe']=CMAKE
    versions={}
    for name,command in {'g++':[str(BIN/'g++.exe'),'--version'],'target':[str(BIN/'g++.exe'),'-dumpmachine'],'cmake':[str(CMAKE),'--version'],'cc1plus':[str(BIN/'g++.exe'),'-print-prog-name=cc1plus']}.items():
        result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,check=False)
        if result.returncode:raise RuntimeError('工具链预检失败：'+name)
        versions[name]=result.stdout.decode('utf-8','replace')
    cc1plus=Path(versions['cc1plus'].strip()).resolve()
    if not cc1plus.is_file():raise FileNotFoundError('cc1plus身份无法确定')
    tools['cc1plus']=cc1plus
    FROZEN.mkdir(parents=True)
    rows={}
    for path in sorted(paths):
        name=path.relative_to(ROOT).as_posix();data=path.read_bytes();target=FROZEN/'sources'/name
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        rows[name]={'sha256':sha(path),'bytes':len(data)}
    configure=[str(CMAKE),'-S',str(ROOT/'experiments/p16-direct-sentinel-runtime-v2'),'-B',str(BUILD),'-G','MinGW Makefiles','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',f'-DCMAKE_C_COMPILER={BIN/"gcc.exe"}',f'-DCMAKE_CXX_COMPILER={BIN/"g++.exe"}',f'-DCMAKE_MAKE_PROGRAM={BIN/"mingw32-make.exe"}']
    build=[str(CMAKE),'--build',str(BUILD),'--target','jshc_direct_sentinel_v2','p16_direct_sentinel_v2_contracts','--parallel','2']
    frozen={'status':'单次独立构建，未执行有限/模型/性能','utc':datetime.now(timezone.utc).isoformat(),'sources':rows,'source_generation_freeze_sha256':sha(source_freeze),'generation_receipt_sha256':sha(generated_path),'toolchain':{name:{'path':str(path),'sha256':sha(path)} for name,path in tools.items()},'versions':versions,'python':sys.version,'platform':platform.platform(),'processor':platform.processor(),'configure_command':configure,'build_command':build,'performance_calls':0}
    save(FROZEN/'frozen.json',frozen)
    BUILD.mkdir(parents=True)
    for name,command in (('configure',configure),('build',build)):
        result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,check=False)
        (BUILD/(name+'-stdout.txt')).write_bytes(result.stdout);(BUILD/(name+'-stderr.txt')).write_bytes(result.stderr)
        save(BUILD/(name+'-receipt.json'),{'command':command,'returncode':result.returncode,'frozen_sha256':sha(FROZEN/'frozen.json'),'performance_calls':0})
        if result.returncode:raise RuntimeError(name+'失败，保留日志/部分产物，不覆盖重建')
    dependencies={};depfiles=sorted(BUILD.rglob('*.obj.d'))
    if not depfiles:raise ValueError('缺实际编译器依赖')
    for dep in depfiles:
        for line in dep.read_text(encoding='utf-8').splitlines()[1:]:
            token=line.strip()
            if token.endswith(' \\'):token=token[:-2].rstrip()
            if not token:continue
            path=Path(token)
            if not path.is_absolute():path=BUILD/path
            path=path.resolve()
            try:name=path.relative_to(ROOT).as_posix()
            except ValueError:continue
            if not path.is_file() or name not in rows or sha(path)!=rows[name]['sha256']:raise ValueError('实际依赖不在冻结闭包：'+name)
            dependencies[name]=sha(path)
    for name,row in rows.items():
        if sha(ROOT/name)!=row['sha256']:raise ValueError('构建后冻结源变更：'+name)
    commands=json.loads((BUILD/'compile_commands.json').read_text(encoding='utf-8'))
    used_commands=[row for row in commands if 'jshc_direct_sentinel_v2.dir' in row['command'] or 'p16_direct_sentinel_v2_contracts.dir' in row['command']]
    if not used_commands:raise ValueError('缺新目标实际编译命令')
    for row in used_commands:
        command=row['command'].lower()
        if any(flag in command for flag in ('-mavx512','-march=native','-march=x86-64-v4')):raise ValueError('发现禁止的AVX512或native构建参数')
        relative=Path(row['file']).resolve().relative_to(ROOT).as_posix()
        if relative not in dependencies:raise ValueError('编译源未被实际依赖审计覆盖：'+relative)
    dll=BUILD/'libjshc_direct_sentinel_v2.dll';contract=BUILD/'p16_direct_sentinel_v2_contracts.exe'
    if not dll.is_file() or not contract.is_file():raise FileNotFoundError('缺构建产物')
    save(BUILD/'build-check.json',{'passed':True,'frozen_sha256':sha(FROZEN/'frozen.json'),'dependency_files':{str(path.relative_to(BUILD)):sha(path) for path in depfiles},'actual_repository_dependencies_sha256':dependencies,'frozen_source_count':len(rows),'new_target_compile_commands':len(used_commands),'dll_sha256':sha(dll),'contract_sha256':sha(contract),'performance_calls':0,'pixel_contracts_executed':False})
    print(json.dumps({'passed':True,'frozen_sources':len(rows),'actual_repository_dependencies':len(dependencies),'dll_sha256':sha(dll),'contract_sha256':sha(contract),'performance_calls':0},ensure_ascii=False))

if __name__=='__main__':main()
