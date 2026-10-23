"""仅从冻结M16D字典与palette导出唯一RGB32块格式，并独立重建全域。"""
import argparse
import hashlib
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,sha,read,save,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(ROOT/'experiments/color-dictionary-v1.json')
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise ValueError('冻结源码变化')
    source=Path(plan['input_rom_path'])
    if sha(source)!=plan['input_rom_sha256']:raise ValueError('源ROM不同')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();raw=source.read_bytes();oldmaps=4194304;maps=3145728
    if raw[:4]!=b'M16D' or struct.unpack_from('<I',raw,8)[0]!=4:raise ValueError('源格式不同')
    palette=np.frombuffer(raw,dtype='<u4',count=256,offset=32);payload=raw[1056:];pool=np.frombuffer(payload,dtype=np.uint8,offset=oldmaps).reshape(-1,16);offsets=np.frombuffer(payload,dtype='<u4',count=1048576)
    ids=((offsets-oldmaps)//16).astype(np.uint32)
    if np.any(offsets<oldmaps) or np.any((offsets-oldmaps)%16) or int(ids.max())>=len(pool) or np.any(palette>0xffffff):raise ValueError('源块或颜色非法')
    expanded=palette[pool].astype('<u4');new_offsets=maps+ids*64;length=maps+expanded.nbytes
    if length>1<<24 or int(new_offsets.max())>0xffffff or int(new_offsets.max())+64>length:raise ValueError('24bit范围不满足')
    encoded=np.empty((len(ids),3),dtype=np.uint8)
    for j in range(3):encoded[:,j]=new_offsets>>(8*j)
    content=encoded.tobytes()+expanded.tobytes();header=b'M16C'+struct.pack('<7I',1,24,4,len(content),0,0,0);path=a.output/'rom-24.bin';path.write_bytes(header+content)
    decoded_offsets=encoded[:,0].astype(np.uint32)|(encoded[:,1].astype(np.uint32)<<8)|(encoded[:,2].astype(np.uint32)<<16)
    logical=hashlib.sha256();colors_old=hashlib.sha256();colors_new=hashlib.sha256();serialized=np.frombuffer(content,dtype=np.uint8)
    for start in range(0,len(ids),65536):
        end=min(start+65536,len(ids));old_ids=pool[ids[start:end]];logical.update(old_ids);original=palette[old_ids].astype('<u4');colors_old.update(original)
        addresses=decoded_offsets[start:end,None]+np.arange(16,dtype=np.uint32)[None,:]*4
        words=np.zeros(addresses.shape,dtype=np.uint32)
        for j in range(4):words|=serialized[addresses+j].astype(np.uint32)<<(8*j)
        if not np.array_equal(original,words):raise AssertionError('序列化RGB32全域重建不同')
        colors_new.update(words.astype('<u4'))
    if logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0' or colors_old.hexdigest()!=colors_new.hexdigest():raise AssertionError('完整逻辑域不同')
    save(a.output/'export.json',dict(purpose=__doc__,environment=env(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'experiments/color-dictionary-v1.json'),source_rom_sha256=sha(source),file_bytes=path.stat().st_size,sha256=sha(path),map_bytes=maps,pool_bytes=expanded.nbytes,unique_blocks=len(pool),model_expected_bytes=32,resident_expected=path.stat().st_size+32,maximum_offset=int(new_offsets.max()),maximum_end=int(new_offsets.max())+64,payload_bytes=length,logical_sha256=logical.hexdigest(),rgb32_old_sha256=colors_old.hexdigest(),rgb32_new_sha256=colors_new.hexdigest(),before=before,after=memory(),scope='保留原pool顺序；只用源palette及ID预展开，无gold/照片选择。全256^3内部R低/B高枚举独立解码RGB32；该枚举SHA不冒充R高输入的native完整域SHA。离线峰值含Python/NumPy临时对象。'))
    print(path,sha(path))
if __name__=='__main__':main()
