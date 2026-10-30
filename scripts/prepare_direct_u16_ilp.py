"""从已冻结287与87实际核生成288初始独立源；后续合同增强以提交源码为准。"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('预期唯一的源码标记失配：'+old)
    return text.replace(old,new,1)


def main():
    source=ROOT/'experiments/p16-direct-u16-runtime';target=ROOT/'experiments/p16-direct-u16-ilp-runtime'
    if target.exists():raise ValueError('不覆盖288源')
    target.mkdir()
    for path in source.iterdir():
        if not path.is_file():continue
        text=path.read_text(encoding='utf-8')
        if path.name=='channel_runtime.cpp':
            text=once(text,'return 287;','return 288;')
            text=once(text,'h.palette_u16.data(),data,data,vectorized);','h.palette_u16.data(),data,data,vectorized,h.andn_normal_supported?(workers>1?2u:1u):0u);')
            text=once(text,'h.palette_u16.data(),in,target,vectorized);','h.palette_u16.data(),in,target,vectorized,h.andn_normal_supported?3u:0u);')
        elif path.name=='direct_u16.hpp':
            text=once(text,'const uint8_t*,uint8_t*,size_t) noexcept;','const uint8_t*,uint8_t*,size_t,uint32_t mode=0) noexcept;')
        elif path.name=='CMakeLists.txt':
            text=text.replace('p16_direct_u16 LANGUAGES','p16_direct_u16_ilp LANGUAGES').replace('jshc_direct_u16','jshc_direct_u16_ilp').replace('p16_direct_u16_contracts','p16_direct_u16_ilp_contracts')
            text=text.replace('direct_u16_avx2.cpp','direct_u16_avx2.cpp linear.cpp andn_inplace.cpp andn_outplace.cpp normal_inplace.cpp')
            text+='\nset_source_files_properties(linear.cpp PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")\n'
            text+='set_source_files_properties(andn_inplace.cpp andn_outplace.cpp normal_inplace.cpp PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off;-mbmi")\n'
        elif path.name=='direct_u16_avx2.cpp':continue
        (target/path.name).write_text(text,encoding='utf-8',newline='\n')
    base=ROOT/'experiments/skylake-andn-normal-runtime'
    for name,original in [('linear.cpp','channel_avx2.cpp'),('andn_inplace.cpp','andn_inplace/channel_avx2.cpp'),
            ('andn_outplace.cpp','andn_outplace/channel_avx2.cpp'),('normal_inplace.cpp','normal_inplace/channel_avx2.cpp')]:
        text=(base/original).read_text(encoding='utf-8')
        text=text.replace('#include "suffix_cache.hpp"','#include "direct_u16.hpp"').replace('#include "../suffix_cache.hpp"','#include "direct_u16.hpp"')
        text=text.replace('const uint32_t* table','const uint16_t* table')
        text=text.replace('reinterpret_cast<const uint8_t*>(table)[code]','table[code]')
        text=text.replace('const uint8_t* bytes=reinterpret_cast<const uint8_t*>(table);','const uint16_t* bytes=table;')
        text=text.replace('avx2_chain_pair48_to','avx2_direct_u16_pair48_to').replace('avx2_chain_pair48','avx2_direct_u16_pair48')
        text=text.replace('avx2_chain_adaptive_linear_to','avx2_direct_u16_linear_to').replace('avx2_chain_adaptive_linear','avx2_direct_u16_linear')
        text=text.replace('avx2_chain_andn_normal_mt','avx2_direct_u16_normal_mt')
        text=text.replace('精确全域字节索引','精确全域uint16索引')
        (target/name).write_text(text,encoding='utf-8',newline='\n')
    (target/'direct_u16_avx2.cpp').write_text('''// 288仅替换apply核；表/prepare/vector与287相同，输入地址仍R低/G中/B高。
#include "direct_u16.hpp"
namespace jshc_channel {
void avx2_direct_u16_linear_to(const uint16_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;
void avx2_direct_u16_pair48(const uint16_t*,const uint32_t*,uint8_t*,size_t) noexcept;
void avx2_direct_u16_pair48_to(const uint16_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;
void avx2_direct_u16_normal_mt(const uint16_t*,const uint32_t*,uint8_t*,size_t) noexcept;
void avx2_direct_u16(const uint16_t* ids,const uint32_t* palette,const uint8_t* source,uint8_t* output,size_t pixels,uint32_t mode) noexcept {
  if(mode==2 && source==output)avx2_direct_u16_normal_mt(ids,palette,output,pixels);
  else if(mode==1 && source==output)avx2_direct_u16_pair48(ids,palette,output,pixels);
  else if(mode==3 || mode==1 || mode==2)avx2_direct_u16_pair48_to(ids,palette,source,output,pixels);
  else avx2_direct_u16_linear_to(ids,palette,source,output,pixels);
}
}
''',encoding='utf-8',newline='\n')
    quality=(ROOT/'scripts/check_direct_u16_native.py').read_text(encoding='utf-8')
    quality=quality.replace('p16_direct_u16_quality_v1','p16_direct_u16_ilp_quality_v1').replace('experiments/p16-direct-u16-runtime','experiments/p16-direct-u16-ilp-runtime')
    quality=quality.replace('experiments/p16-direct-u16-plan-v1.md','experiments/p16-direct-u16-ilp-plan-v1.md')
    quality=once(quality,'library.revision==287','library.revision==288')
    (ROOT/'scripts/check_direct_u16_ilp_native.py').write_text(quality,encoding='utf-8',newline='\n')
    print('288独立源已生成，尚未编译或执行质量。')


if __name__=='__main__':main()
