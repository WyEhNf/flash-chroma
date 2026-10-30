"""只读检查固定64字节块按首ID取模平移后能否显著缩小精确字典。"""
import hashlib,json,platform,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
source=ROOT/'artifacts/skylake-palette-bank-readonly-v1/direct.u8'
raw=source.read_bytes()
assert len(raw)==2**24 and hashlib.sha256(raw).hexdigest()=='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0'
x=np.frombuffer(raw,dtype=np.uint8).reshape(-1,64)
base=x[:,:1]
delta=x-base
unique,inverse=np.unique(delta.view('V64').reshape(-1),return_inverse=True)
pool=unique.view(np.uint8).reshape(-1,64)
recovered=(pool[inverse]+base).reshape(-1)
assert np.array_equal(recovered,np.frombuffer(raw,dtype=np.uint8))
result={'purpose':'只读完整表分析，不执行原生像素或性能','environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input':{'path':source.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},'block_bytes':64,'map_entries':len(x),'map_bytes':len(x)*4,'unique_normalized_blocks':len(unique),'pool_bytes':pool.nbytes,'used_bytes':len(x)*4+pool.nbytes,'decode_byte_mismatches':int(np.count_nonzero(recovered!=np.frombuffer(raw,dtype=np.uint8))),'proposal':'每个32bit映射的高8bit为首ID，低24bit为归一块偏移；读取后ID=(delta+base)&255。仅离线检查固定64字节块，尚未实现或实测。','native_calls':0,'performance_calls':0}
with (HERE/'analysis.json').open('x',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps(result,ensure_ascii=False))