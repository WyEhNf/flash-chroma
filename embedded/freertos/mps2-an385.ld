/* QEMU AN385：低地址代码 SRAM 与 0x20000000 数据 SRAM 各 4 MiB。 */
ENTRY(Reset_Handler)
MEMORY {
  CODE (rx)  : ORIGIN = 0x00000000, LENGTH = 4M
  RAM  (rwx) : ORIGIN = 0x20000000, LENGTH = 4M
}
_estack = ORIGIN(RAM) + LENGTH(RAM);
SECTIONS {
  .vectors : { KEEP(*(.vectors)) } > CODE
  .text : { *(.text*) *(.rodata*) . = ALIGN(4); } > CODE
  .ARM.exidx : { *(.ARM.exidx*) } > CODE
  .data : {
    . = ALIGN(4); _sdata = .; *(.data*) . = ALIGN(4); _edata = .;
  } > RAM AT > CODE
  _sidata = LOADADDR(.data);
  .bss (NOLOAD) : {
    . = ALIGN(8); _sbss = .; *(.bss*) *(COMMON) . = ALIGN(8); _ebss = .;
  } > RAM
  ASSERT(_ebss + 4096 < _estack, "RAM 不足，需保留主栈空间")
}
