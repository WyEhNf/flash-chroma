"""从冻结288另建289，只更改宽ID编码与读取，不修改旧运行时。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]


def replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError('必须唯一匹配：'+old[:100])
    return text.replace(old,new)


def main():
    source=ROOT/'experiments/p16-direct-u16-ilp-runtime';out=ROOT/'experiments/p16-direct-u10-runtime'
    if out.exists():raise ValueError('不覆盖新10bit源码')
    frozen=json.loads((ROOT/'artifacts/p16-direct-u16-ilp-frozen-v1/frozen.json').read_text(encoding='utf-8'))
    # 288原件已由其公开质量/HEAD审计绑定；这里再保留每个实际复制原字节身份。
    sources={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in source.iterdir() if p.is_file()}
    if len(sources)!=10:raise ValueError('288源集合意外变化')
    texts={}
    for path in source.iterdir():
        if not path.is_file():continue
        name=path.name.replace('direct_u16','direct_u10')
        text=path.read_text(encoding='utf-8').replace('direct_u16_ilp','direct_u10').replace('direct_u16','direct_u10').replace('palette_u16','palette_u10').replace('u16_palette','u10_palette')
        texts[name]=text
    header=texts['direct_u10.hpp']
    header=replace_once(header,'n<=65536','n<=1024')
    helper='''// 四ID/5B小端编码；标量读取只访问本ID的两个合法数据字节。
inline uint32_t direct_u10_id(const uint8_t* table,uint32_t address) noexcept {
  const size_t position=size_t(address>>2)*5+(address&3u);
  const uint32_t word=uint32_t(table[position])|(uint32_t(table[position+1])<<8);
  return (word>>(2*(address&3u)))&1023u;
}
'''
    header=replace_once(header,'namespace jshc_channel {','namespace jshc_channel {\n'+helper)
    header=header.replace('uint16_t*','uint8_t*').replace('16bit','10bit').replace('超65536','超1024')
    texts['direct_u10.hpp']=header
    for name in ('linear.cpp','andn_inplace.cpp','andn_outplace.cpp','normal_inplace.cpp','direct_u10_avx2.cpp'):
        text=texts[name].replace('uint16_t*','uint8_t*').replace('uint16索引','10bit索引')
        text=re.sub(r'\b(table|bytes)\[([^\]]+)\]',lambda m:f'direct_u10_id({m[1]},uint32_t({m[2]}))',text)
        texts[name]=text
    runtime=texts['channel_runtime.cpp']
    runtime=runtime.replace('std::vector<uint16_t>','std::vector<uint8_t>').replace('sizeof(uint16_t)','sizeof(uint8_t)').replace('alignof(uint16_t)','alignof(uint8_t)')
    runtime=replace_once(runtime,'info.format=16;info.id_bytes=2;','info.format=10;info.id_bytes=0;')
    runtime=replace_once(runtime,'std::vector<uint8_t> table((size_t{1}<<24)+2,0);','std::vector<uint8_t> table(((size_t{1}<<24)*5)/4+4,0);')
    runtime=replace_once(runtime,'table.data()+begin,begin,65536','table.data()+begin*5/4,begin,65536')
    runtime=runtime.replace('h.direct_u10.size()/2','h.direct_u10.size()/4')
    runtime=replace_once(runtime,'h.palette_u10[h.direct_u10[address]]','h.palette_u10[jshc_channel::direct_u10_id(h.direct_u10.data(),uint32_t(address))]')
    runtime=runtime.replace('*output={1,1,16,0,','*output={1,1,10,0,').replace('精确16bit直接ID研究','精确10bit直接ID研究')
    runtime=runtime.replace('真正uint16数组对象，不对uint32 owner作不兼容类型写入；额外两个u16是4B guard。','按字节拥有5B/四ID数据，另加4B guard；不建立不兼容类型对象。')
    revision=re.search(r'(jshc_cc_revision\(void\)[^\{]*\{[^\}]*?return\s+)(\d+)',runtime)
    if not revision or revision[2]!='288':raise ValueError('不是冻结288版本')
    runtime=runtime[:revision.start(2)]+'289'+runtime[revision.end(2):]
    texts['channel_runtime.cpp']=runtime
    compile=texts['compile_avx2.cpp'];marker='bool avx2_compile_direct_u10('
    start=compile.index(marker);body_start=compile.index('{',start);level=1;end=body_start+1
    while level:
        if compile[end]=='{':level+=1
        elif compile[end]=='}':level-=1
        end+=1
    function=compile[start:end]
    prefix=function[:function.index('    // 无符号65535')].replace('uint16_t* destination','uint8_t* destination')
    suffix='''    // 拒绝任何高于1023的ID，禁止截断或饱和掩盖证明失败。
    const __m256i high=_mm256_srli_epi32(values,10);
    if(!_mm256_testz_si256(high,high))return false;
    uint32_t lanes[8];_mm256_storeu_si256(reinterpret_cast<__m256i*>(lanes),values);
    for(size_t group=0;group<2;++group) {
      const size_t k=4*group;
      const uint64_t packed=uint64_t(lanes[k])|(uint64_t(lanes[k+1])<<10)|
          (uint64_t(lanes[k+2])<<20)|(uint64_t(lanes[k+3])<<30);
      for(size_t byte=0;byte<5;++byte)destination[p*5/4+group*5+byte]=uint8_t(packed>>(8*byte));
    }
  }
  return true;
}'''
    texts['compile_avx2.cpp']=compile[:start]+prefix+suffix+compile[end:]
    contracts=texts['contracts.cpp']
    contracts=contracts.replace('无符号65535','10bit最大1023').replace('direct_u10_palette_fits(65536)','direct_u10_palette_fits(1024)').replace('direct_u10_palette_fits(65537)','direct_u10_palette_fits(1025)')
    a=contracts.index('    for(uint32_t id:');b=contracts.index('    uint8_t original[24]',a)
    replacement='''    for(uint32_t id:{0u,255u,256u,1023u,1024u,65535u,0xffffffffu}) {
      std::array<uint8_t,10> result;result.fill(123);
      const bool ok=avx2_compile_direct_u10(&view,cache,&id,result.data(),0,8);
      require(ok==(id<1024),"编译10bit ID范围证明失败");
      if(ok)for(uint32_t i=0;i<8;++i)require(direct_u10_id(result.data(),i)==id,"10bit编译序列错误");
      else for(uint8_t value:result)require(value==123,"非法ID仍改写输出");
    }
    constexpr size_t count=size_t{1}<<24,payload=count*5/4;
    Guarded table(payload+4),source(24),target(24);
    uint8_t* ids=table.data;std::memset(ids,0,payload+4);
    std::vector<uint32_t> palette(1024);
    for(size_t i=0;i<palette.size();++i)palette[i]=uint32_t((i*257+13)&0xffffff);
    const std::array<uint32_t,8> addresses={0,3,4,255,65535,0xfffffc,0xfffffe,0xffffff};
    const std::array<uint32_t,8> wanted={0,255,256,1023,256,255,1023,1023};
    uint8_t expected[24];
    for(size_t i=0;i<8;++i) {
      const size_t base=size_t(addresses[i]>>2)*5;const uint32_t shift=10*(addresses[i]&3u);
      uint64_t word=0;for(size_t j=0;j<5;++j)word|=uint64_t(ids[base+j])<<(8*j);
      word=(word&~(uint64_t(1023)<<shift))|(uint64_t(wanted[i])<<shift);
      for(size_t j=0;j<5;++j)ids[base+j]=uint8_t(word>>(8*j));
      const uint32_t a=addresses[i],v=palette[wanted[i]];
      for(int c=0;c<3;++c){source.data[3*i+c]=uint8_t(a>>(8*c));expected[3*i+c]=uint8_t(v>>(8*c));}
    }
'''
    contracts=contracts[:a]+replacement+contracts[b:]
    contracts=replace_once(contracts,'require(ids[count]==0 && ids[count+1]==0,"尾guard被写入");','require(ids[payload]==0 && ids[payload+1]==0 && ids[payload+2]==0 && ids[payload+3]==0,"尾guard被写入");')
    contracts=contracts.replace('compile_id_cases\\\":5','compile_id_cases\\\":7').replace('id_max\\\":65535','id_max\\\":1023')
    texts['contracts.cpp']=contracts
    out.mkdir()
    for name,text in texts.items():(out/name).write_text(text,encoding='utf-8',newline='\n')
    receipt={'builder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_directory':str(source),
        'baseline_freeze_keys':list(frozen.keys()),'copied_source':sources,'generated':{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in texts},
        'scope':'仅生成独立10bit源；未编译、未验收、未计时，原288文件不改。'}
    (ROOT/'artifacts/p16-direct-u10-generated-v1.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'generated':len(texts),'output':str(out)},flush=True)


if __name__=='__main__':main()
