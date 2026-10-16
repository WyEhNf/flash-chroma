if(NOT CMAKE_CROSSCOMPILING)
  message(FATAL_ERROR "FreeRTOS 固件需要 Cortex-M3 或 RV32 工具链")
endif()
enable_language(ASM)
include(FetchContent)
# FreeRTOS-Kernel V11.2.0，MIT；固定提交与下载包哈希。
FetchContent_Declare(freertos_kernel
  URL https://codeload.github.com/FreeRTOS/FreeRTOS-Kernel/tar.gz/0adc196d4bd52a2d91102b525b0aafc1e14a2386
  URL_HASH SHA256=6af5d78e39a5237b63faaafdc31672c87b27b68e713e2a57d3528aa3a4c1cee8
  DOWNLOAD_EXTRACT_TIMESTAMP FALSE
  SOURCE_SUBDIR jshc-unused-upstream-build
)
# 仅取源码；显式构建所用端口，不引入上游默认堆实现。
FetchContent_MakeAvailable(freertos_kernel)
configure_file("${freertos_kernel_SOURCE_DIR}/LICENSE.md"
  "${CMAKE_CURRENT_BINARY_DIR}/LICENSE.FreeRTOS-Kernel.md" COPYONLY)
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "cortex-m3")
  set(JSHC_PORT "${freertos_kernel_SOURCE_DIR}/portable/GCC/ARM_CM3")
  set(JSHC_PLATFORM_SOURCES startup.S platform_arm.c)
  set(JSHC_LINKER_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/mps2-an385.ld")
  set(JSHC_TARGET_NAME Cortex-M3)
  set(JSHC_QEMU_NAME qemu-system-arm)
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "riscv32")
  set(JSHC_PORT "${freertos_kernel_SOURCE_DIR}/portable/GCC/RISC-V")
  set(JSHC_PORT_ASM "${JSHC_PORT}/portASM.S")
  set(JSHC_PLATFORM_SOURCES riscv/startup.S riscv/platform.c)
  set(JSHC_LINKER_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/riscv/virt.ld")
  set(JSHC_TARGET_NAME RV32)
  set(JSHC_QEMU_NAME qemu-system-riscv32)
else()
  message(FATAL_ERROR "不支持的 FreeRTOS 目标：${CMAKE_SYSTEM_PROCESSOR}")
endif()
add_library(jshc_freertos STATIC
  "${freertos_kernel_SOURCE_DIR}/tasks.c"
  "${freertos_kernel_SOURCE_DIR}/queue.c"
  "${freertos_kernel_SOURCE_DIR}/list.c"
  "${JSHC_PORT}/port.c" ${JSHC_PORT_ASM}
)
target_include_directories(jshc_freertos PUBLIC
  "${CMAKE_CURRENT_SOURCE_DIR}"
  "${freertos_kernel_SOURCE_DIR}/include"
  "${JSHC_PORT}"
  "${JSHC_PORT}/chip_specific_extensions/RV32I_CLINT_no_extensions"
)
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "riscv32")
  # Debian/Ubuntu 的裸机 GCC 不带 libc 头；仅补通用头，不链接宿主 libc。
  find_path(JSHC_NEWLIB_HEADERS newlib.h PATHS /usr/include/newlib)
  if(JSHC_NEWLIB_HEADERS)
    target_include_directories(jshc_freertos SYSTEM PUBLIC "${JSHC_NEWLIB_HEADERS}")
  endif()
endif()
add_executable(jshc_rtos.elf ${JSHC_PLATFORM_SOURCES} platform.c main.c ../tests/contract.c)
target_link_libraries(jshc_rtos.elf PRIVATE jshc_embedded jshc_freertos gcc)
jshc_attach_portable_contract(jshc_rtos.elf)
target_compile_definitions(jshc_rtos.elf PRIVATE "JSHC_RTOS_TARGET=\"${JSHC_TARGET_NAME}\"")
target_compile_options(jshc_rtos.elf PRIVATE -Wall -Wextra -Werror -fstack-usage)
target_link_options(jshc_rtos.elf PRIVATE -nostdlib
  "-T${JSHC_LINKER_SCRIPT}"
  -Wl,--gc-sections "-Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/jshc_rtos.map"
  -Wl,--print-memory-usage)
set_property(TARGET jshc_rtos.elf APPEND PROPERTY LINK_DEPENDS "${JSHC_LINKER_SCRIPT}")
if(BUILD_TESTING)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)
  find_program(JSHC_QEMU "${JSHC_QEMU_NAME}" REQUIRED)
  add_test(NAME freertos_qemu
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/run_qemu.py"
      --qemu "${JSHC_QEMU}" --target "${CMAKE_SYSTEM_PROCESSOR}" --elf "$<TARGET_FILE:jshc_rtos.elf>")
  set_tests_properties(freertos_qemu PROPERTIES TIMEOUT 45)
endif()
