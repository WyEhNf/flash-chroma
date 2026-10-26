"""固定tag版：常量直接RGB24，非恒定原ID块；不改变已有源或执行数值。"""
from study_memory_rom import ROOT,sha,save

def replace(text,before,after,count=1):
    if text.count(before)!=count:raise AssertionError('生成替换计数不同：'+before)
    return text.replace(before,after)
def main():
    base=ROOT/'experiments/compact-dictionary-runtime';out=ROOT/'experiments/tagged-block16-runtime'
    if (out/'channel_avx2_tag.cpp').exists():raise FileExistsError('不覆盖已生成版本')
    text=(base/'channel_avx2_24.cpp').read_text(encoding='utf-8').replace('namespace jshc_dict_24 {','namespace jshc_tag_16 {').replace('lookup_id','lookup_rgb')
    text=replace(text,'// 精确全域字节索引：四包独立读取先行，按RGB24读取合法对齐词。','// M16T常量直接RGB、其余原ID pool；AVX输入与输出循环保持。')
    text=replace(text,'// map末项的4B读取至多进入owned非空pool一字节；mask/shift丢弃邻接位。','// LE32 map末项恰至map边界；全常量允许无pool，条件返回前不形成fallback地址。')
    text=replace(text,'uint32_t lookup_rgb(const uint8_t* table,uint32_t code)','uint32_t lookup_rgb(const uint8_t* table,const uint32_t* palette,uint32_t code)')
    text=replace(text,'uint32_t off;std::memcpy(&off,table+3*(code>>4),4);return table[(off&0xffffffu)+(code&15)];','uint32_t word;std::memcpy(&word,table+4*(code>>4),4);if(word&0x80000000u)return word&0xffffffu;return palette[table[word+(code&15)]];')
    text=replace(text,'palette[lookup_rgb(table,code)]','lookup_rgb(table,palette,code)',2)
    text=replace(text,'const auto id=[bytes,p]','const auto id=[bytes,p,palette]')
    text=replace(text,'lookup_rgb(bytes,code&0xffffff)','lookup_rgb(bytes,palette,code&0xffffff)')
    for i in range(8):text=replace(text,'palette[i'+str(i)+']','i'+str(i))
    if text.count('palette[')!=1:raise AssertionError('外层仍有palette访问，或fallback被错误移除')
    (out/'channel_avx2_tag.cpp').write_text(text,encoding='utf-8',newline='\n')
    text=(base/'memory_parallel.cpp').read_text(encoding='utf-8');text=replace(text,'namespace jshc_dict_17 {void avx2_chain_adaptive_linear_to(const uint8_t*,const uint32_t*,const uint8_t*,uint8_t*,size_t) noexcept;}\n','');text=text.replace('jshc_dict_24','jshc_tag_16');text=replace(text,'    case 17:fn=jshc_dict_17::avx2_chain_adaptive_linear_to;break;\n','');text=replace(text,'case 24:fn=','case 4:fn=');(out/'memory_parallel.cpp').write_text(text,encoding='utf-8',newline='\n')
    # 复制已经独立验证的受控worker循环，生成后以新文件身份执行，不修改旧模块。
    old=(ROOT/'scripts/bench_le16_block1024.py').read_text(encoding='utf-8');worker=old[old.index('def worker(a):'):old.index("if __name__=='__main__':")];prefix=(ROOT/'scripts/tagged_block16_bench_prefix.py').read_text(encoding='utf-8');suffix=(ROOT/'scripts/tagged_block16_bench_suffix.py').read_text(encoding='utf-8');(ROOT/'scripts/bench_tagged_block16.py').write_text(prefix+'\n'+worker+suffix,encoding='utf-8',newline='\n')
    save(out/'generation.json',dict(inputs={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in (base/'channel_avx2_24.cpp',base/'memory_parallel.cpp',ROOT/'scripts/bench_le16_block1024.py',ROOT/'scripts/tagged_block16_bench_prefix.py',ROOT/'scripts/tagged_block16_bench_suffix.py')},scope='单版普通条件返回，无masked gather/likely或参数扫描。像素外层接最终RGB，只有fallback helper读palette。计时worker复制旧受控循环，六角色由新setup定义。'))
    print(out)
if __name__=='__main__':main()
