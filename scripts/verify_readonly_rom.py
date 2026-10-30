"""新RO加载方式的8完整域/8百图与原M16D边界，质量失败即停止。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import struct
import numpy as np
from win_readonly_rom import API,PLAN,Model,FileView,U8,library,checked_plan,call,query,sha,read,save,env,memory,snapshot

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=checked_plan();a.output.mkdir(parents=True,exist_ok=False)
    before=memory();d=library(plan['library']);finite=0;rejections=0;lifecycle=[];image_guards=0;rom_guards=0;rng=np.random.default_rng(20261024);handles_before=snapshot()['process_handles']
    def reject_address(owner):
        try:owner.address
        except RuntimeError:return
        raise AssertionError('关闭后仍暴露地址')
    # 真实缺失/零长/畸形文件；不动原ROM，所有文件均位于新输出目录。
    zero=a.output/'zero.bin';zero.write_bytes(b'');bad=a.output/'bad.bin';bad.write_bytes(bytes(64))
    for mode in ('cow','readonly'):
        for path in (a.output/'missing.bin',zero):
            try:FileView(path,mode)
            except (OSError,ValueError):rejections+=1
            else:raise AssertionError('无效文件未拒绝')
        broken=FileView(bad,mode)
        try:broken.prepare(d)
        except ValueError:rejections+=1
        else:raise AssertionError('畸形M16D未拒绝')
        if not broken.closed or any(any(bytes(model)) for model in broken.models):raise AssertionError('prepare失败未关闭并清零')
        reject_address(broken);broken.close()
    # 注入WinAPI前四个失败位置，核精确清理顺序；不是实际OS错误覆盖的替代。
    class FailingAPI:
        def __init__(self,stage):self.stage=stage;self.events=[]
        def create_file(self,*args):self.events.append('file');ct.set_last_error(5);return INVALID if self.stage=='file' else 11
        def size(self,handle,value):self.events.append('size');ct.cast(value,ct.POINTER(ct.c_int64)).contents.value=16778272;ct.set_last_error(5);return self.stage!='size'
        def create_mapping(self,*args):self.events.append('mapping');ct.set_last_error(5);return 0 if self.stage=='mapping' else 22
        def map_view(self,*args):self.events.append('view');ct.set_last_error(5);return 0
        def close(self,handle):self.events.append('close'+str(handle));return 1
        def unmap(self,address):raise AssertionError('失败时无合法view可解映射')
    INVALID=(1<<(8*ct.sizeof(ct.c_void_p)))-1
    expected={'file':['file'],'size':['file','size','close11'],'mapping':['file','size','mapping','close11'],'view':['file','size','mapping','view','close22','close11']}
    for stage in expected:
        fake=FailingAPI(stage)
        try:FileView(plan['rom'],'readonly',_api=fake)
        except OSError:pass
        else:raise AssertionError('注入失败未传播')
        if fake.events!=expected[stage]:raise AssertionError('失败清理顺序不同')
        lifecycle.append(dict(injected_stage=stage,events=fake.events))
    class RetryAPI(FailingAPI):
        def __init__(self,stage):super().__init__('never');self.failed_stage=stage;self.failures=0
        def map_view(self,*args):return 4096
        def unmap(self,address):
            if self.failed_stage=='unmap' and not self.failures:self.failures+=1;ct.set_last_error(5);return 0
            return 1
        def close(self,handle):
            if self.failed_stage=='close' and handle==22 and not self.failures:self.failures+=1;ct.set_last_error(5);return 0
            return 1
    for stage in ('unmap','close'):
        fake=RetryAPI(stage);owner=FileView(plan['rom'],'readonly',_api=fake)
        try:owner.close()
        except OSError:pass
        else:raise AssertionError('清理失败未传播')
        if owner.closed:raise AssertionError('失败资源被误标为全清理')
        reject_address(owner);owner.close()
        if not owner.closed:raise AssertionError('失败资源未保留供显式重试')
        lifecycle.append(dict(injected_cleanup_stage=stage,failed_then_explicit_retry=True))
    handles_after=snapshot()['process_handles']
    if handles_before!=handles_after:raise AssertionError('失败合同后句柄数变化')
    configs=[('c99_1',0,1),('c99_4',0,4),('avx_1',1,1),('avx_4',1,4)]
    with FileView(plan['rom'],'readonly') as owner:
        model=owner.prepare(d);address=owner.address;length=owner.length
        if length!=16778272 or ct.sizeof(Model)!=1056 or query(address)['Protect']!=2 or query(address+length-1)['Protect']!=2:raise AssertionError('实际只读/容量不同')
        raw=np.ctypeslib.as_array((ct.c_uint8*length).from_address(address))
        def gold(values,content=raw):
            source=np.asarray(values,dtype=np.uint8).reshape(-1,3);codes=source[:,0].astype(np.uint32)|(source[:,1].astype(np.uint32)<<8)|(source[:,2].astype(np.uint32)<<16);ids=content[1056+codes];return content[32:1056].reshape(256,4)[ids,:3].tobytes()
        # owner拒绝外部写打开；不对源文件进行任何写入。
        writer=API.create_file(str(Path(plan['rom']).resolve()),0x40000000,1,None,3,0x80,None)
        if writer not in (None,INVALID):API.close(writer);raise AssertionError('打开中的只读owner没有拒绝写共享')
        writer_error=ct.get_last_error()
        if writer_error!=32:raise AssertionError('预期共享冲突未出现')
        rejections+=1
        for n in (0,1,7,8,9,15,16,17,31,32,33,73,1023,1024,1025,4095,4096,4097):
            values=rng.integers(0,256,3*n,dtype=np.uint8);expected_rgb=gold(values)
            for label,k,t in configs:
                for same in (False,True):
                    for offset in (0,1,3,7):
                        source=np.full(3*n+offset+17,0xa7,dtype=np.uint8);source[offset:offset+3*n]=values;target=source if same else np.full_like(source,0xa7)
                        if call(d,model,source.ctypes.data+offset,target.ctypes.data+offset,n,k,t) or bytes(target[offset:offset+3*n])!=expected_rgb or not np.all(target[:offset]==0xa7) or not np.all(target[offset+3*n:]==0xa7):raise AssertionError('有限/同址/哨兵不同')
                        finite+=1
        for label,k,t in configs:
            if call(d,model,0,0,0,k,t):raise AssertionError('零长NULL被拒绝')
            finite+=1
        hashes={}
        for label,k,t in configs:
            for same in (False,True):
                digest=hashlib.sha256()
                for begin in range(0,1<<24,1<<18):
                    codes=np.arange(begin,begin+(1<<18),dtype=np.uint32);source=np.empty((len(codes),3),dtype=np.uint8);source[:,0]=codes>>16;source[:,1]=codes>>8;source[:,2]=codes;target=source if same else np.empty_like(source)
                    if call(d,model,source.ctypes.data,target.ctypes.data,len(codes),k,t):raise AssertionError('完整域调用失败')
                    digest.update(target)
                hashes[label+('_in' if same else '_out')]=digest.hexdigest()
        if len(hashes)!=8 or set(hashes.values())!={'3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'}:raise AssertionError('完整域身份不同')
        photos={name:hashlib.sha256() for name in hashes};input_hash=hashlib.sha256()
        with Path(plan['photos']).open('rb') as stream:
            for image in range(100):
                pixels=stream.read(1024*768*3)
                if len(pixels)!=1024*768*3:raise AssertionError('照片截断')
                input_hash.update(pixels);values=np.frombuffer(pixels,dtype=np.uint8)
                for label,k,t in configs:
                    for same in (False,True):
                        target=values.copy() if same else np.empty_like(values)
                        if call(d,model,target.ctypes.data if same else values.ctypes.data,target.ctypes.data,1024*768,k,t):raise AssertionError('百图失败')
                        photos[label+('_in' if same else '_out')].update(target)
            if stream.read(1):raise AssertionError('照片多余')
        photo_hashes={key:value.hexdigest() for key,value in photos.items()}
        if input_hash.hexdigest()!=plan['photos_sha256'] or set(photo_hashes.values())!={'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'}:raise AssertionError('百图身份不同')
        storage=np.full(256,0x5a,dtype=np.uint8);addr=storage.ctypes.data;maximum=(1<<(8*ct.sizeof(ct.c_void_p)))-1
        for label,k,t in configs:
            for src,dst,n in ((0,addr,1),(addr,0,1),(addr,addr+1,16),(addr+1,addr,16),(addr,ct.addressof(model),1),(addr,address,1),(addr,addr,maximum//3+1),(maximum-1,addr,1)):
                original=bytes(storage)
                if not call(d,model,src,dst,n,k,t) or bytes(storage)!=original:raise AssertionError('IO不曾无写拒绝')
                rejections+=1
        k32=ct.WinDLL('kernel32',use_last_error=True);alloc=k32.VirtualAlloc;alloc.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];alloc.restype=ct.c_void_p;protect=k32.VirtualProtect;protect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)];free=k32.VirtualFree;free.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32]
        for n in (1,7,8,9,31,32,40,64,72,73,405,406,1023,1024,1025,4096,65536,65537):
            span=((3*n+4095)//4096)*4096;source_area=alloc(None,span+4096,0x3000,4);target_area=alloc(None,span+4096,0x3000,4)
            if not source_area or not target_area:raise ct.WinError(ct.get_last_error())
            try:
                old=ct.c_uint32()
                if not protect(source_area+span,4096,1,ct.byref(old)) or not protect(target_area+span,4096,1,ct.byref(old)):raise ct.WinError(ct.get_last_error())
                src=source_area+span-3*n;dst=target_area+span-3*n;values=rng.integers(0,256,3*n,dtype=np.uint8);expected_rgb=gold(values)
                for label,k,t in configs:
                    ct.memmove(src,values.ctypes.data,3*n)
                    if call(d,model,src,dst,n,k,t) or ct.string_at(dst,3*n)!=expected_rgb or call(d,model,src,src,n,k,t) or ct.string_at(src,3*n)!=expected_rgb:raise AssertionError('输入/输出guard失败')
                    image_guards+=2
            finally:
                if not free(source_area,0,0x8000) or not free(target_area,0,0x8000):raise ct.WinError(ct.get_last_error())
        # 实际文件view按页取整，不能冒称EOF字节后NOACCESS。另用相同原ROM复制到只读guard夹具。
        fixtures={}
        for kind in ('actual','count1','count256'):
            pages=(length+4095)//4096;area=alloc(None,(pages+1)*4096,0x3000,4)
            if not area:raise ct.WinError(ct.get_last_error())
            try:
                old=ct.c_uint32();start=area+pages*4096-length
                if kind=='actual':ct.memmove(start,address,length)
                else:
                    content=bytearray(length);content[:32]=b'M16D'+struct.pack('<7I',1,0,1 if kind=='count1' else 256,1<<24,0,0,0)
                    for item in range(256 if kind=='count256' else 1):struct.pack_into('<I',content,32+4*item,0xffffff if item==255 else item*65537)
                    if kind=='count256':content[1056:]=bytes(range(256))*(1<<16)
                    source=(ct.c_uint8*length).from_buffer(content);ct.memmove(start,source,length);del source,content
                if not protect(area+pages*4096,4096,1,ct.byref(old)) or not protect(area,pages*4096,2,ct.byref(old)):raise ct.WinError(ct.get_last_error())
                guarded=Model()
                if d.jshc_mem_prepare(ct.byref(guarded),start,length):raise AssertionError('ROM guard prepare失败')
                indices=np.arange(65536,dtype=np.uint32);codes=(indices<<8)|(indices&255);values=np.empty((len(codes),3),dtype=np.uint8);values[:,0]=codes;values[:,1]=codes>>8;values[:,2]=codes>>16;values=values.reshape(-1);fixture_raw=np.ctypeslib.as_array((ct.c_uint8*length).from_address(start));expected_rgb=gold(values,fixture_raw)
                if kind=='count256' and expected_rgb[-3:]!=b'\xff\xff\xff':raise AssertionError('未命中255与末ID')
                for label,k,t in configs:
                    for same in (False,True):
                        target=values.copy() if same else np.empty_like(values)
                        if call(d,guarded,target.ctypes.data if same else values.ctypes.data,target.ctypes.data,65536,k,t) or bytes(target)!=expected_rgb:raise AssertionError('ROM尾guard/全部palette失败')
                        rom_guards+=1
                fixtures[kind]=dict(input_cases=65536,rom_bytes=length,expected_sha256=hashlib.sha256(expected_rgb).hexdigest(),last_rgb=list(expected_rgb[-3:]));del fixture_raw;ct.memset(ct.byref(guarded),0,ct.sizeof(guarded))
            finally:
                if not free(area,0,0x8000):raise ct.WinError(ct.get_last_error())
        del raw,gold
    if not owner.closed or any(bytes(model)):raise AssertionError('成功退出后model仍有效')
    reject_address(owner);owner.close()
    if not call(d,model,0,0,0,0,1):raise AssertionError('已清零model未被native拒绝')
    for mode in ('cow','readonly'):
        with FileView(plan['rom'],mode) as control:
            control_model=control.prepare(d);values=rng.integers(0,256,4097*3,dtype=np.uint8);target=np.empty_like(values)
            expected_rgb=bytearray()
            for red,green,blue in values.reshape(-1,3):
                code=int(red)|(int(green)<<8)|(int(blue)<<16);value=control_model.palette[control_model.table[code]];expected_rgb.extend(int(value).to_bytes(4,'little')[:3])
            for label,k,t in configs:
                if call(d,control_model,values.ctypes.data,target.ctypes.data,4097,k,t) or bytes(target)!=bytes(expected_rgb):raise AssertionError('owner控制调用失败')
        if any(bytes(control_model)):raise AssertionError('control关闭未清零')
        control.close();reject_address(control);lifecycle.append(dict(mode=mode,closed_model_zero=True,idempotent=True))
    if sha(plan['rom'])!=plan['input_sha256'][plan['rom']] or sha(plan['library'])!=plan['input_sha256'][plan['library']]:raise AssertionError('原ROM/库改变')
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,environment=env(),plan_sha256=sha(PLAN),rom_sha256=sha(plan['rom']),library_sha256=sha(plan['library']),model_bytes=1056,rom_bytes=16778272,resident=16779328,hashes=hashes,photo_hashes=photo_hashes,photo_input_sha256=input_hash.hexdigest(),finite=finite,rejections=rejections,image_guards=image_guards,rom_guards=rom_guards,fixtures=fixtures,lifecycle=lifecycle,failure_handles_before=handles_before,failure_handles_after=handles_after,writer_error=writer_error,before=before,after=memory(),scope='只有RO加载方式新增，C99/AVX/ROM字节未改；质量非吞吐，文件EOF页取整与独立字节精确NOACCESS夹具分开；Windows loader不代表跨平台。'))
    print(dict(passed=True,finite=finite,rejections=rejections,image_guards=image_guards,rom_guards=rom_guards))
if __name__=='__main__':main()
