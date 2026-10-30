"""从冻结紧密17bit快照生成独立16+1bit双平面源码，不执行编译或测量。"""
from study_memory_rom import ROOT,sha

def replace(text,before,after,count=1):
    if text.count(before)!=count:raise AssertionError('生成替换计数不同：'+before)
    return text.replace(before,after)

def main():
    source=ROOT/'experiments/compact-dictionary-runtime';out=ROOT/'experiments/split-dictionary-runtime'
    out.mkdir(parents=True,exist_ok=False)
    text=(source/'memory_rom.h').read_text(encoding='utf-8')
    text=text.replace('JSHC_COMPACT_DICTIONARY_H','JSHC_SPLIT_DICTIONARY_H')
    text=replace(text,'/* 独立M16P实验格式，固定16B块，entry_bits=24绝对字节偏移或17bit块ID。\n   结构布局与首阶段Python适配器一致；log2_block字段在本格式表示entry_bits。 */','/* 独立M16S实验格式：固定16B块，17bit块ID分为LE16低平面和1bit高平面。\n   结构布局与首阶段Python适配器一致；log2_block固定为17。 */')
    (out/'memory_rom.h').write_text(text,encoding='utf-8',newline='\n')
    text=(source/'memory_rom.c').read_text(encoding='utf-8')
    begin=text.index('static size_t map_bytes(');end=text.index('size_t jshc_mem_model_size',begin)
    text=text[:begin]+'''static uint32_t offset(const uint8_t* table,uint32_t block) {
  const uint8_t* low=table+2*block;
  const uint32_t lo=(uint32_t)low[0]|((uint32_t)low[1]<<8);
  const uint32_t hi=(table[2097152u+(block>>3)]>>(block&7))&1u;
  return 2228224u+((lo|(hi<<16))<<4);
}
'''+text[end:]
    text=replace(text,'memcmp(p,"M16P",4)','memcmp(p,"M16S",4)')
    text=replace(text,'(mode!=17 && mode!=24)','mode!=17')
    text=replace(text,'maps=map_bytes(mode);','maps=2228224u;')
    text=replace(text,'(mode==17 && (length-maps)/16>131072u)','(length-maps)/16>131072u')
    text=replace(text,'offset(m.table,mode,(uint32_t)i)','offset(m.table,(uint32_t)i)')
    text=replace(text,'offset(m->table,m->log2_block,code>>4)','offset(m->table,code>>4)')
    (out/'memory_rom.c').write_text(text,encoding='utf-8',newline='\n')
    text=(source/'channel_avx2_17.cpp').read_text(encoding='utf-8')
    text=text.replace('namespace jshc_dict_17 {','namespace jshc_split_17 {')
    text=replace(text,'// map末项的4B读取至多进入owned非空pool一字节；mask/shift丢弃邻接位。','// LE16低平面与高位字节均在map内，两个map读取互相独立；无需ROM对齐或padding。')
    text=replace(text,'const uint32_t bit=17*(code>>4);uint32_t word;std::memcpy(&word,table+(bit>>3),4);return table[2228224u+(((word>>(bit&7))&131071u)<<4)+(code&15)];','const uint32_t block=code>>4;uint16_t lo;std::memcpy(&lo,table+2*block,2);const uint32_t hi=(table[2097152u+(block>>3)]>>(block&7))&1u;return table[2228224u+((uint32_t(lo)|(hi<<16))<<4)+(code&15)];')
    (out/'channel_avx2_split.cpp').write_text(text,encoding='utf-8',newline='\n')
    text=(source/'memory_parallel.cpp').read_text(encoding='utf-8')
    text=text.replace('namespace jshc_dict_17 {','namespace jshc_split_17 {')
    line='namespace jshc_dict_24 {void avx2_chain_adaptive_linear_to(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;}\n'
    text=replace(text,line,'')
    text=replace(text,'case 17:fn=jshc_dict_17::avx2_chain_adaptive_linear_to;break;','case 17:fn=jshc_split_17::avx2_chain_adaptive_linear_to;break;')
    text=replace(text,'    case 24:fn=jshc_dict_24::avx2_chain_adaptive_linear_to;break;\n','')
    (out/'memory_parallel.cpp').write_text(text,encoding='utf-8',newline='\n')
    print(out,sha(source/'channel_avx2_17.cpp'))
if __name__=='__main__':main()
