/* Cortex-M3 向量表；SVC/PendSV/SysTick 直接接入 FreeRTOS ARM_CM3 端口。 */
.syntax unified
.cpu cortex-m3
.thumb
.section .vectors,"a",%progbits
.word _estack
.word Reset_Handler
.rept 9
.word Default_Handler
.endr
.word vPortSVCHandler
.word Default_Handler
.word 0
.word xPortPendSVHandler
.word xPortSysTickHandler
.section .text.Reset_Handler,"ax",%progbits
.global Reset_Handler
.thumb_func
Reset_Handler:
  ldr r0, =_sidata
  ldr r1, =_sdata
  ldr r2, =_edata
1:
  cmp r1, r2
  bcs 2f
  ldr r3, [r0], #4
  str r3, [r1], #4
  b 1b
2:
  ldr r1, =_sbss
  ldr r2, =_ebss
  movs r3, #0
3:
  cmp r1, r2
  bcs 4f
  str r3, [r1], #4
  b 3b
4:
  bl main
  b Default_Handler
.section .text.Default_Handler,"ax",%progbits
.global Default_Handler
.thumb_func
Default_Handler:
  bl jshc_platform_fail
  b .
