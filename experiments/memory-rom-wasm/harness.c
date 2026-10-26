#include "memory_rom.h"
/* 固定静态地址空间用于宿主注入ROM/像素；测试夹具不使用堆。 */
static uint8_t rom[16778272u+8u];
static uint8_t input[196608u+32u];
static uint8_t output[196608u+32u];
static jshc_mem_model model;
uint32_t rom_address(void) { return (uint32_t)(uintptr_t)rom; }
uint32_t input_address(void) { return (uint32_t)(uintptr_t)input; }
uint32_t output_address(void) { return (uint32_t)(uintptr_t)output; }
uint32_t prepare_rom(uint32_t bytes, uint32_t offset) {
  if(offset>8 || bytes>sizeof(rom)-offset) return 1;
  return (uint32_t)jshc_mem_prepare(&model,rom+offset,bytes);
}
uint32_t apply_pixels(uint32_t n,uint32_t source_offset,uint32_t target_offset) {
  if(source_offset>16 || target_offset>16 || n>65536) return 1;
  return (uint32_t)jshc_mem_apply(&model,input+source_offset,output+target_offset,n);
}
uint32_t apply_inplace(uint32_t n,uint32_t offset) {
  if(offset>16 || n>65536) return 1;
  return (uint32_t)jshc_mem_apply(&model,input+offset,input+offset,n);
}
uint32_t reject_partial_overlap(void) {
  return (uint32_t)jshc_mem_apply(&model,input,input+1,32);
}
uint32_t reject_rom_output(void) {
  return (uint32_t)jshc_mem_apply(&model,input,rom,32);
}
uint32_t reject_null_output(void) {
  return (uint32_t)jshc_mem_apply(&model,input,(uint8_t*)0,32);
}
uint32_t empty_null(void) {
  return (uint32_t)jshc_mem_apply(&model,(const uint8_t*)0,(uint8_t*)0,0);
}
