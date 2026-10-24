"""独立复算16组直方图/逐图六档/T、双DLL完整流与外域下界见证。"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];CACHE=Path('F:/Hackathon/projects/16-lut-color');sys.path.insert(0,str(ROOT/'python'))
from audit_cinema_max48_quality import metrics


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖完整双DLL独立质量复核')
    folder=ROOT/'artifacts/cinema-current-full-quality-v2';frozen_path=ROOT/'artifacts/cinema-current-full-quality-frozen-v2.json'
    frozen=read(frozen_path);result=read(folder/'results.json');identity=read(folder/'identity.json')
    assert frozen['ast_pass'] and identity['frozen_sha256']==sha(frozen_path) and identity['source_sha256']==frozen['source_sha256']
    for n,expected in frozen['source_sha256'].items():assert sha(ROOT/n)==expected,n
    for n,expected in frozen['input_sha256'].items():assert sha(n)==expected,n
    import numpy as np
    from lutlab import channel_hotspot_support as hs,channel_coordinates as cc,io
    from run_channel_tail_nodes import load_model
    from verify_channel_coordinates import integer_oracle
    with np.load(folder/'histograms.npz') as data:new={n:data[n] for n in data.files}
    with np.load(ROOT/'artifacts/cinema-max48-pareto-quality-v1/histograms.npz') as data:old={n:data[n] for n in data.files}
    roles=('a399','best','current741','candidate');names=('mean','rms','p99','max','cvar_1pct');groups=0
    for scope,values in (('cube',result['cube']),('photos',result['photos']),('training60',result['training60']),('standalone_first',result['standalone_first_vs_original_table1'])):
        for role in roles:
            key=scope+'_'+role
            hist=new[key] if key in new else old[scope+'_'+frozen['roles'][role]['prior_role']]
            observed=metrics(hist)
            for n,v in observed.items():assert abs(values[role][n]-v)<=1e-12,(scope,role,n)
            groups+=1
    expected=sha(folder/'candidate.rgb');assert result['candidate_oracle_sha256']==expected
    assert result['reference_payload_sha256']=='493c9084a90186a15ec42cd4553e02ee6b915f9ee4511d77cb2b40adcb82f0a9'
    assert result['full_native_configs']==12 and result['whole4t_streams']==4 and result['actual_photo_configs']==400 and result['mismatches']==0
    for library,values in result['native_full_stream_sha256'].items():assert library in ('87','292') and len(values)==6 and set(values.values())=={expected}
    assert len(result['whole4t'])==4 and len(result['read_only_team_snapshots'])==8
    for row in result['whole4t']:
        assert row['pixels']==1<<24 and row['blocks']==256 and row['sha256']==expected and row['mismatches']==0 and len(set(row['surrounding_team_os_tids']))==4
    for row in result['read_only_team_snapshots']:
        assert row['action']==0 and len(row['records'])==4
        assert all(v['team_size']==4 and v['omp_tid']==i and v['set_attempted']==0 for i,v in enumerate(row['records']))
    assert result['native_inner_tid_instrumentation'] is False and len(result['unique_libgomp'])==1
    photo_map={r['image']:r for r in result['photos']['candidate']['per_image']};assert len(photo_map)==100 and len(result['photo_matrix'])==400
    for row in result['photo_matrix']:assert row['sha256']==photo_map[row['image']]['prediction_sha256'] and row['mismatches']==0
    assert len(result['native_100photos_sha256'])==4 and len(set(result['native_100photos_sha256'].values()))==1
    comparisons=0
    for base in ('a399','best','current741'):
        changes={n:{k:0 for k in ('好','平','差')} for n in names};worst=100.
        for scope in ('cube','photos','training60'):
            a,b=result[scope][base],result[scope]['candidate'];item=result['pairs'][base][scope];ratios=[]
            for n in names:
                ratio=100. if b[n]==0 else min(100.,a[n]/b[n]*100) if a[n] else 0.
                assert abs(item['metrics'][n]['retained_percent']-ratio)<=1e-12;ratios.append(ratio)
            assert abs(item['minimum_retained_percent']-min(ratios))<=1e-12
        for before,after,row in zip(result['photos'][base]['per_image'],result['photos']['candidate']['per_image'],result['pairs'][base]['per_image']):
            assert before['image']==after['image']==row['image'];ratios=[]
            for n in names:
                label='平' if abs(after[n]-before[n])<=1e-12 else '好' if after[n]<before[n] else '差';changes[n][label]+=1
                ratio=100. if after[n]==0 else min(100.,before[n]/after[n]*100) if before[n] else 0.
                assert row['metrics'][n]['change']==label and abs(row['metrics'][n]['retained_percent']-ratio)<=1e-12;ratios.append(ratio)
            minimum=min(ratios);assert abs(row['minimum_retained_percent']-minimum)<=1e-12
            assert row['tiers_pass']=={str(t):minimum+1e-12>=t for t in (100,90,80,70,60,50)};worst=min(worst,minimum);comparisons+=1
        assert changes==result['pairs'][base]['per_metric_changes'] and abs(worst-result['pairs'][base]['worst_image_retained_percent'])<=1e-12
    for role in roles:
        for t in (4,5,6,7,7.5,7.7,8,8.2):assert result['nonofficial_strict_max_T_counts'][role][str(t)]==sum(r['max']<t for r in result['photos'][role]['per_image'])
    passed=all(result[scope]['candidate'][n]<=result[scope]['best'][n]+1e-12 for scope in ('cube','photos','training60') for n in ('mean','p99','max'))
    assert passed==result['mean_p99_max_against_best_aggregates'] and not result['overall_upgrade']
    witness=result['outside41_witness'];key=witness['source_key'];point=np.array([witness['source_rgb']],np.uint8);assert int(hs.key(point)[0])==key
    with np.load(ROOT/'artifacts/cinema-max48-risk-upper-v1/screen.npz') as data:selected,keys=data['selected_nodes'],data['keys']
    assert key not in set(int(v) for v in keys)
    model=load_model(ROOT/frozen['plan']['候选目录']/'model.npz');i,w=hs.corners(model,point);assert not np.any(w[np.isin(i,selected)])
    output=point.copy()
    models=[model,*[cc.from_sparse(io.load_sparse(p,competition=True)) for p in frozen['roles']['candidate']['models'][1:]]]
    for stage in models:output=integer_oracle(stage,output)
    truth=point.copy()
    for spec in read(ROOT/'experiments/cinema-current-anchor-v1.json')['tables']:
        table=io.load_full(CACHE/spec['path'],mmap=True).reshape(-1,3);truth=table[hs.key(truth)]
    assert output[0].tolist()==witness['output_rgb'] and truth[0].tolist()==witness['gold_rgb']
    assert sum((int(a)-int(b))**2 for a,b in zip(output[0],truth[0]))==41==witness['squared_error']
    record={'pass':True,'results_sha256':sha(folder/'results.json'),'histograms_sha256':sha(folder/'histograms.npz'),'source_files_checked':len(frozen['source_sha256']),
        'input_files_checked':len(frozen['input_sha256']),'histogram_groups':groups,'per_image_comparisons':comparisons,'full_native_configs':12,
        'whole4t_streams':4,'actual_photo_configs':400,'outside41_witness_verified':True,'mean_p99_max_against_best_aggregates':passed,'overall_upgrade':False,
        'scope':'离线独立复算16直方图/300逐图六档/T与双DLL身份，另独立1点重放下界见证；未补跑完整域或照片/性能。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'groups':groups,'comparisons':comparisons,'outside41_witness':True},flush=True)


if __name__=='__main__':main()
