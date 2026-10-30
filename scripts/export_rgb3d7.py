"""消费已封存频数，唯一导出C7BK并独立解释全部序列化RGB，不重census。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile
import numpy as np
from rgb3d7_support import ROOT,PLAN,TABLE,TABLE_START,GUARD,PALETTE,ROM_BYTES,bank,pack7,header,sha,read,save,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(PLAN)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise AssertionError('冻结执行源变化')
    census=Path(plan['census_zip'])
    if sha(census)!=plan['census_zip_sha256']:raise AssertionError('封存频数ZIP不同')
    with zipfile.ZipFile(census) as z:support_raw=z.read('frequency-support.json');support=json.loads(support_raw)
    if hashlib.sha256(support_raw).hexdigest()!=plan['frequency_support_sha256']:raise AssertionError('原频数支持不同')
    # 只核原已完整频数，不重新按原输出分类或选择新key。
    frequencies=np.asarray(support['bank_global_id_frequency'],dtype=np.int64);global_palette=np.asarray(support['palette_rgb24'],dtype='<u4')
    if frequencies.shape!=(512,230) or np.any(frequencies<0) or not np.all(frequencies.sum(axis=1)==32768) or len(np.unique(global_palette))!=230:raise AssertionError('频数范围不同')
    counts=(frequencies>0).sum(axis=1).astype('<u2')
    if int(counts.max())!=95 or np.any(counts<1) or np.any(counts>128):raise AssertionError('新7bit存在性证据不同')
    mapping=np.full((512,256),255,dtype=np.uint8);palettes=np.zeros((512,128),dtype='<u4')
    for b in range(512):
        used=np.flatnonzero(frequencies[b]);mapping[b,used]=np.arange(len(used),dtype=np.uint8);palettes[b,:len(used)]=global_palette[used]
    source=Path(plan['source_rom'])
    if sha(source)!=plan['source_rom_sha256']:raise AssertionError('原M16D不同')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();old=source.read_bytes();old_palette=np.frombuffer(old,dtype='<u4',count=256,offset=32);old_offsets=np.frombuffer(old,dtype='<u4',count=1048576,offset=1056);old_payload=np.frombuffer(old,dtype=np.uint8,offset=1056)
    if old[:4]!=b'M16D' or struct.unpack_from('<I',old,8)[0]!=4 or not np.array_equal(old_palette[:230],global_palette):raise AssertionError('原模型palette/格式不同')
    packed=bytearray(TABLE)
    for begin in range(0,1<<24,1<<18):
        codes=np.arange(begin,begin+(1<<18),dtype=np.uint32);ids=old_payload[old_offsets[codes>>4]+(codes&15)];local=mapping[bank(codes),ids]
        if np.any(local==255):raise AssertionError('源颜色未在固定bank频数内')
        start=7*begin//8;packed[start:start+7*len(codes)//8]=pack7(local)
    raw=header()+counts.tobytes()+packed+bytes(4)+palettes.tobytes()
    if len(raw)!=ROM_BYTES:raise AssertionError('实际文件长度错误')
    path=a.output/'rgb3d7.bin';path.write_bytes(raw);serialized=np.frombuffer(raw,dtype=np.uint8);serialized_palette=np.frombuffer(raw,dtype='<u4',count=65536,offset=PALETTE);digest=hashlib.sha256();logical=hashlib.sha256()
    for begin in range(0,1<<24,1<<18):
        codes=np.arange(begin,begin+(1<<18),dtype=np.uint32);bit=7*codes;position=TABLE_START+(bit>>3);word=serialized[position].astype(np.uint16)|(serialized[position+1].astype(np.uint16)<<8);local=(word>>(bit&7))&127;decoded=serialized_palette[(bank(codes)<<7)|local];ids=old_payload[old_offsets[codes>>4]+(codes&15)]
        if not np.array_equal(decoded,old_palette[ids]) or np.any(local>=counts[bank(codes)]):raise AssertionError('独立序列化完整RGB不同')
        digest.update(decoded.astype('<u4'));logical.update(ids)
    if digest.hexdigest()!='29a15ba4cb83d0840cfaa99015cda43848fa4ca43a9a1f224c19eaa7dd252497' or logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('全域摘要不同')
    save(a.output/'export.json',dict(purpose=__doc__,environment=env(),plan_sha256=sha(PLAN),rom_bytes=len(raw),rom_sha256=sha(path),model_expected_bytes=32,resident_expected=len(raw)+32,table_bytes=TABLE,count_bytes=1024,palette_bytes=262144,guard_bytes=4,bank_counts=counts.tolist(),maximum_bank_colors=int(counts.max()),frequency_support_sha256=plan['frequency_support_sha256'],source_rom_sha256=sha(source),rgb32_sha256=digest.hexdigest(),logical_sha256=logical.hexdigest(),before=before,after=memory(),scope='不重新统计bank选择，只消费原频数生成唯一编号；实际字节全域独立反解，质量/native与速度尚分开。峰值为离线Python临时。'))
    print(path,sha(path))
if __name__=='__main__':main()
