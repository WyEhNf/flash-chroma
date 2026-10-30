"""生成唯一C7BK AVX lookup及固定受控测量驱动，不执行像素或导出。"""
from study_memory_rom import ROOT,sha,save
def replace(text,before,after):
    if text.count(before)!=1:raise AssertionError('唯一生成替换计数：'+before)
    return text.replace(before,after)
def main():
    source=ROOT/'experiments/tagged-block16-runtime/channel_avx2_tag.cpp';out=ROOT/'experiments/rgb3d-palette7-runtime/channel_avx2_rgb3d7.cpp'
    if out.exists():raise FileExistsError(out)
    text=source.read_text(encoding='utf-8').replace('jshc_tag_16','jshc_rgb3d7').replace('const uint32_t* palette','const uint8_t* palette')
    text=replace(text,'// M16T常量直接RGB、其余原ID pool；AVX输入与输出循环保持。','// C7BK精确7bit本地palette；沿用原输入/输出循环。')
    text=replace(text,'// LE32 map末项恰至map边界；全常量允许无pool，条件返回前不形成fallback地址。','// byte指针与memcpy允许非对齐ROM；最后bitstream短读只进入自有guard。')
    text=replace(text,'uint32_t word;std::memcpy(&word,table+4*(code>>4),4);if(word&0x80000000u)return word&0xffffffu;return palette[table[word+(code&15)]];','const uint32_t bit=7*code,bank=((code>>5)&7)|((code>>10)&56)|((code>>15)&448);uint16_t word;std::memcpy(&word,table+(bit>>3),2);const uint32_t id=(word>>(bit&7))&127;uint32_t value;std::memcpy(&value,palette+4*((bank<<7)|id),4);return value;')
    if 'palette[' in text or 'word&0x80000000' in text:raise AssertionError('残留旧lookup')
    out.write_text(text,encoding='utf-8',newline='\n')
    old=(ROOT/'scripts/bench_le16_block1024.py').read_text(encoding='utf-8');worker=old[old.index('def worker(a):'):old.index("if __name__=='__main__':")];prefix=ROOT/'scripts/rgb3d7_bench_prefix.py';suffix=ROOT/'scripts/rgb3d7_bench_suffix.py';(ROOT/'scripts/bench_rgb3d7.py').write_text(prefix.read_text(encoding='utf-8')+'\n'+worker+suffix.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    save(out.parent/'generation.json',dict(inputs={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in (source,ROOT/'scripts/bench_le16_block1024.py',prefix,suffix)},scope='只替换lookup、palette字节指针和namespace/说明；外层输入/输出/OMP不变。worker复制已验证0x55循环，六角色由新setup定义。'))
    print(out)
if __name__=='__main__':main()
