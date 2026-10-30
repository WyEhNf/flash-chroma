"""离线把原精确16B字典转换为16+1bit双平面，并重建全部16MiB逻辑ID。"""
import argparse
import hashlib
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,sha,read,save,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(ROOT/'experiments/split-dictionary-v1.json')
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise ValueError('冻结源码变化')
    source=Path(plan['input_rom_path'])
    if sha(source)!=plan['input_rom_sha256']:raise ValueError('源ROM不同')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();raw=source.read_bytes();oldmaps=4194304
    if raw[:4]!=b'M16D' or struct.unpack_from('<I',raw,8)[0]!=4:raise ValueError('源格式不同')
    payload=raw[1056:];pool=np.frombuffer(payload,dtype=np.uint8,offset=oldmaps).reshape(-1,16);offsets=np.frombuffer(payload,dtype='<u4',count=1048576)
    ids=((offsets-oldmaps)//16).astype(np.uint32)
    if np.any(offsets<oldmaps) or np.any((offsets-oldmaps)%16) or int(ids.max())>=len(pool) or len(pool)>131072:raise ValueError('源块非法')
    low=ids.astype('<u2');high=np.packbits((ids>>16).astype(np.uint8),bitorder='little');encoded=low.tobytes()+high.tobytes()
    block=np.arange(len(ids),dtype=np.uint32);decoded=low.astype(np.uint32)|(((high[block>>3]>>(block&7)).astype(np.uint32)&1)<<16)
    digest=hashlib.sha256(pool[decoded].reshape(-1)).hexdigest()
    if len(encoded)!=2228224 or not np.array_equal(ids,decoded) or digest!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('完整逻辑ID不同')
    count=struct.unpack_from('<I',raw,12)[0];content=encoded+pool.tobytes();header=b'M16S'+struct.pack('<7I',1,17,count,len(content),0,0,0)+raw[32:1056];path=a.output/'rom-17.bin';path.write_bytes(header+content)
    save(a.output/'export.json',dict(purpose=__doc__,environment=env(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'experiments/split-dictionary-v1.json'),source_rom_sha256=sha(source),file_bytes=path.stat().st_size,sha256=sha(path),low_bytes=low.nbytes,high_bytes=high.nbytes,pool_bytes=pool.nbytes,unique_blocks=len(pool),logical_sha256=digest,before=before,after=memory(),scope='固定原字典pool及palette顺序；全部256^3个ID重建，未读gold/照片。峰值含Python/NumPy及离线临时对象，不是运行时容量。'))
    print(path,sha(path))
if __name__=='__main__':main()
