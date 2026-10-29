"""仅用标准库核对精简归档、直方图、全部计时和实测源码身份。"""
from pathlib import Path
from collections import Counter
import ast
import hashlib
import json
import math
import re
import statistics
import zipfile

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'report/official-pr95-20261029'
E=REPORT/'evidence'
manifest=json.loads((E/'archive-manifest.json').read_text(encoding='utf-8'))
for item in manifest['files']:
    p=ROOT/item['path']
    assert p.stat().st_size==item['bytes'], item['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'], item['path']
for p in Path(__file__).parent.glob('*.py'):
    ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
summary=json.loads((E/'summary.json').read_text(encoding='utf-8'))
old=json.loads((E/'summary-unpinned.json').read_text(encoding='utf-8'))
hist=json.loads((E/'pixel-error-histograms.json').read_text())
source=json.loads((E/'input-manifest.json').read_text(encoding='utf-8'))
def equal(a,b): assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-9),(a,b)
def quality(h):
    n=sum(h.values()); target=math.ceil(.99*n);acc=0;p99=None
    for sq,count in sorted(h.items()):
        assert isinstance(sq,int) and 0<=sq<=195075 and count>0
        acc+=count
        if p99 is None and acc>=target:p99=math.sqrt(sq)
    return {'pixels':n,'mean':math.fsum(math.sqrt(sq)*count for sq,count in h.items())/n,'p99':p99,'max':math.sqrt(max(h))}
for m in ('17','33'):
    group=summary['sets'][m];pooled=Counter()
    for row in group['photos']:
        one=Counter(dict(hist[m][str(row['image'])]));pooled.update(one)
        assert sum(one.values())==1024*768
        for k,v in quality(one).items():equal(v,row[k])
        assert row['independent_numpy_equal'] is True
    for k,v in quality(pooled).items():equal(v,group['quality'][k])
    for filename,data in [('extended-pinned.log',summary),('extended.log',old)]:
        log=(E/f'm{m}'/filename).read_text()
        assert log.rstrip().endswith('COMPLETED=1')
        assert len(re.findall(r'^CONFIG .*full_domain_equal=1$',log,re.M))==4
        assert len(re.findall(r'^NOT_APPLICABLE .*status=10 ',log,re.M))==4
        assert 'FULL_DOMAIN_C99 pixels=16777216' in log
        for conf in data['sets'][m]['configs']:
            b,r=conf['backend'],conf['rep']
            samples=[float(t) for t in re.findall(rf'^BATCH cycle=\d+ backend={b} rep={r} ms=([\d.]+)$',log,re.M)]
            assert len(samples)==9 and samples==conf['batch_samples_ms']
            equal(statistics.median(samples),conf['batch_median_ms'])
            equal(statistics.median(samples)/4,conf['per_image_average_ms'])
            for i,row in enumerate(group['photos'],1):
                match=re.search(rf'^QUALITY backend={b} rep={r} image={i} mean=([\d.]+) p99=([\d.]+) max=([\d.]+) mismatch=0$',log,re.M)
                assert match
                for key,val in zip(('mean','p99','max'),match.groups()):equal(float(val),row[key])
    official=(E/f'm{m}/official.log').read_text()
    means=re.findall(r'/image/\d+\.bin TimeCost: [\d.]+, Delta: [\d.]+ ([\d.]+)',official)
    assert len(means)==4
    for logged,row in zip(means,group['photos']): assert abs(float(logged)-row['mean'])<.0000006
with zipfile.ZipFile(E/'executed-sources.zip') as z:
    assert z.testzip() is None
    assert hashlib.sha256(z.read('generated/official_adapter.cpp')).hexdigest()==source['generated_sha256']
    for name in z.namelist():
        if name.startswith('code/'):
            assert z.read(name)==(ROOT/'code/official-pr95-20261029'/Path(name).name).read_bytes()
    for member,original in [('official/Readme.md','test/Readme.md'),('official/C++/main.cpp','test/C++/main.cpp')]:
        item=next(x for x in source['files'] if x['path'].replace('\\','/')==original)
        assert hashlib.sha256(z.read(member)).hexdigest()==item['sha256']
for receipt in ('run-receipt.json','run-pinned-receipt.json'):
    data=json.loads((E/receipt).read_text(encoding='utf-8'))
    assert data['completed'] and all(x['returncode']==0 for x in data['runs'])
    if 'pinned' in receipt:assert all(x['actual_child_affinity']==[0] for x in data['runs'])
print(json.dumps({'归档文件数':len(manifest['files']),'照片误差直方图':8,'合并指标组':2,'热批次原始计时':144,'源码身份':'一致','官方均值复算':'通过','归档验证':'通过'},ensure_ascii=False))
