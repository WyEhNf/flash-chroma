"""静态核验M16P的Git暂存/清单/工作区原字节及三个可重放ROM。"""
import hashlib
import io
import subprocess
import zipfile
from study_memory_rom import ROOT,read,save,sha

def main():
    prefix='report/data/p16-compact-dictionary-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+n for n in manifest['files']];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+n for n in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('缺少暂存原件：'+name)
        blob=stream.read(int(header[2]));assert stream.read(1)==b'\n';source=ROOT/name;expected=manifest['files'][source.name]
        if blob!=source.read_bytes() or len(blob)!=expected['bytes'] or hashlib.sha256(blob).hexdigest()!=expected['sha256']:raise AssertionError('字节不一致：'+name)
        if source.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                if z.testzip():raise AssertionError('CRC错误：'+name)
                members+=len(z.infolist())
    frozen=read(ROOT/'experiments/compact-dictionary-v1.json')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in frozen['source_sha256'].items():
            if sha(ROOT/name)!=value or hashlib.sha256(z.read(name)).hexdigest()!=value:raise AssertionError('所测源码变化：'+name)
    with zipfile.ZipFile(directory/'exact-roms.zip') as z:
        if hashlib.sha256(z.read('original-rom-32.bin')).hexdigest()!=frozen['input_rom_sha256']:raise AssertionError('原32bit ROM不同')
        for r in read(directory/'export.json')['models']:
            if hashlib.sha256(z.read('rom-'+str(r['entry_bits'])+'.bin')).hexdigest()!=r['sha256']:raise AssertionError('新ROM不同')
    save(directory/'git-byte-audit.json',dict(purpose=__doc__,passed=True,files=len(names),zip_members=members,scope='全部静态核对，不重跑或修改数值/计时。'))
    print('通过',len(names),'原件',members,'ZIP成员')
if __name__=='__main__':main()
