/* 只复用已验证的范围/重叠校验；旧格式出口改名保留，不修改冻结核心。 */
#define jshc_mem_prepare jshc_mem_prepare_legacy
#define jshc_mem_apply jshc_mem_apply_legacy
#include "../memory-rom/memory_rom.c"
#undef jshc_mem_prepare
#undef jshc_mem_apply

static uint32_t bit_id(const uint8_t* table,uint32_t code) {
  const uint32_t bit=code*7u,offset=bit>>3;
  return (((uint32_t)table[offset]|((uint32_t)table[offset+1]<<8))>>(bit&7u))&127u;
}
JSHC_MEM_API int jshc_mem_prepare(jshc_mem_model* out,const void* memory,size_t bytes) {
  const uint8_t* p=(const uint8_t*)memory;
  jshc_mem_model model;
  uint32_t count;
  size_t i;
  if(!out)return 1;
  if(bytes>UINTPTR_MAX-(uintptr_t)memory || overlaps((uintptr_t)out,sizeof(*out),(uintptr_t)memory,bytes))return 1;
  memset(out,0,sizeof(*out));
  if(!p || bytes!=14681124u || memcmp(p,"P16B",4) || le32(p+4)!=1 || le32(p+8)!=7 ||
     le32(p+16)!=14680064u || le32(p+20) || le32(p+24) || le32(p+28))return 1;
  count=le32(p+12);
  if(!count || count>128)return 1;
  for(i=bytes-4;i<bytes;++i)if(p[i])return 1;
  memset(&model,0,sizeof(model));
  model.blob=p;model.blob_bytes=bytes;model.table=p+1056;model.log2_block=7;model.palette_size=count;
  for(i=0;i<256;++i) {
    model.palette[i]=le32(p+32+4*i);
    if(model.palette[i]>0xffffffu || (i>=count && model.palette[i]))return 1;
  }
  for(i=0;i<16777216u;++i)if(bit_id(model.table,(uint32_t)i)>=count)return 1;
  *out=model;return 0;
}
JSHC_MEM_API int jshc_mem_apply(const jshc_mem_model* m,const uint8_t* source,uint8_t* target,size_t n) {
  size_t p=0;
  if(jshc_mem_validate_io(m,source,target,n))return 1;
  for(;n-p>=8;p+=8) {
    uint32_t ids[8];unsigned k;
    for(k=0;k<8;++k) {
      const uint8_t* in=source+3*(p+k);
      ids[k]=bit_id(m->table,(uint32_t)in[0]|((uint32_t)in[1]<<8)|((uint32_t)in[2]<<16));
    }
    for(k=0;k<7;++k)memcpy(target+3*(p+k),m->blob+32+4*ids[k],4);
    memcpy(target+3*(p+7),m->blob+32+4*ids[7],3);
  }
  for(;p<n;++p) {
    const uint32_t code=(uint32_t)source[3*p]|((uint32_t)source[3*p+1]<<8)|((uint32_t)source[3*p+2]<<16);
    memcpy(target+3*p,m->blob+32+4*bit_id(m->table,code),3);
  }
  return 0;
}
