"""一次固定亮度16bank的精确本地色数普查；不生成ROM，不读gold/照片或测吞吐。"""
import argparse
from datetime import datetime,timezone
import hashlib
from pathlib import Path
import struct
import time
import numpy as np
from study_memory_rom import ROOT,read,save,sha,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();planpath=ROOT/'experiments/luminance-palette-census-v1.json';plan=read(planpath)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()):raise AssertionError('冻结普查源改变')
    output=a.output.resolve()
    if output!=(ROOT/plan['output_path']).resolve():raise AssertionError('只允许唯一预登记输出目录，不追加独立择优普查')
    output.mkdir(parents=True,exist_ok=False);before=memory();start=time.perf_counter();source=Path(plan['input_rom_path'])
    save(output/'run.json',dict(purpose=__doc__,plan_sha256=sha(planpath),source_path=str(source),expected_source_sha256=plan['input_rom_sha256'],started_utc=datetime.now(timezone.utc).isoformat(),environment=env(),scope='唯一全域普查；无照片/gold/位宽或key扫描，无native/速度。'))
    if sha(source)!=plan['input_rom_sha256']:raise AssertionError('固定源ROM身份不同')
    raw=source.read_bytes();header=struct.unpack_from('<7I',raw,4)
    if raw[:4]!=b'M16D' or header!=(1,4,230,len(raw)-1056,0,0,0):raise AssertionError('不是固定a399的原16B精确字典')
    palette=np.frombuffer(raw,dtype='<u4',count=256,offset=32);offsets=np.frombuffer(raw,dtype='<u4',count=1048576,offset=1056);payload=np.frombuffer(raw,dtype=np.uint8,offset=1056);pool=payload[4194304:]
    if len(raw)!=5918672 or pool.size!=1723312 or np.any(palette>0xffffff) or np.any(palette[230:]) or np.any(pool>=230) or np.any(offsets<4194304) or np.any(offsets>len(payload)-16) or np.any((offsets-4194304)%16):raise AssertionError('源格式范围不符')
    if len(np.unique(palette[:230]))!=230:raise AssertionError('固定源palette互异前提不同，停止而不改变普查算法')
    frequencies=np.zeros((16,256),dtype=np.int64);logical=hashlib.sha256();bank_total=np.zeros(16,dtype=np.int64)
    # code按原ROM的R低/G中/B高顺序；不会为不同分区重读源域。
    for begin in range(0,1<<24,1<<18):
        codes=np.arange(begin,begin+(1<<18),dtype=np.uint32);red=codes&255;green=(codes>>8)&255;blue=codes>>16
        bank=(red+2*green+blue)>>6
        if int(bank.max())>15:raise AssertionError('固定亮度key越界')
        ids=payload[offsets[codes>>4]+(codes&15)];logical.update(ids)
        joint=((bank<<8)|ids).astype(np.intp);frequencies+=np.bincount(joint,minlength=4096).reshape(16,256);bank_total+=np.bincount(bank,minlength=16)
    if logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('完整16M逻辑ID不符')
    # 仅由输入key独立卷积计算16个域大小，不接触输出或替换分区。
    one=np.ones(256,dtype=np.int64);twice=np.zeros(511,dtype=np.int64);twice[::2]=1;sums=np.convolve(np.convolve(one,one),twice);expected=np.array([sums[64*b:64*(b+1)].sum() for b in range(16)],dtype=np.int64)
    if not np.array_equal(frequencies.sum(axis=1),bank_total) or not np.array_equal(expected,bank_total) or int(frequencies.sum())!=(1<<24) or np.any(frequencies[:,230:]):raise AssertionError('域覆盖/频数/ID范围不符')
    rows=[]
    for bank in range(16):
        used=np.flatnonzero(frequencies[bank]);colors=np.unique(palette[used]);rows.append(dict(bank=bank,input_colors=int(bank_total[bank]),distinct_output_colors=len(colors),distinct_global_ids=len(used),seven_bit_feasible=len(colors)<=128,global_ids=used.tolist(),output_rgb24=colors.tolist()))
    passed=all(row['seven_bit_feasible'] for row in rows);global_used=np.flatnonzero(frequencies.sum(axis=0))
    save(output/'frequency-support.json',dict(purpose='完整单次域的bank×globalID联合频数，用于离线复算色数/权重，不是新模型或ROM。',palette_rgb24=palette[:230].tolist(),bank_global_id_frequency=frequencies[:,:230].tolist(),input_count_by_bank=bank_total.tolist(),source_rom_sha256=sha(source),logical_sha256=logical.hexdigest()))
    save(output/'results.json',dict(purpose=__doc__,environment=env(),plan_sha256=sha(planpath),source_rom_sha256=sha(source),logical_sha256=logical.hexdigest(),domain_colors=1<<24,global_reachable_colors=len(np.unique(palette[global_used])),key='bank=(R+2*G+B)>>6',bank_count=16,local_id_bits=7,banks=rows,max_bank_colors=max(r['distinct_output_colors'] for r in rows),failing_banks=[r['bank'] for r in rows if not r['seven_bit_feasible']],gate_passed=passed,decision='仅容量存在性通过；是否实施单版native另由root决定，当前无实际压缩ROM/速度。' if passed else '固定16bank/7bit机制失败并停止；不得更改key/bank/位宽或删除输入补过线。',projected_format=plan['projected_format'],frequency_support_sha256=sha(output/'frequency-support.json'),before=before,after=memory(),resource_wall_seconds=time.perf_counter()-start,scope='固定源ROM唯一全256^3逻辑ID普查，230合法项并未按实际命中缩短原契约；本地色数按真实RGB互异计数。无照片/gold/其它key或位宽扫描，无打包导出/native构建/性能/WASM；投影不是实际内存收益。'))
    print(dict(gate_passed=passed,bank_colors=[r['distinct_output_colors'] for r in rows],output=str(output)))
if __name__=='__main__':main()
