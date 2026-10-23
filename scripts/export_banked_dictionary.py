"""只导出已选4bank：2MiB LE16局部索引、四个base及按bank重复的原16B块。"""
import argparse
import hashlib
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,read,save,sha,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=ROOT/'experiments/banked-dictionary-native-v1.json';plan=read(path)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise AssertionError('冻结源码变化')
    profile=read(ROOT/'artifacts/p16-banked-dictionary-profile-v1/results.json');selected=profile['selected']
    if selected['banks']!=4 or sha(ROOT/'artifacts/p16-banked-dictionary-profile-v1/results.json')!=plan['profile_result_sha256']:raise AssertionError('选型变化')
    source=Path(plan['input_rom_path'])
    if sha(source)!=plan['input_rom_sha256']:raise AssertionError('源ROM变化')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();raw=source.read_bytes();payload=raw[1056:];ids=((np.frombuffer(payload,dtype='<u4',count=1048576)-4194304)//16).astype(np.uint32);pool=np.frombuffer(payload,dtype=np.uint8,offset=4194304).reshape(-1,16)
    encoded=np.empty(1048576,dtype='<u2');pools=[];bases=[];base=2097152+16;logical=hashlib.sha256();counts=[]
    for bank in range(4):
        start=bank*262144;unique,inverse=np.unique(ids[start:start+262144],return_inverse=True)
        if len(unique)>65536:raise AssertionError('选定bank溢出LE16')
        encoded[start:start+262144]=inverse;bases.append(base);part=pool[unique].tobytes();pools.append(part);base+=len(part);counts.append(len(unique));logical.update(pool[unique[inverse]].reshape(-1))
    digest=logical.hexdigest()
    if digest!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0' or counts!=selected['bank_unique']:raise AssertionError('完整逻辑ID或选型统计变化')
    content=encoded.tobytes()+struct.pack('<4I',*bases)+b''.join(pools);header=b'M16B'+struct.pack('<7I',1,4,struct.unpack_from('<I',raw,12)[0],len(content),0,0,0)+raw[32:1056];rom=a.output/'rom-4.bin';rom.write_bytes(header+content)
    if rom.stat().st_size!=selected['rom_bytes']:raise AssertionError('实际ROM与剖析不符')
    save(a.output/'export.json',dict(purpose=__doc__,environment=env(),plan_sha256=sha(path),script_sha256=sha(__file__),source_rom_sha256=sha(source),rom_sha256=sha(rom),rom_bytes=rom.stat().st_size,bank_unique=counts,bases=bases,model_bytes=1072,resident_bytes=rom.stat().st_size+1072,profile_assumed_model_bytes=1056,extra_native_model_bytes=16,logical_sha256=digest,before=before,after=memory(),scope='仅选定4bank，没有扫描native其它bank。ROM原palette保留256合法项；独立bases[4]使model比离线排序假设多16B，原profile不回写。'))
    print(rom,sha(rom))
if __name__=='__main__':main()
