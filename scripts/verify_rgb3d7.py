"""C7BK实际32B ABI、8完整域/百图、128项正向与图像/ROM末端合同；不计性能。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import struct
import numpy as np
from rgb3d7_support import ROOT,U8,Model,PLAN,TABLE,TABLE_START,GUARD,PALETTE,ROM_BYTES,library,load,pack7,header,independent,sha,read,save,env
from bench_memory_rom import memory

def fixture(count):
    counts=np.full(512,count,dtype='<u2');table=bytearray(TABLE);palette=np.zeros((512,128),dtype='<u4')
    if count==128:
        palette[:]=np.arange(65536,dtype='<u4').reshape(512,128);palette[-1,-1]=0xffffff
        for begin in range(0,1<<24,1<<18):
            code=np.arange(begin,begin+(1<<18),dtype=np.uint32);ids=(code&31)|(((code>>8)&3)<<5);start=7*begin//8;table[start:start+7*len(code)//8]=pack7(ids)
    elif count==1:palette[:,0]=np.arange(512,dtype='<u4')
    else:raise ValueError(count)
    return header()+counts.tobytes()+table+bytes(4)+palette.tobytes()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('build','roms','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--rss',choices=['pure','desktop']);a=p.parse_args();plan=read(PLAN)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise AssertionError('冻结源变化')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();path=a.roms/'rgb3d7.bin';desktop=a.build/'jshc_rgb3d7.dll';pure=a.build/'jshc_rgb3d7_c99.dll'
    if a.rss:
        libpath=pure if a.rss=='pure' else desktop;d=library(libpath);model,keep=load(d,path);save(a.output/'rss.json',dict(label=a.rss,environment=env(),plan_sha256=sha(PLAN),library_sha256=sha(libpath),rom_sha256=sha(path),model_bytes=ct.sizeof(Model),rom_bytes=path.stat().st_size,resident=ct.sizeof(Model)+path.stat().st_size,before=before,prepared=memory(),scope='独立新进程，相同支持模块导入；只prepare无照片/夹具，不是纯核心RAM或prepare专属峰。'));return
    d=library(desktop);c=library(pure);m,keep=load(d,path);portable,pk=load(c,path);raw=path.read_bytes();rng=np.random.default_rng(202610247);finite=0;rejects=0;image_guards=0;rom_guards=0
    configs=[('c99',c,portable,0,1),('desktop_scalar',d,m,0,1),('avx2_1',d,m,1,1),('avx2_4',d,m,1,4)]
    def call(lib,model,source,target,n,k=1,t=1):
        source=ct.cast(source,U8);target=ct.cast(target,U8)
        return lib.jshc_mem_apply(ct.byref(model),source,target,n) if lib is c else lib.jshc_mem_apply_parallel(ct.byref(model),source,target,n,k,t)
    for n in (0,1,7,8,9,15,16,17,31,32,33,73,1023,1024,1025,4095,4096,4097):
        values=rng.integers(0,256,3*n,dtype=np.uint8);gold=independent(raw,values)
        for label,lib,model,k,t in configs:
            for same in (False,True):
                for offset in (0,1,3,7):
                    source=np.full(3*n+offset+17,0xa7,dtype=np.uint8);source[offset:offset+3*n]=values;target=source if same else np.full_like(source,0xa7)
                    if call(lib,model,source.ctypes.data+offset,target.ctypes.data+offset,n,k,t) or bytes(target[offset:offset+3*n])!=gold or not np.all(target[:offset]==0xa7) or not np.all(target[offset+3*n:]==0xa7):raise AssertionError('有限/原地/哨兵不同：'+label)
                    finite+=1
    for label,lib,model,k,t in configs:
        if call(lib,model,0,0,0,k,t):raise AssertionError('零长空指针未接受')
        finite+=1
    hashes={}
    for label,lib,model,k,t in configs:
        for same in (False,True):
            digest=hashlib.sha256()
            for begin in range(0,1<<24,1<<18):
                codes=np.arange(begin,begin+(1<<18),dtype=np.uint32);source=np.empty((len(codes),3),dtype=np.uint8);source[:,0]=codes>>16;source[:,1]=codes>>8;source[:,2]=codes;target=source if same else np.empty_like(source)
                if call(lib,model,source.ctypes.data,target.ctypes.data,len(codes),k,t):raise AssertionError('完整域调用失败')
                digest.update(target)
            name=label+('_inplace' if same else '_outplace');hashes[name]=digest.hexdigest()
            if hashes[name]!='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22':raise AssertionError('完整域SHA不同：'+name)
    photo=Path(plan['photos']);input_hash=hashlib.sha256();photo_hashes={label+('_inplace' if same else '_outplace'):hashlib.sha256() for label,lib,model,k,t in configs for same in (False,True)}
    with photo.open('rb') as stream:
        for image in range(100):
            pixels=stream.read(1024*768*3)
            if len(pixels)!=1024*768*3:raise AssertionError('百图截断')
            input_hash.update(pixels);values=np.frombuffer(pixels,dtype=np.uint8)
            for label,lib,model,k,t in configs:
                for same in (False,True):
                    target=values.copy() if same else np.empty_like(values)
                    if call(lib,model,target.ctypes.data if same else values.ctypes.data,target.ctypes.data,1024*768,k,t):raise AssertionError('百图调用失败')
                    photo_hashes[label+('_inplace' if same else '_outplace')].update(target)
        if stream.read(1):raise AssertionError('百图多余字节')
    if input_hash.hexdigest()!=plan['photos_sha256']:raise AssertionError('照片输入身份不同')
    photo_hashes={k:v.hexdigest() for k,v in photo_hashes.items()}
    if set(photo_hashes.values())!={'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'}:raise AssertionError('百图输出SHA不同')
    def bad(data):
        nonlocal rejects
        buffer=(ct.c_uint8*len(data)).from_buffer(data);model=Model()
        for lib in (d,c):
            if not lib.jshc_mem_prepare(ct.byref(model),buffer,len(data)) or any(bytes(model)):raise AssertionError('非法ROM未清零拒绝')
            rejects+=1
    for n in (0,1,31,1055,len(raw)-1):bad(bytearray(raw[:n]))
    for offset,value in ((4,2),(8,511),(12,6),(16,TABLE-1),(20,2),(24,127),(28,1),(GUARD,1),(PALETTE,0xffffffff)):
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);bad(data)
    for value in (0,129,65535):
        data=bytearray(raw);struct.pack_into('<H',data,32,value);bad(data)
    data=bytearray(raw);data[:4]=b'C6BK';bad(data)
    first_count=struct.unpack_from('<H',raw,32)[0];data=bytearray(raw);data[TABLE_START]=(data[TABLE_START]&128)|first_count;bad(data)
    data=bytearray(raw);struct.pack_into('<I',data,PALETTE+4*first_count,1);bad(data)
    for offset in (1,3,7,31):
        storage=bytearray(offset)+raw;buffer=(ct.c_uint8*len(storage)).from_buffer(storage);model=Model()
        if d.jshc_mem_prepare(ct.byref(model),ct.addressof(buffer)+offset,len(raw)):raise AssertionError('非对齐prepare失败')
        values=rng.integers(0,256,4097*3,dtype=np.uint8);target=np.empty_like(values)
        if call(d,model,values.ctypes.data,target.ctypes.data,4097,1,4) or bytes(target)!=independent(raw,values):raise AssertionError('非对齐输出不同')
        finite+=1
    data=bytearray(raw);buffer=(ct.c_uint8*len(data)).from_buffer(data);original=bytes(data);overlap=ct.cast(ct.addressof(buffer)+32,ct.POINTER(Model))
    for lib in (d,c):
        if not lib.jshc_mem_prepare(overlap,buffer,len(data)) or bytes(data)!=original:raise AssertionError('prepare重叠不是无写拒绝')
        rejects+=1
    storage=np.full(256,0x5a,dtype=np.uint8);addr=storage.ctypes.data;maximum=(1<<(8*ct.sizeof(ct.c_void_p)))-1
    for lib,model in ((d,m),(c,portable)):
        for src,dst,n in ((0,addr,1),(addr,0,1),(addr,addr+1,16),(addr+1,addr,16),(addr,ct.addressof(model),1),(addr,ct.cast(model.blob,ct.c_void_p).value,1),(addr,addr,maximum//3+1),(maximum-1,addr,1)):
            original=bytes(storage)
            if not call(lib,model,src,dst,n) or bytes(storage)!=original:raise AssertionError('IO越界/重叠未无写拒绝')
            rejects+=1
    k32=ct.WinDLL('kernel32',use_last_error=True);alloc=k32.VirtualAlloc;alloc.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];alloc.restype=ct.c_void_p;protect=k32.VirtualProtect;protect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)];free=k32.VirtualFree;free.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32]
    for n in (1,7,8,9,31,32,40,64,72,73,405,406,1023,1024,1025,4096,65536,65537):
        span=((3*n+4095)//4096)*4096;address=alloc(None,span+4096,0x3000,4);output=alloc(None,span+4096,0x3000,4)
        if not address or not output:raise OSError(ct.get_last_error())
        try:
            old=ct.c_uint32()
            if not protect(address+span,4096,1,ct.byref(old)) or not protect(output+span,4096,1,ct.byref(old)):raise OSError(ct.get_last_error())
            src=address+span-3*n;dst=output+span-3*n;values=rng.integers(0,256,3*n,dtype=np.uint8);gold=independent(raw,values)
            for label,lib,model,k,t in configs:
                ct.memmove(src,values.ctypes.data,3*n)
                if call(lib,model,src,dst,n,k,t) or ct.string_at(dst,3*n)!=gold or call(lib,model,src,src,n,k,t) or ct.string_at(src,3*n)!=gold:raise AssertionError('双图像保护页不同：'+label)
                image_guards+=2
        finally:
            if not free(address,0,0x8000) or not free(output,0,0x8000):raise OSError(ct.get_last_error())
    fixture_records={}
    for label,content in (('actual',raw),('count1',fixture(1)),('count128',fixture(128))):
        pages=(len(content)+4095)//4096;address=alloc(None,(pages+1)*4096,0x3000,4)
        if not address:raise OSError(ct.get_last_error())
        try:
            old=ct.c_uint32()
            if not protect(address+pages*4096,4096,1,ct.byref(old)):raise OSError(ct.get_last_error())
            start=address+pages*4096-len(content);ct.memmove(start,content,len(content))
            if not protect(address,pages*4096,2,ct.byref(old)):raise OSError(ct.get_last_error())
            model=Model()
            for lib in (d,c):
                if lib.jshc_mem_prepare(ct.byref(model),start,len(content)):raise AssertionError('正向ROM末端prepare失败')
            b=np.repeat(np.arange(512,dtype=np.uint32),128);local=np.tile(np.arange(128,dtype=np.uint32),512);values=np.empty((len(b),3),dtype=np.uint8);values[:,0]=((b&7)<<5)|(local&31);values[:,1]=(((b>>3)&7)<<5)|28|(local>>5);values[:,2]=((b>>6)<<5)|31;values=values.reshape(-1);gold=independent(content,values)
            if label=='count128' and gold[-3:]!=b'\xff\xff\xff':raise AssertionError('未命中最后palette词')
            for backend,lib,unused,k,t in configs:
                for same in (False,True):
                    target=values.copy() if same else np.empty_like(values)
                    if call(lib,model,target.ctypes.data if same else values.ctypes.data,target.ctypes.data,len(values)//3,k,t) or bytes(target)!=gold:raise AssertionError('ROM末端/全部本地槽不同：'+label+'/'+backend)
                    rom_guards+=1
            fixture_records[label]=dict(bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),input_cases=len(values)//3,expected_sha256=hashlib.sha256(gold).hexdigest(),bank_count=512,maximum_legal_local_id=127 if label=='count128' else None)
        finally:
            if not free(address,0,0x8000):raise OSError(ct.get_last_error())
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,environment=env(),plan_sha256=sha(PLAN),libraries={str(x):sha(x) for x in (desktop,pure)},model_size=ct.sizeof(Model),rom_bytes=len(raw),rom_sha256=sha(path),resident=len(raw)+ct.sizeof(Model),finite=finite,refusals=rejects,image_guards=image_guards,rom_guards=rom_guards,fixtures=fixture_records,hashes=hashes,photo_hashes=photo_hashes,photo_input_sha256=input_hash.hexdigest(),before=before,after=memory(),scope='8完整域及8百图输出不变；count128夹具覆盖每bank全部128槽、7bit八起点和最后ROM词，只读/NOACCESS边界；峰值含Python/库/夹具，质量非性能，无WASM/实板。'))
    print(dict(passed=True,model_size=ct.sizeof(Model),resident=len(raw)+ct.sizeof(Model),finite=finite,refusals=rejects,image_guards=image_guards,rom_guards=rom_guards))
if __name__=='__main__':main()
