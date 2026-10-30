"""99唯一私有native合同执行与原件回执；完整域/照片不在此入口。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('99唯一finite执行不覆盖')
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    row=lambda path:{'path':str(path),'sha256':sha(path)}
    frozen=ROOT/'experiments/p16-b2-packed-static-v1.json'
    assert sha(frozen)=='f51415ce4d8e705c8f9d6ff77e4a7b124a1f3543488c43e5798025c15c44a033'
    plan=json.loads(frozen.read_text(encoding='utf-8'))
    for entry in plan['sources']:assert sha(Path(entry['path']))==entry['sha256']
    build=ROOT/'artifacts/p16-b2-packed-build-v1'
    receipt=build/'build-receipt.json';summary=json.loads(receipt.read_text(encoding='utf-8'))
    assert summary['return_code']==0 and summary['sources_unchanged'] and summary['all_eight_old_objects_byte_identical']
    disassembly=ROOT/'artifacts/p16-b2-packed-production-disassembly-v1.txt'
    symbols=ROOT/'artifacts/p16-b2-packed-production-symbols-v1.txt'
    assembly=disassembly.read_text(encoding='utf-8')
    assert not re.search(r'\bcall\w*\s',assembly)
    assert not re.search(r'\bvmov(?:aps|apd|dqa)\s+%ymm[^\n]*\(%rsp\)',assembly)
    assert len(re.findall(r'\bT jshc_channel::',symbols.read_text(encoding='utf-8')))==1
    contract_plan=json.loads((ROOT/'experiments/p16-b2-packed-axis-contract-v1.json').read_text(encoding='utf-8'))
    model=Path(contract_plan['models']['ordinary']['path'])
    assert sha(model)==contract_plan['models']['ordinary']['sha256']
    executable=build/'p16_b2_packed_contract.exe'
    library=build/'libjshc_b2_packed.dll'
    command=[str(executable),str(model)]
    execution={'purpose':'99唯一私有native首级u64/owner/偏移合同，不执行生产全域或照片',
        'runner':row(Path(__file__)),'source_freeze':row(frozen),'build_receipt':row(receipt),
        'executable':row(executable),'library':row(library),'model':row(model),'command':command,
        'disassembly':row(disassembly),'symbols':row(symbols),
        'assembly_audit':{'production_function_symbols':1,'call_instructions':0,
            'ymm_aligned_rsp_stores':0,'observed_ymm_spills_use_vmovdqu':True,
            'production_su_static_bytes':352,'previous97_shared_su_static_bytes':240,
            'scope':'新object无callee/hidden-return helper，YMM rsp存储用unaligned指令；XMM保存仍需原Win64的16B栈合同。非动态栈峰值/性能。'},
        'native_contract_calls':1,'production_full_domain_calls':0,'photo_calls':0,'performance_calls':0}
    args.output.mkdir(parents=True)
    (args.output/'executed-plan.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    environment=dict(os.environ);environment['PATH']='E:/mingw64/bin'+os.pathsep+environment.get('PATH','')
    run=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (args.output/'stdout.txt').write_text(run.stdout,encoding='utf-8')
    (args.output/'stderr.txt').write_text(run.stderr,encoding='utf-8')
    result={'return_code':run.returncode,'passed':False,'execution_plan_sha256':sha(args.output/'executed-plan.json'),
        'source_freeze_sha256':sha(frozen),'executable_sha256':sha(executable),'library_sha256':sha(library),
        'runner_sha256':sha(Path(__file__)),'native_contract_calls':1,'production_full_domain_calls':0,'photo_calls':0,'performance_calls':0}
    try:
        native=json.loads(run.stdout)
        result['native_result']=native
        result['passed']=run.returncode==0 and native['passed'] and native['first_stage_u64_pixels']==33554432 and native['canary_cases']==36 and native['private_reject_cases']==8 and native['owner_size']==8 and native['axis_and_nodes_mod64']==0
    except (ValueError,KeyError) as error:
        result['parse_error']=str(error)
    (args.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert result['passed'],'99唯一finite失败原件保留，停止'
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    main()
