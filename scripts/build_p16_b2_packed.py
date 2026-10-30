"""99唯一独立构建/旧对象审计；只在root明确grant构建窗口后执行。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    frozen = ROOT/'experiments/p16-b2-packed-static-v1.json'
    plan = json.loads(frozen.read_text(encoding='utf-8'))
    for row in plan['sources']:
        assert digest(Path(row['path'])) == row['sha256'], row['path']
    if a.output.exists():
        raise FileExistsError('99首次构建不覆盖')
    a.output.mkdir(parents=True)
    environment = dict(os.environ)
    environment['PATH'] = 'E:/mingw64/bin'+os.pathsep+environment.get('PATH','')
    cmake = 'C:/Program Files (x86)/CMake/bin/cmake.exe'
    commands = [[cmake,'-S',str(ROOT/'experiments/p16-b2-packed-runtime'),'-B',str(a.output),
        '-G','MinGW Makefiles','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe',
        '-DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe'],
        [cmake,'--build',str(a.output),'--target','jshc_b2_packed','p16_b2_packed_contract','-j','1']]
    logs,codes=[],[]
    for command in commands:
        run=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,encoding='utf-8',errors='replace')
        logs.append(run.stdout+run.stderr);codes.append(run.returncode)
        if run.returncode:break
    (a.output/'build.log').write_text('\n'.join(logs),encoding='utf-8')
    pairs=[]
    if not any(codes):
        old=ROOT/'artifacts/p16-shared-proven-build-v1/CMakeFiles/jshc_shared_proven.dir'
        new=a.output/'CMakeFiles/jshc_b2_packed.dir'
        for prior in sorted(old.rglob('*.obj')):
            relative=prior.relative_to(old)
            if relative.as_posix()=='channel_runtime.cpp.obj':continue
            candidate=new/relative
            assert candidate.is_file(),str(candidate)
            pairs.append({'relative_object':relative.as_posix(),'previous_sha256':digest(prior),
                'candidate_sha256':digest(candidate),'byte_identical':digest(prior)==digest(candidate)})
        assert len(pairs)==8
    receipt={'return_code':next((code for code in codes if code),0),'commands':commands,
        'source_freeze_sha256':digest(frozen),'sources_unchanged':all(digest(Path(r['path']))==r['sha256'] for r in plan['sources']),
        'old_object_pairs':pairs,'all_eight_old_objects_byte_identical':bool(pairs) and all(r['byte_identical'] for r in pairs),
        'quality_calls':0,'performance_calls':0}
    library=a.output/'libjshc_b2_packed.dll'
    if library.exists():receipt['library_sha256']=digest(library)
    (a.output/'build-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert receipt['return_code']==0 and receipt['sources_unchanged']
    assert receipt['all_eight_old_objects_byte_identical'],'旧对象差异保留停止，不能宣称字节保持'
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':
    main()
