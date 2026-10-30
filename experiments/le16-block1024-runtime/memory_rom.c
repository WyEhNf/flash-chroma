#include "memory_rom.h"
#include <limits.h>
#include <string.h>

typedef char jshc_mem_requires_octets[(CHAR_BIT == 8) ? 1 : -1];
static uint32_t le16(const uint8_t* p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8);}
static uint32_t le32(const uint8_t* p) {
  return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static int overlaps(uintptr_t a,size_t na,uintptr_t b,size_t nb) {
  return na && nb && a < b+nb && b < a+na;
}
size_t jshc_mem_model_size(void) { return sizeof(jshc_mem_model); }
int jshc_mem_prepare(jshc_mem_model* out,const void* memory,size_t bytes) {
  const uint8_t* p=(const uint8_t*)memory;
  jshc_mem_model model;
  uint32_t bits,count,length;
  size_t map_bytes,i;
  if(!out)return 1;
  if(bytes>UINTPTR_MAX-(uintptr_t)memory ||
     overlaps((uintptr_t)out,sizeof(*out),(uintptr_t)memory,bytes))return 1;
  memset(out,0,sizeof(*out));
  if(!p || bytes<1056 || memcmp(p,"M10L",4) || le32(p+4)!=1 || le32(p+20) || le32(p+24) || le32(p+28))return 1;
  bits=le32(p+8);count=le32(p+12);length=le32(p+16);
  if(bits!=10 || !count || count>256 || length!=bytes-1056)return 1;
  map_bytes=32768u;
  if(length<map_bytes+1024u || (length-map_bytes)%1024u || (length-map_bytes)/1024u>65536u)return 1;
  memset(&model,0,sizeof(model));
  model.blob=p;model.blob_bytes=bytes;model.table=p+1056;model.log2_block=bits;model.palette_size=count;
  for(i=0;i<256;++i) {
    model.palette[i]=le32(p+32+4*i);
    if(model.palette[i]>0xffffffu || (i>=count && model.palette[i]))return 1;
  }
  for(i=0;i<map_bytes;i+=2) {
    const uint32_t id=le16(model.table+i);
    if(id>=(length-map_bytes)/1024u)return 1;
  }
  for(i=map_bytes;i<length;++i)if(model.table[i]>=count)return 1;
  *out=model;return 0;
}
int jshc_mem_validate_io(const jshc_mem_model* m,const uint8_t* source,uint8_t* target,size_t n) {
  size_t bytes;
  uintptr_t src=(uintptr_t)source,dst=(uintptr_t)target;
  if(!m || !m->table || !m->blob || n>SIZE_MAX/3)return 1;
  bytes=n*3;
  if(!bytes)return 0;
  if(!source || !target || bytes>UINTPTR_MAX-src || bytes>UINTPTR_MAX-dst)return 1;
  if(source!=target && overlaps(src,bytes,dst,bytes))return 1;
  if(overlaps(dst,bytes,(uintptr_t)m,sizeof(*m)) || overlaps(dst,bytes,(uintptr_t)m->blob,m->blob_bytes))return 1;
  return 0;
}
int jshc_mem_apply(const jshc_mem_model* m,const uint8_t* source,uint8_t* target,size_t n) {
  size_t p;
  const uint32_t bits=m ? m->log2_block : 0;
  if(jshc_mem_validate_io(m,source,target,n))return 1;
  for(p=0;p<n;++p) {
    const uint32_t code=(uint32_t)source[3*p]|((uint32_t)source[3*p+1]<<8)|((uint32_t)source[3*p+2]<<16);
    const uint32_t offset=32768u+(le16(m->table+2*(code>>bits))<<10);
    const uint32_t v=m->palette[m->table[offset+(code&1023u)]];
    target[3*p]=(uint8_t)v;target[3*p+1]=(uint8_t)(v>>8);target[3*p+2]=(uint8_t)(v>>16);
  }
  return 0;
}
