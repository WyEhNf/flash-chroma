"""从现有稀疏模型运行库导出精确ROM，集中核验全域和边界，独立比较内存/可移植性。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import mmap
import os
from pathlib import Path
import platform
import struct
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
U8=ct.POINTER(ct.c_uint8)
class Model(ct.Structure):
    _fields_=[('blob',U8),('blob_bytes',ct.c_size_t),('table',U8),('palette',ct.c_uint32*256),('log2_block',ct.c_uint32),('palette_size',ct.c_uint32)]
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def env():return dict(platform=platform.platform(),machine=platform.machine(),python=sys.version,numpy=np.__version__,thread_environment={k:os.environ.get(k) for k in ('OMP_NUM_THREADS','OMP_DYNAMIC','OMP_WAIT_POLICY','OPENBLAS_NUM_THREADS')})
def native(path):
    d=ct.CDLL(str(path));text=ct.POINTER(ct.c_char)
    d.jshc_cc_create.argtypes=[ct.POINTER(ct.c_char_p),ct.POINTER(ct.c_char_p),ct.c_size_t,ct.POINTER(ct.c_void_p),text,ct.c_size_t]
    d.jshc_cc_destroy.argtypes=[ct.c_void_p]
    d.jshc_cc_apply.argtypes=[ct.c_void_p,U8,ct.c_size_t,ct.c_int,ct.c_int,text,ct.c_size_t]
    d.jshc_cc_model_bytes.argtypes=[ct.c_void_p];d.jshc_cc_model_bytes.restype=ct.c_size_t
    d.jshc_cc_copy_direct.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t]
    d.jshc_cc_copy_palette.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t,ct.POINTER(ct.c_uint32),ct.c_size_t]
    return d
def create(d,data):
    p=data/'artifacts';spec=read(ROOT/'experiments/skylake-andn-split-v1.json')
    paths=[data/spec['fixed_inputs']['base']['path'],*[data/x['path'] for x in spec['suffix_models']]]
    sides=[data/spec['fixed_inputs']['sidecar']['path'],None,None,None]
    for path,s in zip(paths,[spec['fixed_inputs']['base'],*spec['suffix_models']]):
        if sha(path)!=s['sha256']:raise ValueError('模型身份不同')
    if sha(sides[0])!=spec['fixed_inputs']['sidecar']['sha256']:raise ValueError('侧表身份不同')
    names=(ct.c_char_p*4)(*[str(x).encode() for x in paths]);fractions=(ct.c_char_p*4)(*[str(x).encode() if x else None for x in sides])
    h=ct.c_void_p();error=ct.create_string_buffer(1024)
    if d.jshc_cc_create(names,fractions,4,ct.byref(h),error,1024):raise RuntimeError(error.value.decode())
    return h
def romlib(path):
    d=ct.CDLL(str(path));d.jshc_mem_prepare.argtypes=[ct.POINTER(Model),ct.c_void_p,ct.c_size_t]
    d.jshc_mem_apply.argtypes=[ct.POINTER(Model),U8,U8,ct.c_size_t]
    if hasattr(d,'jshc_mem_apply_parallel'):
        d.jshc_mem_apply_parallel.argtypes=[ct.POINTER(Model),U8,U8,ct.c_size_t,ct.c_int,ct.c_int]
    return d
def loadrom(d,path,offset=0):
    # 保留不可变mmap；ctypes只取得其底层地址，映射为copy-on-write但从不写ROM。
    f=path.open('rb');mapping=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_COPY)
    view=(ct.c_uint8*len(mapping)).from_buffer(mapping);m=Model()
    if d.jshc_mem_prepare(ct.byref(m),ct.addressof(view),len(mapping)):raise ValueError('ROM格式拒绝')
    return m,(f,mapping,view)
def export(a):
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    d=native(a.baseline);h=create(d,a.data_root)
    try:
        table=(ct.c_uint32*(1<<22))();pal=(ct.c_uint32*256)();compiled=(ct.c_uint32*(1<<21))()
        if d.jshc_cc_copy_direct(h,table,len(table)) or d.jshc_cc_copy_palette(h,compiled,len(compiled),pal,256):raise ValueError('无法导出精确线性表')
        direct=bytes(table);palette=list(pal)
        # 缓存调色板含完整RGB域未命中的合法色，不能只以最大已见ID截断。
        count=max(max(direct)+1,max((i+1 for i,v in enumerate(palette) if v),default=1))
        if hashlib.sha256(direct).hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise ValueError('线性表不同于已验a399')
        del table,compiled
        stats={}
        for bits in (0,4,6,8,10):
            start=time.perf_counter()
            if bits==0:payload=direct;unique=1<<24
            else:
                block=1<<bits;map_bytes=(len(direct)//block)*4;pool=bytearray();offsets=bytearray(map_bytes);dictionary={}
                for i in range(len(direct)//block):
                    key=direct[i*block:(i+1)*block]
                    off=dictionary.get(key)
                    if off is None:off=map_bytes+len(pool);dictionary[key]=off;pool.extend(key)
                    struct.pack_into('<I',offsets,4*i,off)
                payload=offsets+pool;unique=len(dictionary)
                # 独立重建全部逻辑字节，不调用原生lookup。
                reconstructed=b''.join(payload[struct.unpack_from('<I',payload,4*i)[0]:struct.unpack_from('<I',payload,4*i)[0]+block] for i in range(len(direct)//block))
                if reconstructed!=direct:raise AssertionError('字典重建不同')
                del dictionary,reconstructed,offsets,pool
            header=b'M16D'+struct.pack('<7I',1,bits,count,len(payload),0,0,0)+struct.pack('<256I',*palette)
            path=out/f'rom-{bits}.bin';path.write_bytes(header+payload)
            stats[str(bits)]=dict(block_bytes=1<<bits if bits else None,unique_blocks=unique,file_bytes=path.stat().st_size,payload_bytes=len(payload),sha256=sha(path),export_seconds=time.perf_counter()-start)
        save(out/'export.json',dict(purpose=__doc__,environment=env(),baseline_library=str(a.baseline),baseline_sha256=sha(a.baseline),baseline_runtime_capacity=d.jshc_cc_model_bytes(h),logical_table_sha256=hashlib.sha256(direct).hexdigest(),palette_size=count,model_source='仅调用冻结a399四级稀疏模型；不读取照片、完整原LUT或gold构建',models=stats))
        print(json.dumps(stats,ensure_ascii=False))
    finally:d.jshc_cc_destroy(h)

def verify(a):
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    d=romlib(a.library);c=romlib(a.library.parent/'jshc_memory_c99.dll');rng=np.random.default_rng(20261023)
    lengths=[0,1,7,8,9,31,32,39,40,63,64,65,71,72,73,405,406,4095,4096,65535,65536,65537]
    expect=(a.data_root/'artifacts/cinema-current-anchor-accept-v1/cube.rgb').read_bytes()
    if hashlib.sha256(expect).hexdigest()!='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22':raise ValueError('gold SHA不同')
    expected=np.frombuffer(expect,dtype=np.uint8).reshape(-1,3);counts={};hashes={}
    for bits in (0,4,6,8,10):
        path=a.roms/f'rom-{bits}.bin';m,keep=loadrom(d,path);cm,ckeep=loadrom(c,path)
        cases=0
        for n in lengths:
            source=rng.integers(0,256,n*3,dtype=np.uint8);codes=source.reshape(-1,3).astype(np.uint32)
            indices=(codes[:,0]<<16)|(codes[:,1]<<8)|codes[:,2]
            target=expected[indices].reshape(-1)
            for offset in (0,1,7,31,63):
                for kernel,threads in ((0,1),(1,1),(1,4)):
                    for inplace in (False,True):
                        storage=np.full(n*3+offset+33,0xa7,dtype=np.uint8);output=storage[offset:offset+n*3]
                        if inplace:output[:]=source;src=output
                        else:src=source
                        if d.jshc_mem_apply_parallel(ct.byref(m),src.ctypes.data_as(U8),output.ctypes.data_as(U8),n,kernel,threads):raise AssertionError('映射拒绝')
                        if not np.array_equal(output,target) or not np.all(storage[:offset]==0xa7) or not np.all(storage[offset+n*3:]==0xa7):raise AssertionError('有限合同不符')
                        cases+=1
                storage=np.full(n*3+offset+33,0xa7,dtype=np.uint8);output=storage[offset:offset+n*3]
                if c.jshc_mem_apply(ct.byref(cm),source.ctypes.data_as(U8),output.ctypes.data_as(U8),n) or not np.array_equal(output,target):raise AssertionError('独立C99错误')
                cases+=1
        counts[str(bits)]=cases;hashes[str(bits)]={}
        for kernel,threads in ((0,1),(1,1),(1,4)):
            hasher=hashlib.sha256()
            for start in range(0,1<<24,1<<18):
                codes=np.arange(start,start+(1<<18),dtype=np.uint32);source=np.empty((len(codes),3),dtype=np.uint8)
                source[:,0]=codes>>16;source[:,1]=codes>>8;source[:,2]=codes
                output=np.empty_like(source)
                if d.jshc_mem_apply_parallel(ct.byref(m),source.ctypes.data_as(U8),output.ctypes.data_as(U8),len(codes),kernel,threads):raise AssertionError('全域拒绝')
                if not np.array_equal(output,expected[start:start+len(codes)]):raise AssertionError('全域不同')
                hasher.update(output)
            hashes[str(bits)][f'{kernel}_{threads}']=hasher.hexdigest()
        del keep,ckeep
    # 拒绝合同集中在一个完整格式上；每种损坏均重新prepare。
    raw=bytearray((a.roms/'rom-6.bin').read_bytes());rejects=0
    for offset,value in ((0,0),(4,2),(8,5),(12,0),(20,1),(1056,1)):
        bad=bytearray(raw);bad[offset]=value;buf=(ct.c_uint8*len(bad)).from_buffer(bad);model=Model()
        if not d.jshc_mem_prepare(ct.byref(model),buf,len(buf)):raise AssertionError('畸形ROM未拒绝')
        rejects+=1
    save(out/'results.json',dict(pass_=True,purpose=__doc__,environment=env(),library_sha256=sha(a.library),export_sha256=sha(a.roms/'export.json'),model_struct_bytes=ct.sizeof(Model),finite_cases=counts,full_domain_hashes=hashes,malformed_rejections=rejects,scope='固定a399四级，全部256^3颜色与各后端1/4线程逐字节等价；独立C99有限合同。未作性能或新模型精度声明。'))
    print(json.dumps({'pass':True,'cases':counts,'full_configurations':15},ensure_ascii=False))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=['export','verify'])
    p.add_argument('--output',type=Path,required=True);p.add_argument('--data-root',type=Path,required=True)
    p.add_argument('--baseline',type=Path);p.add_argument('--library',type=Path);p.add_argument('--roms',type=Path)
    a=p.parse_args();{'export':export,'verify':verify}[a.phase](a)
if __name__=='__main__':main()
