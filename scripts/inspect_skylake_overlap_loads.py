"""静态对比45/46的组首读取宽度；地址相交说明不代替硬件stall事件。"""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(name):
    path=ROOT/f'artifacts/skylake-{name}-linux-static-v1/candidate.asm';text=path.read_text()
    functions=re.split(r'^[0-9a-f]+ <([^>]+)>:\s*\n',text,flags=re.M)
    assert len(functions)==5
    first=functions[2];second=functions[4]
    return {'assembly':path.relative_to(ROOT).as_posix(),'assembly_sha256':sha(path),'first_symbol':functions[1],'group_mask_ffff00_count':len(re.findall(r'\band\s+\$0xffff00,',first)),'first_function_movzwl_count':len(re.findall(r'\bmovzwl\b',first)),'first_function_non_temporal_store_count':first.count('vmovntdq'),'outplace_non_temporal_store_count':second.count('vmovntdq')}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖静态分析')
    old=inspect('overlap');new=inspect('overlap16')
    assert old['group_mask_ffff00_count']==17 and old['first_function_movzwl_count']==1
    assert new['group_mask_ffff00_count']==0 and new['first_function_movzwl_count']-old['first_function_movzwl_count']==17
    assert old['first_function_non_temporal_store_count']==new['first_function_non_temporal_store_count']==0
    assert old['outplace_non_temporal_store_count']==new['outplace_non_temporal_store_count']==6
    result={'pass':True,'purpose':__doc__,'old45':old,'new46':new,'source_address_intervals_half_open':{'previous_last_write':[-3,1],'old_first_read':[0,4],'new_first_read':[1,3],'old_intersection_bytes':[0],'new_intersection_bytes':[]},'limitation':'静态观察首读32位再掩码和首读16位的变化；未测专用store forwarding stall事件，周期变化必须另看同场配对','new_native_calls':0,'new_performance_calls':0,'script_sha256':sha(Path(__file__))}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('45/46组首加载静态分析通过')
if __name__=='__main__':main()
