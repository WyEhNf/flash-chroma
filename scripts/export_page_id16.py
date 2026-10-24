"""只消费封存3082页分类导出唯一P4ID，不重新census或读取照片/gold。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-id16-runtime-v1.json'
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=json.loads(PLAN.read_text(encoding='utf-8'))
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('冻结源/原件不同')
    a.output.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(plan['census_zip']) as archive:raw=archive.read('support.json');support=json.loads(raw)
    if hashlib.sha256(raw).hexdigest()!='bfc96db68384a70c40c7df596b8d6a1fb1411a189d8059620b44e58b02dc3025':raise AssertionError('封存分类不同')
    ids=support['page_ids'];target=a.output/'page-id16.bin'
    with Path(plan['alias']).open('rb') as source,target.open('wb') as output:
        previous=source.read(4096);metadata=source.read(16384)
        if previous[:32]!=b'P4AL'+struct.pack('<7I',1,4096,4096,3082,16384,20480,0) or list(struct.unpack('<4096I',metadata))!=ids:raise AssertionError('已有容器/pageID不同')
        old=previous[3040:]
        if old[:32]!=b'M16D'+struct.pack('<7I',1,0,230,1<<24,0,0,0):raise AssertionError('原palette头不同')
        output.write(b'P4ID'+struct.pack('<7I',1,12,230,1<<24,3082,0,0));output.write(old[32:]);output.write(struct.pack('<4096H',*ids))
        for page in range(3082):
            block=source.read(4096)
            if len(block)!=4096 or hashlib.sha256(block).hexdigest()!=support['unique_page_sha256'][page]:raise AssertionError('封存pool页不同')
            output.write(block)
        if source.read(1):raise AssertionError('已有alias文件多字节')
        output.write(bytes(4))
    canonical=hashlib.sha256();old_digest=hashlib.sha256(old)
    with target.open('rb') as stream:
        header=stream.read(1056);encoded=stream.read(8192)
        if header[32:]!=old[32:] or list(struct.unpack('<4096H',encoded))!=ids:raise AssertionError('新palette/map逐项不同')
        for identifier in ids:
            stream.seek(9248+identifier*4096);block=stream.read(4096);canonical.update(block);old_digest.update(block)
    if target.stat().st_size!=12633124 or canonical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0' or old_digest.hexdigest()!='146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5':raise AssertionError('实际长度或封存全ID重放不同')
    result=dict(purpose=__doc__,plan_sha256=sha(PLAN),output=dict(path=str(target),bytes=target.stat().st_size,sha256=sha(target)),logical_id_sha256=canonical.hexdigest(),old_canonical_sha256=old_digest.hexdigest(),pages=4096,unique_pages=3082,map_bytes=8192,pool_bytes=12623872,guard_bytes=4,scope='实际文件仅导出后报告；Model ABI/native质量/速度和RSS另验，未重分类或读取图片。')
    (a.output/'export.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
