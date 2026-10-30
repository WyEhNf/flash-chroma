"""核对RGB24发布原字节、ZIP CRC、测量源及Git暂存对象。"""
import hashlib
import io
import subprocess
import zipfile
from study_memory_rom import ROOT,read,save,sha

def main():
    prefix='report/data/p16-rgb24-sparse-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+n for n in manifest['files']]
    output=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+n for n in names)+'\n').encode(),cwd=ROOT);stream=io.BytesIO(output);members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('无暂存项：'+name)
        blob=stream.read(int(header[2]));assert stream.read(1)==b'\n';source=ROOT/name;expected=manifest['files'][source.name]
        if blob!=source.read_bytes() or len(blob)!=expected['bytes'] or hashlib.sha256(blob).hexdigest()!=expected['sha256']:raise AssertionError('字节不一致：'+name)
        if source.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                if z.testzip():raise AssertionError('CRC失败：'+name)
                members+=len(z.infolist())
    plan=read(ROOT/'experiments/rgb24-sparse-v1.json')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if sha(ROOT/name)!=value or hashlib.sha256(z.read(name)).hexdigest()!=value:raise AssertionError('所测源变化：'+name)
    save(directory/'git-byte-audit.json',dict(purpose=__doc__,passed=True,files=len(names),zip_members=members,scope='静态核对，没有重跑/覆盖数值或性能。'))
    print('通过',len(names),'原件与',members,'ZIP成员')
if __name__=='__main__':main()
