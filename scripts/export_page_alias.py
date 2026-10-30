"""消费封存4KiB pageID导出唯一alias与对齐未去重控制，不重新普查。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-alias-runtime-v1.json'
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def header(original,unique,kind):
    value=bytearray(4096);value[:32]=b'P4AL'+struct.pack('<7I',1,4096,4096,unique,16384 if kind==0 else 0,20480 if kind==0 else 4096,kind)
    value[32:64]=bytes.fromhex('a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0');value[64:96]=bytes.fromhex('146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5');value[3040:]=original;return value
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(PLAN)
    if any(sha(ROOT/name)!=v for name,v in plan['source_sha256'].items()) or any(sha(Path(name))!=v for name,v in plan['input_sha256'].items()):raise AssertionError('冻结源/输入改变')
    a.output.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(plan['census_zip']) as archive:support_raw=archive.read('support.json');support=json.loads(support_raw)
    if hashlib.sha256(support_raw).hexdigest()!='bfc96db68384a70c40c7df596b8d6a1fb1411a189d8059620b44e58b02dc3025':raise AssertionError('封存pageID不同')
    ids=support['page_ids'];pool=[None]*3082;source_digest=hashlib.sha256();logical=hashlib.sha256()
    with Path(plan['original_rom']).open('rb') as stream:
        original=stream.read(1056);source_digest.update(original)
        with (a.output/'aligned.bin').open('wb') as target:
            target.write(header(original,4096,1))
            for page,identifier in enumerate(ids):
                raw=stream.read(4096);source_digest.update(raw);logical.update(raw)
                if len(raw)!=4096 or hashlib.sha256(raw).hexdigest()!=support['unique_page_sha256'][identifier]:raise AssertionError('原页身份不同')
                if pool[identifier] is None:pool[identifier]=raw
                elif pool[identifier]!=raw:raise AssertionError('封存同页ID实际bytes不同')
                target.write(raw)
            if stream.read(1):raise AssertionError('原ROM多余字节')
    if source_digest.hexdigest()!='146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5' or logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0' or any(raw is None for raw in pool):raise AssertionError('完整源/ID/pool身份不同')
    with (a.output/'alias.bin').open('wb') as target:
        target.write(header(original,3082,0));target.write(struct.pack('<4096I',*ids))
        for raw in pool:target.write(raw)
    outputs={name:dict(bytes=(a.output/name).stat().st_size,sha256=sha(a.output/name)) for name in ('alias.bin','aligned.bin')}
    if outputs['alias.bin']['bytes']!=12644352 or outputs['aligned.bin']['bytes']!=16781312:raise AssertionError('实际导出尺寸不同')
    result=dict(purpose=__doc__,plan_sha256=sha(PLAN),outputs=outputs,census_support_sha256=hashlib.sha256(support_raw).hexdigest(),canonical_rom_sha256=source_digest.hexdigest(),logical_id_sha256=logical.hexdigest(),unique_pages=3082,logical_blob_bytes=16778272,model_view_span=16781312,scope='真实backing文件尚未表示实际页映射/物理RAM或吞吐；原DLL与Model未变，未重census/读照片gold。')
    (a.output/'export.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(outputs)
if __name__=='__main__':main()
