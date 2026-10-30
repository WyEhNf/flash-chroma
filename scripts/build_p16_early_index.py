"""101唯一-j1生产/私有EXE构建；9旧对象核对，不运行native合同。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    frozen=ROOT/'experiments/p16-early-index-static-v1.json';plan=json.loads(frozen.read_text(encoding='utf-8'))
    for entry in plan['sources']:assert sha(Path(entry['path']))==entry['sha256'],entry['path']
    if args.output.exists():raise FileExistsError('101唯一构建不覆盖')
    args.output.mkdir(parents=True)
    environment=dict(os.environ);environment['PATH']='E:/mingw64/bin'+os.pathsep+environment.get('PATH','')
    cmake='C:/Program Files (x86)/CMake/bin/cmake.exe'
    commands=[[cmake,'-S',str(ROOT/'experiments/p16-early-index-runtime'),'-B',str(args.output),'-G','MinGW Makefiles',
        '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe','-DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe'],
        [cmake,'--build',str(args.output),'--target','jshc_early_index','p16_early_index_contract','-j','1']]
    logs=[];codes=[]
    for command in commands:
        run=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,encoding='utf-8',errors='replace')
        logs.append(run.stdout+run.stderr);codes.append(run.returncode)
        if run.returncode:break
    (args.output/'build.log').write_text('\n'.join(logs),encoding='utf-8');pairs=[]
    if not any(codes):
        previous=ROOT/'artifacts/p16-scanline-prepare-build-v1/CMakeFiles/jshc_scanline_prepare.dir'
        candidate=args.output/'CMakeFiles/jshc_early_index.dir'
        for path in sorted(previous.rglob('*.obj')):
            relative=path.relative_to(previous)
            if relative.as_posix()=='channel_runtime.cpp.obj':continue
            new=candidate/relative
            pairs.append({'relative_object':relative.as_posix(),'previous_sha256':sha(path),
                'candidate_sha256':sha(new) if new.is_file() else None,'byte_identical':new.is_file() and path.read_bytes()==new.read_bytes()})
    receipt={'return_code':next((v for v in codes if v),0),'commands':commands,'source_freeze_sha256':sha(frozen),
        'sources_unchanged':all(sha(Path(r['path']))==r['sha256'] for r in plan['sources']),
        'old_object_pairs':pairs,'all_nine_old_objects_byte_identical':len(pairs)==9 and all(r['byte_identical'] for r in pairs),
        'native_executions':0,'performance_calls':0}
    for name,key in [('libjshc_early_index.dll','library'),('p16_early_index_contract.exe','executable')]:
        path=args.output/name
        if path.is_file():receipt[key+'_sha256']=sha(path)
    (args.output/'build-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert receipt['return_code']==0 and receipt['sources_unchanged']
    assert receipt['all_nine_old_objects_byte_identical'],'9旧对象不同，保留STOP'
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':main()
