"""只读复算同87调用边界探针的所有场景和失败控制，不追加计时。"""
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
    plan=read('executed-plan.json');proof=read('correctness.json');r=read('results.json')
    assert proof['passed'] and proof['finite_cases']==56 and proof['rejection_cases']==17 and len(proof['photos'])==9
    assert proof['library']==plan['library'] and proof['probe']==plan['probe']
    workers=[read(f'worker{i}.json') for i in range(4)]
    assert r['worker_sha256']==[hashlib.sha256(raw(f'worker{i}.json')).hexdigest() for i in range(4)]
    for w in workers:assert len(w['records'])==36 and w['environment']['affinity']==plan['cpus']
    expected={(x['role'],x['scale'],x['images']):x['output_sha256'] for x in proof['photos']}
    assert expected['direct',1,100]=='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
    assert proof['state']['direct']['direct']['enabled'] and not proof['state']['fallback']['direct']['enabled']
    for w in workers:
        for x in w['records']:
            assert len(x['seconds'])==len(x['control'])==plan['repeats'][str(x['images'])]
            assert x['output_sha256']==expected[x['role'],x['scale'],x['images']]
    for row in r['summary']:
        ratios=[];controls=[];sources=set()
        for w in workers:
            pair={x['mode']:x for x in w['records'] if (x['role'],x['scale'],x['images'],x['threads'])==(row['role'],row['scale'],row['images'],row['threads'])}
            assert len(pair)==2
            ratios.append(st.median(pair[0]['seconds'])/st.median(pair[1]['seconds']))
            controls.extend(st.median(pair[m]['control'])/st.median(pair[m]['seconds']) for m in (0,1))
            sources.update(x['source_sha256'] for x in pair.values())
        assert len(sources)==1 and row['bulk_over_loop_ratios']==ratios and row['controls']==controls
        assert row['median_ratio']==st.median(ratios) and row['worst_retained']==1/max(ratios)
        valid=all(plan['control_min']<=v<=plan['control_max'] for v in controls);assert row['control_valid']==valid
        assert row['grades']=={str(g):valid and 1/max(ratios)>=g/100 for g in plan['grades']}
    assert len(r['summary'])==18
    if z:z.close()
    print(json.dumps({'raw_records':144,'scenarios':18,'control_valid_scenarios':sum(row['control_valid'] for row in r['summary']),
        'control_invalid_scenarios':sum(not row['control_valid'] for row in r['summary']),
        'all_pair_statistics_recomputed':True,'new_batch_api_implemented':False,'pure_fork_join_cost_measured':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
