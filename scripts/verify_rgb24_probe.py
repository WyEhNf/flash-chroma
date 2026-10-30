"""RGB24 AVX2节点读取的实际保护页验收，覆盖全部3*i对齐余数及最后节点。"""
import argparse
import ctypes as ct
from pathlib import Path
import numpy as np
from study_memory_rom import save,sha,env

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    k=ct.WinDLL('kernel32',use_last_error=True);k.VirtualAlloc.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];k.VirtualAlloc.restype=ct.c_void_p;k.VirtualProtect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)];k.VirtualFree.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32]
    lib=ct.CDLL(str(a.library.resolve()));fn=lib.jshc_rgb24_probe8;fn.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_void_p];fn.restype=None;rng=np.random.default_rng(2026102406);count=0
    for nodes in (1,2,3,4,5,7,8,9,15,16,17,33,4913,5832,15625,35937):
        size=((3*nodes+3)//4+1)*4;pages=(size+4095)//4096;address=k.VirtualAlloc(None,(pages+1)*4096,0x3000,4)
        if not address:raise OSError(ct.get_last_error())
        try:
            old=ct.c_uint32()
            if not k.VirtualProtect(address+pages*4096,4096,1,ct.byref(old)):raise OSError(ct.get_last_error())
            start=address+pages*4096-size;data=rng.integers(0,256,(nodes,3),dtype=np.uint8);ct.memmove(start,data.ctypes.data,data.nbytes)
            for repeat in range(16):
                indexes=rng.integers(0,nodes,8,dtype=np.int32);indexes[0]=nodes-1;indexes[1]=0
                output=np.zeros(8,dtype=np.uint32);fn(start,indexes.ctypes.data,output.ctypes.data);selected=data[indexes].astype(np.uint32);expected=selected[:,0]|(selected[:,1]<<8)|(selected[:,2]<<16)
                if not np.array_equal(output,expected):raise AssertionError('节点gather读取不同')
                count+=1
        finally:
            if not k.VirtualFree(address,0,0x8000):raise OSError(ct.get_last_error())
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,environment=env(),script_sha256=sha(__file__),library_sha256=sha(a.library),comparisons=count,scope='owned uint32存储整体4B对齐、真实guardword后紧贴PAGE_NOACCESS；每次含最后节点和随机节点，不依赖外部padding。'))
    print(count)
if __name__=='__main__':main()
