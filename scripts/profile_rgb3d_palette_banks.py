"""唯一RGB高3位512bank/6bit精确palette普查；任一bank超64即停止该机制。"""
import argparse
from datetime import datetime,timezone
import hashlib
from pathlib import Path
import struct
import time
import numpy as np
from study_memory_rom import ROOT,read,save,sha,env
from bench_memory_rom import memory

def bank_from_code(code):
    if type(code)!=int or code<0 or code>0xffffff:raise ValueError('输入只接受完整RGB24整数')
    return ((code>>5)&7)|((code>>10)&56)|((code>>15)&448)

def finite_contract():
    edges=(0,1,30,31,32,33,63,64,95,96,127,128,159,160,191,192,223,224,254,255);cases=0
    for red in edges:
        for green in edges:
            for blue in edges:
                code=red|(green<<8)|(blue<<16)
                if bank_from_code(code)!=((red>>5)|((green>>5)<<3)|((blue>>5)<<6)):raise AssertionError('独立分通道bank公式不同')
                cases+=1
    for code in (-1,1<<24):
        try:bank_from_code(code)
        except ValueError:cases+=1
        else:raise AssertionError('输入越界未拒绝')
    if bank_from_code(0)!=0 or bank_from_code(0xffffff)!=511:raise AssertionError('bank极值错误')
    return cases

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();planpath=ROOT/'experiments/rgb3d-palette-census-v1.json';plan=read(planpath)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()):raise AssertionError('冻结普查源改变')
    output=a.output.resolve()
    if output!=(ROOT/plan['output_path']).resolve():raise AssertionError('只允许唯一预登记输出目录')
    output.mkdir(parents=True,exist_ok=False);before=memory();start=time.perf_counter();source=Path(plan['input_rom_path']);finite=finite_contract()
    save(output/'run.json',dict(purpose=__doc__,plan_sha256=sha(planpath),source_path=str(source),expected_source_sha256=plan['input_rom_sha256'],started_utc=datetime.now(timezone.utc).isoformat(),environment=env(),finite_index_cases=finite,scope='单个预定key/512banks/6bit，只做一次全域普查；无照片/gold/其它参数/native/速度。'))
    if sha(source)!=plan['input_rom_sha256']:raise AssertionError('固定源ROM身份不同')
    raw=source.read_bytes();header=struct.unpack_from('<7I',raw,4)
    if raw[:4]!=b'M16D' or header!=(1,4,230,len(raw)-1056,0,0,0):raise AssertionError('不是固定a399原16B精确字典')
    palette=np.frombuffer(raw,dtype='<u4',count=256,offset=32);offsets=np.frombuffer(raw,dtype='<u4',count=1048576,offset=1056);payload=np.frombuffer(raw,dtype=np.uint8,offset=1056);pool=payload[4194304:]
    if len(raw)!=5918672 or pool.size!=1723312 or np.any(palette>0xffffff) or np.any(palette[230:]) or np.any(pool>=230) or np.any(offsets<4194304) or np.any(offsets>len(payload)-16) or np.any((offsets-4194304)%16):raise AssertionError('原格式范围不同')
    if len(np.unique(palette[:230]))!=230:raise AssertionError('原230合法RGB互异条件不同')
    frequencies=np.zeros((512,256),dtype=np.int64);bank_total=np.zeros(512,dtype=np.int64);logical=hashlib.sha256()
    for begin in range(0,1<<24,1<<18):
        codes=np.arange(begin,begin+(1<<18),dtype=np.uint32);red=codes&255;green=(codes>>8)&255;blue=codes>>16;bank=(red>>5)|((green>>5)<<3)|((blue>>5)<<6)
        alternative=((codes>>5)&7)|((codes>>10)&56)|((codes>>15)&448)
        if not np.array_equal(bank,alternative) or int(bank.max())>511:raise AssertionError('完整域两种同一key公式不同')
        ids=payload[offsets[codes>>4]+(codes&15)];logical.update(ids);joint=((bank<<8)|ids).astype(np.intp);frequencies+=np.bincount(joint,minlength=131072).reshape(512,256);bank_total+=np.bincount(bank,minlength=512)
    if logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('完整16M逻辑ID不同')
    if not np.array_equal(frequencies.sum(axis=1),bank_total) or not np.all(bank_total==32768) or int(frequencies.sum())!=(1<<24) or np.any(frequencies[:,230:]):raise AssertionError('512个32^3域未完整覆盖')
    rows=[]
    for bank in range(512):
        used=np.flatnonzero(frequencies[bank]);colors=np.unique(palette[used]);rows.append(dict(bank=bank,red_high3=bank&7,green_high3=(bank>>3)&7,blue_high3=bank>>6,input_colors=int(bank_total[bank]),distinct_output_colors=len(colors),distinct_global_ids=len(used),six_bit_feasible=len(colors)<=64,global_ids=used.tolist(),output_rgb24=colors.tolist()))
    passed=all(row['six_bit_feasible'] for row in rows);global_used=np.flatnonzero(frequencies.sum(axis=0))
    save(output/'frequency-support.json',dict(purpose='唯一完整域bank×globalID联合频数，不是本地ID表或新ROM。',palette_rgb24=palette[:230].tolist(),bank_global_id_frequency=frequencies[:,:230].tolist(),input_count_by_bank=bank_total.tolist(),source_rom_sha256=sha(source),logical_sha256=logical.hexdigest()))
    save(output/'results.json',dict(purpose=__doc__,environment=env(),plan_sha256=sha(planpath),source_rom_sha256=sha(source),logical_sha256=logical.hexdigest(),finite_index_cases=finite,domain_colors=1<<24,global_reachable_colors=len(np.unique(palette[global_used])),key='bank=(R>>5)|((G>>5)<<3)|((B>>5)<<6)',bank_count=512,local_id_bits=6,banks=rows,max_bank_colors=max(r['distinct_output_colors'] for r in rows),failing_banks=[r['bank'] for r in rows if not r['six_bit_feasible']],gate_passed=passed,decision='只证明固定6bit表示存在；是否单版native另由root决定，无实际压缩文件或速度。' if passed else '固定512bank/6bit失败停止，不改key/位宽/划分、不加例外或删除输入。',projected_format=plan['projected_format'],frequency_support_sha256=sha(output/'frequency-support.json'),before=before,after=memory(),resource_wall_seconds=time.perf_counter()-start,scope='原a399完整256^3唯一普查，局部集合按最终RGB计数。230合法项与实际命中色数区分；不读gold/照片/其它参数，不导出本地ID/ROM/构建/性能/WASM，投影不作为内存收益。'))
    print(dict(gate_passed=passed,max_bank_colors=max(r['distinct_output_colors'] for r in rows),failing_banks=[r['bank'] for r in rows if not r['six_bit_feasible']],output=str(output)))
if __name__=='__main__':main()
