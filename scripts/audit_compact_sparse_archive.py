"""静态核对compact发布原字节、ZIP CRC及暂存Git blob，不重跑数值。"""
import argparse
import hashlib
import io
import subprocess
import zipfile
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=str,default='report/data/p16-compact-sparse-v1');a=p.parse_args();directory=ROOT/a.directory
    manifest=read(directory/'manifest.json');names=[a.directory+'/'+n for n in manifest['files']]
    batch=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+n for n in names)+'\n').encode(),cwd=ROOT);stream=io.BytesIO(batch)
    members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('暂存项不存在：'+name)
        blob=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        source=ROOT/name;expected=manifest['files'][source.name]
        if blob!=source.read_bytes() or len(blob)!=expected['bytes'] or hashlib.sha256(blob).hexdigest()!=expected['sha256']:raise AssertionError('入库字节不一致：'+name)
        if source.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                if z.testzip():raise AssertionError('CRC失败：'+name)
                members+=len(z.infolist())
    plan=read(ROOT/'experiments/compact-sparse-v1.json')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=value or sha(ROOT/name)!=value:raise AssertionError('测量源码变化：'+name)
    save(directory/'git-byte-audit.json',dict(purpose=__doc__,passed=True,files=len(names),zip_members=members,scope='核对本次暂存blob、工作树、发布清单及所测源码；不修改原始JSON、不重跑测量。'))
    print('通过：',len(names),'原件，',members,'ZIP成员')
if __name__=='__main__':main()
