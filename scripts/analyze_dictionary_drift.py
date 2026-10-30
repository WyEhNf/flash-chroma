"""按运行前独立冻结的H1/H2经验判定复算全部诊断调用，不筛样本或恢复资格。"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path);p.add_argument('--freeze',action='store_true');a=p.parse_args();path=ROOT/'experiments/dictionary-drift-analysis-v1.json';parent=ROOT/'experiments/dictionary-drift-diagnostic-v1.json'
    if a.freeze:
        if path.exists():raise FileExistsError(path)
        save(path,dict(purpose=__doc__,source_sha256=sha(__file__),parent_plan_sha256=sha(parent),quantile_method='linear',h1_a_p90_p10_max=1.10,h1_localratio_p90_p10_min=1.25,h2_support_absolute_ratio_difference=0.10,h2_support_same_sign_workers=3,h2_nosupport_all_worker_abs_difference_below=0.05,qualification='只按先前写定阈值做描述性原因检验，不是显著性/因果证明，不赋速度档，不恢复推荐，所有组/核心/调用均纳入。'));print(path,sha(path));return
    import numpy as np
    plan=read(path);parentplan=read(parent)
    if plan['source_sha256']!=sha(__file__) or plan['parent_plan_sha256']!=sha(parent):raise AssertionError('分析规则冻结身份不同')
    if a.input is None:raise ValueError('需要--input')
    results=[];rows_count=0;groups_count=0;hashes=0;effects=[]
    def spread(values):return float(np.quantile(values,.9,method='linear')/np.quantile(values,.1,method='linear'))
    for i in range(4):
        pathworker=a.input/f'worker-{i}/results.json';worker=read(pathworker);rows=worker['rows'];groups=worker['groups']
        if worker['plan_sha256']!=sha(parent) or len(rows)!=128 or len(groups)!=32:raise AssertionError('固定样本不完整')
        local=[]
        for group in groups:
            call=[rows[index] for index in group['rows']]
            if ''.join('A' if row['label']=='ref80' else 'B' for row in call)!=group['sequence']:raise AssertionError('序列身份不符')
            if group['output_sha256']!='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528':raise AssertionError('组末输出SHA不同')
            at=[row['wall_ns'] for row in call if row['label']=='ref80'];bt=[row['wall_ns'] for row in call if row['label']=='avx2_24'];ratio=statistics.median(bt)/statistics.median(at)
            local.append(dict(sequence=group['sequence'],block=group['block'],group=group['group'],a_wall_ns_median=statistics.median(at),b_wall_ns_median=statistics.median(bt),b_over_a=ratio))
        aspread=spread([row['a_wall_ns_median'] for row in local]);rspread=spread([row['b_over_a'] for row in local]);ab=statistics.median(row['b_over_a'] for row in local if row['sequence']=='ABBA');ba=statistics.median(row['b_over_a'] for row in local if row['sequence']=='BAAB');effect=ab/ba;effects.append(effect)
        changed=sum(row['cpu_endpoint_changed'] for row in rows);cpus=sorted({row['cpu_before'] for row in rows}|{row['cpu_after'] for row in rows});shares=[row['cpu_execution_over_wall'] for row in rows]
        results.append(dict(worker_index=i,local_groups=local,h1_a_p90_p10=aspread,h1_localratio_p90_p10=rspread,h1_simple_common_factor_refuted=aspread<=plan['h1_a_p90_p10_max'] and rspread>=plan['h1_localratio_p90_p10_min'],h2_abba_median=ab,h2_baab_median=ba,h2_abba_over_baab=effect,cpu_endpoint_changed_calls=changed,cpu_endpoints_observed=cpus,cpu_share_min=min(shares),cpu_share_median=statistics.median(shares),cpu_share_max=max(shares),affinities=worker['affinities'],raw_result_sha256=sha(pathworker)))
        rows_count+=len(rows);groups_count+=len(groups);hashes+=len(groups)
    positive=sum(value-1>=plan['h2_support_absolute_ratio_difference'] for value in effects);negative=sum(1-value>=plan['h2_support_absolute_ratio_difference'] for value in effects)
    h2='与>=10%同向顺序关联相容，非因果证明' if max(positive,negative)>=plan['h2_support_same_sign_workers'] else ('本场全部偏离<5%，不支持>=10%量级效应' if all(abs(value-1)<plan['h2_nosupport_all_worker_abs_difference_below'] for value in effects) else '证据不足，保留全部原值')
    save(a.input/'summary.json',dict(purpose=__doc__,analysis_plan_sha256=sha(path),measurement_plan_sha256=sha(parent),workers=results,call_count=rows_count,group_count=groups_count,output_hash_count=hashes,h2_effects=effects,h2_result=h2,scope=plan['qualification'],not_claimed='H3/H4只列原始CPU时间/周期/壁钟和端点/affinity，不将周期换频率，不将端点相同解释为无迁移。'))
    print(a.input/'summary.json',h2)
if __name__=='__main__':main()
