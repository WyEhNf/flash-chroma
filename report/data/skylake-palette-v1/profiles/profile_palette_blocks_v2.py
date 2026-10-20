"""只读完整域流，检查固定8色/3bit差值块的精确编码资格；不映射或计时。"""
from pathlib import Path
import hashlib,json
import numpy as np
root=Path(__file__).resolve().parents[1];out=root/'artifacts/skylake-palette-block-profile-v2';out.mkdir(exist_ok=False)
path=root/'artifacts/cinema-current-anchor-accept-v1/cube.rgb';sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha=='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'
x=np.memmap(path,np.uint8,'r',shape=(256**3,3));u=x[:,0].astype(np.uint32)|(x[:,1].astype(np.uint32)<<8)|(x[:,2].astype(np.uint32)<<16)
palette=np.unique(np.fromfile(root/'artifacts/skylake-server-matrix-v1/server-inputs/cache-gold.u32',dtype='<u4'));ids=np.searchsorted(palette,u).astype(np.uint8);blocks=ids.reshape(-1,8);span=blocks.max(1).astype(np.int16)-blocks.min(1)
gold=np.fromfile(root/'artifacts/skylake-server-matrix-v1/server-inputs/cache-gold.u32',dtype='<u4');gp=np.unique(gold)
primary={str(c):len(np.unique((gp>>(8*c))&255)) for c in range(3)}
photos=np.memmap(root/'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb',np.uint8,'r',shape=(100,1024*768,3))
photo_counts=[]
for photo in photos:
 code=photo[:,0].astype(np.uint32)*65536+photo[:,1].astype(np.uint32)*256+photo[:,2].astype(np.uint32)
 exceptional=span[code>>3]>7
 photo_counts.append({'pixels':int(exceptional.sum()),'any_8':int(exceptional.reshape(-1,8).any(1).sum())})
result={'photos_exception_packets_fraction':sum(r['any_8'] for r in photo_counts)/(100*1024*768/8),'per_photo':photo_counts,'purpose':__doc__,'input_sha256':sha,'palette_values':len(palette),'cache_palette_values':len(gp),'cache_primary_unique':primary,'blocks':len(blocks),'max_span':int(span.max()),'span_le_7_fraction':float((span<=7).mean()),'exception_blocks':int((span>7).sum()),'packed_bytes':len(blocks)*4,'exception_bytes':int((span>7).sum())*8,'native_calls':0,'performance_calls':0}
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='per_photo'},ensure_ascii=False))
