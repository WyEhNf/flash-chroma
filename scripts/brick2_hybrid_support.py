"""修订84只读诊断与全部2³块的独立整数解码；不计性能。"""
import ctypes as ct
import hashlib
from paged_table_support import PagedInfo, paged_info

class HybridInfo(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','enabled','format','reserved')]+[
        (n,ct.c_uint64) for n in ('entries','table_capacity_bytes')]+[
        (n,ct.c_int32) for n in ('dg_min','db_min')]+[
        (n,ct.c_uint64) for n in ('normal_blocks','bad_blocks')]

def hybrid_info(d,h):
    f=d.jshc_cc_get_hybrid_info
    f.argtypes=[ct.c_void_p,ct.POINTER(HybridInfo),ct.c_size_t];f.restype=ct.c_int
    v=HybridInfo()
    if f(h,ct.byref(v),ct.sizeof(v)) or v.version!=1:
        raise ValueError('混合表诊断ABI不符')
    return {n:getattr(v,n) for n,_ in v._fields_}

def hybrid_paged_info(d,h):
    class Proxy:
        jshc_cc_get_paged_info=d.jshc_cc_get_hybrid_paged_info
    return paged_info(Proxy(),h)

def verify_model(d,handles):
    h=handles['chain'];info=hybrid_info(d,h)
    if hybrid_info(d,handles['single'])['enabled']:
        raise AssertionError('单级错误启用混合表')
    assert info==dict(version=1,enabled=1,format=22,reserved=0,entries=2**21,
        table_capacity_bytes=2**24,dg_min=-11,db_min=-6,normal_blocks=2033554,bad_blocks=63598),info
    pages=hybrid_paged_info(d,h)
    assert pages['bytes']==2**24 and pages['aligned_2m']
    words=(ct.c_uint64*(2**21))()
    f=d.jshc_cc_copy_hybrid
    f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint64),ct.c_size_t];f.restype=ct.c_int
    assert f(h,words,len(words))==0
    raw=bytes(words);view=memoryview(raw).cast('Q')
    direct=(ct.c_uint32*(2**22))();old=(ct.c_uint32*(2**21))();palette=(ct.c_uint32*256)()
    d.jshc_cc_copy_direct.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t]
    d.jshc_cc_copy_direct.restype=ct.c_int
    assert d.jshc_cc_copy_direct(h,direct,len(direct))==0
    g=d.jshc_cc_copy_palette
    g.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t,ct.POINTER(ct.c_uint32),ct.c_size_t];g.restype=ct.c_int
    assert g(h,old,len(old),palette,256)==0
    ids=bytes(direct);pal=tuple(int(x) for x in palette)
    normal=bad=colors=0
    # 以物理块坐标反推输入，逐项重算RGB通道，不复用C++打包器或SIMD表达式。
    for q,w in enumerate(view):
        if w>>63:
            assert w==1<<63
            bad+=1
            continue
        normal+=1
        base=(q&127)*2+((q>>7)&127)*512+(q>>14)*131072
        br=w&255;bdg=((w>>8)&15)+info['dg_min'];bdb=((w>>12)&7)+info['db_min']
        assert 0<=br+bdg<=255 and 0<=br+bdb<=255
        for k in range(8):
            source=base+(k&1)+((k&2)<<7)+((k&4)<<14)
            c=(w>>(15+6*k))&63
            r=br+(c&7);g=r+bdg+((c>>3)&3);b=r+bdb+((c>>5)&1)
            assert 0<=r<=255 and 0<=g<=255 and 0<=b<=255
            assert r+(g<<8)+(b<<16)==pal[ids[source]],(q,k)
            colors+=1
    assert (normal,bad)==(info['normal_blocks'],info['bad_blocks'])
    guard=(ct.c_uint64*8)(*([0xa7a7a7a7a7a7a7a7]*8))
    for handle,pointer,count in ((None,guard,len(words)),(h,guard,len(words)-1),(h,None,len(words))):
        assert f(handle,pointer,count)==1 and list(guard)==[0xa7a7a7a7a7a7a7a7]*8
    for structure,function in ((HybridInfo,d.jshc_cc_get_hybrid_info),(PagedInfo,d.jshc_cc_get_hybrid_paged_info)):
        function.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_size_t];function.restype=ct.c_int
        v=structure();ct.memset(ct.byref(v),0xa7,ct.sizeof(v));before=bytes(v)
        for handle,pointer,count in ((None,ct.byref(v),ct.sizeof(v)),(h,None,ct.sizeof(v)),(h,ct.byref(v),ct.sizeof(v)-1)):
            assert function(handle,pointer,count)==1 and bytes(v)==before
    return dict(info=info,pages=pages,table_sha256=hashlib.sha256(raw).hexdigest(),
        independently_decoded_normal_colors=colors,independently_checked_tag_blocks=bad,
        independently_checked_blocks=normal+bad,negative_checks=9,byte_mismatches=0,
        fallback_proof='所有tag词仅bit63；实际异常输入由完整RGB8运行时矩阵对比独立cube验证')
