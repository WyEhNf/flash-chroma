#include "memory_rom.h"
#include <limits.h>
#include <string.h>
typedef char jshc_requires_octets[(CHAR_BIT==8)?1:-1];
static uint32_t le24(const uint8_t* p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16);}
static uint32_t le32(const uint8_t* p) {return le24(p)|((uint32_t)p[3]<<24);}
static int overlaps(uintptr_t a,size_t na,uintptr_t b,size_t nb) {return na && nb && a<b+nb && b<a+na;}
static size_t map_bytes(uint32_t mode) {return mode==24?3145728u:2228224u;}
static uint32_t offset(const uint8_t* table,uint32_t mode,uint32_t block) {
  if(mode==24)return le24(table+3*block);
  {
    const uint32_t bit=17*block;
    const uint32_t id=(le24(table+(bit>>3))>>(bit&7))&131071u;
    return 2228224u+(id<<4);
  }
}
size_t jshc_mem_model_size(void) {return sizeof(jshc_mem_model);}
int jshc_mem_prepare(jshc_mem_model* out,const void* memory,size_t bytes) {
  const uint8_t* p=(const uint8_t*)memory;
  uint32_t mode,count,length;
  size_t maps,i;
  jshc_mem_model m;
  if(!out)return 1;
  if(bytes>UINTPTR_MAX-(uintptr_t)memory || overlaps((uintptr_t)out,sizeof(*out),(uintptr_t)memory,bytes))return 1;
  memset(out,0,sizeof(*out));
  if(!p || bytes<1056 || memcmp(p,"M16P",4) || le32(p+4)!=1 || le32(p+20) || le32(p+24) || le32(p+28))return 1;
  mode=le32(p+8);count=le32(p+12);length=le32(p+16);
  if((mode!=17 && mode!=24) || !count || count>256 || length!=bytes-1056)return 1;
  maps=map_bytes(mode);
  if(length<maps+16 || (length-maps)%16 || (mode==17 && (length-maps)/16>131072u))return 1;
  memset(&m,0,sizeof(m));m.blob=p;m.blob_bytes=bytes;m.table=p+1056;m.log2_block=mode;m.palette_size=count;
  for(i=0;i<256;++i) {
    m.palette[i]=le32(p+32+4*i);
    if(m.palette[i]>0xffffffu || (i>=count && m.palette[i]))return 1;
  }
  for(i=0;i<1048576u;++i) {
    const uint32_t off=offset(m.table,mode,(uint32_t)i);
    if(off<maps || off>length-16 || (off-maps)%16)return 1;
  }
  for(i=maps;i<length;++i)if(m.table[i]>=count)return 1;
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
  size_t i;
  if(jshc_mem_validate_io(m,source,target,n))return 1;
  for(i=0;i<n;++i) {
    const uint32_t code=(uint32_t)source[3*i]|((uint32_t)source[3*i+1]<<8)|((uint32_t)source[3*i+2]<<16);
    const uint32_t off=offset(m->table,m->log2_block,code>>4);
    const uint32_t value=m->palette[m->table[off+(code&15)]];
    target[3*i]=(uint8_t)value;target[3*i+1]=(uint8_t)(value>>8);target[3*i+2]=(uint8_t)(value>>16);
  }
  return 0;
}
