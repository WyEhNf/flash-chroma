"""补齐已有只读OMP观察器的0x55进程允许掩码前提；不改291或完整域算法。"""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    source=ROOT/'scripts/check_direct_sentinel_full_mt_v2.py';target=ROOT/'scripts/check_direct_sentinel_full_mt_v3.py';receipt=ROOT/'artifacts/p16-direct-sentinel-mt-v3-generated.json'
    if target.exists() or receipt.exists():raise FileExistsError('不覆盖整幅MT观察修订')
    text=source.read_bytes().decode('utf-8')
    old="OUT.mkdir(parents=True)\n    dirs="
    if text.count(old)!=1:raise ValueError('观察器前提修复非唯一')
    text=text.replace(old,"OUT.mkdir(parents=True)\n    psutil.Process().cpu_affinity([0,2,4,6])\n    save(OUT/'process-preflight.json',{'allowed_cpus':psutil.Process().cpu_affinity(),'per_tid_pin':False,'performance_calls':0})\n    dirs=")
    text=text.replace('p16-direct-sentinel-v2-full-mt-frozen-v1','p16-direct-sentinel-v2-full-mt-frozen-v2').replace('p16-direct-sentinel-v2-full-mt-v1','p16-direct-sentinel-v2-full-mt-v2')
    text=text.replace("row={'return_code':code,'action':0,'members':[{name:getattr(value,name) for name,_ in Record._fields_} for value in records]};teams.append(row)","row={'return_code':code,'action':0,'members':[{name:getattr(value,name) for name,_ in Record._fields_} for value in records]};teams.append(row)\n        save(OUT/f'team-{len(teams):02d}.json',row)")
    text=text.replace("if code:raise ValueError('只读线程观察失败')","if code:raise ValueError('只读线程观察失败：'+str(code))")
    ast.parse(text);target.write_bytes(text.encode('utf-8'))
    receipt.write_text(json.dumps({'old_sha256':sha(source),'new_sha256':sha(target),'generator_sha256':sha(__file__),'scope':'只补已存在helper的process allowed 0x55前提及逐snapshot原始日志；不逐TID固定，不改native/model/像素验收','previous_failure':'V2未满足观察器前提而停止在首snapshot，未执行10整幅流；原return code未记入日志，不推测具体值','performance_calls':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'generated':True,'target_sha256':sha(target),'performance_calls':0}))

if __name__=='__main__':main()
