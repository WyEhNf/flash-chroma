"""静态核对全部512调用、固定序列/地址、线程计数及预冻结H1/H2统计。"""
import hashlib
import io
import json
from pathlib import Path
import statistics
import subprocess
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def main():
    prefix='report/data/p16-dictionary-drift-diagnostic-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('未暂存：'+name)
        raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;expected=manifest['files'].get(path.name)
        if raw!=path.read_bytes() or (expected and (len(raw)!=expected['bytes'] or sha(raw)!=expected['sha256'])):raise AssertionError('原字节改变')
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if z.testzip():raise AssertionError('ZIP CRC失败')
                members+=len(z.infolist())
    parent=ROOT/'experiments/dictionary-drift-diagnostic-v1.json';apath=ROOT/'experiments/dictionary-drift-analysis-v1.json';plan=read(parent);analysis=read(apath);summary=read(directory/'diagnosis.json')
    if analysis['parent_plan_sha256']!=sha(parent.read_bytes()) or summary['measurement_plan_sha256']!=sha(parent.read_bytes()) or summary['analysis_plan_sha256']!=sha(apath.read_bytes()):raise AssertionError('预冻结计划不符')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('实际源不同')
        if sha(z.read('scripts/analyze_dictionary_drift.py'))!=analysis['source_sha256']:raise AssertionError('分析源不同')
    count=0;groups=0;changed=0;effects=[]
    with zipfile.ZipFile(directory/'raw-observations.zip') as z:
        for i in range(4):
            raw=z.read(f'worker-{i}/results.json');worker=json.loads(raw);rows=worker['rows'];grows=worker['groups'];published=summary['workers'][i]
            if sha(raw)!=published['raw_result_sha256'] or len(rows)!=128 or len(grows)!=32:raise AssertionError('样本总数或原件不同')
            seqs=['ABBA','BAAB'] if i%2==0 else ['BAAB','ABBA']
            if worker['sequences']!=seqs:raise AssertionError('序列块次序改变')
            for label,record in worker['identities'].items():
                expected=plan['role_identities'][label]
                if record['sha256']!=expected['library_sha256'] or record['capacity']!=expected['capacity']:raise AssertionError('驻留二进制或容量改变')
            ioaddr=rows[0]['actual_input_addr'];srcaddr=rows[0]['immutable_source_addr'];local=[]
            for j,row in enumerate(rows):
                sequence=seqs[j//64];symbol=sequence[j%4]
                if row['index']!=j or row['label']!=plan['timed_roles'][symbol] or row['sequence']!=sequence or row['position']!=j%4 or row['group']!=(j//4)%16 or row['block']!=j//64:raise AssertionError('调用缺失/新增或次序改变')
                if row['actual_input_addr']!=ioaddr or row['actual_output_addr']!=ioaddr or row['immutable_source_addr']!=srcaddr:raise AssertionError('实际输入输出地址发生改变')
                if row['cpu_endpoint_changed']!=(row['cpu_before']!=row['cpu_after']):raise AssertionError('迁移端点标记不同')
                share=(row['kernel_ticks100ns']+row['user_ticks100ns'])*100/row['wall_ns']
                if share!=row['cpu_execution_over_wall']:raise AssertionError('线程CPU占比不同')
            for j,group in enumerate(grows):
                if group['rows']!=list(range(4*j,4*j+4)) or group['output_sha256']!='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528':raise AssertionError('组末SHA或调用映射不同')
                calls=rows[4*j:4*j+4];at=statistics.median(row['wall_ns'] for row in calls if row['label']=='ref80');bt=statistics.median(row['wall_ns'] for row in calls if row['label']=='avx2_24');local.append(dict(sequence=group['sequence'],block=group['block'],group=group['group'],a_wall_ns_median=at,b_wall_ns_median=bt,b_over_a=bt/at))
            if local!=published['local_groups']:raise AssertionError('局部全部组统计不同')
            def spread(values):return float(np.quantile(values,.9,method='linear')/np.quantile(values,.1,method='linear'))
            asp=spread([row['a_wall_ns_median'] for row in local]);rsp=spread([row['b_over_a'] for row in local]);refute=asp<=1.10 and rsp>=1.25;effect=statistics.median(row['b_over_a'] for row in local if row['sequence']=='ABBA')/statistics.median(row['b_over_a'] for row in local if row['sequence']=='BAAB')
            if asp!=published['h1_a_p90_p10'] or rsp!=published['h1_localratio_p90_p10'] or refute!=published['h1_simple_common_factor_refuted'] or effect!=published['h2_abba_over_baab']:raise AssertionError('预冻结H1/H2复算不同')
            moved=sum(row['cpu_endpoint_changed'] for row in rows)
            if moved!=published['cpu_endpoint_changed_calls'] or worker['affinities']!=published['affinities']:raise AssertionError('CPU/affinity记录不同')
            effects.append(effect);count+=len(rows);groups+=len(grows);changed+=moved
    positive=sum(value-1>=.10 for value in effects);negative=sum(1-value>=.10 for value in effects);h2='与>=10%同向顺序关联相容，非因果证明' if max(positive,negative)>=3 else ('本场全部偏离<5%，不支持>=10%量级效应' if all(abs(value-1)<.05 for value in effects) else '证据不足，保留全部原值')
    if effects!=summary['h2_effects'] or h2!=summary['h2_result'] or count!=summary['call_count'] or groups!=summary['group_count'] or groups!=summary['output_hash_count']:raise AssertionError('全量计数或H2判定不同')
    result=dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,calls=count,groups=groups,hashes=groups,cpu_endpoint_changed_calls=changed,h2_result=h2,scope='全部样本/地址/affinity/计数及预冻结规则静态复算；不重跑候选、不恢复速度资格。');(directory/'git-byte-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
