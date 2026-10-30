"""100唯一-j1独立构建及八旧对象逐字审计；不执行native质量。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();frozen=ROOT/'experiments/p16-scanline-prepare-static-v1.json'
    plan=json.loads(frozen.read_text(encoding='utf-8'))
    for row in plan['sources']:assert sha(Path(row['path']))==row['sha256'],row['path']
    if args.output.exists():raise FileExistsError('100唯一构建不覆盖')
    args.output.mkdir(parents=True)
    environment=dict(os.environ);environment['PATH']='E:/mingw64/bin'+os.pathsep+environment.get('PATH','')
    cmake='C:/Program Files (x86)/CMake/bin/cmake.exe'
    commands=[[cmake,'-S',str(ROOT/'experiments/p16-scanline-prepare-runtime'),'-B',str(args.output),'-G','MinGW Makefiles',
        '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe','-DCMAKE_C_COMPILER=E:/mingw64/bin/gcc.exe'],
        [cmake,'--build',str(args.output),'--target','jshc_scanline_prepare','p16_scanline_contract','-j','1']]
    logs=[];codes=[]
    for command in commands:
        run=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,encoding='utf-8',errors='replace')
        logs.append(run.stdout+run.stderr);codes.append(run.returncode)
        if run.returncode:break
    (args.output/'build.log').write_text('\n'.join(logs),encoding='utf-8')
    pairs=[]
    if not any(codes):
        old=ROOT/'artifacts/p16-shared-proven-build-v1/CMakeFiles/jshc_shared_proven.dir'
        new=args.output/'CMakeFiles/jshc_scanline_prepare.dir'
        for previous in sorted(old.rglob('*.obj')):
            relative=previous.relative_to(old)
            if relative.as_posix()=='channel_runtime.cpp.obj':continue
            candidate=new/relative
            pairs.append({'relative_object':relative.as_posix(),'previous_sha256':sha(previous),
                'candidate_sha256':sha(candidate) if candidate.is_file() else None,
                'byte_identical':candidate.is_file() and previous.read_bytes()==candidate.read_bytes()})
    receipt={'return_code':next((code for code in codes if code),0),'commands':commands,'source_freeze_sha256':sha(frozen),
        'sources_unchanged':all(sha(Path(r['path']))==r['sha256'] for r in plan['sources']),
        'old_object_pairs':pairs,'all_eight_old_objects_byte_identical':len(pairs)==8 and all(r['byte_identical'] for r in pairs),
        'native_quality_calls':0,'performance_calls':0}
    for name,key in [('libjshc_scanline_prepare.dll','library'),('p16_scanline_contract.exe','executable')]:
        path=args.output/name
        if path.exists():receipt[key+'_sha256']=sha(path)
    (args.output/'build-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert receipt['return_code']==0 and receipt['sources_unchanged']
    assert receipt['all_eight_old_objects_byte_identical'],'旧八对象不同，原件保留STOP'
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':main()
