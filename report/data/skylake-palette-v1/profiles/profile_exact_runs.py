"""只读已有四级完整域流，评估64码分段的无损游程结构；不映射新像素或计时。"""
from pathlib import Path
import hashlib,json
import numpy as np
root=Path(__file__).resolve().parents[1];out=root/'artifacts/skylake-exact-runs-profile-v1';out.mkdir(exist_ok=False)
cube=root/'artifacts/cinema-current-anchor-accept-v1/cube.rgb'
sha=hashlib.sha256(cube.read_bytes()).hexdigest();assert sha=='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'
x=np.memmap(cube,np.uint8,'r',shape=(256**3,3));u=x[:,0].astype(np.uint32)|(x[:,1].astype(np.uint32)<<8)|(x[:,2].astype(np.uint32)<<16)
unique=np.unique(u);blocks=u.reshape(-1,64);starts=np.ones_like(blocks,dtype=bool);starts[:,1:]=blocks[:,1:]!=blocks[:,:-1]
counts=starts.sum(1);n=int(counts.sum());gold=np.fromfile(root/'artifacts/skylake-server-matrix-v1/server-inputs/cache-gold.u32',dtype='<u4')
result={'purpose':__doc__,'cube_sha256':sha,'pixels':len(x),'segments':len(blocks),'global_values':len(unique),'suffix_cache_values':len(np.unique(gold)),'runs':n,'run_fraction':n/len(x),'run_count_percentiles':np.percentile(counts,[0,50,90,99,100]).tolist(),'bytes_with_u8_ids':len(blocks)*12+n+len(unique)*4,'bytes_with_u16_ids':len(blocks)*12+n*2+len(unique)*4,'dense_rgb_bytes':x.nbytes,'dense_u32_bytes':u.nbytes,'native_calls':0,'performance_calls':0}
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
