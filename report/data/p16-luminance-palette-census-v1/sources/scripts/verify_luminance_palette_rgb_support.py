"""独立流式聚合固定3c9c完整RGB输出，与a020逻辑域的正频数逐色及逐频数比较。"""
import argparse
from collections import Counter
import hashlib
from pathlib import Path
import sys
import time
import numpy as np
from study_memory_rom import ROOT,read,save,sha,env
from bench_memory_rom import memory

EXPECTED='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('保留独立核对原件，不覆盖')
    directory=ROOT/'artifacts/p16-luminance-palette-census-v1';planpath=ROOT/'experiments/luminance-palette-census-v1.json';results=read(directory/'results.json');support_path=directory/'frequency-support.json';support=read(support_path)
    if sha(support_path)!=results['frequency_support_sha256'] or support['logical_sha256']!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0' or support['source_rom_sha256']!='904f768b4729e1a71c8b03ddaa953b4ad183baee65498b6741068cbbc218ab22':raise AssertionError('独立比较对象的身份不同')
    source=Path('F:/Hackathon/projects/16-lut-color/artifacts/cinema-current-anchor-accept-v1/cube.rgb');digest=hashlib.sha256();actual=Counter();bytes_read=0;before=memory();start=time.perf_counter()
    with source.open('rb') as stream:
        while raw:=stream.read(3*(1<<18)):
            if len(raw)%3:raise AssertionError('完整RGB流有非三字节尾部')
            digest.update(raw);bytes_read+=len(raw);rgb=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).astype(np.uint32);codes=rgb[:,0]|(rgb[:,1]<<8)|(rgb[:,2]<<16);values,counts=np.unique(codes,return_counts=True);actual.update({int(v):int(n) for v,n in zip(values,counts)})
    if digest.hexdigest()!=EXPECTED or bytes_read!=50331648:raise AssertionError('完整模型RGB流身份不同')
    expected=Counter();zero_ids=[]
    for index,color in enumerate(support['palette_rgb24']):
        count=sum(row[index] for row in support['bank_global_id_frequency'])
        if count:expected[color]+=count
        else:zero_ids.append(index)
    if actual!=expected or len(actual)!=221 or sum(actual.values())!=(1<<24):raise AssertionError('独立RGB输出集合/频数与逻辑域不同')
    save(a.output,dict(passed=True,purpose=__doc__,environment=env(),script_sha256=sha(Path(__file__)),plan_sha256=sha(planpath),census_results_sha256=sha(directory/'results.json'),frequency_support_sha256=sha(support_path),rgb_source_path=str(source),rgb_source_sha256=digest.hexdigest(),rgb_source_bytes=bytes_read,logical_id_sha256=support['logical_sha256'],source_rom_sha256=support['source_rom_sha256'],unique_rgb_count=len(actual),global_palette_legal_count=len(support['palette_rgb24']),unreachable_legal_palette_ids=zero_ids,unreachable_legal_palette_count=len(zero_ids),sets_equal=set(actual)==set(expected),frequencies_equal=actual==expected,total_pixels=sum(actual.values()),rgb_frequencies=[dict(rgb24=v,count=actual[v]) for v in sorted(actual)],before=before,after=memory(),resource_wall_seconds=time.perf_counter()-start,scope='原3c9c输出为R高RGB流，a020为R低globalID流；顺序不同但完整256^3范围、最终颜色集合及逐色频数相同。独立只读核对，不重复亮度分类，不改旧原件；只读取模型输出，不读取目标滤镜gold/照片、导出ROM或执行native/性能。'))
    print(dict(passed=True,unique_rgb_count=len(actual),legal_palette_count=230,unreachable_legal_palette_count=len(zero_ids),sets_equal=True,frequencies_equal=True))
if __name__=='__main__':main()
