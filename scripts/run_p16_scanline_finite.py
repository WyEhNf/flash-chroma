"""100唯一私有有限native执行；只消费已冻结源/构建/汇编回执。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
row=lambda path:{'path':str(path),'sha256':sha(path)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('100唯一finite不覆盖')
    frozen=ROOT/'experiments/p16-scanline-prepare-static-v1.json';plan=json.loads(frozen.read_text(encoding='utf-8'))
    for entry in plan['sources']:assert sha(Path(entry['path']))==entry['sha256'],entry['path']
    build=ROOT/'artifacts/p16-scanline-prepare-build-v1';receipt=build/'build-receipt.json'
    summary=json.loads(receipt.read_text(encoding='utf-8'))
    assert summary['return_code']==0 and summary['sources_unchanged'] and summary['all_eight_old_objects_byte_identical']
    assembly=ROOT/'artifacts/p16-scanline-prepare-assembly-audit-v1.json'
    audited=json.loads(assembly.read_text(encoding='utf-8'));assert audited['passed']
    executable=build/'p16_scanline_contract.exe';library=build/'libjshc_scanline_prepare.dll'
    assert sha(executable)==summary['executable_sha256'] and sha(library)==summary['library_sha256']
    execution={'purpose':'100唯一私有有限prepare数学/地址/只读合同，无完整链/照片/性能',
        'runner':row(Path(__file__)),'source_freeze':row(frozen),'build_receipt':row(receipt),'assembly_audit':row(assembly),
        'executable':row(executable),'library':row(library),'command':[str(executable)],
        'expected':plan['finite_expected'],'native_executable_calls':1,'full_chain_calls':0,'photo_calls':0,'performance_calls':0}
    args.output.mkdir(parents=True)
    (args.output/'executed-plan.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    environment=dict(os.environ);environment['PATH']='E:/mingw64/bin'+os.pathsep+environment.get('PATH','')
    run=subprocess.run(execution['command'],cwd=ROOT,env=environment,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (args.output/'stdout.txt').write_text(run.stdout,encoding='utf-8');(args.output/'stderr.txt').write_text(run.stderr,encoding='utf-8')
    result={'return_code':run.returncode,'passed':False,'execution_plan_sha256':sha(args.output/'executed-plan.json'),
        'source_freeze_sha256':sha(frozen),'executable_sha256':sha(executable),'library_sha256':sha(library),
        'native_executable_calls':1,'full_chain_calls':0,'photo_calls':0,'performance_calls':0}
    try:
        native=json.loads(run.stdout);result['native_result']=native
        result['passed']=run.returncode==0 and native['passed'] and all(native.get(k)==v for k,v in plan['finite_expected'].items())
    except (ValueError,KeyError) as error:result['parse_error']=str(error)
    (args.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert result['passed'],'100唯一finite失败，原件保留STOP'
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
