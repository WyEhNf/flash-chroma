"""只读核对既有完整域输出与精确后缀表的通道投影机会；不运行映射核或计时。"""
from pathlib import Path
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parents[1];out=root/'artifacts/skylake-projection-profile-v1';out.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
gold=root/'artifacts/skylake-server-matrix-v1/server-inputs/cache-gold.u32'
assert sha(gold)=='f223e56756ed281372b0ebd858b254110c04ca1f5b2afb6d091c40df3a1ffe90'
table=np.fromfile(gold,dtype='<u4').reshape(232,20,40)
rr=np.arange(232)[:,None,None];dg=np.arange(-16,4)[None,:,None];db=np.arange(-36,4)[None,None,:]
valid=(rr+dg>=0)&(rr+dg<=255)&(rr+db>=0)&(rr+db<=255)&(dg>=-15)&(dg<=2)&(db>=-35)&(db<=2)
lower=np.where(valid,table,np.uint32(0xffffffff));upper=np.where(valid,table,0)
constant_r=lower.min((1,2))==upper.max((1,2))
constant_rg=(lower.min(2)==upper.max(2))&valid.any(2)
constant_rb=(lower.min(1)==upper.max(1))&valid.any(1)
first=root/'artifacts/skylake-domain-isolated-full-v1/first-stage.rgb'
assert sha(first)=='7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146'
rgb=np.memmap(first,np.uint8,'r',shape=(256**3,3));x=rgb.astype(np.int16);r=x[:,0];g=x[:,1]-r;b=x[:,2]-r
result={'purpose':__doc__,'inputs':{'gold_sha256':sha(gold),'prefix_cube_sha256':sha(first)},'certified_bounds':{'r':[0,231],'dg':[-15,2],'db':[-35,2]},'constant_r_count':int(constant_r.sum()),'constant_rg_count':int(constant_rg.sum()),'constant_rb_count':int(constant_rb.sum()),'cube':{}}
for key,mask in [('r',constant_r[r]),('rg',constant_rg[r,g+16]),('rb',constant_rb[r,b+36])]:
 result['cube'][key]={'pixels':int(mask.sum()),'fraction':float(mask.mean()),'all_8_fraction':float(mask.reshape(-1,8).all(1).mean())}
result['native_calls']=result['performance_calls']=0
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
