"""标准库只读页诊断，核对MADV建议与实际AnonHugePages，二者分开报告。"""
import ctypes as ct
import re
from pathlib import Path

class DirectInfo(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','enabled','format','reserved')]+[(n,ct.c_uint64) for n in ('entries','table_capacity_bytes')]+[(n,ct.c_int32) for n in ('dg_min','db_min')]
class PagedInfo(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','advised','reserved0','reserved1')]+[(n,ct.c_uint64) for n in ('base','bytes')]

def direct_info(d,handle):
    if not hasattr(d,'jshc_cc_get_direct_info'):return None
    f=d.jshc_cc_get_direct_info;f.argtypes=[ct.c_void_p,ct.POINTER(DirectInfo),ct.c_size_t];f.restype=ct.c_int
    v=DirectInfo()
    if f(handle,ct.byref(v),ct.sizeof(v)) or v.version!=1:raise ValueError('直表ABI不符')
    return {n:getattr(v,n) for n,_ in v._fields_}

def paged_info(d,handle):
    if not hasattr(d,'jshc_cc_get_paged_info'):return None
    f=d.jshc_cc_get_paged_info;f.argtypes=[ct.c_void_p,ct.POINTER(PagedInfo),ct.c_size_t];f.restype=ct.c_int
    v=PagedInfo()
    if f(handle,ct.byref(v),ct.sizeof(v)) or v.version!=1:raise ValueError('页诊断ABI不符')
    state={n:getattr(v,n) for n,_ in v._fields_}
    if not v.base or not v.bytes:return state
    text=Path('/proc/self/smaps').read_text();blocks=re.split(r'(?=^[0-9a-f]+-[0-9a-f]+ )',text,flags=re.M)
    found=[]
    for block in blocks:
        lines=block.splitlines()
        if not lines:continue
        match=re.match(r'^([0-9a-f]+)-([0-9a-f]+) ',lines[0])
        if not match:continue
        lo,hi=(int(x,16) for x in match.groups())
        if lo<=v.base and v.base+v.bytes<=hi:
            properties={k.strip():val.strip() for line in lines[1:] if ':' in line for k,val in [line.split(':',1)]}
            found.append({'header':lines[0],'properties':properties,'mapping_bytes':hi-lo})
    if len(found)!=1:raise ValueError('无法唯一定位直表的完整smaps区域')
    region=found[0];huge=int(region['properties'].get('AnonHugePages','0 kB').split()[0])*1024
    state.update(smaps=region,anon_huge_bytes=huge,fully_huge=huge>=v.bytes,aligned_2m=v.base%(2**21)==0)
    return state
