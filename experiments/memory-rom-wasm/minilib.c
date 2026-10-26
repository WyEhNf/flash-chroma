#include <stddef.h>
/* 无系统库的测试支撑；不更改核心，不提供分配器。 */
void *memset(void *p, int value, size_t n) {
  unsigned char *q = (unsigned char *)p;
  size_t i;
  for (i=0; i<n; ++i) q[i]=(unsigned char)value;
  return p;
}
int memcmp(const void *a, const void *b, size_t n) {
  const unsigned char *x=(const unsigned char *)a, *y=(const unsigned char *)b;
  size_t i;
  for (i=0; i<n; ++i) if(x[i]!=y[i]) return x[i]<y[i] ? -1 : 1;
  return 0;
}
