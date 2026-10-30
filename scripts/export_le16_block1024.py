"""唯一1024B块LE16格式：保留原pool及palette，全16MiB逻辑ID独立重建。"""
import argparse
import hashlib
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,sha,read,save,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(ROOT/'experiments/le16-block1024-v1.json')
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise ValueError('冻结源变化')
    source=Path(plan['input_rom_path'])
    if sha(source)!=plan['input_rom_sha256']:raise ValueError('原1024ROM不同')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();raw=source.read_bytes()
    if raw[:4]!=b'M16D' or struct.unpack_from('<I',raw,8)[0]!=10:raise ValueError('原格式不同')
    offsets=np.frombuffer(raw,dtype='<u4',count=16384,offset=1056);pool=np.frombuffer(raw,dtype=np.uint8,offset=1056+65536).reshape(-1,1024);ids=((offsets-65536)//1024).astype(np.uint32)
    if np.any(offsets<65536) or np.any((offsets-65536)%1024) or int(ids.max())>=len(pool) or len(pool)>65536 or len(pool)!=10482:raise ValueError('原map/pool非法')
    encoded=ids.astype('<u2').tobytes();payload=encoded+pool.tobytes();header=b'M10L'+struct.pack('<7I',1,10,struct.unpack_from('<I',raw,12)[0],len(payload),0,0,0)+raw[32:1056];path=a.output/'rom-10.bin';path.write_bytes(header+payload);decoded=np.frombuffer(encoded,dtype='<u2');digest=hashlib.sha256()
    for start in range(0,len(ids),256):
        end=min(start+256,len(ids));expected=pool[ids[start:end]];actual=pool[decoded[start:end]]
        if not np.array_equal(expected,actual):raise AssertionError('独立LE16全域重建不同')
        digest.update(actual)
    if digest.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('逻辑ID SHA不同')
    save(a.output/'export.json',dict(purpose=__doc__,environment=env(),plan_sha256=sha(ROOT/'experiments/le16-block1024-v1.json'),source_rom_sha256=sha(source),rom_bytes=path.stat().st_size,rom_sha256=sha(path),map_bytes=len(encoded),pool_bytes=pool.nbytes,unique_blocks=len(pool),maximum_id=int(ids.max()),model_expected_bytes=1056,resident_expected=path.stat().st_size+1056,saved_bytes=len(raw)-path.stat().st_size,logical_sha256=digest.hexdigest(),before=before,after=memory(),scope='pool与palette原字节保留，仅原map转LE16块ID；无gold/照片选择。离线峰值含Python/NumPy及临时对象，不是运行时RAM。'))
    print(path,sha(path))
if __name__=='__main__':main()
