#include "FreeRTOS.h"
#include "task.h"

int jshc_embedded_contract(void (*checkpoint)(void));
void jshc_platform_write(const char *message);
void jshc_platform_number(uint32_t value);
void jshc_platform_exit(uint32_t status);

static StaticTask_t worker_tcb, observer_tcb, idle_tcb;
static StackType_t worker_stack[2048] __attribute__((aligned(16)));
static StackType_t observer_stack[256] __attribute__((aligned(16)));
static StackType_t idle_stack[256] __attribute__((aligned(16)));
static volatile uint32_t heartbeat;

void vApplicationGetIdleTaskMemory(StaticTask_t **tcb, StackType_t **stack, uint32_t *depth)
{
    *tcb = &idle_tcb; *stack = idle_stack; *depth = 256;
}
void vApplicationStackOverflowHook(TaskHandle_t task, char *name)
{
    (void)task; (void)name;
    jshc_platform_fail();
}
static void observer(void *argument)
{
    (void)argument;
    for (;;) { ++heartbeat; vTaskDelay(1); }
}
static void checkpoint(void) { vTaskDelay(2); }
static void worker(void *argument)
{
    int result;
    TickType_t start = xTaskGetTickCount();
    (void)argument;
    jshc_platform_write("FreeRTOS：开始 " JSHC_RTOS_TARGET " LUT 契约测试\n");
    result = jshc_embedded_contract(checkpoint);
    jshc_platform_write("失败行="); jshc_platform_number((uint32_t)result);
    jshc_platform_write("，心跳="); jshc_platform_number(heartbeat);
    jshc_platform_write("，tick="); jshc_platform_number(xTaskGetTickCount() - start);
    jshc_platform_write("，任务栈剩余字数=");
    jshc_platform_number((uint32_t)uxTaskGetStackHighWaterMark(NULL));
    jshc_platform_write("\n");
    if (result || !heartbeat || xTaskGetTickCount() == start) jshc_platform_fail();
    jshc_platform_write("PASS: FreeRTOS " JSHC_RTOS_TARGET " LUT contract\n");
    jshc_platform_exit(0);
}
int main(void)
{
    configASSERT(xTaskCreateStatic(worker, "lut", 2048, NULL, 2, worker_stack, &worker_tcb));
    configASSERT(xTaskCreateStatic(observer, "observer", 256, NULL, 1, observer_stack, &observer_tcb));
    vTaskStartScheduler();
    jshc_platform_fail();
    return 1;
}
