if(NOT CMAKE_SYSTEM_NAME STREQUAL "Linux" OR NOT CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64")
  message(FATAL_ERROR "Linux 固件需要 embedded/cmake/aarch64-linux.cmake 工具链")
endif()
add_executable(jshc_linux_init init.c ../tests/contract.c)
target_link_libraries(jshc_linux_init PRIVATE jshc_embedded)
jshc_attach_portable_contract(jshc_linux_init)
target_compile_options(jshc_linux_init PRIVATE -Wall -Wextra -Werror)
target_link_options(jshc_linux_init PRIVATE -static)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/initramfs.cpio"
  COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/make_initramfs.py"
    "$<TARGET_FILE:jshc_linux_init>" "${CMAKE_CURRENT_BINARY_DIR}/initramfs.cpio"
  DEPENDS jshc_linux_init "${CMAKE_CURRENT_SOURCE_DIR}/make_initramfs.py" VERBATIM)
add_custom_target(jshc_initramfs ALL DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/initramfs.cpio")
if(BUILD_TESTING)
  find_program(QEMU_AARCH64 qemu-system-aarch64 REQUIRED)
  add_test(NAME linux_cortex_a53_qemu
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/run_qemu.py"
      --qemu "${QEMU_AARCH64}" --cache "${CMAKE_CURRENT_BINARY_DIR}/kernel"
      --initramfs "${CMAKE_CURRENT_BINARY_DIR}/initramfs.cpio")
  set_tests_properties(linux_cortex_a53_qemu PROPERTIES TIMEOUT 180)
endif()
