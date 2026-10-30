"""C7BK六角色同场：全部最劣worker、双接口1/4线程与A/A原件保留。"""
import ctypes as ct
import hashlib
import os
from pathlib import Path
import statistics
import sys
import time
import bench_memory_rom as bench
from bench_le16_block1024 import affinity,control_affinity,ALLOWED,K32
from study_memory_rom import ROOT,U8,read,save,sha,env,romlib,loadrom,Model as OldModel
from rgb3d7_support import Model,library,load,PLAN
original_setup=bench.setup
def actual(d,path):
    get=ct.windll.kernel32.GetModuleFileNameW;get.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];buffer=ct.create_unicode_buffer(32768)
    if not get(d._handle,buffer,len(buffer)) or Path(buffer.value).resolve()!=path.resolve():raise AssertionError('实际模块路径不同')
def setup(a,label):
    plan=read(PLAN)
    if label in ('ref78','ref80'):
        result=original_setup(a,label);actual(result[1][0],Path(result[3]));return result
    if label in ('linear8_avx','linear8_clang_c99'):
        path=Path(plan['linear_reference']['library']);rom=Path(plan['linear_reference']['rom']);d=romlib(path);m,keep=loadrom(d,rom);size=ct.sizeof(OldModel)
    else:
        path=a.build/'jshc_rgb3d7.dll';rom=a.roms/'rgb3d7.bin';d=library(path);m,keep=load(d,rom);size=ct.sizeof(Model)
    actual(d,path);kernel=0 if label in ('linear8_clang_c99','rgb3d7_c99') else 1
    def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,kernel,threads)
    return apply,(d,m,keep),rom.stat().st_size+size,str(path),sha(path)
