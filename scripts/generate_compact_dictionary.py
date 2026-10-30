"""生成独立3B偏移/17bit块ID的AVX2桌面快照，不改已测ROM库。"""
from study_memory_rom import ROOT,sha

def replace(text,before,after,count=1):
    if text.count(before)!=count:raise AssertionError('生成替换计数不同：'+before)
    return text.replace(before,after)

def main():
    directory=ROOT/'experiments/compact-dictionary-runtime'
    original=ROOT/'experiments/skylake-andn-split-runtime/channel_avx2.cpp'
    source=original.read_text(encoding='utf-8')
    for mode in (17,24):
        text=source.replace('#include "suffix_cache.hpp"','#include <cstdint>')
        text=text.replace('namespace jshc_channel {','namespace jshc_dict_'+str(mode)+' {').replace('const uint32_t* table','const uint8_t* table')
        if mode==24:
            lookup='uint32_t off;std::memcpy(&off,table+3*(code>>4),4);return table[(off&0xffffffu)+(code&15)];'
        else:
            lookup='const uint32_t bit=17*(code>>4);uint32_t word;std::memcpy(&word,table+(bit>>3),4);return table[2228224u+(((word>>(bit&7))&131071u)<<4)+(code&15)];'
        helper='\n// map末项的4B读取至多进入owned非空pool一字节；mask/shift丢弃邻接位。\ninline __attribute__((always_inline)) uint32_t lookup_id(const uint8_t* table,uint32_t code) {\n  '+lookup+'\n}\n'
        text=text.replace('namespace {','namespace {\n'+helper,1)
        text=text.replace('reinterpret_cast<const uint8_t*>(table)[code]','lookup_id(table,code)').replace('return bytes[code&0xffffff];','return lookup_id(bytes,code&0xffffff);')
        (directory/('channel_avx2_'+str(mode)+'.cpp')).write_text(text,encoding='utf-8',newline='\n')
    text=(ROOT/'experiments/memory-rom/memory_parallel.cpp').read_text(encoding='utf-8')
    begin=text.index('#if defined(JSHC_MEM_AVX2)');end=text.index('uint32_t jshc_mem_capabilities')
    text=text[:begin]+'''#if defined(JSHC_MEM_AVX2)
namespace jshc_dict_17 {void avx2_chain_adaptive_linear_to(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;}
namespace jshc_dict_24 {void avx2_chain_adaptive_linear_to(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;}
#endif
'''+text[end:]
    begin=text.index('  switch(m->log2_block)');end=text.index('#if defined(_OPENMP)',begin)
    text=text[:begin]+'''  switch(m->log2_block) {
    case 17:fn=jshc_dict_17::avx2_chain_adaptive_linear_to;break;
    case 24:fn=jshc_dict_24::avx2_chain_adaptive_linear_to;break;
    default:return 1;
  }
#endif
'''+text[end:]
    begin=text.index('#if defined(JSHC_MEM_ANDN)');end=text.index('      fn(',begin)
    text=text[:begin]+text[end:]
    (directory/'memory_parallel.cpp').write_text(text,encoding='utf-8',newline='\n')
    text=(ROOT/'scripts/verify_memory_rom_contract.py').read_text(encoding='utf-8')
    text=text.replace('rom-6.bin','rom-24.bin').replace('for bits in (0,4,6,8,10):','for bits in (17,24):')
    (ROOT/'scripts/verify_compact_dictionary_contract.py').write_text(text,encoding='utf-8',newline='\n')
    text=(ROOT/'scripts/bench_memory_rom.py').read_text(encoding='utf-8')
    begin=text.index('def labels():');end=text.index('def setup(',begin)
    text=text[:begin]+"def labels():return ['ref78','ref80','dict32','avx2_24','avx2_17','c99_24','c99_17']\n"+text[end:]
    text=replace(text,'def setup(a,label):','''def setup(a,label):
    if label=='dict32':
        plan=read(ROOT/'experiments/compact-dictionary-v1.json');path=Path(plan['reference32']['path']);rom=Path(plan['input_rom_path'])
        if sha(path)!=plan['reference32']['sha256'] or sha(rom)!=plan['input_rom_sha256']:raise ValueError('原32bit字典身份变化')
        d=romlib(path);m,keep=loadrom(d,rom)
        def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,1,threads)
        return apply,(d,m,keep),rom.stat().st_size+ct.sizeof(Model),str(path),sha(path)
''')
    text=replace(text,'    if a.worker_index is not None or a.rss:return worker(a)','''    plan=read(ROOT/'experiments/compact-dictionary-v1.json')
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or a.repeats!=5:raise ValueError('冻结源/五轮协议变化')
    if a.worker_index is not None or a.rss:return worker(a)''')
    text=replace(text,"    save(a.output/'summary.json',dict(purpose=__doc__,script_sha256=sha(__file__),ratios=ratios,tiers=tiers,",'''    for key,control in controls.items():
        if not control['pass_']:tiers[key]={str(t):None for t in (100,90,80,70,60,50)}
    save(a.output/'summary.json',dict(purpose=__doc__,script_sha256=sha(__file__),plan_sha256=sha(ROOT/'experiments/compact-dictionary-v1.json'),ratios=ratios,tiers=tiers,''')
    (ROOT/'scripts/bench_compact_dictionary.py').write_text(text,encoding='utf-8',newline='\n')
    print(directory,sha(original))
if __name__=='__main__':main()
