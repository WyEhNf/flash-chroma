"""把已冻结精确16B字典的32bit偏移改写为3B偏移/17bit块ID，独立完整逻辑表重建。"""
import argparse
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,sha,read,save,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    plan=read(ROOT/'experiments/compact-dictionary-v1.json')
    if sha(a.rom)!=plan['input_rom_sha256']:raise ValueError('源ROM身份不同')
    before=memory();raw=a.rom.read_bytes()
    if raw[:4]!=b'M16D' or struct.unpack_from('<I',raw,8)[0]!=4:raise ValueError('必须为已验16B精确字典')
    oldmaps=1048576*4;palette=raw[32:1056];count=struct.unpack_from('<I',raw,12)[0];payload=raw[1056:];pool=np.frombuffer(payload,dtype=np.uint8,offset=oldmaps).reshape(-1,16)
    offsets=np.frombuffer(payload,dtype='<u4',count=1048576);ids=((offsets-oldmaps)//16).astype(np.uint32)
    if np.any(offsets<oldmaps) or np.any((offsets-oldmaps)%16) or int(ids.max())>=len(pool) or len(pool)>131072:raise ValueError('源块偏移非法')
    records=[]
    for mode in (24,17):
        maps=1048576*mode//8
        if mode==24:
            values=ids*16+maps
            if int(values.max())>=1<<24:raise ValueError('3B偏移溢出')
            packed=np.empty((len(ids),3),dtype=np.uint8)
            for j in range(3):packed[:,j]=values>>(8*j)
            encoded=packed.reshape(-1)
            decoded=(packed[:,0].astype(np.uint32)|(packed[:,1].astype(np.uint32)<<8)|(packed[:,2].astype(np.uint32)<<16))-maps
            if np.any(decoded%16):raise AssertionError('3B偏移对齐丢失')
            decoded//=16
        else:
            bit=np.arange(len(ids),dtype=np.uint32)*17;byte=bit>>3;shift=bit&7;values=ids<<shift;encoded=np.zeros(maps+2,dtype=np.uint8)
            for j in range(3):np.bitwise_or.at(encoded,byte+j,(values>>(8*j)).astype(np.uint8))
            decoded=((encoded[byte].astype(np.uint32)|(encoded[byte+1].astype(np.uint32)<<8)|(encoded[byte+2].astype(np.uint32)<<16))>>shift)&131071
            encoded=encoded[:maps]
        logical=pool[decoded].reshape(-1)
        import hashlib
        digest=hashlib.sha256(logical).hexdigest()
        if not np.array_equal(ids,decoded) or digest!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('完整16MiB逻辑ID表不同')
        content=encoded.tobytes()+pool.tobytes();header=b'M16P'+struct.pack('<7I',1,mode,count,len(content),0,0,0)+palette;path=a.output/f'rom-{mode}.bin';path.write_bytes(header+content)
        records.append(dict(entry_bits=mode,map_bytes=maps,pool_bytes=pool.nbytes,unique_blocks=len(pool),file_bytes=path.stat().st_size,sha256=sha(path),logical_sha256=digest))
        del logical,content,header,encoded,decoded
    save(a.output/'export.json',dict(purpose=__doc__,environment=env(),source_rom_sha256=sha(a.rom),script_sha256=sha(__file__),models=records,before=before,after=memory(),scope='只压已冻结模型编译得到的精确字典；独立重建所有256^3个ID，未读照片/gold/原滤镜。进程RSS/峰包括Python/NumPy与两种格式离线导出的全部临时对象。'))
    print(records)
if __name__=='__main__':main()
