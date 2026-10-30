"""100离线展开全部126冷热门与实际RSS，不删除失效/最劣轮。"""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'artifacts/p16-scanline-prepare-performance-v1'
output=folder/'summary.json'
if output.exists():raise FileExistsError('100离线汇总不覆盖')
result=json.loads((folder/'results.json').read_text(encoding='utf-8'))
rows=[]
for row in result['hot']:
    rows.append({**row,'metric':'hot_'+row['boundary'],'kind':'hot'})
for row in result['cold']:
    for metric,value in row['metrics'].items():
        rows.append({**value,**{k:v for k,v in row.items() if k!='metrics'},'metric':metric,'kind':'cold','threads':4})
assert len(rows)==126
summary={'scope':'全部126统计集、原AA和最劣保留；无新增native或计时','denominators':{}}
for denominator in ('reference','previous','isolated'):
    selected=[row for row in rows if row['denominator']==denominator]
    valid=[row for row in selected if row['control_valid']]
    worst=min(valid,key=lambda r:r['worst_throughput_retained']) if valid else None
    summary['denominators'][denominator]={'sets':len(selected),'aa_valid':len(valid),'aa_invalid':len(selected)-len(valid),
        'valid_below50':sum(r['worst_throughput_retained']<.5 for r in valid),
        'no_obvious_count':sum(r['no_obvious_slowdown'] for r in selected),
        'all_scope_grades':{str(g):all(r['grades'][str(g)] for r in selected) for g in (100,90,80,70,60,50)},
        'grades_valid_count':{str(g):sum(r['grades'][str(g)] for r in selected) for g in (100,90,80,70,60,50)},
        'worst_valid':worst,
        'target_prepare_wall':[r for r in selected if r['kind']=='cold' and r['metric'] in ('prepare_seconds','create_to_first_wall_seconds')],
        'valid_no_obvious':[r for r in selected if r['no_obvious_slowdown']]}
rss=[]
for path in sorted(folder.glob('rss-*.json')):
    data=json.loads(path.read_text(encoding='utf-8'))
    rss.append({'model':data['model'],'role':data['role'],'images':data['images'],'rss_delta_bytes':data['rss_delta_bytes'],
        'after_rss':data['after']['rss'],'peak_wset':data['after'].get('peak_wset'),'model_bytes':data['state']['model_bytes']})
assert len(rss)==16
summary['rss']=rss
summary['rows']=rows
output.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (folder/'all-grades.csv').open('w',encoding='utf-8',newline='') as stream:
    fields=['denominator','model','images','kind','metric','threads','control_valid','median_time_ratio','worst_throughput_retained','no_obvious_slowdown']+[f'grade{g}' for g in (100,90,80,70,60,50)]
    writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
    for row in rows:
        writer.writerow({**{name:row.get(name) for name in fields if not name.startswith('grade')},
            **{f'grade{g}':row['grades'][str(g)] for g in (100,90,80,70,60,50)}})
for denominator,data in summary['denominators'].items():
    print(json.dumps({'denominator':denominator,**{k:v for k,v in data.items() if k not in ('target_prepare_wall','valid_no_obvious','worst_valid')},
        'worst_valid':{k:data['worst_valid'][k] for k in ('model','images','metric','median_time_ratio','worst_throughput_retained')} if data['worst_valid'] else None},ensure_ascii=False))
    for row in data['target_prepare_wall']:
        print(json.dumps({k:row[k] for k in ('denominator','model','images','metric','control_valid','median_time_ratio','worst_throughput_retained','no_obvious_slowdown')},ensure_ascii=False))
print(json.dumps({'rss':rss},ensure_ascii=False))
