"""派生80归档及独立原始数组复算入口；测试结束后才另行执行。"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'report/data/skylake-pair48-v1/archive.py'
text=source.read_text(encoding='utf-8')
text=text.replace("('prepare_pair48_checks.py','prepare_pair48_perf_glue.py')","('prepare_andn_normal_checks.py',)")
text=text.replace('归档79','归档80').replace('skylake-pair48','skylake-andn-normal').replace('pair48','andn_normal')
needle="assert full['pass'] and full['andn_normal_enabled']=={'single':0,'chain':1}"
assert text.count(needle)==1
text=text.replace(needle,needle+"\n    assert full['normal_inplace_alignment_comparisons']==64 and full['normal_inplace_actual_offsets']==list(range(64))")
target=ROOT/'report/data/skylake-andn-normal-v1'
target.mkdir(exist_ok=False)
with (target/'archive.py').open('x',encoding='utf-8') as stream:
    stream.write(text)
