"""C7BK独立32B ABI、固定布局及序列化助手，不混用旧1056B对象。"""
import ctypes as ct
import mmap
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,U8,sha,read,save,env

TABLE=14680064
TABLE_START=1056
GUARD=14681120
PALETTE=14681124
ROM_BYTES=14943268
PLAN=ROOT/'experiments/rgb3d-palette7-native-v1.json'
class Model(ct.Structure):_fields_=[('blob',U8),('blob_bytes',ct.c_size_t),('table',U8),('palettes',U8)]
def library(path):
    d=ct.CDLL(str(path));d.jshc_mem_prepare.argtypes=[ct.POINTER(Model),ct.c_void_p,ct.c_size_t];d.jshc_mem_apply.argtypes=[ct.POINTER(Model),U8,U8,ct.c_size_t];d.jshc_mem_model_size.restype=ct.c_size_t
    if d.jshc_mem_model_size()!=ct.sizeof(Model):raise AssertionError('真实C7BK ABI不同')
    if hasattr(d,'jshc_mem_apply_parallel'):d.jshc_mem_apply_parallel.argtypes=[ct.POINTER(Model),U8,U8,ct.c_size_t,ct.c_int,ct.c_int]
    return d
def load(d,path):
    stream=Path(path).open('rb');mapping=mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_COPY);view=(ct.c_uint8*len(mapping)).from_buffer(mapping);m=Model()
    if d.jshc_mem_prepare(ct.byref(m),view,len(view)):raise AssertionError('C7BK prepare拒绝')
    return m,(stream,mapping,view)
def bank(codes):return ((codes>>5)&7)|((codes>>10)&56)|((codes>>15)&448)
def pack7(ids):
    ids=np.asarray(ids,dtype=np.uint8).reshape(-1,8);words=np.zeros(len(ids),dtype=np.uint64)
    for k in range(8):words|=ids[:,k].astype(np.uint64)<<(7*k)
    return ((words[:,None]>>np.arange(0,56,8,dtype=np.uint64))&255).astype(np.uint8).tobytes()
def header():return b'C7BK'+struct.pack('<7I',1,512,7,TABLE,1,128,0)
def independent(raw,values):
    result=bytearray()
    for red,green,blue in np.asarray(values,dtype=np.uint8).reshape(-1,3):
        code=int(red)|(int(green)<<8)|(int(blue)<<16);b=((int(red)>>5)|((int(green)>>5)<<3)|((int(blue)>>5)<<6));bit=7*code;word=raw[TABLE_START+(bit>>3)]|(raw[TABLE_START+(bit>>3)+1]<<8);i=(word>>(bit&7))&127;start=PALETTE+4*(128*b+i);result.extend(raw[start:start+3])
    return bytes(result)
