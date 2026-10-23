"""按唯一census与固定M16T布局导出，独立解码所有序列化RGB32。"""
import argparse
import hashlib
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,sha,read,save,env
from bench_memory_rom import memory
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();planpath=ROOT/'experiments/tagged-block16-native-v1.json';plan=read(planpath)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()):raise AssertionError('冻结源变化')
    source=Path(plan['input_rom_path']);census=Path(plan['census_path'])
    if sha(source)!=plan['input_rom_sha256'] or sha(census)!=plan['census_sha256']:raise AssertionError('源/census身份不同')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();raw=source.read_bytes();palette=np.frombuffer(raw,dtype='<u4',count=256,offset=32);pool=np.frombuffer(raw,dtype=np.uint8,offset=1056+4194304).reshape(-1,16);offsets=np.frombuffer(raw,dtype='<u4',count=1048576,offset=1056);ids=(offsets-4194304)//16;constant=np.all(palette[pool]==palette[pool[:,:1]],axis=1);selected=constant[ids];mapping=np.zeros(len(pool),dtype=np.uint32);mapping[~constant]=np.arange(np.count_nonzero(~constant),dtype=np.uint32);words=np.empty(len(ids),dtype='<u4');words[~selected]=4194304+16*mapping[ids[~selected]];words[selected]=0x80000000|palette[pool[ids[selected],0]];kept=pool[~constant];payload=words.tobytes()+kept.tobytes();rom=b'M16T'+struct.pack('<7I',1,4,struct.unpack_from('<I',raw,12)[0],len(payload),0,0,0)+raw[32:1056]+payload;path=a.output/'rom-4.bin';path.write_bytes(rom);fixed=read(census)
    if int(selected.sum())!=fixed['constant_map_entries'] or len(rom)!=fixed['projected_rom_bytes'] or len(kept)!=fixed['nonconstant_unique']:raise AssertionError('改变已冻结census或布局')
    serialized=np.frombuffer(payload,dtype=np.uint8);actual_words=np.frombuffer(payload,dtype='<u4',count=1048576);digest=hashlib.sha256();old_digest=hashlib.sha256();logical=hashlib.sha256()
    for start in range(0,len(ids),65536):
        end=min(start+65536,len(ids));e=actual_words[start:end];tag=(e&0x80000000)!=0;out=np.empty((len(e),16),dtype='<u4');out[tag]=(e[tag]&0xffffff)[:,None];addresses=e[~tag,None]+np.arange(16,dtype=np.uint32)[None,:];out[~tag]=palette[serialized[addresses]];old_ids=pool[ids[start:end]];expected=palette[old_ids]
        if not np.array_equal(out,expected):raise AssertionError('实际序列化全部颜色不同')
        digest.update(out);old_digest.update(expected.astype('<u4'));logical.update(old_ids)
    if digest.hexdigest()!=old_digest.hexdigest() or logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('完整域摘要不同')
    save(a.output/'export.json',dict(purpose=__doc__,environment=env(),plan_sha256=sha(planpath),census_sha256=sha(census),source_rom_sha256=sha(source),rom_bytes=len(rom),rom_sha256=sha(path),map_bytes=4194304,pool_bytes=kept.nbytes,nonconstant_unique=len(kept),constant_unique=int(constant.sum()),constant_map_entries=int(selected.sum()),model_expected_bytes=1056,resident_expected=len(rom)+1056,logical_sha256=logical.hexdigest(),rgb32_sha256=digest.hexdigest(),old_rgb32_sha256=old_digest.hexdigest(),before=before,after=memory(),scope='原ID块非恒定部分稳定压紧，palette原字节保持，常量直接RGB24；只按已冻结census实现，无照片/gold/参数扫描。峰值含离线Python/NumPy，不是核心RAM。'))
    print(path,sha(path))
if __name__=='__main__':main()
