"""99只从冻结raw统计生成完整门槛索引，不重测或排除失效/负例。"""
import argparse
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path)
    a=p.parse_args();out=a.source/'threshold-summary.json'
    if out.exists():raise FileExistsError('99门槛索引不覆盖')
    result=json.loads((a.source/'results.json').read_text(encoding='utf-8'))
    rows=[]
    for row in result['hot']:
        rows.append({**{k:row[k] for k in ('denominator','model','images','threads','boundary')},
            **{k:row[k] for k in ('control_valid','median_time_ratio','worst_throughput_retained','grades','no_obvious_slowdown')}})
    for row in result['cold']:
        for name,value in row['metrics'].items():
            rows.append({**{k:row[k] for k in ('denominator','model','images')},'boundary':name,
                **{k:value[k] for k in ('control_valid','median_time_ratio','worst_throughput_retained','grades','no_obvious_slowdown')}})
    summary={}
    for denominator in ('reference','previous','isolated'):
        own=[r for r in rows if r['denominator']==denominator]
        valid=[r for r in own if r['control_valid']]
        summary[denominator]={'total_hot_and_cold_metrics':len(own),'control_valid':len(valid),
            'valid_below50':[r for r in valid if r['worst_throughput_retained']<.5],
            'worst_valid_throughput_retained':min((r['worst_throughput_retained'] for r in valid),default=None),
            'no_obvious_count':sum(r['no_obvious_slowdown'] for r in own),
            'all_scene50_proven':all(r['grades']['50'] for r in own)}
    value={'denominators':summary,'all_rows':rows,'scope':'全部126统计保留；失效不授档。N100 direct控制不能当B2布局收益，未测N86不授性能档。'}
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'summary':summary,'ordinary_N1_N10_vs97':[r for r in rows if r['denominator']=='isolated' and r['model']=='ordinary' and r['images'] in (1,10)]},ensure_ascii=False))


if __name__=='__main__':main()
