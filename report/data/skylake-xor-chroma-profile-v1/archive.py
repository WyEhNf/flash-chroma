"""归档唯一异或布局筛查并从原统计独立复算门槛；不重跑统计。"""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import platform
import sys
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'artifacts/skylake-xor-chroma-profile-v1'
DST=ROOT/'report/data/skylake-xor-chroma-profile-v1'
DST.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[]
for source in sorted(SRC.iterdir()):
    assert source.is_file()
    target=DST/source.name
    shutil.copyfile(source,target)
    assert source.read_bytes()==target.read_bytes()
    files.append({'source':source.relative_to(ROOT).as_posix(),'archive':target.name,'bytes':target.stat().st_size,'sha256':sha(target)})
for name in ('prepare_xor_chroma_profile.py','run_xor_chroma_profile.py'):
    source=ROOT/'artifacts'/name
    shutil.copyfile(source,DST/name)
    files.append({'source':source.relative_to(ROOT).as_posix(),'archive':name,'bytes':source.stat().st_size,'sha256':sha(source)})
p,r,e,start=map(lambda n:read(DST/n),('protocol.json','results.json','exit.json','execution-start.json'))
assert e['exit_code']==0 and e['results_sha256']==sha(DST/'results.json')
assert r['protocol_sha256']==e['protocol_sha256']==start['protocol_sha256']==sha(DST/'protocol.json')
assert p['script_sha256']==r['script_sha256']==e['script_sha256']==start['script_sha256']==sha(DST/'analyze.py')
assert e['stdout_sha256']==sha(DST/'stdout.log') and e['stderr_sha256']==sha(DST/'stderr.log')
assert not (DST/'stderr.log').read_bytes()
for name in ('analyze.py','prepare_xor_chroma_profile.py','run_xor_chroma_profile.py'):
    ast.parse((DST/name).read_text(encoding='utf-8'))
rows=r['images']
assert len(rows)==100 and [x['image'] for x in rows]==list(range(100))
windows=sum(x['windows'] for x in rows)
assert windows==r['windows']==1228800
old=sum(x['R_low_sum_lines'] for x in rows)
new=sum(x['xor_chroma_sum_lines'] for x in rows)
assert old==60721470
for key,total in [('R_low',old),('xor_chroma',new)]:
    hist=r['hist_unique_lines'][key]
    assert len(hist)==65 and sum(hist)==windows and sum(i*n for i,n in enumerate(hist))==total
for row in rows:
    assert row['ratio']==row['xor_chroma_sum_lines']/row['R_low_sum_lines']
assert r['R_low_mean_unique_lines']==old/windows and r['xor_chroma_mean_unique_lines']==new/windows
assert r['xor_over_R_mean_lines_ratio']==new/old
maximum=max(x['ratio'] for x in rows)
assert maximum==r['maximum_image_ratio']
passed=new/old<=p['gate']['mean_lines_ratio_max'] and maximum<=p['gate']['any_image_lines_ratio_max']
assert passed==r['native_implementation_warranted']==False
assert r['index_colors_checked']==2**24 and r['inverse_mismatches']==r['range_mismatches']==0
assert r['native_calls']==r['performance_calls']==0
for item in r['inputs'].values():assert sha(ROOT/item['path'])==item['sha256']
manifest=read(ROOT/'assets/photos/manifest.json')
assert [x['input_sha256'] for x in rows]==[x['evaluation']['pixel_sha256'] for x in manifest['images']]
save(DST/'manifest.json',{'purpose':'九份原件；复算脚本与回执不进入自身清单','files':files})
save(DST/'audit.json',{'purpose':__doc__,'pass':True,'environment':{'platform':platform.platform(),'python':sys.version},'script_sha256':sha(Path(__file__)),'files':len(files),'windows':windows,'old_lines':old,'new_lines':new,'ratio':new/old,'maximum_image_ratio':maximum,'candidate_gate_passed':passed,'limits':'复算冻结JSON的汇总和哈希；不重新生成照片行集合或遍历16M逆映射；不是RGB8映射或性能验证','native_calls':0,'performance_calls':0})
print(json.dumps({'files':len(files),'audit_pass':True,'candidate_gate_passed':passed,'ratio':new/old},ensure_ascii=False))
