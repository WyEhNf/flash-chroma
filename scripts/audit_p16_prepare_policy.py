"""只读复算88摊销矩阵，接受原目录或保留原字节的ZIP。"""
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
    plan=read('executed-plan.json');full=read('correctness.json');result=read('results.json')
    assert full['passed'] and full['full_colors']==1<<24 and full['byte_mismatches']==0
    assert len(set(full['output_sha256'].values()))==1 and full['old_create_matches_policy0']
    workers=[read(f'worker{i}.json') for i in range(4)]
    assert result['worker_sha256']==[hashlib.sha256(raw(f'worker{i}.json')).hexdigest() for i in range(4)]
    for w in workers:
        assert len(w['records'])==72
        assert all(r['create_plus_first_seconds']==r['create_seconds']+r['first_outplace_seconds'] for r in w['records'])
    for row in result['summary']:
        scale,n,threads=row['scale'],row['images'],row['threads'];parts=[];controls=[];outputs=set()
        for w in workers:
            subset=[r for r in w['records'] if r['scale']==scale and r['images']==n and r['threads']==threads]
            p={v:[r for r in subset if r['policy']==v] for v in (0,1)}
            assert all(len(p[v])==3 for v in (0,1));outputs.update(r['output_sha256'] for r in subset)
            parts.append({'create_ratio':st.median(r['create_seconds'] for r in p[1])/st.median(r['create_seconds'] for r in p[0]),
                'first_ratio':st.median(r['first_outplace_seconds'] for r in p[1])/st.median(r['first_outplace_seconds'] for r in p[0]),
                'end_to_end_ratio':st.median(r['create_plus_first_seconds'] for r in p[1])/st.median(r['create_plus_first_seconds'] for r in p[0]),
                'steady_ratio':st.median(p[1][0]['steady'])/st.median(p[0][0]['steady'])})
            controls.extend(st.median(p[v][0]['control'])/st.median(p[v][0]['steady']) for v in (0,1))
        assert len(outputs)==1 and row['pairs']==parts and row['controls']==controls
        valid=all(plan['control_min']<=v<=plan['control_max'] for v in controls);assert valid==row['control_valid']
        for metric in ('create','first','end_to_end','steady'):
            ratios=[p[metric+'_ratio'] for p in parts]
            assert row[metric]['median_time_ratio']==st.median(ratios) and row[metric]['worst_throughput_retained']==1/max(ratios)
            assert row[metric]['grades']=={str(v):valid and 1/max(ratios)>=v/100 for v in (100,90,80,70,60,50)}
    assert len(result['summary'])==12
    if z:z.close()
    print(json.dumps({'full_integer_verification':True,'raw_statistics_verified':True,'cold_creates':288,
        'control_valid_cases':sum(r['control_valid'] for r in result['summary']),
        'control_invalid_cases':sum(not r['control_valid'] for r in result['summary']),
        'steady_meets_50_percent_cases':sum(r['steady']['grades']['50'] for r in result['summary']),
        'end_to_end_meets_50_percent_cases':sum(r['end_to_end']['grades']['50'] for r in result['summary'])},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
