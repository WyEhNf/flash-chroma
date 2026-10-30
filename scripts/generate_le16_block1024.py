"""固定1024B块，只将原实测4B绝对map改为LE16局部块ID。"""
from study_memory_rom import ROOT,sha,save

def replace(text,before,after,count=1):
    if text.count(before)!=count:raise AssertionError('生成替换计数不同：'+before)
    return text.replace(before,after)

def main():
    out=ROOT/'experiments/le16-block1024-runtime';out.mkdir(parents=True,exist_ok=False)
    base=ROOT/'experiments/memory-rom';header=(base/'memory_rom.h').read_text(encoding='utf-8').replace('JSHC_MEMORY_ROM_H','JSHC_LE16_BLOCK1024_H');header=replace(header,'/* 实验ROM：借用不可变字节，调用者保持其生命周期；不改变SLUT v1。 */','/* M10L v1固定1024B块与LE16局部ID；不可变借用，不改变SLUT或旧M16D。 */');(out/'memory_rom.h').write_text(header,encoding='utf-8',newline='\n')
    text=(base/'memory_rom.c').read_text(encoding='utf-8');text=replace(text,'static uint32_t le32(const uint8_t* p) {','static uint32_t le16(const uint8_t* p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8);}\nstatic uint32_t le32(const uint8_t* p) {')
    text=replace(text,'memcmp(p,"M16D",4)','memcmp(p,"M10L",4)')
    text=replace(text,'(bits!=0 && bits!=4 && bits!=6 && bits!=8 && bits!=10)','bits!=10')
    text=replace(text,'  if(bits==0 && length!=16777216u)return 1;\n','')
    text=replace(text,'  map_bytes=bits ? ((size_t)1<<(24-bits))*4 : 0;','  map_bytes=32768u;')
    text=replace(text,'  if(length<map_bytes || (bits && (length<map_bytes+((size_t)1<<bits) || (length-map_bytes)%((size_t)1<<bits))))return 1;','  if(length<map_bytes+1024u || (length-map_bytes)%1024u || (length-map_bytes)/1024u>65536u)return 1;')
    text=replace(text,'  if(bits)for(i=0;i<map_bytes;i+=4) {\n    const size_t offset=le32(model.table+i);\n    if(offset<map_bytes || offset>length-((size_t)1<<bits) || (offset-map_bytes)%((size_t)1<<bits))return 1;\n  }','  for(i=0;i<map_bytes;i+=2) {\n    const uint32_t id=le16(model.table+i);\n    if(id>=(length-map_bytes)/1024u)return 1;\n  }')
    begin=text.index('  if(bits==0) {',text.index('int jshc_mem_apply'));end=text.index('  return 0;\n}',begin)
    text=text[:begin]+'''  for(p=0;p<n;++p) {
    const uint32_t code=(uint32_t)source[3*p]|((uint32_t)source[3*p+1]<<8)|((uint32_t)source[3*p+2]<<16);
    const uint32_t offset=32768u+(le16(m->table+2*(code>>bits))<<10);
    const uint32_t v=m->palette[m->table[offset+(code&1023u)]];
    target[3*p]=(uint8_t)v;target[3*p+1]=(uint8_t)(v>>8);target[3*p+2]=(uint8_t)(v>>16);
  }
'''+text[end:];(out/'memory_rom.c').write_text(text,encoding='utf-8',newline='\n')
    source=ROOT/'artifacts/p16-memory-build-v2/memory_avx2_10.cpp';text=source.read_text(encoding='utf-8').replace('namespace jshc_mem_10 {','namespace jshc_le16_10 {');text=replace(text,'uint32_t offset;std::memcpy(&offset,table+4*(code>>10),4);return table[offset+(code&1023)];','uint16_t id;std::memcpy(&id,table+2*(code>>10),2);return table[32768u+(uint32_t(id)<<10)+(code&1023)];');(out/'channel_avx2_le16.cpp').write_text(text,encoding='utf-8',newline='\n')
    text=(ROOT/'experiments/compact-dictionary-runtime/memory_parallel.cpp').read_text(encoding='utf-8');text=replace(text,'namespace jshc_dict_17 {void avx2_chain_adaptive_linear_to(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;}\n','');text=text.replace('jshc_dict_24','jshc_le16_10');text=replace(text,'    case 17:fn=jshc_dict_17::avx2_chain_adaptive_linear_to;break;\n','');text=replace(text,'case 24:fn=','case 10:fn=');(out/'memory_parallel.cpp').write_text(text,encoding='utf-8',newline='\n')
    save(out/'generation.json',dict(source_sha256={str(x.relative_to(ROOT)).replace('\\','/'):sha(x) for x in (source,base/'memory_rom.h',base/'memory_rom.c',ROOT/'experiments/compact-dictionary-runtime/memory_parallel.cpp')},generated_sha256={x.name:sha(x) for x in out.glob('*') if x.suffix in ('.c','.h','.cpp')},scope='只生成固定1024块LE16版本。AVX像素仅lookup及namespace变化；C99逐像素算法不叠加store/ILP。'))
    print(out)
if __name__=='__main__':main()
