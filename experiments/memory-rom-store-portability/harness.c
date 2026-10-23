#include "memory_rom_store.h"
/* 同一地址/边界夹具只改调用出口；原夹具源码不变。 */
#define jshc_mem_apply jshc_mem_apply_store
#include "../memory-rom-wasm/harness.c"
