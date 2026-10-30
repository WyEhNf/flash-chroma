// 36核心使用普通整数载荷和64bit拼装，仍经原AVX2资格分派；原回退保持。
#include "suffix_cache.hpp"
#include <cstring>
namespace jshc_channel {
namespace {
template<size_t Offset,bool Wide>
inline __attribute__((always_inline)) uint32_t lookup(const uint32_t* table,const uint32_t* palette,const uint8_t* source) {
  uint32_t code;
  if constexpr(Wide || Offset<21) {std::memcpy(&code,source+Offset,4);code&=0xffffff;}
  else {uint16_t low;std::memcpy(&low,source+Offset,2);code=uint32_t(low)|(uint32_t(source[Offset+2])<<16);}
  return palette[reinterpret_cast<const uint8_t*>(table)[code]];
}
template<bool Wide>
inline __attribute__((always_inline)) void packet(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination) {
  const uint32_t v0=lookup<0,Wide>(table,palette,source),v1=lookup<3,Wide>(table,palette,source),v2=lookup<6,Wide>(table,palette,source);
  const uint64_t a=uint64_t(v0)|(uint64_t(v1)<<24)|(uint64_t(v2)<<48);
  std::memcpy(destination,&a,8);
  // 已读取的颜色才会被覆盖；后续输入从第9字节开始，不与首个8字节输出重叠。
  const uint32_t v3=lookup<9,Wide>(table,palette,source),v4=lookup<12,Wide>(table,palette,source),v5=lookup<15,Wide>(table,palette,source);
  const uint64_t b=uint64_t(v2>>16)|(uint64_t(v3)<<8)|(uint64_t(v4)<<32)|(uint64_t(v5)<<56);
  std::memcpy(destination+8,&b,8);
  const uint32_t v6=lookup<18,Wide>(table,palette,source),v7=lookup<21,Wide>(table,palette,source);
  const uint64_t c=uint64_t(v5>>8)|(uint64_t(v6)<<16)|(uint64_t(v7)<<40);
  std::memcpy(destination+16,&c,8);
}
inline __attribute__((always_inline)) void run(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {
  size_t p=0;
  for(;p+16<=pixels;p+=8)packet<true>(table,palette,source+3*p,destination+3*p);
  for(;p<pixels;p+=8)packet<false>(table,palette,source+3*p,destination+3*p);
}
}
void avx2_chain_swar(const uint32_t* table,const uint32_t* palette,uint8_t* data,size_t pixels) noexcept {run(table,palette,data,data,pixels);}
void avx2_chain_swar_to(const uint32_t* table,const uint32_t* palette,const uint8_t* source,uint8_t* destination,size_t pixels) noexcept {run(table,palette,source,destination,pixels);}
}
