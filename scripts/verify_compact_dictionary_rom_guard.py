"""补验M16P整个ROM末端保护页，并强制映射pool最后字节；不改候选源码。"""
import argparse
import ctypes as ct
from pathlib import Path
import numpy as np
from study_memory_rom import Model,U8,romlib,sha,save,env

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','roms','original','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    original=a.original.read_bytes();payload=np.frombuffer(original,dtype='<u4',offset=1056,count=1048576);block=int(np.argmax(payload));code=(block<<4)|15
    source=np.tile(np.array((code&255,(code>>8)&255,code>>16),dtype=np.uint8),73)
    d=romlib(a.build/'jshc_memory_rom.dll');c=romlib(a.build/'jshc_dict_c99.dll');k=ct.WinDLL('kernel32',use_last_error=True);k.VirtualAlloc.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];k.VirtualAlloc.restype=ct.c_void_p;k.VirtualProtect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)];k.VirtualFree.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32];count=0
    for mode in (17,24):
        path=a.roms/f'rom-{mode}.bin';raw=path.read_bytes();pages=(len(raw)+4095)//4096;address=k.VirtualAlloc(None,(pages+1)*4096,0x3000,4)
        if not address:raise OSError(ct.get_last_error())
        try:
            old=ct.c_uint32()
            if not k.VirtualProtect(address+pages*4096,4096,1,ct.byref(old)):raise OSError(ct.get_last_error())
            start=address+pages*4096-len(raw);ct.memmove(start,raw,len(raw));m=Model()
            if d.jshc_mem_prepare(ct.byref(m),start,len(raw)):raise AssertionError('紧贴保护页ROM准备失败')
            expected=np.empty_like(source)
            if c.jshc_mem_apply(ct.byref(m),source.ctypes.data_as(U8),expected.ctypes.data_as(U8),73):raise AssertionError('C99映射失败')
            for t in (1,4):
                for same in (False,True):
                    target=source.copy() if same else np.empty_like(source)
                    if d.jshc_mem_apply_parallel(ct.byref(m),target.ctypes.data_as(U8) if same else source.ctypes.data_as(U8),target.ctypes.data_as(U8),73,1,t) or not np.array_equal(target,expected):raise AssertionError('ROM末端映射不同')
                    count+=1
        finally:
            if not k.VirtualFree(address,0,0x8000):raise OSError(ct.get_last_error())
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,environment=env(),script_sha256=sha(__file__),libraries={n:sha(a.build/n) for n in ('jshc_memory_rom.dll','jshc_dict_c99.dll')},source_rom_sha256=sha(a.original),input_code=code,comparisons=count,scope='整个ROM准确末端后PAGE_NOACCESS；使用原u32偏移最大块的末像素，强制pool最后字节，桌面原地/分离1/4线程与独立C99对照。'))
    print(count)
if __name__=='__main__':main()
