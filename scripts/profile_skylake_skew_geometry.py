"""只读索引几何：证明缓存行置换及2MiB页号不变，组分散仅为低位组索引模型，不冒充真实替换。"""
import argparse,json,hashlib
from pathlib import Path
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖几何回执')
    seen=bytearray(2**18)
    for line in range(2**18):
        mixed=line^(line>>10)
        assert mixed^(mixed>>10)==line and not seen[mixed] and mixed>>15==line>>15
        seen[mixed]=1
    assert all(seen)
    caches=[]
    for path in sorted(Path('/sys/devices/system/cpu/cpu0/cache').glob('index*')):
        caches.append({k:(path/k).read_text().strip() for k in ('level','type','size','number_of_sets','ways_of_associativity','coherency_line_size')})
    rows=[]
    for sets in (64,1024,2048):
        plain=set();skew=set()
        for b in range(256):
            code=128|(128<<8)|(b<<16);h=code^(code>>10)
            plain.add((code>>6)&(sets-1));skew.add((h>>6)&(sets-1))
        rows.append({'model_sets':sets,'fixed_rg':[128,128],'varying_b_values':256,'plain_unique_model_sets':len(plain),'skew_unique_model_sets':len(skew)})
    result={'purpose':__doc__,'pass':True,'verified_line_permutation_entries':2**18,'line_bytes':64,'within_line_permutation':'低6bit与固定G高6bit异或，逐行64字节双射','two_mib_page_number_preserved':True,'cacheline_group_cardinality_preserved':True,'cpu0_observed_caches':caches,'conventional_low_bits_index_model':rows,'limitations':'仅通常低位组索引的模型；CPU可使用其他哈希/替换策略，没有测L1/L2真实miss或预测吞吐；不是Skylake实机','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'new_native_pixel_calls':0,'new_performance_calls':0}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
