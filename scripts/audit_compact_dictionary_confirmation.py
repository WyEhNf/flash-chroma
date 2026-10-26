"""静态重算八worker最劣门禁及确认归档原字节，不重跑性能。"""
import hashlib
import io
import json
from pathlib import Path
import statistics
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    prefix='report/data/p16-compact-dictionary-confirm-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+n for n in manifest['files']];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+n for n in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('未暂存：'+name)
        blob=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;expected=manifest['files'][path.name]
        if blob!=path.read_bytes() or len(blob)!=expected['bytes'] or sha(blob)!=expected['sha256']:raise AssertionError('原字节不一致：'+name)
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                if z.testzip():raise AssertionError('CRC失败：'+name)
                members+=len(z.infolist())
    first=read(directory/'first-performance.json');second=read(directory/'second-performance.json');combined=read(directory/'combined.json')
    for row in combined['rows']:
        key=(row['label'],row['mode'],row['threads']);a=next(x for x in first['ratios'] if (x['label'],x['mode'],x['threads'])==key);b=next(x for x in second['ratios'] if (x['label'],x['mode'],x['threads'])==key);raw=a['per_worker']+b['per_worker'];control_key=row['mode']+'_'+str(row['threads']);controls=[first['controls'][control_key],second['controls'][control_key]]
        if raw!=row['all_eight_workers'] or min(raw)!=row['worst_raw'] or statistics.median(raw)!=row['median_raw']:raise AssertionError('八worker聚合不同')
        for threshold,value in row['stable_tiers'].items():
            if bool(all(x['pass_'] for x in controls) and min(raw)>=int(threshold)/100)!=value:raise AssertionError('门槛重算不同')
    plan=read(ROOT/'experiments/compact-dictionary-confirm-v2.json')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('实际v2源码不同')
    failed=read(directory/'failed-preflight-v1.json')
    if any(failed[n] for n in ('started_workers','timing_samples','aa_samples')):raise AssertionError('v1技术失败被混入测量')
    result=dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,rows=len(combined['rows']),stable_3byte_global_50=combined['stable_3byte_global_50'],scope='仅静态复算与Git原字节核对；首轮及确认数据均未修改。')
    (directory/'git-byte-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
