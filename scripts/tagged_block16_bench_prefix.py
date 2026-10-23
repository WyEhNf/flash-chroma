"""M16T六角色受控同场测量；四worker双接口单四线程，完整五轮不补跑。"""
import ctypes as ct
import hashlib
import os
from pathlib import Path
import statistics
import sys
import time
import bench_memory_rom as bench
from bench_le16_block1024 import affinity,control_affinity,ALLOWED,K32
from study_memory_rom import ROOT,Model,U8,romlib,loadrom,sha,read,save,env

original_setup=bench.setup
def actual(d,path):
    get=ct.windll.kernel32.GetModuleFileNameW;get.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];buffer=ct.create_unicode_buffer(32768)
    if not get(d._handle,buffer,len(buffer)) or Path(buffer.value).resolve()!=path.resolve():raise AssertionError('DLL实际路径不同')
def setup(a,label):
    plan=read(ROOT/'experiments/tagged-block16-native-v1.json')
    if label in ('ref78','ref80'):
        result=original_setup(a,label);actual(result[1][0],Path(result[3]));return result
    if label in ('old32','old3B'):path=Path(plan[label]['library']);rom=Path(plan[label]['rom'])
    else:path=a.build/'jshc_memory_tag16.dll';rom=a.roms/'rom-4.bin'
    d=romlib(path);actual(d,path);d.jshc_mem_model_size.restype=ct.c_size_t
    if d.jshc_mem_model_size()!=ct.sizeof(Model):raise AssertionError('实际ABI不是1056B')
    m,keep=loadrom(d,rom)
    def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,0 if label=='tag_c99' else 1,threads)
    return apply,(d,m,keep),rom.stat().st_size+ct.sizeof(Model),str(path),sha(path)
