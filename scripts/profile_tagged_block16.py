"""唯一只读16B常量tag普查，不生成ROM、不读照片/gold、不作性能测试。"""
import argparse
import hashlib
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,read,save,sha,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();planpath=ROOT/'experiments/tagged-block16-census-v1.json';plan=read(planpath)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()):raise AssertionError('冻结普查源变化')
    path=Path(plan['input_rom_path'])
    if sha(path)!=plan['input_rom_sha256']:raise AssertionError('原16B ROM不同')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();raw=path.read_bytes()
    if raw[:4]!=b'M16D' or struct.unpack_from('<I',raw,8)[0]!=4 or struct.unpack_from('<I',raw,16)[0]!=len(raw)-1056:raise AssertionError('原格式不同')
    count=struct.unpack_from('<I',raw,12)[0];palette=np.frombuffer(raw,dtype='<u4',offset=32,count=256);offsets=np.frombuffer(raw,dtype='<u4',offset=1056,count=1048576);pool=np.frombuffer(raw,dtype=np.uint8,offset=1056+4194304).reshape(-1,16);ids=((offsets-4194304)//16).astype(np.uint32)
    if count!=230 or len(pool)!=107707 or np.any(palette>0xffffff) or np.any(palette[count:]) or np.any(pool>=count) or np.any(offsets<4194304) or np.any((offsets-4194304)%16) or int(ids.max())>=len(pool):raise AssertionError('原模型/范围不符合固定普查')
    unique_rgb=len(np.unique(palette[:count]));values=palette[pool];constant_rgb=np.all(values==values[:,:1],axis=1);constant_id=np.all(pool==pool[:,:1],axis=1);references=np.bincount(ids,minlength=len(pool));used=references>0
    if not np.all(used):raise AssertionError('原pool存在未引用块，不改变一次普查布局')
    if unique_rgb!=count or not np.array_equal(constant_rgb,constant_id):raise AssertionError('固定源palette互异前提不符，停止而不改变推导')
    constant_unique=int(np.count_nonzero(constant_rgb));tag_entries=int(references[constant_rgb].sum());remaining=len(pool)-constant_unique;projected_rom=1056+4194304+16*remaining;projected_capacity=projected_rom+1056;logical=hashlib.sha256()
    for start in range(0,len(ids),65536):logical.update(pool[ids[start:start+65536]])
    if logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0' or constant_unique>count:raise AssertionError('完整逻辑表或理论边界不符')
    coverage=tag_entries/len(ids);hist=[dict(rgb24=int(palette[pool[i,0]]),source_pool_id=int(i),map_references=int(references[i]),input_colors=16*int(references[i])) for i in np.flatnonzero(constant_rgb)]
    save(a.output/'results.json',dict(purpose=__doc__,environment=env(),plan_sha256=sha(planpath),source_rom_sha256=sha(path),source_rom_bytes=len(raw),logical_sha256=logical.hexdigest(),palette_count=count,distinct_palette_values=unique_rgb,map_entries=len(ids),source_unique=len(pool),constant_unique=constant_unique,constant_unique_fraction=constant_unique/len(pool),constant_map_entries=tag_entries,map_weighted_coverage=coverage,constant_input_colors=tag_entries*16,nonconstant_unique=remaining,projected_map_bytes=4194304,projected_pool_bytes=16*remaining,projected_rom_bytes=projected_rom,projected_model_bytes=1056,projected_capacity=projected_capacity,source32_capacity=5919728,source3B_capacity=4871152,saved_from32=5919728-projected_capacity,extra_over3B=projected_capacity-4871152,extra_over3B_fraction=projected_capacity/4871152-1,theoretical_min_capacity=5916048,theoretical_max_capacity=5919728,ideal_dependent_read_count=3-2*coverage,constant_references=hist,before=before,after=memory(),scope='只对冻结a399原ROM做一次完整map引用普查，无照片/gold/格式扫描/新ROM/构建/mapper计时。容量只是确定布局投影，不是已实现部署；均匀全域覆盖不是照片命中或分支预测。'))
    print(a.output)
if __name__=='__main__':main()
