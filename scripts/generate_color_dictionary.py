"""从冻结3B map像素循环生成M16C源码；只改变最终颜色读取依赖。"""
from study_memory_rom import ROOT,sha,save

def replace(text,before,after,count=1):
    if text.count(before)!=count:raise AssertionError('生成替换计数不同：'+before)
    return text.replace(before,after)

def main():
    source=ROOT/'experiments/compact-dictionary-runtime';out=ROOT/'experiments/color-dictionary-runtime'
    text=(source/'channel_avx2_24.cpp').read_text(encoding='utf-8')
    text=replace(text,'// 精确全域字节索引：四包独立读取先行，按RGB24读取合法对齐词。','// 精确RGB32块：3B map直接指向64B最终颜色块，省去palette依赖读取。')
    text=text.replace('namespace jshc_dict_24 {','namespace jshc_color_24 {')
    text=text.replace('lookup_id','lookup_color')
    text=replace(text,'uint32_t off;std::memcpy(&off,table+3*(code>>4),4);return table[(off&0xffffffu)+(code&15)];','uint32_t off,value;std::memcpy(&off,table+3*(code>>4),4);std::memcpy(&value,table+(off&0xffffffu)+4*(code&15),4);return value;')
    text=replace(text,'const auto value=[table,palette](uint32_t code) {return int32_t(palette[lookup_color(table,code)]);};','const auto value=[table](uint32_t code) {return int32_t(lookup_color(table,code));};')
    for i in range(8):text=replace(text,'palette[i'+str(i)+']','i'+str(i))
    text=replace(text,'const uint32_t value=palette[lookup_color(table,code)];','const uint32_t value=lookup_color(table,code);')
    if 'palette[' in text:raise AssertionError('仍有依赖palette读取')
    (out/'channel_avx2_color.cpp').write_text(text,encoding='utf-8',newline='\n')
    text=(source/'memory_parallel.cpp').read_text(encoding='utf-8')
    text=replace(text,'namespace jshc_dict_17 {void avx2_chain_adaptive_linear_to(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;}\n','')
    text=text.replace('namespace jshc_dict_24 {','namespace jshc_color_24 {')
    text=replace(text,'    case 17:fn=jshc_dict_17::avx2_chain_adaptive_linear_to;break;\n','')
    text=text.replace('jshc_dict_24::','jshc_color_24::')
    text=replace(text,'fn(m->table,m->palette,src+3*start,dst+3*start,n);','fn(m->table,nullptr,src+3*start,dst+3*start,n);')
    (out/'memory_parallel.cpp').write_text(text,encoding='utf-8',newline='\n')
    save(out/'generation.json',dict(source_sha256={str(x.relative_to(ROOT)):sha(x) for x in (source/'channel_avx2_24.cpp',source/'memory_parallel.cpp')},generated_sha256={str(x.relative_to(ROOT)):sha(x) for x in (out/'channel_avx2_color.cpp',out/'memory_parallel.cpp')},scope='循环/预取/输出布局继承旧3B；查表helper改为读取RGB32，移除palette依赖。旧源不修改。'))
    print(out)
if __name__=='__main__':main()
