#include "memory_rom_store.h"
#include <string.h>

/* 固定8像素全部ID先读；前7项组内写4字节、末项写3字节。仅标准C99。 */
static uint32_t code24(const uint8_t* source) {
  return (uint32_t)source[0]|((uint32_t)source[1]<<8)|((uint32_t)source[2]<<16);
}
static uint32_t load_le32(const uint8_t* p) {
  return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void emit8(const uint8_t* restrict palette,const uint32_t* ids,uint8_t* target) {
  unsigned k;
  for(k=0;k<7;++k)memcpy(target+3*k,palette+4*ids[k],4);
  memcpy(target+21,palette+4*ids[7],3);
}
JSHC_MEM_API int jshc_mem_apply_store(const jshc_mem_model* m,const uint8_t* source,uint8_t* target,size_t n) {
  size_t p=0;
  uint32_t bits;
  if(jshc_mem_validate_io(m,source,target,n))return 1;
  bits=m->log2_block;
  if(!bits) {
    const uint8_t* restrict table=m->table;
    for(;n-p>=8;p+=8) {
      uint32_t ids[8];unsigned k;
      for(k=0;k<8;++k)ids[k]=table[code24(source+3*(p+k))];
      emit8(m->blob+32,ids,target+3*p);
    }
    for(;p<n;++p) {
      const uint32_t id=table[code24(source+3*p)];
      memcpy(target+3*p,m->blob+32+4*id,3);
    }
  } else {
    const uint8_t* restrict table=m->table;
    const uint32_t mask=((uint32_t)1<<bits)-1;
    for(;n-p>=8;p+=8) {
      uint32_t ids[8];unsigned k;
      for(k=0;k<8;++k) {
        const uint32_t code=code24(source+3*(p+k));
        ids[k]=table[load_le32(table+4*(code>>bits))+(code&mask)];
      }
      emit8(m->blob+32,ids,target+3*p);
    }
    for(;p<n;++p) {
      const uint32_t code=code24(source+3*p);
      const uint32_t id=table[load_le32(table+4*(code>>bits))+(code&mask)];
      memcpy(target+3*p,m->blob+32+4*id,3);
    }
  }
  return 0;
}
