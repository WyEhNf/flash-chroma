"""101唯一私有finite；必须在root复核实库并另grant后执行。"""
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
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('101唯一finite不覆盖')
    frozen=ROOT/'experiments/p16-early-index-static-v1.json';plan=json.loads(frozen.read_text(encoding='utf-8'))
    for entry in plan['sources']:assert sha(Path(entry['path']))==entry['sha256'],entry['path']
    build=ROOT/'artifacts/p16-early-index-build-v1';receipt=build/'build-receipt.json';summary=json.loads(receipt.read_text(encoding='utf-8'))
    assert summary['return_code']==0 and summary['sources_unchanged'] and summary['all_nine_old_objects_byte_identical']
    assembly=ROOT/'artifacts/p16-early-index-assembly-audit-v1.json'
    assert json.loads(assembly.read_text(encoding='utf-8'))['passed']
    executable=build/'p16_early_index_contract.exe';library=build/'libjshc_early_index.dll'
    assert sha(executable)==summary['executable_sha256'] and sha(library)==summary['library_sha256']
    execution={'purpose':'101唯一私有整数/合法cache边界有限合同，不是完整链/照片或计时',
        'runner':row(Path(__file__)),'source_freeze':row(frozen),'build_receipt':row(receipt),'assembly_audit':row(assembly),
        'executable':row(executable),'library':row(library),'command':[str(executable)],'expected':plan['finite_expected'],
        'derived_prepare_entry_count_including_fallback_nesting':3620,'native_executable_calls':1,'full_chain_calls':0,'photo_calls':0,'performance_calls':0}
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
    assert result['passed'],'101唯一finite失败原件保留STOP'
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
