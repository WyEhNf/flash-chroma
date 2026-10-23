#include "../memory-rom-wasm/minilib.c"
/* 只用于freestanding执行夹具；核心仍调用标准memcpy。 */
void *memcpy(void *restrict target, const void *restrict source, size_t count) {
  unsigned char *out = (unsigned char *)target;
  const unsigned char *in = (const unsigned char *)source;
  size_t i;
  for (i = 0; i < count; ++i) out[i] = in[i];
  return target;
}
