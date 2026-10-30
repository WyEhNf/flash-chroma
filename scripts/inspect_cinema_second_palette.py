"""只读第二级候选的旧87资格、cache和完整输出唯一数；不改模型/后端。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
import numpy as np
from channel_native import Library
from inspect_tail_runtime_eligibility import CacheInfo,DomainInfo,PaletteInfo,DirectInfo
from run_channel_tail_nodes import digest,save


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache-root',type=Path,required=True)
    p.add_argument('--study',type=Path,required=True);p.add_argument('--accept-root',type=Path,required=True)
    p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖调色板资格诊断')
    directory=os.add_dll_directory('E:/mingw64/bin');dll_dir=os.add_dll_directory(str(args.library.resolve().parent))
    library=Library(args.library,'58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158');records={}
    for mode in ('max_first','p99_first'):
        candidate=args.study/mode/'candidate'
        paths=[candidate/'candidate-base.slut',candidate/'stage2.slut',
            args.cache_root/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut',candidate/'stage4.slut']
        with library.chain(paths,[candidate/'channel-frac.bin',None,None,None]) as chain:
            row={'model_bytes':chain.model_bytes,'models':{str(path):digest(path) for path in [*paths,candidate/'channel-frac.bin']}}
            for name,cls in (('cache',CacheInfo),('domain',DomainInfo),('palette',PaletteInfo),('direct',DirectInfo)):
                function=getattr(library.dll,'jshc_cc_get_'+name+'_info');function.argtypes=[ct.c_void_p,ct.POINTER(cls),ct.c_size_t];function.restype=ct.c_int
                value=cls()
                if function(chain.handle,ct.byref(value),ct.sizeof(value))!=0:raise AssertionError('旧ABI查询失败')
                row[name]={field:getattr(value,field) for field,_ in cls._fields_}
            values=np.empty(row['cache']['entries'],np.uint32);function=library.dll.jshc_cc_copy_cache
            function.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];function.restype=ct.c_int
            if function(chain.handle,values.ctypes.data_as(ct.POINTER(ct.c_uint32)),values.size)!=0:raise AssertionError('旧cache复制失败')
            row['cache_unique_including_invalid_zero']=int(len(np.unique(values)))
            row['cache_copy_sha256']=hashlib.sha256(memoryview(values).cast('B')).hexdigest()
        accept=args.accept_root/('cinema-second-accept-'+mode+'-v1');result=json.loads((accept/'results.json').read_text(encoding='utf-8'))
        if digest(accept/'candidate.rgb')!=result['sha256']['oracle']:raise ValueError('完整已验收输出变更')
        raw=np.memmap(accept/'candidate.rgb',np.uint8,'r',shape=(256**3,3));seen=np.zeros(1<<24,np.uint8)
        for start in range(0,len(raw),1<<18):
            rgb=raw[start:start+(1<<18)].astype(np.uint32);keys=(rgb[:,0]<<16)|(rgb[:,1]<<8)|rgb[:,2];seen[keys]=1
        unique=np.flatnonzero(seen).astype(np.uint32);row['actual_output_unique']=len(unique)
        row['actual_sorted_unique_sha256']=hashlib.sha256(memoryview(unique).cast('B')).hexdigest()
        records[mode]=row
    save(args.output,{'records':records,'library_sha256':library.sha256,'revision':library.revision,
        'sources':{path.relative_to(ROOT).as_posix():digest(path) for path in (Path(__file__),ROOT/'scripts/inspect_tail_runtime_eligibility.py',ROOT/'experiments/channel-runtime/channel_native.py')},
        'scope':'旧87只读构造/完整输出集合资格，无运行时映射/受控性能；实际输出集合用于判断后续可达集合压缩可行性，不依赖gold。'})
    dll_dir.close();directory.close();print(records,flush=True)


if __name__=='__main__':main()
