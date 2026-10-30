#include "memory_rom_ilp.h"

/* 固定8像素分三步：全部ID、全部调色板值、全部RGB写入。仅标准C99。 */
static uint32_t code24(const uint8_t* source) {
  return (uint32_t)source[0]|((uint32_t)source[1]<<8)|((uint32_t)source[2]<<16);
}
static uint32_t load_le32(const uint8_t* p) {
  return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void emit8(const uint32_t* restrict palette,const uint32_t* ids,uint8_t* target) {
  uint32_t values[8];
  unsigned k;
  for(k=0;k<8;++k)values[k]=palette[ids[k]];
  for(k=0;k<8;++k) {
    const uint32_t v=values[k];
    target[3*k]=(uint8_t)v;target[3*k+1]=(uint8_t)(v>>8);target[3*k+2]=(uint8_t)(v>>16);
  }
}
JSHC_MEM_API int jshc_mem_apply_ilp(const jshc_mem_model* m,const uint8_t* source,uint8_t* target,size_t n) {
  size_t p=0;
  uint32_t bits;
  if(jshc_mem_validate_io(m,source,target,n))return 1;
  bits=m->log2_block;
  if(!bits) {
    const uint8_t* restrict table=m->table;
    for(;n-p>=8;p+=8) {
      uint32_t ids[8];unsigned k;
      for(k=0;k<8;++k)ids[k]=table[code24(source+3*(p+k))];
      emit8(m->palette,ids,target+3*p);
    }
    for(;p<n;++p) {
      const uint32_t v=m->palette[table[code24(source+3*p)]];
      target[3*p]=(uint8_t)v;target[3*p+1]=(uint8_t)(v>>8);target[3*p+2]=(uint8_t)(v>>16);
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
      emit8(m->palette,ids,target+3*p);
    }
    for(;p<n;++p) {
      const uint32_t code=code24(source+3*p);
      const uint32_t v=m->palette[table[load_le32(table+4*(code>>bits))+(code&mask)]];
      target[3*p]=(uint8_t)v;target[3*p+1]=(uint8_t)(v>>8);target[3*p+2]=(uint8_t)(v>>16);
    }
  }
  return 0;
}
