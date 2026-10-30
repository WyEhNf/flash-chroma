"""仅验证发布完整性与重算统计，不执行数值内核或性能测试。"""
from pathlib import Path
import ast,hashlib,json,statistics,zipfile,sys,platform

ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def close(a,b):assert abs(a-b)<1e-10,(a,b)
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf8'))
for name,h in manifest['files'].items():assert sha((ROOT/name).read_bytes())==h,name
members=json.loads((ROOT/'members.json').read_text(encoding='utf8'))
with zipfile.ZipFile(ROOT/'evidence.zip') as z:
 assert set(z.namelist())==set(members)
 for name,record in members.items():
  b=z.read(name);assert len(b)==record['bytes'] and sha(b)==record['sha256'],name
  if name.endswith('.py'):ast.parse(b.decode('utf8'))
 for experiment in ['20261023','20261023-hoisted']:
  def read(name):return json.loads(z.read(experiment+'/'+name))
  plan=read('plan.json');lock=read('run-lock.json');v=read('verification.json');summary=read('summary.json')
  for name,h in lock['files'].items():assert sha(z.read(experiment+'/'+name))==h,name
  assert v['complete'] and v['baseline_ast_identical'] and v['inputs_unchanged']
  assert len(v['cases'])==len(summary['rows'])==len(plan['cases'])==6
  workers=[read(f'worker-{i}.json') for i in [0,1]]
  controls=[]
  for w in workers:
   assert w['complete'] and w['inputs_unchanged'] and len(w['cases'])==6
   assert w['plan_sha256']==v['plan_sha256']==sha(z.read(experiment+'/plan.json'))
   assert w['input_sha256']==v['input_sha256']
   ratios=[]
   for pair in w['control']['pairs']:
    a,b=pair['values']['A'],pair['values']['B']
    assert a['output_sha256']==b['output_sha256']
    close(pair['ratio'],b['seconds']/a['seconds']);ratios.append(pair['ratio'])
   close(w['control']['median_ratio'],statistics.median(ratios))
   ok=.95<=statistics.median(ratios)<=1.05 and all(.90<=r<=1.10 for r in ratios)
   assert ok==w['control']['valid'];controls.append(ok)
  assert summary['control_valid']==all(controls)
  for s in summary['rows']:
   key=(s['recipe'],s['m'])
   verification=next(c for c in v['cases'] if (c['recipe'],c['m'])==key)
   assert verification['full_cube_pixels']==256**3 and verification['full_cube_mismatches']==0
   assert verification['baseline_cube_sha256']==verification['candidate_cube_sha256']
   cases=[next(c for c in w['cases'] if (c['recipe'],c['m'])==key) for w in workers]
   pairs=[p for c in cases for p in c['pairs']];assert len(pairs)==6
   for p in pairs:
    values=p['values'];assert all(r['output_sha256']==verification['photos_output_sha256'] for r in values.values())
    close(p['ratio'],values['candidate']['seconds']/values['baseline']['seconds'])
    for r in values.values():close(r['ms_per_image'],r['seconds']*10)
   ratios=[p['ratio'] for p in pairs];medians=[statistics.median(p['ratio'] for p in c['pairs']) for c in cases]
   close(s['paired_median_ratio'],statistics.median(ratios))
   close(s['time_reduction_percent'],100*(1-statistics.median(ratios)))
   close(s['speedup'],1/statistics.median(ratios))
   for role in ['baseline','candidate']:close(s[role+'_ms'],statistics.median(p['values'][role]['ms_per_image'] for p in pairs))
   passed=all(controls) and all(r<=.95 for r in medians) and max(ratios)<=1.02
   if experiment.endswith('hoisted'):
    for p in pairs:close(p['intermediate_ratio'],p['values']['candidate']['seconds']/p['values']['intermediate']['seconds'])
    extra=[p['intermediate_ratio'] for p in pairs]
    close(s['candidate_vs_intermediate_ratio'],statistics.median(extra))
    passed=passed and all(statistics.median(p['intermediate_ratio'] for p in c['pairs'])<=.95 for c in cases) and max(extra)<=1.02
   assert bool(passed)==s['gate_pass'],key
  assert summary['all_cases_pass']==all(s['gate_pass'] for s in summary['rows'])
  print(experiment,'通过：归档身份、完整域证据、逐轮SHA、配对统计及门槛复算')
 for name in ['kernels.py','study.py','run.py','report.py']:
  assert (ROOT/'code'/name).read_bytes()==z.read('20261023-hoisted/code/'+name),name
for p in (ROOT/'code').glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
print('发布静态检查通过；未重跑精度或性能。环境：',platform.platform(),sys.version.split()[0])
