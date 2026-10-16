/* virt 的单 hart M-mode 启动，不使用 OpenSBI；陷阱交给 FreeRTOS。 */
.section .text.start,"ax",@progbits
.global _start
.align 2
_start:
  csrw mie, zero
  li t0, 8
  csrc mstatus, t0
  .option push
  .option norelax
  la gp, __global_pointer$
  .option pop
  la sp, _estack
  la t0, _sbss
  la t1, _ebss
1:
  bgeu t0, t1, 2f
  sw zero, 0(t0)
  addi t0, t0, 4
  j 1b
2:
  la t0, freertos_risc_v_trap_handler
  csrw mtvec, t0
  call main
  call jshc_platform_fail
  j .
