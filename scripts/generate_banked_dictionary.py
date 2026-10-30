"""只为离线冻结规则选中的4bank生成独立M16B源码与验证快照，不构建native。"""
from study_memory_rom import ROOT,read,sha

def replace(text,before,after,count=1):
    if text.count(before)!=count:raise AssertionError('替换计数不同：'+before)
    return text.replace(before,after)

def main():
    result=read(ROOT/'artifacts/p16-banked-dictionary-profile-v1/results.json')
    if not result['selected'] or result['selected']['banks']!=4 or result['selected']['resident_bytes']!=4248640:raise AssertionError('必须遵守唯一最小容量选择')
    old=ROOT/'experiments/split-dictionary-runtime';out=ROOT/'experiments/banked-dictionary-runtime';out.mkdir(parents=True,exist_ok=False)
    text=(old/'memory_rom.h').read_text(encoding='utf-8').replace('JSHC_SPLIT_DICTIONARY_H','JSHC_BANKED_DICTIONARY_H')
    text=replace(text,'/* 独立M16S实验格式：固定16B块，17bit块ID分为LE16低平面和1bit高平面。\n   结构布局与首阶段Python适配器一致；log2_block固定为17。 */','/* 独立M16B实验格式：四个连续bank，LE16局部ID，保留256合法palette。\n   独立bases[4]缓存已验证pool base，model较旧格式增加16B；log2_block为4。 */')
    text=replace(text,'  uint32_t palette_size;','  uint32_t palette_size;\n  uint32_t bases[4];')
    (out/'memory_rom.h').write_text(text,encoding='utf-8',newline='\n')
    text=(old/'memory_rom.c').read_text(encoding='utf-8');begin=text.index('static uint32_t offset(');end=text.index('size_t jshc_mem_model_size',begin)
    text=text[:begin]+'''static uint32_t offset(const uint8_t* table,const uint32_t* bases,uint32_t block) {
  const uint8_t* p=table+2*block;
  const uint32_t local=(uint32_t)p[0]|((uint32_t)p[1]<<8);
  return bases[block>>18]+(local<<4);
}
'''+text[end:]
    text=text.replace('memcmp(p,"M16S",4)','memcmp(p,"M16B",4)').replace('mode!=17','mode!=4')
    text=replace(text,'maps=2228224u;','maps=2097152u;')
    text=replace(text,'if(length<maps+16 || (length-maps)%16 || (length-maps)/16>131072u)return 1;','if(length<maps+16+64)return 1;')
    text=replace(text,'  for(i=0;i<1048576u;++i) {','''  /* ROM末端length与四个连续pool base共同限定每bank范围。 */
  for(i=0;i<4;++i) {
    const uint32_t base=le32(m.table+maps+4*i);
    const uint32_t end=i==3?length:le32(m.table+maps+4*(i+1));
    if((!i && base!=maps+16) || end<=base || (end-base)%16 || (end-base)/16>65536u)return 1;
    m.bases[i]=base;
  }
  for(i=0;i<1048576u;++i) {''')
    text=replace(text,'const uint32_t off=offset(m.table,(uint32_t)i);\n    if(off<maps || off>length-16 || (off-maps)%16)return 1;','const uint32_t bank=(uint32_t)i>>18;\n    const uint32_t off=offset(m.table,m.bases,(uint32_t)i);\n    const uint32_t end=bank==3?length:m.bases[bank+1];\n    if(off<m.bases[bank] || off>end-16)return 1;')
    text=replace(text,'for(i=maps;i<length;++i)','for(i=maps+16;i<length;++i)')
    text=replace(text,'offset(m->table,code>>4)','offset(m->table,m->bases,code>>4)')
    (out/'memory_rom.c').write_text(text,encoding='utf-8',newline='\n')
    text=(old/'channel_avx2_split.cpp').read_text(encoding='utf-8').replace('namespace jshc_split_17 {','namespace jshc_bank_4 {')
    text=replace(text,'// LE16低平面与高位字节均在map内，两个map读取互相独立；无需ROM对齐或padding。','// map只读LE16；四个base已验证并缓存到独立model.bases，不复用palette槽。')
    text=replace(text,'lookup_id(const uint8_t* table,uint32_t code)','lookup_id(const uint8_t* table,const uint32_t* bases,uint32_t code)')
    text=replace(text,'const uint32_t block=code>>4;uint16_t lo;std::memcpy(&lo,table+2*block,2);const uint32_t hi=(table[2097152u+(block>>3)]>>(block&7))&1u;return table[2228224u+((uint32_t(lo)|(hi<<16))<<4)+(code&15)];','uint16_t local;std::memcpy(&local,table+2*(code>>4),2);return table[bases[code>>22]+(uint32_t(local)<<4)+(code&15)];')
    text=text.replace('const uint32_t* palette,','const uint32_t* palette,const uint32_t* bases,').replace('[table,palette]','[table,palette,bases]').replace('[bytes,p]','[bytes,p,bases]')
    text=text.replace('lookup_id(table,code)','lookup_id(table,bases,code)').replace('lookup_id(bytes,code&0xffffff)','lookup_id(bytes,bases,code&0xffffff)')
    for name in ('read','read_wide','scalar_one','run'):text=text.replace(name+'(table,palette,',name+'(table,palette,bases,')
    (out/'channel_avx2_bank.cpp').write_text(text,encoding='utf-8',newline='\n')
    text=(old/'memory_parallel.cpp').read_text(encoding='utf-8').replace('jshc_split_17','jshc_bank_4').replace('case 17:','case 4:')
    text=text.replace('const uint8_t*,const uint32_t*,const uint8_t*','const uint8_t*,const uint32_t*,const uint32_t*,const uint8_t*').replace('fn(m->table,m->palette,','fn(m->table,m->palette,m->bases,')
    (out/'memory_parallel.cpp').write_text(text,encoding='utf-8',newline='\n')
    text=(ROOT/'scripts/build_split_dictionary.py').read_text(encoding='utf-8').replace('M16S','M16B').replace('split-dictionary-v1.json','banked-dictionary-native-v1.json').replace('split-dictionary-runtime','banked-dictionary-runtime').replace('jshc_split_c99.dll','jshc_bank_c99.dll').replace('channel_avx2_split','channel_avx2_bank').replace('jshc_memory_split.dll','jshc_memory_bank.dll')
    (ROOT/'scripts/build_banked_dictionary.py').write_text(text,encoding='utf-8',newline='\n')
    text=(ROOT/'scripts/verify_split_dictionary.py').read_text(encoding='utf-8').replace('M16S','M16B').replace('split-dictionary-v1.json','banked-dictionary-native-v1.json').replace('jshc_split_c99.dll','jshc_bank_c99.dll').replace('jshc_memory_split.dll','jshc_memory_bank.dll').replace('rom-17.bin','rom-4.bin').replace('2026102411','2026102412')
    text=replace(text,'from study_memory_rom import ROOT,Model,U8,romlib,loadrom,sha,read,save,env','from study_memory_rom import ROOT,U8,sha,read,save,env\nfrom banked_dictionary_support import BankModel as Model,banklib as romlib,loadbank as loadrom')
    text=replace(text,'((4,2),(8,24),(12,0),(12,257),(16,4),(20,1),(32,0xffffffff))','((4,2),(8,17),(12,0),(12,257),(16,4),(20,1),(32,0xffffffff))')
    text=replace(text,"data[1056:1058]=b'\\xff\\xff';data[1056+2097152]|=1","data[1056:1058]=b'\\xff\\xff'")
    text=replace(text,'last_id=(len(raw)-1056-2228224)//16-1','last_base=struct.unpack_from(\'<I\',raw,1056+2097152+12)[0];last_id=(len(raw)-1056-last_base)//16-1')
    text=replace(text,'    forced[1056+2228223]=(forced[1056+2228223]&127)|((last_id>>16)<<7)\n','')
    extra='''    for byte,value in ((1056+2097152,0),(1056+2097152+4,0),(1056+2097152+12,0xffffffff)):
        data=bytearray(raw);struct.pack_into('<I',data,byte,value);bad(data)
'''
    text=replace(text,'    for offset in (1,3,7,31):',extra+'    for offset in (1,3,7,31):')
    fixture='''    # 完整256项palette的正向合同：最高四个ID不得被bases缓存覆盖。
    legal=bytearray(raw);struct.pack_into('<I',legal,12,256)
    last_base=struct.unpack_from('<I',legal,1056+2097152+12)[0];last_local=(len(legal)-1056-last_base)//16-1
    struct.pack_into('<H',legal,1056+2097150,last_local);legal[-4:]=bytes((252,253,254,255));gold=bytearray()
    for j in range(4):
        color=bytes((11+37*j,22+23*j,33+13*j));legal[32+4*(252+j):36+4*(252+j)]=color+b'\\x00';gold.extend(color)
    holder=(ct.c_uint8*len(legal)).from_buffer(legal);model=Model()
    if d.jshc_mem_prepare(ct.byref(model),holder,len(legal)):raise AssertionError('256项palette未接受')
    values=np.array((252,255,255,253,255,255,254,255,255,255,255,255),dtype=np.uint8)
    for kernel,threads in ((0,1),(1,1),(1,4)):
        for same in (False,True):
            target=values.copy() if same else np.empty_like(values)
            if apply(target.ctypes.data if same else values.ctypes.data,target.ctypes.data,4,kernel,threads,model) or bytes(target)!=bytes(gold):raise AssertionError('最高四个合法palette颜色被覆盖')
            finite+=1
'''
    text=replace(text,'    forced=bytearray(raw);',fixture+'    forced=bytearray(raw);')
    (ROOT/'scripts/verify_banked_dictionary.py').write_text(text,encoding='utf-8',newline='\n')
    print(out,sha(out/'memory_rom.c'))
if __name__=='__main__':main()
