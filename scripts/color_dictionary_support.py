"""M16C专用32B借用ABI，禁止复用旧1056B/1072B解释器对象。"""
import ctypes as ct
import mmap
from study_memory_rom import U8

class ColorModel(ct.Structure):
    _fields_=[('blob',U8),('blob_bytes',ct.c_size_t),('table',U8),('log2_block',ct.c_uint32),('palette_size',ct.c_uint32)]

def colorlib(path):
    d=ct.CDLL(str(path));d.jshc_mem_model_size.restype=ct.c_size_t
    if d.jshc_mem_model_size()!=ct.sizeof(ColorModel):raise AssertionError('M16C真实ABI与对象容量不符')
    d.jshc_mem_prepare.argtypes=[ct.POINTER(ColorModel),ct.c_void_p,ct.c_size_t];d.jshc_mem_apply.argtypes=[ct.POINTER(ColorModel),U8,U8,ct.c_size_t]
    if hasattr(d,'jshc_mem_apply_parallel'):d.jshc_mem_apply_parallel.argtypes=[ct.POINTER(ColorModel),U8,U8,ct.c_size_t,ct.c_int,ct.c_int]
    return d

def loadcolor(d,path):
    file=path.open('rb');mapping=mmap.mmap(file.fileno(),0,access=mmap.ACCESS_COPY);view=(ct.c_uint8*len(mapping)).from_buffer(mapping);m=ColorModel()
    if d.jshc_mem_prepare(ct.byref(m),ct.addressof(view),len(mapping)):raise ValueError('M16C格式拒绝')
    return m,(file,mapping,view)
