/* Cortex-M3 测试诊断；运行时库不依赖 semihosting。 */
#include <stdint.h>
static void semihost(uint32_t operation, const void *argument)
{
    register uint32_t r0 __asm__("r0") = operation;
    register const void *r1 __asm__("r1") = argument;
    __asm__ volatile("bkpt 0xab" : "+r"(r0), "+r"(r1) :: "memory");
}
void jshc_platform_write(const char *message) { semihost(4, message); }
void jshc_platform_exit(uint32_t status)
{
    const uint32_t args[2] = {0x20026, status};
    semihost(0x20, args);
    for (;;) __asm__ volatile("wfi");
}
