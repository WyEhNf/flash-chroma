"""仅离线核验固定R连续8色块的3bit无损表示与照片集合；不构建/加载原生候选或计时。"""
from __future__ import annotations
import hashlib,json,platform,re,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SPECS={
 'cache_gold':('artifacts/skylake-matrix-cache-gold-v1/cache-gold.u32','f223e56756ed281372b0ebd858b254110c04ca1f5b2afb6d091c40df3a1ffe90'),
 'cube':('artifacts/cinema-current-anchor-accept-v1/cube.rgb','3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'),
 'photos':('artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb','e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'),
 'manifest':('assets/photos/manifest.json','10893812e0d3cecea7ba8b6bbf4700addd09927feed220149501def03c374f7c'),
 'old_palette_crosscheck':('artifacts/skylake-palette-bank-readonly-v1/palette.u32','53cedaeca7403d5afd1b96133339be866840059685abdd3846aad7fe10998fbe')}
DIRECT_SHA='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0'
PHOTO_OUTPUT_SHA='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
def digest(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(name,value):
 with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def coarse(c):return c>>3
def fine(c):return c&7
def inverse(q,k):return (q<<3)|k
def set_counts(lines):
 a=lines.reshape(-1,64).copy();a.sort(axis=1)
 return 1+np.count_nonzero(a[:,1:]!=a[:,:-1],axis=1)
def history():
 paths=set((ROOT/'docs/stages').glob('*skylake*.md'))|set((ROOT/'scripts').glob('*skylake*.py'))
 for folder in (ROOT/'experiments').glob('skylake*-runtime'):
  paths.update(folder.rglob('*.cpp'));paths.update(folder.rglob('*.hpp'))
 pattern=re.compile(r'R连续.*3bit|3bit.*R连续|R低.*3bit|3bit.*R低|r8.*pack|code.*>>3',re.I)
 matches=[]
 for p in sorted(paths):
  for n,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
   if pattern.search(line):matches.append(dict(path=p.relative_to(ROOT).as_posix(),line=n,text=line))
 related=['experiments/skylake-wordload-runtime/channel_avx2.cpp','experiments/skylake-tilebmi2-runtime/tiled/channel_avx2.cpp','experiments/skylake-pack5-runtime/channel_avx2.cpp','experiments/skylake-block-dictionary-runtime/channel_avx2.cpp',
  'docs/stages/2026-10-20-skylake-cache-hints.md','docs/stages/2026-10-21-skylake-tiles.md','docs/stages/2026-10-21-skylake-pack5.md','docs/stages/2026-10-21-skylake-block-dictionary.md']
 return dict(searched_files=len(paths),searched_source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)},pattern=pattern.pattern,matches=matches,
  related_source_sha256={p:digest(ROOT/p) for p in related if (ROOT/p).exists()},
  conclusion='本轮只统计固定R连续8色/3bit表示，不据关键词搜索断言完整组合从未实现。23/42为B连续8色3bit，62为R连续8色5bit；实现前仍须主流程完整历史核对。')
def main():
 if (OUT/'analysis.json').exists():raise ValueError('不覆盖已完成统计')
 protocol=read(OUT/'protocol.json')
 if protocol['script_sha256']!=digest(__file__):raise ValueError('统计前脚本与冻结协议不符')
 if protocol['gate']!={'exception_packet8_fraction_max':0.05,'mean_word_lines_per64_ratio_max':0.80}:raise ValueError('不得改变事前门槛')
 paths={};inputs={}
 for name,(relative,expected) in SPECS.items():
  p=ROOT/relative
  if digest(p)!=expected:raise ValueError('输入SHA不同：'+relative)
  paths[name]=p;inputs[name]=dict(path=relative,sha256=expected,bytes=p.stat().st_size)
 generation_path=ROOT/'artifacts/skylake-matrix-cache-gold-v1/generation.json'
 generation=read(generation_path)
 assert generation['generation_completed'] and generation['gold_sha256']==SPECS['cache_gold'][1]
 inputs['cache_generation']=dict(path=generation_path.relative_to(ROOT).as_posix(),sha256=digest(generation_path),model_inputs=generation['inputs'])
 palette=np.unique(np.fromfile(paths['cache_gold'],dtype='<u4'))
 assert len(palette)==230
 old=np.fromfile(paths['old_palette_crosscheck'],dtype='<u4')
 assert len(old)==256 and np.array_equal(old[:230],palette) and np.all(old[230:]==0)
 assert inputs['cube']['bytes']==3*(1<<24)
 cube=np.memmap(paths['cube'],dtype=np.uint8,mode='r',shape=(256,256,256,3))
 direct=np.empty((256,256,256),dtype=np.uint8)
 output_frequency=np.zeros(230,dtype=np.int64)
 for r in range(256):
  slab=cube[r].astype(np.uint32);rgb=slab[:,:,0]|(slab[:,:,1]<<8)|(slab[:,:,2]<<16)
  ids=np.searchsorted(palette,rgb)
  assert ids.max()<230 and np.array_equal(palette[ids],rgb)
  direct[:,:,r]=ids.T
  output_frequency+=np.bincount(ids.ravel(),minlength=230)
 linear=direct.ravel()
 assert hashlib.sha256(linear).hexdigest()==DIRECT_SHA
 members=linear.reshape(-1,8)
 base=members.min(axis=1);span=members.max(axis=1).astype(np.uint16)-base
 bad=span>7;bad_count=int(bad.sum())
 words=base.astype(np.uint32)
 for k in range(8):words|=((members[:,k].astype(np.uint32)-base)&7)<<np.uint32(8+3*k)
 # 唯一固定的审计用例外编码：低字节255，余24bit为顺序8字节例外块编号；不改变调色板顺序。
 exceptions=members[bad].copy();words[bad]=np.uint32(255)|(np.arange(bad_count,dtype=np.uint32)<<8)
 assert bad_count<(1<<24)
 decode_mismatches=0;inverse_mismatches=0
 for first in range(0,1<<24,1<<20):
  c=np.arange(first,first+(1<<20),dtype=np.uint32);q=coarse(c);k=fine(c)
  inverse_mismatches+=int(np.count_nonzero(inverse(q,k)!=c))
  w=words[q];exception=(w&255)==255
  decoded=((w&255)+((w>>(8+3*k))&7)).astype(np.uint8)
  if np.any(exception):decoded[exception]=exceptions[w[exception]>>8,k[exception]]
  decode_mismatches+=int(np.count_nonzero(decoded!=linear[first:first+(1<<20)]))
 assert decode_mismatches==inverse_mismatches==0
 max_span=int(span.max());worst=int(np.argmax(span))
 manifest=read(paths['manifest']);assert len(manifest['images'])==100 and inputs['photos']['bytes']==235929600
 photos=np.memmap(paths['photos'],dtype=np.uint8,mode='r',shape=(100,1024*768,3))
 rows=[];output_sha=hashlib.sha256();hist_old=np.zeros(65,dtype=np.int64);hist_word=hist_old.copy();hist_total=np.zeros(129,dtype=np.int64)
 for i,image in enumerate(photos):
  meta=manifest['images'][i];image_sha=hashlib.sha256(image).hexdigest();assert image_sha==meta['evaluation']['pixel_sha256']
  c=image[:,0].astype(np.uint32)|(image[:,1].astype(np.uint32)<<8)|(image[:,2].astype(np.uint32)<<16)
  q=coarse(c);k=fine(c);w=words[q];exception=(w&255)==255
  ids=((w&255)+((w>>(8+3*k))&7)).astype(np.uint8)
  if np.any(exception):ids[exception]=exceptions[w[exception]>>8,k[exception]]
  assert np.array_equal(ids,linear[c])
  rgb=palette[ids];output=np.column_stack((rgb&255,(rgb>>8)&255,(rgb>>16)&255)).astype(np.uint8);output_sha.update(output)
  counts_old=set_counts(c>>6);counts_word=set_counts(q>>4)
  # 额外保守报告例外池的行集合：8B/块，另起对齐缓存区，不能与主词行合并。
  exception_lines=np.where(exception,(w>>8)>>3,np.uint32(0xffffffff)).reshape(-1,64).copy();exception_lines.sort(axis=1)
  real=exception_lines!=np.uint32(0xffffffff)
  counts_exception=real[:,0].astype(np.int64)+np.count_nonzero(real[:,1:]&(exception_lines[:,1:]!=exception_lines[:,:-1]),axis=1)
  counts_total=counts_word+counts_exception
  hist_old+=np.bincount(counts_old,minlength=65);hist_word+=np.bincount(counts_word,minlength=65);hist_total+=np.bincount(counts_total,minlength=129)
  packets=len(c)//8;hits=int(np.any(exception.reshape(-1,8),axis=1).sum())
  rows.append(dict(image_index=i,image_id=meta['id'],pixel_sha256=image_sha,pixels=len(c),packets8=packets,exception_pixels=int(exception.sum()),exception_packets8=hits,exception_packet8_fraction=hits/packets,
   windows64=len(counts_old),sum_original_id_lines=int(counts_old.sum()),sum_word_lines=int(counts_word.sum()),sum_exception_pool_lines=int(counts_exception.sum()),
   mean_original_id_lines=float(counts_old.mean()),mean_word_lines=float(counts_word.mean()),word_lines_ratio=float(counts_word.sum()/counts_old.sum()),word_plus_exception_lines_ratio=float(counts_total.sum()/counts_old.sum())))
 assert output_sha.hexdigest()==PHOTO_OUTPUT_SHA
 windows=sum(r['windows64'] for r in rows);packets=sum(r['packets8'] for r in rows)
 old_sum=sum(r['sum_original_id_lines'] for r in rows);new_sum=sum(r['sum_word_lines'] for r in rows);pool_sum=sum(r['sum_exception_pool_lines'] for r in rows)
 hits=sum(r['exception_packets8'] for r in rows);fraction=hits/packets;ratio=new_sum/old_sum
 gate=dict(exception_packet8_fraction=fraction,exception_packet8_fraction_max=0.05,exception_packets_pass=fraction<=.05,mean_word_lines_ratio=ratio,mean_word_lines_ratio_max=.8,line_set_pass=ratio<=.8)
 gate['passed']=gate['exception_packets_pass'] and gate['line_set_pass']
 result=dict(purpose=__doc__,analysis_completed=True,script_sha256=digest(__file__),protocol_sha256=digest(OUT/'protocol.json'),
  environment=dict(platform=platform.platform(),python=sys.version,numpy=np.__version__),inputs=inputs,
  palette=dict(source='只从cache-gold.u32按uint32数值升序去重；不是从完整cube的221个实际输出重新编号',entries=230,values_rgb32=[int(v) for v in palette],complete_cube_used_entries=int(np.count_nonzero(output_frequency)),output_id_frequency=output_frequency.tolist(),matches_old_export=True),
  mapping=dict(code='R | (G<<8) | (B<<16)',coarse='c>>3，固定G/B的连续8个R',fine='c&7',
   normal_word='min_ID | sum((ID[k]-min_ID) << (8+3*k)), span<=7',exception_word='255 | (ordinal_of_exception_block<<8)',exception_payload='按coarse升序，每例外块连续8个原230项调色板ID',word_line='coarse>>4；每行16个32bit字，空间覆盖128×1×1个RGB8颜色',original_line='c>>6；每行64×1×1颜色'),
  full_domain=dict(colors=1<<24,blocks=1<<21,normal_blocks=(1<<21)-bad_count,exception_blocks=bad_count,exception_block_fraction=bad_count/(1<<21),max_id_span=max_span,
   span_histogram=np.bincount(span,minlength=230).tolist(),worst_block=dict(coarse=worst,rgb_min=[int(inverse(np.uint32(worst),np.uint32(0)))&255,(int(inverse(np.uint32(worst),np.uint32(0)))>>8)&255,(int(inverse(np.uint32(worst),np.uint32(0)))>>16)&255],ids=members[worst].tolist()),
   decode_id_mismatches=decode_mismatches,index_inverse_mismatches=inverse_mismatches,linear_id_sha256=DIRECT_SHA,word_bytes=words.nbytes,word_sha256=hashlib.sha256(words.astype('<u4',copy=False)).hexdigest(),exception_payload_bytes=exceptions.nbytes,exception_payload_sha256=hashlib.sha256(exceptions).hexdigest(),total_payload_bytes=words.nbytes+exceptions.nbytes),
  photos=dict(images=100,pixels=235929600//3,packets8=packets,exception_pixels=sum(r['exception_pixels'] for r in rows),exception_packets8=hits,exception_packet8_fraction=fraction,windows64=windows,
   mean_original_id_lines_per64=old_sum/windows,mean_word_lines_per64=new_sum/windows,mean_exception_pool_lines_per64=pool_sum/windows,word_lines_ratio=ratio,word_plus_exception_lines_ratio=(new_sum+pool_sum)/old_sum,
   original_lines_histogram=hist_old.tolist(),word_lines_histogram=hist_word.tolist(),word_plus_exception_lines_histogram=hist_total.tolist(),decoded_output_sha256=output_sha.hexdigest()),
  per_image=rows,gate=gate,history=history(),decision='仅通过离线事前筛查，是否实现仍由主流程决定；不构成性能证据' if gate['passed'] else '未通过固定离线门槛，停止此方向，不构建原生、不扫描其他尺寸或参数',
  limitations=['集合计数不是cache miss、周期或吞吐，未计标量位移、异常分支与调色板依赖成本。','主门槛按请求使用主词表行集合；同时报告含精确例外池的更保守行集合。','照片按每图像素0起固定8/64窗口，不扫描偏移；真实对齐前缀可能改变窗口。','profile使用已验输出流，仅判断可行性；未来运行时构造仍必须来自原模型，禁止读取照片或gold。'],
  native_calls=0,performance_calls=0,compiler_calls=0,new_fits=0)
 save('analysis.json',result)
 print(json.dumps(dict(full_domain={k:result['full_domain'][k] for k in ('exception_blocks','max_id_span','decode_id_mismatches','index_inverse_mismatches','word_bytes','exception_payload_bytes')},photos={k:result['photos'][k] for k in ('exception_packet8_fraction','mean_original_id_lines_per64','mean_word_lines_per64','word_lines_ratio','word_plus_exception_lines_ratio')},gate=gate,result_sha256=digest(OUT/'analysis.json')),ensure_ascii=True),flush=True)
if __name__=='__main__':main()
