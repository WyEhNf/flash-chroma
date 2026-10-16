#include <stdint.h>

void jshc_platform_write(const char *message)
{
    volatile uint8_t *const uart = (volatile uint8_t *)0x10000000;
    while (*message) {
        while (!(uart[5] & 0x20)) { }
        uart[0] = (uint8_t)*message++;
    }
}
void jshc_platform_exit(uint32_t status)
{
    /* SiFive test finisher：0x5555 成功，0x3333 失败并携带非零退出码。 */
    *(volatile uint32_t *)0x100000 = status ? (status << 16) | 0x3333 : 0x5555;
    for (;;) __asm__ volatile("wfi");
}
void jshc_platform_fail(void);
void freertos_risc_v_application_exception_handler(void) { jshc_platform_fail(); }
void freertos_risc_v_application_interrupt_handler(void) { jshc_platform_fail(); }
