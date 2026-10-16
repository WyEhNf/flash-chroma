ENTRY(_start)
MEMORY { RAM (rwx) : ORIGIN = 0x80000000, LENGTH = 16M }
PHDRS {
  code PT_LOAD FLAGS(5);
  data PT_LOAD FLAGS(6);
}
SECTIONS {
  .text : { KEEP(*(.text.start)) *(.text*) *(.rodata*) } > RAM :code
  .data : { . = ALIGN(16); *(.data*) *(.sdata*) } > RAM :data
  PROVIDE(__global_pointer$ = . + 0x800);
  .bss (NOLOAD) : {
    . = ALIGN(16); _sbss = .; *(.bss*) *(.sbss*) *(COMMON) . = ALIGN(16); _ebss = .;
  } > RAM :data
  _estack = ORIGIN(RAM) + LENGTH(RAM);
  ASSERT(_ebss + 4096 < _estack, "RAM 不足，需保留主栈空间")
}
