"""固定P4单版九模式完整域/百图及独立u64、IO/ROM guard质量；无吞吐。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import struct
import numpy as np
from page_id16_common import ROOT,PLAN,PageModel,Borrowed,library,call,checked_plan,sha,save,env,API,query,snapshot
K32=ct.WinDLL('kernel32',use_last_error=True)
ALLOC=K32.VirtualAlloc;ALLOC.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];ALLOC.restype=ct.c_void_p
PROTECT=K32.VirtualProtect;PROTECT.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)];PROTECT.restype=ct.c_int
FREE=K32.VirtualFree;FREE.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32];FREE.restype=ct.c_int
class Guard:
    def __init__(self,length):
        self.length=length;self.span=((length+4095)//4096)*4096;self.base=ALLOC(None,self.span+4096,0x3000,4)
        if not self.base:raise ct.WinError(ct.get_last_error())
        self.start=self.base+self.span-length;old=ct.c_uint32()
        if not PROTECT(self.base+self.span,4096,1,ct.byref(old)):raise ct.WinError(ct.get_last_error())
    def readonly(self):
        old=ct.c_uint32()
        if not PROTECT(self.base,self.span,2,ct.byref(old)):raise ct.WinError(ct.get_last_error())
    def close(self):
        if self.base:
            if not FREE(self.base,0,0x8000):raise ct.WinError(ct.get_last_error())
            self.base=None
    def __enter__(self):return self
    def __exit__(self,*unused):self.close()
def codes(values):
    rgb=np.asarray(values,dtype=np.uint8).reshape(-1,3).astype(np.uint64)
    return rgb[:,0]|(rgb[:,1]<<8)|(rgb[:,2]<<16)
def pixels(values):
    value=np.asarray(values,dtype=np.uint64);rgb=np.empty((len(value),3),dtype=np.uint8);rgb[:,0]=value;rgb[:,1]=value>>8;rgb[:,2]=value>>16;return rgb.reshape(-1)
def fixture(count,unique):
    data=bytearray(9248+unique*4096+4);data[:32]=b'P4ID'+struct.pack('<7I',1,12,count,1<<24,unique,0,0)
    for color in range(count):struct.pack_into('<I',data,32+4*color,0x030201 if count==1 else color*0x10101)
    for page in range(4096):struct.pack_into('<H',data,1056+2*page,page%unique)
    block=bytes(4096) if count==1 else bytes(range(256))*16
    for page in range(unique):data[9248+page*4096:9248+(page+1)*4096]=block
    return data
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=checked_plan();a.output.mkdir(parents=True,exist_ok=False);before=snapshot();d=library(a.build/'jshc_page_id16.dll',True);c=library(a.build/'jshc_page_id16_c99.dll',False);rng=np.random.default_rng(20261024)
    export=__import__('json').loads((a.rom.parent/'export.json').read_text(encoding='utf-8'))
    if a.rom.stat().st_size!=12633124 or sha(a.rom)!=export['output']['sha256'] or export['plan_sha256']!=sha(PLAN):raise AssertionError('实际ROM/冻结计划不同')
    old=np.memmap(plan['original_rom'],dtype=np.uint8,mode='r');old_palette=old[32:1056].reshape(256,4)
    def oracle(values):
        key=codes(values);ids=old[1056+key];return old_palette[ids,:3].reshape(-1).copy()
    full={};photo={};finite=0;rejections=0;image_guards=0;rom_guards=0;unaligned_rom=0;fixture_receipts={}
    with Borrowed(a.rom,d) as owner,Borrowed(a.rom,c) as portable:
        configs=[('core_out',c,portable.model,None,1,False)]
        for k in (0,1):
            for t in (1,4):
                for same in (False,True):configs.append((('c99' if k==0 else 'avx')+str(t)+('_in' if same else '_out'),d,owner.model,k,t,same))
        finite_configs=configs+[('core_in',c,portable.model,None,1,True)]
        actual_abi=ct.sizeof(PageModel);actual_capacity=a.rom.stat().st_size+actual_abi
        if actual_abi!=40 or 16779328-actual_capacity<(1<<20) or owner.model.blob_bytes!=a.rom.stat().st_size or owner.model.page_ids!=owner.model.blob+1056 or owner.model.pool!=owner.model.blob+9248 or owner.model.palette!=owner.model.blob+32:raise AssertionError('实际ABI/账本/借用字段不同')
        if query(owner.model.blob)['Protect']!=2 or query(owner.model.blob+owner.model.blob_bytes-1)['Protect']!=2:raise AssertionError('实际ROM不是只读')
        for n in (0,1,7,8,9,31,32,40,64,72,73,405,406,1023,1024,1025,4095,4096,4097,65535,65536,65537):
            values=rng.integers(0,256,3*n,dtype=np.uint8);expected=oracle(values)
            for label,lib,model,k,t,same in finite_configs:
                for offset in (0,1,3,7):
                    source=np.full(3*n+offset+17,0xa7,dtype=np.uint8);source[offset:offset+3*n]=values;target=source if same else np.full_like(source,0xa7)
                    if call(lib,model,source.ctypes.data+offset,target.ctypes.data+offset,n,k,t) or not np.array_equal(target[offset:offset+3*n],expected) or np.any(target[:offset]!=0xa7) or np.any(target[offset+3*n:]!=0xa7):raise AssertionError('有限/u64/同址/哨兵失败：'+label)
                    finite+=1
        for label,lib,model,k,t,same in finite_configs:
            if call(lib,model,0,0,0,k,t):raise AssertionError('有效Model零长NULL失败')
            finite+=1
        hashes={label:hashlib.sha256() for label,*_ in configs};reference=hashlib.sha256()
        for begin in range(0,1<<24,1<<18):
            enumerated=np.arange(begin,begin+(1<<18),dtype=np.uint64);values=np.empty((len(enumerated),3),dtype=np.uint8);values[:,0]=enumerated>>16;values[:,1]=enumerated>>8;values[:,2]=enumerated;values=values.reshape(-1);expected=oracle(values);reference.update(expected)
            for label,lib,model,k,t,same in configs:
                target=values.copy() if same else np.empty_like(values)
                if call(lib,model,target.ctypes.data if same else values.ctypes.data,target.ctypes.data,len(enumerated),k,t) or not np.array_equal(target,expected):raise AssertionError('完整域/u64失败：'+label)
                hashes[label].update(target)
        full={name:value.hexdigest() for name,value in hashes.items()}
        if reference.hexdigest()!='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22' or set(full.values())!={reference.hexdigest()}:raise AssertionError('完整域原输出身份不同')
        photo_hashes={label:hashlib.sha256() for label,*_ in configs};input_hash=hashlib.sha256();images=[]
        with Path(plan['photos']).open('rb') as stream:
            for index in range(100):
                raw=stream.read(1024*768*3)
                if len(raw)!=1024*768*3:raise AssertionError('照片截断')
                input_hash.update(raw);values=np.frombuffer(raw,dtype=np.uint8);expected=oracle(values);row=dict(image=index,oracle_sha256=hashlib.sha256(expected).hexdigest(),modes={})
                for label,lib,model,k,t,same in configs:
                    target=values.copy() if same else np.empty_like(values)
                    if call(lib,model,target.ctypes.data if same else values.ctypes.data,target.ctypes.data,1024*768,k,t) or not np.array_equal(target,expected):raise AssertionError('逐图/u64失败：'+label)
                    photo_hashes[label].update(target);row['modes'][label]=hashlib.sha256(target).hexdigest()
                images.append(row)
            if stream.read(1):raise AssertionError('照片多余字节')
        photo={name:value.hexdigest() for name,value in photo_hashes.items()}
        if input_hash.hexdigest()!=plan['photos_sha256'] or set(photo.values())!={'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'}:raise AssertionError('百图原身份不同')
        storage=np.full(256,0x5a,dtype=np.uint8);address=storage.ctypes.data;maximum=(1<<(8*ct.sizeof(ct.c_void_p)))-1
        for label,lib,model,k,t,same in finite_configs:
            for src,dst,n in ((0,address,1),(address,0,1),(address,address+1,16),(address+1,address,16),(ct.addressof(model),address,1),(address,ct.addressof(model),1),(model.blob,address,1),(address,model.blob,1),(address,address,maximum//3+1),(maximum-1,address,1)):
                prior=bytes(storage)
                if not call(lib,model,src,dst,n,k,t) or bytes(storage)!=prior:raise AssertionError('范围/重叠未无写拒绝：'+label)
                rejections+=1
        for kernel,threads in ((-1,1),(2,1),(0,0),(0,257),(1,0),(1,257)):
            prior=bytes(storage)
            if not call(d,owner.model,address,address,1,kernel,threads) or bytes(storage)!=prior:raise AssertionError('无效kernel/threads未无写拒绝')
            rejections+=1
        for n in (1,7,8,9,31,32,40,64,72,73,405,406,1023,1024,1025,4096,65536,65537):
            values=rng.integers(0,256,3*n,dtype=np.uint8);expected=oracle(values).tobytes()
            with Guard(3*n) as source,Guard(3*n) as target:
                for label,lib,model,k,t,same in configs:
                    ct.memmove(source.start,values.ctypes.data,3*n)
                    dest=source.start if same else target.start
                    if call(lib,model,source.start,dest,n,k,t) or ct.string_at(dest,3*n)!=expected:raise AssertionError('九模式source/dst精确guard失败：'+label)
                    image_guards+=1
                ct.memmove(source.start,values.ctypes.data,3*n)
                if call(c,portable.model,source.start,source.start,n) or ct.string_at(source.start,3*n)!=expected:raise AssertionError('独立core同址guard失败')
                image_guards+=1
        actual=a.rom.read_bytes();probe=np.concatenate([pixels(np.array([0,1,4094,4095,4096,4097,(1<<24)-2,(1<<24)-1],dtype=np.uint64)),pixels((np.arange(4096,dtype=np.uint64)<<12)|4095)])
        for kind in ('actual','count1','count256','max4096'):
            content=actual if kind=='actual' else fixture(1 if kind=='count1' else 256,4096 if kind=='max4096' else 1);view=np.frombuffer(content,dtype=np.uint8);maps=np.frombuffer(content,dtype='<u2',count=4096,offset=1056).astype(np.uint64);palette=view[32:1056].reshape(256,4);key=codes(probe);ids=view[9248+maps[key>>12]*4096+(key&4095)];expected=palette[ids,:3].reshape(-1).tobytes()
            if kind in ('count256','max4096') and expected[21:24]!=b'\xff\xff\xff':raise AssertionError('未命中末ID255')
            with Guard(len(content)) as area:
                buffer=(ct.c_uint8*len(content)).from_buffer_copy(content);ct.memmove(area.start,buffer,len(content));del buffer;area.readonly();model=PageModel()
                if d.jshc_p4_prepare(ct.byref(model),area.start,len(content)):raise AssertionError('ROM精确guard prepare失败')
                for label,lib,unused,k,t,same in configs:
                    target=probe.copy() if same else np.empty_like(probe)
                    if call(lib,model,target.ctypes.data if same else probe.ctypes.data,target.ctypes.data,len(probe)//3,k,t) or bytes(target)!=expected:raise AssertionError('九模式ROM尾/map/palette guard失败：'+kind+label)
                    rom_guards+=1
                ct.memset(ct.byref(model),0,ct.sizeof(model))
            fixture_receipts[kind]=dict(bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),all_palette_slots=256,probe_pixels=len(probe)//3,expected_sha256=hashlib.sha256(expected).hexdigest())
        expected=oracle(probe).tobytes()
        for offset in range(8):
            content=bytearray(len(actual)+offset);content[offset:]=actual;array=(ct.c_uint8*len(content)).from_buffer(content);model=PageModel()
            if d.jshc_p4_prepare(ct.byref(model),ct.addressof(array)+offset,len(actual)):raise AssertionError('非对齐ROM拒绝')
            for label,lib,unused,k,t,same in configs:
                target=probe.copy() if same else np.empty_like(probe)
                if call(lib,model,target.ctypes.data if same else probe.ctypes.data,target.ctypes.data,len(probe)//3,k,t) or bytes(target)!=expected:raise AssertionError('非对齐ROM输出失败')
                unaligned_rom+=1
            ct.memset(ct.byref(model),0,ct.sizeof(model));del array,content
        # 固定小夹具逐项变异，不把24份大ROM同时常驻。
        small=fixture(1,1);mutations=[('magic',0,b'X'),('version',4,struct.pack('<I',2)),('shift',8,struct.pack('<I',11)),('count0',12,struct.pack('<I',0)),('count257',12,struct.pack('<I',257)),('logical',16,struct.pack('<I',0)),('unique0',20,struct.pack('<I',0)),('unique4097',20,struct.pack('<I',4097)),('reserved1',24,b'\x01'),('reserved2',28,b'\x01'),('palette-alpha',35,b'\xff'),('unused-palette',36,b'\x01'),('first-map4096',1056,struct.pack('<H',4096)),('last-map65535',1056+8190,struct.pack('<H',65535)),('pool-id',9248,b'\x01'),('guard',len(small)-1,b'\x01')];rejected_formats=[]
        for name,offset,raw in mutations:
            content=bytearray(small);content[offset:offset+len(raw)]=raw;array=(ct.c_uint8*len(content)).from_buffer(content);model=PageModel();ct.memset(ct.byref(model),0xa5,ct.sizeof(model))
            if not d.jshc_p4_prepare(ct.byref(model),ct.addressof(array),len(content)) or any(bytes(model)):raise AssertionError('畸形未拒绝或Model未清零：'+name)
            rejected_formats.append(name);del array,content
        for length in (0,31,1056,len(small)-1,len(small)+1):
            content=bytearray(small)+b'\x00';array=(ct.c_uint8*len(content)).from_buffer(content);model=PageModel()
            if not d.jshc_p4_prepare(ct.byref(model),ct.addressof(array),length) or any(bytes(model)):raise AssertionError('畸形长度未拒绝')
            rejected_formats.append('length'+str(length));del array,content
        # Model与readonly blob重叠必须先无写拒绝；其余异常prepare应清零。
        prior=ct.string_at(owner.model.blob,40)
        if not d.jshc_p4_prepare(ct.cast(owner.model.blob,ct.POINTER(PageModel)),owner.model.blob,len(actual)) or ct.string_at(owner.model.blob,40)!=prior:raise AssertionError('Model重叠ROM未无写拒绝')
        rejections+=1
        bad=PageModel();ct.memset(ct.byref(bad),0xa5,ct.sizeof(bad))
        if not d.jshc_p4_prepare(ct.byref(bad),maximum-1,3) or any(bytes(bad)):raise AssertionError('溢出blob范围未清零拒绝')
        rejections+=1
        for pointer,length in ((None,0),(None,len(actual))):
            ct.memset(ct.byref(bad),0xa5,ct.sizeof(bad))
            if not d.jshc_p4_prepare(ct.byref(bad),pointer,length) or any(bytes(bad)):raise AssertionError('NULL blob失败未清零')
            rejections+=1
        if not d.jshc_p4_prepare(None,owner.model.blob,len(actual)):raise AssertionError('NULL Model未拒绝')
        rejections+=1
    if any(bytes(owner.model)) or any(bytes(portable.model)) or not owner.view.closed or not portable.view.closed:raise AssertionError('ROM借用关闭未清零')
    owner.close();portable.close()
    for lib in (c,d):
        if not call(lib,owner.model,0,0,0):raise AssertionError('已关闭Model未拒绝')
        rejections+=1
    del old_palette,old
    if any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('原输入在质量期间改变')
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,plan_sha256=sha(PLAN),environment=env(),rom_sha256=sha(a.rom),library_sha256=sha(a.build/'jshc_page_id16.dll'),standalone_sha256=sha(a.build/'jshc_page_id16_c99.dll'),actual_rom_bytes=a.rom.stat().st_size,actual_model_bytes=actual_abi,actual_capacity=actual_capacity,net_saving=16779328-actual_capacity,full_hashes=full,photo_hashes=photo,photo_input_sha256=input_hash.hexdigest(),photos=images,finite=finite,io_rejections=rejections,image_guards=image_guards,rom_guards=rom_guards,unaligned_rom=unaligned_rom,fixture_receipts=fixture_receipts,rejected_formats=rejected_formats,closed_models_zero=True,per_image_heap_scratch=0,before=before,after=snapshot(),scope='标准C99/AVX2仅本机质量，未性能/WASM/BE运行；全部原输出等价不等于原误差为0；真实ABI/容量不含Python/库/OS且RSS含统计/夹具。'))
    print(dict(passed=True,actual_capacity=actual_capacity,finite=finite,image_guards=image_guards,rom_guards=rom_guards,unaligned_rom=unaligned_rom))
if __name__=='__main__':
    try:main()
    except BaseException as error:
        # 失败由单次driver保留stderr/returncode，不在脚本内修后重采。
        raise
