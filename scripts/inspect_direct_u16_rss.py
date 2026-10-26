"""独立新进程观察直接表构造前后RSS/OS峰值；不是吞吐或受控构造性能。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'experiments/channel-runtime')]
import psutil
from channel_native import Library


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def memory():return dict(psutil.Process().memory_info()._asdict())


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frozen',type=Path,required=True);p.add_argument('--library',type=Path,required=True)
    p.add_argument('--sha256',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--model',choices=['max_first','p99_first','old_best']);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖RSS观察')
    if args.model is None:
        args.output.mkdir(parents=True)
        for model in ('max_first','p99_first','old_best'):
            subprocess.run([sys.executable,str(Path(__file__)),'--frozen',str(args.frozen),'--library',str(args.library),
                '--sha256',args.sha256,'--output',str(args.output/(model+'.json')),'--model',model],check=True,cwd=ROOT)
        return
    frozen=json.loads(args.frozen.read_text(encoding='utf-8'));spec=frozen['models'][args.model]
    for name,sha in spec['input_sha256'].items():
        if digest(Path(name))!=sha:raise ValueError('模型变更')
    dirs=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str(args.library.resolve().parent))]
    library=Library(args.library,args.sha256);before=memory();started=time.perf_counter()
    chain=library.chain(spec['models'],spec['sidecars']);construct=time.perf_counter()-started;after=memory()
    capacity=chain.model_bytes;diagnostic=None
    if hasattr(library.dll,'p16_cc_get_direct_u16_info'):
        class Info(ct.Structure):
            _fields_=[(n,ct.c_uint32) for n in ('version','enabled','format','reason','palette_size','id_bytes','guard_bytes','reserved')]
            _fields_ += [(n,ct.c_uint64) for n in ('input_entries','raw_words','table_capacity_bytes','palette_capacity_bytes','temporary_peak_bytes','guaranteed_alignment','data_mod_64')]
            _fields_ += [('prepare_seconds',ct.c_double)]
        value=Info();f=library.dll.p16_cc_get_direct_u16_info;f.argtypes=[ct.c_void_p,ct.POINTER(Info),ct.c_size_t];f.restype=ct.c_int
        if f(chain.handle,ct.byref(value),ct.sizeof(value)):raise AssertionError('Info失败')
        diagnostic={n:getattr(value,n) for n,_ in Info._fields_}
    chain.close();closed=memory()
    result={'model':args.model,'revision':library.revision,'library_sha256':library.sha256,'frozen_sha256':digest(args.frozen),
        'before':before,'after_construct':after,'after_destroy':closed,'rss_delta_after_construct':after['rss']-before['rss'],
        'OS_peak_wset_before':before.get('peak_wset'),'OS_peak_wset_after_construct':after.get('peak_wset'),
        'model_bytes':capacity,'wide':diagnostic,'diagnostic_construction_seconds':construct,'performance_calls':0,'apply_calls':0,
        'environment':{'platform':sys.platform,'machine':os.environ.get('PROCESSOR_IDENTIFIER'),'python':sys.version,'psutil':psutil.__version__},
        'scope':'每模型全新进程；baseline已导入Python/NumPy/psutil并加载DLL，constructor后立即读OS working set及进程历史峰值。峰值含全部模块/allocator/OpenMP，不能当精确净table或整个系统RAM；无照片/完整oracle/性能。'}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'model':args.model,'revision':library.revision,'rss_delta':result['rss_delta_after_construct'],'OS_peak_wset':result['OS_peak_wset_after_construct']}),flush=True)


if __name__=='__main__':main()
