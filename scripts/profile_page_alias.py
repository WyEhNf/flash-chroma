"""固定4KiB原ID页唯一普查及有限公式合同；不部署页映射、不读照片/gold。"""
import argparse
from collections import Counter
import ctypes as ct
import hashlib
import json
from pathlib import Path
import platform
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-alias-census-v1.json'
PAGE=4096
TABLE=1<<24
PAGES=4096
PREFIX=1056
class OwnerState(ct.Structure):
    _fields_=[('file',ct.c_void_p),('section',ct.c_void_p),('base',ct.c_void_p),('span',ct.c_size_t),('mapped_pages',ct.c_uint32),('split_pages',ct.c_uint32),('state',ct.c_uint32),('reserved',ct.c_uint32)]
class Counters(ct.Structure):
    _fields_=[('cb',ct.c_uint32),('PageFaultCount',ct.c_uint32),*[(name,ct.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]]
def memory():
    value=Counters();value.cb=ct.sizeof(value);process=ct.windll.kernel32.GetCurrentProcess;process.restype=ct.c_void_p;get=ct.windll.psapi.GetProcessMemoryInfo;get.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_uint32]
    if not get(process(),ct.byref(value),ct.sizeof(value)):raise ct.WinError()
    return {name:getattr(value,name) for name in ('PeakWorkingSetSize','WorkingSetSize','PrivateUsage','PeakPagefileUsage','QuotaPagedPoolUsage','QuotaNonPagedPoolUsage')}
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def code_parts(code):
    if not isinstance(code,int) or code<0 or code>=TABLE:raise ValueError('24bit逻辑code越界')
    return code//PAGE,code%PAGE
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args();plan=json.loads(PLAN.read_text(encoding='utf-8'))
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or sha(plan['rom'])!=plan['rom_sha256']:raise AssertionError('预冻结源/原ROM身份不同')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();owner=OwnerState();owner_bytes=ct.sizeof(owner)
    if owner_bytes!=48 or ct.sizeof(ct.c_void_p)!=8:raise AssertionError('原型实际ABI不是本次固定x64布局')
    pool=[];page_ids=[];lookup={};frequency=Counter();direct=Counter();source_digest=hashlib.sha256();logical_digest=hashlib.sha256();probes=[]
    with Path(plan['rom']).open('rb') as stream:
        header=stream.read(PREFIX);source_digest.update(header)
        if header[:4]!=b'M16D' or struct.unpack_from('<7I',header,4)!=(1,0,230,TABLE,0,0,0):raise AssertionError('原linear header不同')
        palette=struct.unpack_from('<256I',header,32)
        if any(value>0xffffff or (index>=230 and value) for index,value in enumerate(palette)):raise AssertionError('原palette不同')
        for page in range(PAGES):
            content=stream.read(PAGE)
            if len(content)!=PAGE or max(content)>=230:raise AssertionError('页截断/非法原ID')
            source_digest.update(content);logical_digest.update(content)
            direct[content]+=1
            identifier=lookup.get(content)
            if identifier is None:identifier=len(pool);pool.append(content);lookup[content]=identifier
            page_ids.append(identifier);frequency[identifier]+=1
            probes.append(bytes(content[offset] for offset in (0,1,4094,4095)))
        if stream.read(1):raise AssertionError('ROM多余字节')
    if source_digest.hexdigest()!=plan['rom_sha256'] or logical_digest.hexdigest()!=plan['logical_id_sha256']:raise AssertionError('完整源/ID身份不同')
    # 独立Counter直接以完整byte页为key，避免只复用首次编号的统计。
    if len(direct)!=len(pool) or sum(frequency.values())!=PAGES or any(direct[content]!=frequency[index] for index,content in enumerate(pool)):raise AssertionError('独立频数/页数不同')
    replay=hashlib.sha256();finite=0;rejected=0
    for page,identifier in enumerate(page_ids):
        replay.update(pool[identifier])
        for index,offset in enumerate((0,1,4094,4095)):
            code=page*PAGE+offset;p,o=code_parts(code);virtual=PAGE+code;via_page=(p+1)*PAGE+o;old_file=PREFIX+code
            if p!=page or o!=offset or virtual!=via_page or old_file!=PREFIX+page*PAGE+offset or pool[page_ids[p]][o]!=probes[page][index]:raise AssertionError('独立页/字节/虚拟公式不同')
            finite+=1
    for invalid in (-1,TABLE):
        try:code_parts(invalid)
        except ValueError:rejected+=1
        else:raise AssertionError('越界code未拒绝')
    if replay.hexdigest()!=plan['logical_id_sha256'] or finite!=16384 or rejected!=2:raise AssertionError('完整pool回放/有限合同不同')
    header_bias=PAGE-PREFIX;metadata_bytes=PAGES*4;pool_offset=PAGE+metadata_bytes;backing=pool_offset+len(pool)*PAGE;total=backing+owner_bytes+1056;baseline=16779328;saving=baseline-total;gate=saving>=(1<<20)
    if header_bias+PREFIX!=PAGE or pool_offset%PAGE or (PAGE-1)*4+4!=metadata_bytes or PAGE+TABLE!=(PAGES+1)*PAGE:raise AssertionError('header/metadata/虚拟末端布局不同')
    support=dict(page_ids=page_ids,unique_page_references=[frequency[index] for index in range(len(pool))],unique_page_sha256=[hashlib.sha256(content).hexdigest() for content in pool],source_page_probe_hex=[value.hex() for value in probes])
    save(a.output/'support.json',support)
    result=dict(passed=True,purpose=__doc__,plan_sha256=sha(PLAN),environment=dict(platform=platform.platform(),machine=platform.machine(),python=sys.version),rom_sha256=source_digest.hexdigest(),logical_id_sha256=logical_digest.hexdigest(),replay_sha256=replay.hexdigest(),source_bytes=PREFIX+TABLE,pages=PAGES,page_bytes=PAGE,unique_pages=len(pool),duplicate_page_occurrences=PAGES-len(pool),header_page=PAGE,original_header_bias=header_bias,metadata_bytes=metadata_bytes,pool_bytes=len(pool)*PAGE,backing_bytes=backing,owner_state_bytes=owner_bytes,owner_offsets={name:getattr(OwnerState,name).offset for name,_ in OwnerState._fields_},old_model_bytes=1056,projected_total_bytes=total,baseline_total_bytes=baseline,net_backing_saving_bytes=saving,minimum_net_saving_bytes=1<<20,gate_pass=gate,status='representable-backing-gate-only' if gate else 'STOP-backing-gate',virtual_span_bytes=(PAGES+1)*PAGE,logical_blob_bytes=PREFIX+TABLE,finite_contracts=finite,invalid_codes_rejected=rejected,support_sha256=sha(a.output/'support.json'),scope='只普查固定4KiB字节页，实际原型状态48B不等于部署owner/OS总开销；没有MapViewOfFile3/新ROM/编译/速度或PFN物理页测量，不能称虚拟capacity/WS减少。')
    result['before']=before;result['after']=memory();result['memory_scope']='纯Python普查进程，before在流式SHA校验后；峰含解释器/页字节/Counter/JSON，不是部署内存或PTE/VAD成本。'
    save(a.output/'results.json',result);print({key:result[key] for key in ('unique_pages','backing_bytes','owner_state_bytes','net_backing_saving_bytes','gate_pass','status')})
if __name__=='__main__':main()
