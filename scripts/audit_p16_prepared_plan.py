"""只读复算89显式owner原始轮次、容量和纯映射门槛，不加载DLL。"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics as st
import zipfile

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);a=p.parse_args()
    z=zipfile.ZipFile(a.source) if a.source.is_file() else None
    raw=lambda n:z.read(n) if z else (a.source/n).read_bytes()
    read=lambda n:json.loads(raw(n).decode('utf-8'))
    plan=read('executed-plan.json');proof=read('correctness.json');full=read('runtime/correctness.json');r=read('results.json')
    assert proof['passed'] and full['passed'] and full['full_colors']==1<<24 and full['full_byte_mismatches']==0
    assert hashlib.sha256(raw('runtime/correctness.json')).hexdigest()==proof['runtime_proof_sha256']
    assert full['output_sha256']==proof['runtime_output_sha256'] and len(set(full['output_sha256'].values()))==1
    workers=[read(f'worker{i}.json') for i in range(4)]
    assert r['worker_sha256']==[hashlib.sha256(raw(f'worker{i}.json')).hexdigest() for i in range(4)]
    for w in workers:
        assert len(w['lifecycle'])==18 and len(w['mapping'])==4
        assert w['environment']['affinity']==plan['cpus']
        assert w['source_sha256']=='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'
        assert {r['output_sha256'] for r in w['mapping']}=={'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'}
        for row in w['lifecycle']:
            n=row['owners'];candidate=row['variant']=='candidate'
            assert row['unique_handles']==(1 if candidate else n)
            assert row['owner_count']==(n if candidate else None)
            assert row['unique_capacity_bytes']==(18579220 if candidate else 18579204*n)
    controls=[]
    for row in r['mapping']:
        pairs=[{v:next(x for x in w['mapping'] if x['variant']==v and x['threads']==row['threads']) for v in ('baseline','candidate')} for w in workers]
        for pair in pairs:
            for v in ('baseline','candidate'):
                controls.extend((st.median(pair[v]['control'])/st.median(pair[v]['apply']),st.median(pair[v]['control_outplace'])/st.median(pair[v]['outplace'])))
        for metric in ('apply','outplace'):
            ratios=[st.median(p['candidate'][metric])/st.median(p['baseline'][metric]) for p in pairs]
            assert ratios==row[metric]['ratios'] and st.median(ratios)==row[metric]['median_ratio']
            assert row[metric]['worst_retained']==1/max(ratios)
    valid=all(plan['control_min']<=v<=plan['control_max'] for v in controls)
    assert controls==r['controls'] and valid==r['control_valid']
    for row in r['mapping']:
        for metric in ('apply','outplace'):
            assert row[metric]['grades']=={str(g):valid and row[metric]['worst_retained']>=g/100 for g in plan['grades']}
    for row in r['lifecycle']:
        n=row['owners'];pairs=[{v:[x for x in w['lifecycle'] if x['owners']==n and x['variant']==v] for v in ('baseline','candidate')} for w in workers]
        assert all(len(p[v])==3 for p in pairs for v in p)
        ratios=[st.median(x['construct_wall_seconds'] for x in p['candidate'])/st.median(x['construct_wall_seconds'] for x in p['baseline']) for p in pairs]
        assert ratios==row['construct_ratios'] and st.median(ratios)==row['median_ratio'] and row['worst_retained']==1/max(ratios)
        assert row['capacity_bytes']=={v:sorted({x['unique_capacity_bytes'] for p in pairs for x in p[v]}) for v in ('baseline','candidate')}
    gate=plan['interpretation_gate'];no_obvious=valid and all(row[k]['median_ratio']<=gate['pure_mapping_median_time_ratio_max'] and max(row[k]['ratios'])<=gate['pure_mapping_any_process_time_ratio_max'] for row in r['mapping'] for k in ('apply','outplace'))
    memory=read('memory-summary.json')
    for row in memory['summary']:
        n=row['owners'];ratios=[];deltas=[]
        for i,w in enumerate(workers):
            variants=row['workers'][i]['variants']
            for v in ('baseline','candidate'):
                rawrows=[x for x in w['lifecycle'] if x['owners']==n and x['variant']==v]
                assert variants[v]['rss_before']==[x['memory_before']['rss'] for x in rawrows]
                assert variants[v]['rss_after']==[x['memory_after_construct']['rss'] for x in rawrows]
                assert variants[v]['rss_destroyed']==[x['memory_after_destroy']['rss'] for x in rawrows]
                assert variants[v]['rss_delta']==[x['memory_after_construct']['rss']-x['memory_before']['rss'] for x in rawrows]
                assert variants[v]['private_after']==[x['memory_after_construct'].get('private') for x in rawrows]
            ratios.append(st.median(variants['candidate']['rss_after'])/st.median(variants['baseline']['rss_after']))
            deltas.append(st.median(variants['candidate']['rss_delta'])/st.median(variants['baseline']['rss_delta']))
        assert row['median_rss_after_ratio']==st.median(ratios) and row['median_rss_delta_ratio']==st.median(deltas)
        for variant in ('baseline','candidate'):
            assert row['median_rss_after_bytes'][variant]==st.median(st.median(w['variants'][variant]['rss_after']) for w in row['workers'])
            assert row['median_rss_delta_bytes'][variant]==st.median(st.median(w['variants'][variant]['rss_delta']) for w in row['workers'])
    if z:z.close()
    print(json.dumps({'runtime_full_colors':1<<24,'lifecycle_records':72,'mapping_records':16,'controls':len(controls),
        'control_valid':valid,'all_mapping_meet_50':all(row[k]['grades']['50'] for row in r['mapping'] for k in ('apply','outplace')),
        'no_obvious_mapping_regression':no_obvious,'raw_statistics_recomputed':True,'rss_samples_recomputed':True},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
