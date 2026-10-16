/* 测试固件的最小支持层；semihosting 只输出诊断与退出码。 */
#include <stddef.h>
#include <stdint.h>

void *memcpy(void *dst, const void *src, size_t n)
{
    uint8_t *d = dst;
    const uint8_t *s = src;
    size_t i;
    for (i = 0; i < n; ++i) d[i] = s[i];
    return dst;
}
void *memset(void *dst, int value, size_t n)
{
    uint8_t *d = dst;
    size_t i;
    for (i = 0; i < n; ++i) d[i] = (uint8_t)value;
    return dst;
}

static void semihost(uint32_t operation, const void *argument)
{
    register uint32_t r0 __asm__("r0") = operation;
    register const void *r1 __asm__("r1") = argument;
    __asm__ volatile("bkpt 0xab" : "+r"(r0), "+r"(r1) :: "memory");
}
void jshc_platform_write(const char *message) { semihost(4, message); }
void jshc_platform_number(uint32_t value)
{
    char text[11];
    size_t end = sizeof(text) - 1;
    text[end] = 0;
    do { text[--end] = (char)('0' + value % 10); value /= 10; } while (value);
    jshc_platform_write(text + end);
}
void jshc_platform_exit(uint32_t status)
{
    const uint32_t args[2] = {0x20026, status};
    semihost(0x20, args);
    for (;;) __asm__ volatile("wfi");
}
void jshc_platform_fail(void)
{
    jshc_platform_write("FAIL：RTOS 断言、异常或栈溢出\n");
    jshc_platform_exit(1);
}
