"""独立离线核copy4机器码/新符号/九模式质量与原对象；不重编或运行native。"""
import argparse
from pathlib import Path
from page_id16_copy4_common import ROOT,PLAN,checked_plan,sha,save
from study_memory_rom import read

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    plan=checked_plan()
    run=read(args.input/'run.json')
    build=read(args.input/'build/build.json')
    gate=read(args.input/'build/machine-code-gate.json')
    quality=read(args.input/'quality/results.json')
    if not run['passed'] or [row['label'] for row in run['jobs']]!=['build','quality'] or [row['returncode'] for row in run['jobs']]!=[0,0] or any(value['plan_sha256']!=sha(PLAN) for value in (run,build,quality)):raise AssertionError('唯一两步执行/计划不同')
    if not gate['passed'] or len(gate['palette_dword_reads'])!=8 or gate['forbidden_mnemonics'] or gate!=build['machine_code_gate']:raise AssertionError('实际机器码门不同')
    for name,value in build['outputs'].items():
        path=args.input/'build'/name
        if path.stat().st_size!=value['bytes'] or sha(path)!=value['sha256']:raise AssertionError('实际库/对象/栈不同')
    for name,value in build['reused_objects'].items():
        if value['path']!=plan['old_objects'][name] or sha(value['path'])!=value['sha256'] or value['sha256']!=plan['input_sha256'][value['path']]:raise AssertionError('原core/AVX对象不是原字节')
    labels={'core_out','c991_out','c991_in','c994_out','c994_in','avx1_out','avx1_in','avx4_out','avx4_in'}
    if not quality['passed'] or set(quality['full_hashes'])!=labels or set(quality['photo_hashes'])!=labels or set(quality['full_hashes'].values())!={plan['quality']['expected_full_sha256']} or set(quality['photo_hashes'].values())!={plan['quality']['expected_photos_sha256']}:raise AssertionError('九模式完整输出不同')
    if len(quality['photos'])!=100 or [row['image'] for row in quality['photos']]!=list(range(100)) or any(set(row['modes'])!=labels or set(row['modes'].values())!={row['oracle_sha256']} for row in quality['photos']):raise AssertionError('逐图独立u64不同')
    if (quality['finite'],quality['io_rejections'],len(quality['rejected_formats']),quality['image_guards'],quality['rom_guards'],quality['unaligned_rom'])!=(890,113,21,180,36,72) or not quality['closed_models_zero'] or quality['per_image_heap_scratch']!=0:raise AssertionError('固定质量/guard全部计数不同')
    if (quality['actual_rom_bytes'],quality['actual_model_bytes'],quality['actual_capacity'])!=(12633124,40,12633164) or quality['rom_sha256']!=sha(plan['page_rom']) or quality['rom_sha256']!=plan['input_sha256'][plan['page_rom']]:raise AssertionError('原ROM/实ABI改变')
    receipts=quality['entrypoint_receipts']
    if len(receipts)!=2 or [row['calls'] for row in receipts]!=[dict(core=1,omp_c99=1174,omp_avx=1176),dict(core=411,omp_c99=0,omp_avx=0)] or any(row['old_apply_address']==row['new_apply_address'] or row['new_apply_symbol']!='jshc_p4_apply_copy4' for row in receipts) or receipts[0]['parallel_symbol']!='jshc_p4_apply_copy4_parallel':raise AssertionError('质量未明确覆盖新入口')
    if receipts[0]['library_sha256']!=quality['library_sha256'] or receipts[1]['library_sha256']!=quality['standalone_sha256']:raise AssertionError('实际新入口库不同')
    value=dict(audit_passed=True,purpose=__doc__,plan_sha256=sha(PLAN),full_modes=9,photo_modes=9,images=100,finite=890,io_rejections=113,format_rejections=21,image_guards=180,rom_guards=36,unaligned_rom=72,palette_dword_reads=8,actual_capacity=12633164,library_sha256=quality['library_sha256'],standalone_sha256=quality['standalone_sha256'],scope='离线原件/身份/显式新符号完整复核；不运行native/吞吐/WASM，不用旧AVX50档替新C99背书。')
    save(args.output,value)
    print(value)

if __name__=='__main__':main()
