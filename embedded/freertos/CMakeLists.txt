if(NOT CMAKE_CROSSCOMPILING OR NOT CMAKE_SYSTEM_PROCESSOR STREQUAL "cortex-m3")
  message(FATAL_ERROR "FreeRTOS 固件需要 embedded/cmake/cortex-m3.cmake 工具链")
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
add_library(jshc_freertos STATIC
  "${freertos_kernel_SOURCE_DIR}/tasks.c"
  "${freertos_kernel_SOURCE_DIR}/queue.c"
  "${freertos_kernel_SOURCE_DIR}/list.c"
  "${freertos_kernel_SOURCE_DIR}/portable/GCC/ARM_CM3/port.c"
)
target_include_directories(jshc_freertos PUBLIC
  "${CMAKE_CURRENT_SOURCE_DIR}"
  "${freertos_kernel_SOURCE_DIR}/include"
  "${freertos_kernel_SOURCE_DIR}/portable/GCC/ARM_CM3"
)
add_executable(jshc_rtos.elf startup.S platform.c main.c ../tests/contract.c)
target_link_libraries(jshc_rtos.elf PRIVATE jshc_embedded jshc_freertos gcc)
target_compile_options(jshc_rtos.elf PRIVATE -Wall -Wextra -Werror -fstack-usage)
target_link_options(jshc_rtos.elf PRIVATE -nostdlib
  "-T${CMAKE_CURRENT_SOURCE_DIR}/mps2-an385.ld"
  -Wl,--gc-sections "-Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/jshc_rtos.map"
  -Wl,--print-memory-usage)
set_property(TARGET jshc_rtos.elf APPEND PROPERTY LINK_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/mps2-an385.ld")
if(BUILD_TESTING)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)
  find_program(QEMU_SYSTEM_ARM qemu-system-arm REQUIRED)
  add_test(NAME freertos_qemu
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/run_qemu.py"
      --qemu "${QEMU_SYSTEM_ARM}" --elf "$<TARGET_FILE:jshc_rtos.elf>")
  set_tests_properties(freertos_qemu PROPERTIES TIMEOUT 45)
endif()
