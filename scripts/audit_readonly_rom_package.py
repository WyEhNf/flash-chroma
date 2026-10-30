"""RO发布包暂存字节/CRC、三fresh独立提交差和冻结Decimal复算，不新增运行。"""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
from study_memory_rom import ROOT,read,save,sha
from audit_readonly_rom_performance import compute
def main():
    prefix='report/data/p16-memory-readonly-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('发布件未暂存')
        raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;info=manifest['files'].get(path.name)
        if raw!=path.read_bytes() or (info and (len(raw)!=info['bytes'] or hashlib.sha256(raw).hexdigest()!=info['sha256'])):raise AssertionError('发布字节不同')
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                if archive.testzip():raise AssertionError('CRC不同')
                members+=len(archive.infolist())
    with zipfile.ZipFile(directory/'measured-source.zip') as archive:
        plan_raw=archive.read('experiments/memory-rom-readonly-performance-v1.json');plan=json.loads(plan_raw)
        if hashlib.sha256(plan_raw).hexdigest()!=sha(ROOT/'experiments/memory-rom-readonly-performance-v1.json'):raise AssertionError('正式计划字节不同')
        for name,value in plan['source_sha256'].items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=value or sha(ROOT/name)!=value:raise AssertionError('执行源冻结不同')
        qraw=archive.read('experiments/memory-rom-readonly-v1.json');qplan=json.loads(qraw)
        if hashlib.sha256(qraw).hexdigest()!='95b289d4f0a40baa1974fd902a6ceb59f7986c5bc67216f8ae8714468d1cc855':raise AssertionError('已执行质量计划不同')
        for name,value in qplan['source_sha256'].items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=value:raise AssertionError('质量执行源不同')
    class ZPath:
        def __init__(self,z,name=''):self.z=z;self.name=name
        def __truediv__(self,other):return ZPath(self.z,self.name+'/'+other if self.name else other)
        def read_bytes(self):return self.z.read(self.name)
    with zipfile.ZipFile(directory/'performance-raw.zip') as archive:
        if archive.read('summary.json')!=(directory/'performance.json').read_bytes():raise AssertionError('原summary与发布不同')
        if compute(ZPath(archive),plan)!=read(directory/'decimal-audit.json'):raise AssertionError('Decimal发布不同')
    records={name:read(directory/file) for name,file in (('original_cow','original-cow.json'),('cow','win-cow.json'),('readonly','win-readonly.json'))};summary=read(directory/'commit-summary.json')
    deltas={name:{phase:data['phases'][phase]['PrivateUsage']-data['phases']['before']['PrivateUsage'] for phase in ('mapped_untouched','prepared','all_pages_read','closed')} for name,data in records.items()}
    gains={phase:min(deltas['original_cow'][phase],deltas['cow'][phase])-deltas['readonly'][phase] for phase in ('mapped_untouched','prepared','all_pages_read')}
    if deltas!=summary['deltas'] or gains!=summary['conservative_gain_bytes'] or summary['passed']!=all(v>=(1<<20) for v in gains.values()):raise AssertionError('独立提交增量不同')
    for name,data in records.items():
        if not data['passed'] or data['resident']!=16779328 or not data['closed_model_zero']:raise AssertionError('三fresh容量/清零不同')
        for phase in ('mapped_untouched','prepared','all_pages_read'):
            for point in ('first','last'):
                value=data['phases'][phase]['view'][point]
                if value['Protect']!=(2 if name=='readonly' else 8) or value['Type']!=0x40000:raise AssertionError('实际文件保护不同')
    quality=read(directory/'quality.json')
    if not quality['passed'] or quality['resident']!=16779328 or len(quality['hashes'])!=8 or set(quality['hashes'].values())!={'3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'} or len(quality['photo_hashes'])!=8 or set(quality['photo_hashes'].values())!={'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'}:raise AssertionError('8域/8百图质量不同')
    if (quality['finite'],quality['rejections'],quality['image_guards'],quality['rom_guards'])!=(580,39,144,24) or quality['failure_handles_before']!=quality['failure_handles_after'] or quality['fixtures']['count256']['last_rgb']!=[255,255,255] or quality['writer_error']!=32:raise AssertionError('有限/guard/生命周期合同不同')
    save(directory/'git-byte-audit.json',dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,native_performance_calls=848,quality_hashes=8,photo_hashes=8,private_commit_conservative_gain_bytes=gains,scope='只复算既有原件；capacity不变、原COW句柄+1与全部速度失败/失效保留。'))
    print(dict(passed=True,files=len(names),zip_members=members))
if __name__=='__main__':main()
