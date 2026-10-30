#include "memory_rom.h"
#include <limits.h>
#include <string.h>
typedef char jshc_octets[(CHAR_BIT==8)?1:-1];
static uint32_t le16(const uint8_t* p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8);}
static uint32_t le32(const uint8_t* p) {return le16(p)|(le16(p+2)<<16);}
static int overlaps(uintptr_t a,size_t na,uintptr_t b,size_t nb) {return na && nb && a<b+nb && b<a+na;}
static uint32_t bank_id(uint32_t code) {return ((code>>5)&7)|((code>>10)&56)|((code>>15)&448);}
static uint32_t local_id(const uint8_t* table,uint32_t code) {const uint32_t bit=7*code;return (le16(table+(bit>>3))>>(bit&7))&127;}
static uint32_t index_id(const uint8_t* table,uint32_t code) {return (bank_id(code)<<7)|local_id(table,code);}
size_t jshc_mem_model_size(void) {return sizeof(jshc_mem_model);}
int jshc_mem_prepare(jshc_mem_model* out,const void* memory,size_t bytes) {
  const uint8_t* p=(const uint8_t*)memory;
  jshc_mem_model m;
  uint32_t bank,i;
  if(!out)return 1;
  if(bytes>UINTPTR_MAX-(uintptr_t)memory || overlaps((uintptr_t)out,sizeof(*out),(uintptr_t)memory,bytes))return 1;
  memset(out,0,sizeof(*out));
  if(!p || bytes!=14943268u || memcmp(p,"C7BK",4) || le32(p+4)!=1 || le32(p+8)!=512 || le32(p+12)!=7 || le32(p+16)!=14680064u || le32(p+20)!=1 || le32(p+24)!=128 || le32(p+28))return 1;
  m.blob=p;m.blob_bytes=bytes;m.table=p+1056;m.palettes=p+14681124u;
  for(i=0;i<4;++i)if(p[14681120u+i])return 1;
  for(bank=0;bank<512;++bank) {
    const uint32_t count=le16(p+32+2*bank);
    if(!count || count>128)return 1;
    for(i=0;i<128;++i) {const uint32_t value=le32(m.palettes+4*(128*bank+i));if(value>0xffffffu || (i>=count && value))return 1;}
  }
  for(i=0;i<16777216u;++i)if(local_id(m.table,i)>=le16(p+32+2*bank_id(i)))return 1;
  *out=m;return 0;
}
int jshc_mem_validate_io(const jshc_mem_model* m,const uint8_t* source,uint8_t* target,size_t n) {
  const uintptr_t src=(uintptr_t)source,dst=(uintptr_t)target;
  size_t bytes;
  if(!m || !m->blob || !m->table || !m->palettes || n>SIZE_MAX/3)return 1;
  bytes=3*n;if(!bytes)return 0;
  if(!source || !target || bytes>UINTPTR_MAX-src || bytes>UINTPTR_MAX-dst)return 1;
  if(source!=target && overlaps(src,bytes,dst,bytes))return 1;
  if(overlaps(dst,bytes,(uintptr_t)m,sizeof(*m)) || overlaps(dst,bytes,(uintptr_t)m->blob,m->blob_bytes))return 1;
  return 0;
}
int jshc_mem_apply(const jshc_mem_model* m,const uint8_t* source,uint8_t* target,size_t n) {
  size_t p=0;
  if(jshc_mem_validate_io(m,source,target,n))return 1;
  for(;n-p>=8;p+=8) {
    uint32_t indices[8];unsigned k;
    /* 先读完全部输入，随后重叠4B写只覆盖本组下一像素，末像素仅写3B。 */
    for(k=0;k<8;++k) {const uint8_t* in=source+3*(p+k);const uint32_t code=(uint32_t)in[0]|((uint32_t)in[1]<<8)|((uint32_t)in[2]<<16);indices[k]=index_id(m->table,code);}
    for(k=0;k<7;++k)memcpy(target+3*(p+k),m->palettes+4*indices[k],4);
    memcpy(target+3*(p+7),m->palettes+4*indices[7],3);
  }
  for(;p<n;++p) {const uint32_t code=(uint32_t)source[3*p]|((uint32_t)source[3*p+1]<<8)|((uint32_t)source[3*p+2]<<16);memcpy(target+3*p,m->palettes+4*index_id(m->table,code),3);}
  return 0;
}
