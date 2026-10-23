#include "memory_rom.h"
#include <limits.h>
#include <string.h>

typedef char jshc_requires_octets[(CHAR_BIT==8)?1:-1];
static uint32_t le24(const uint8_t* p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16);}
static uint32_t le32(const uint8_t* p) {return le24(p)|((uint32_t)p[3]<<24);}
static int overlaps(uintptr_t a,size_t na,uintptr_t b,size_t nb) {return na && nb && a<b+nb && b<a+na;}
static const uint8_t* color(const uint8_t* table,const uint8_t* p) {
  const uint32_t code=(uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16);
  return table+le24(table+3*(code>>4))+4*(code&15);
}
size_t jshc_mem_model_size(void) {return sizeof(jshc_mem_model);}
int jshc_mem_prepare(jshc_mem_model* out,const void* memory,size_t bytes) {
  const uint8_t* p=(const uint8_t*)memory;
  const uint32_t maps=3145728u;
  uint32_t length;
  size_t i;
  jshc_mem_model m;
  if(!out)return 1;
  if(bytes>UINTPTR_MAX-(uintptr_t)memory || overlaps((uintptr_t)out,sizeof(*out),(uintptr_t)memory,bytes))return 1;
  memset(out,0,sizeof(*out));
  if(!p || bytes<32 || memcmp(p,"M16C",4) || le32(p+4)!=1 || le32(p+8)!=24 || le32(p+12)!=4 || le32(p+20) || le32(p+24) || le32(p+28))return 1;
  length=le32(p+16);
  if(length!=bytes-32 || length<maps+64 || length>16777216u || (length-maps)%64)return 1;
  memset(&m,0,sizeof(m));m.blob=p;m.blob_bytes=bytes;m.table=p+32;m.log2_block=24;
  for(i=0;i<1048576u;++i) {
    const uint32_t off=le24(m.table+3*i);
    if(off<maps || off>length-64 || (off-maps)%64)return 1;
  }
  for(i=maps+3;i<length;i+=4)if(m.table[i])return 1;
  *out=m;return 0;
}
int jshc_mem_validate_io(const jshc_mem_model* m,const uint8_t* source,uint8_t* target,size_t n) {
  uintptr_t src=(uintptr_t)source,dst=(uintptr_t)target;
  size_t bytes;
  if(!m || !m->blob || !m->table || n>SIZE_MAX/3)return 1;
  bytes=3*n;
  if(!bytes)return 0;
  if(!source || !target || bytes>UINTPTR_MAX-src || bytes>UINTPTR_MAX-dst)return 1;
  if(source!=target && overlaps(src,bytes,dst,bytes))return 1;
  if(overlaps(dst,bytes,(uintptr_t)m,sizeof(*m)) || overlaps(dst,bytes,(uintptr_t)m->blob,m->blob_bytes))return 1;
  return 0;
}
int jshc_mem_apply(const jshc_mem_model* m,const uint8_t* source,uint8_t* target,size_t n) {
  size_t i=0,j;
  if(jshc_mem_validate_io(m,source,target,n))return 1;
  for(;n-i>=8;i+=8) {
    const uint8_t* colors[8];
    /* 先读全8个输入；序列化RGB32字节可标准memcpy，最后一项仅写3B。 */
    for(j=0;j<8;++j)colors[j]=color(m->table,source+3*(i+j));
    for(j=0;j<7;++j)memcpy(target+3*(i+j),colors[j],4);
    memcpy(target+3*(i+7),colors[7],3);
  }
  for(;i<n;++i)memcpy(target+3*i,color(m->table,source+3*i),3);
  return 0;
}
