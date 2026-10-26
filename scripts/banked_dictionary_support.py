"""M16B独立ctypes ABI：model增加四个bases，不能复用旧1056B对象。"""
import ctypes as ct
import mmap
from study_memory_rom import Model,U8

class BankModel(ct.Structure):
    _fields_=Model._fields_+[('bases',ct.c_uint32*4)]

def banklib(path):
    d=ct.CDLL(str(path));d.jshc_mem_model_size.restype=ct.c_size_t
    if d.jshc_mem_model_size()!=ct.sizeof(BankModel):raise AssertionError('新ABI model字节数不符，禁止prepare写入旧对象')
    d.jshc_mem_prepare.argtypes=[ct.POINTER(BankModel),ct.c_void_p,ct.c_size_t];d.jshc_mem_apply.argtypes=[ct.POINTER(BankModel),U8,U8,ct.c_size_t]
    if hasattr(d,'jshc_mem_apply_parallel'):d.jshc_mem_apply_parallel.argtypes=[ct.POINTER(BankModel),U8,U8,ct.c_size_t,ct.c_int,ct.c_int]
    return d

def loadbank(d,path,offset=0):
    if offset:raise ValueError('非对齐试验须显式保留原始ROM长度，由专用verify处理')
    f=path.open('rb');mapping=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_COPY);view=(ct.c_uint8*len(mapping)).from_buffer(mapping);m=BankModel()
    if d.jshc_mem_prepare(ct.byref(m),ct.addressof(view),len(mapping)):raise ValueError('M16B格式拒绝')
    return m,(f,mapping,view)
