cmake_minimum_required(VERSION 3.24)
project(p16_unified LANGUAGES CXX C)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
option(P16_ENABLE_AVX512 "构建显式选择的Skylake-SP AVX512 direct核" ON)
get_filename_component(JSHC_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(BASE "${JSHC_ROOT}/experiments/skylake-andn-normal-runtime")
set(WIDE "${JSHC_ROOT}/experiments/p16-direct-u16-cache2-runtime")
set(SCAN "${JSHC_ROOT}/experiments/p16-scanline-prepare-runtime")
add_subdirectory("${BASE}" baseline)
find_package(OpenMP REQUIRED COMPONENTS CXX)

add_library(jshc_unified SHARED channel_runtime.cpp compile_shared_avx2.cpp
  "${SCAN}/compile_scanline_avx2.cpp"
  "${WIDE}/direct_u16_avx2.cpp" "${WIDE}/linear.cpp"
  "${WIDE}/andn_inplace.cpp" "${WIDE}/andn_outplace.cpp" "${WIDE}/normal_inplace.cpp"
  "${BASE}/outplace_bench.cpp" "${BASE}/channel_avx2.cpp"
  "${BASE}/andn_inplace/channel_avx2.cpp" "${BASE}/andn_outplace/channel_avx2.cpp"
  "${BASE}/normal_inplace/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(jshc_unified PRIVATE "${BASE}" "${WIDE}" "${SCAN}"
  "${JSHC_ROOT}/experiments/channel-runtime")
target_link_libraries(jshc_unified PRIVATE jshc_core OpenMP::OpenMP_CXX)
target_compile_definitions(jshc_unified PRIVATE JSHC_CC_HAVE_AVX2=1 P16_PREPARE_SIMD=1)
target_compile_options(jshc_unified PRIVATE -Wall -Wextra -fvisibility=hidden -fstack-usage)
set_source_files_properties(compile_shared_avx2.cpp "${SCAN}/compile_scanline_avx2.cpp"
  "${WIDE}/direct_u16_avx2.cpp" "${WIDE}/linear.cpp"
  "${BASE}/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
set_source_files_properties("${WIDE}/andn_inplace.cpp" "${WIDE}/andn_outplace.cpp" "${WIDE}/normal_inplace.cpp"
  "${BASE}/andn_inplace/channel_avx2.cpp" "${BASE}/andn_outplace/channel_avx2.cpp"
  "${BASE}/normal_inplace/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-mbmi;-ffp-contract=off")

if(P16_ENABLE_AVX512)
  include(CheckCXXCompilerFlag)
  check_cxx_compiler_flag("-mavx512f -mavx512bw -mavx512dq -mavx512vl" P16_COMPILER_HAS_AVX512)
  if(NOT P16_COMPILER_HAS_AVX512)
    message(FATAL_ERROR "编译器不支持Skylake-SP AVX512，可用-DP16_ENABLE_AVX512=OFF构建回退库")
  endif()
  add_library(p16_direct_avx512 OBJECT direct_avx512.cpp)
  set_target_properties(p16_direct_avx512 PROPERTIES POSITION_INDEPENDENT_CODE ON)
  target_compile_options(p16_direct_avx512 PRIVATE -Wall -Wextra -fvisibility=hidden
    -mavx512f -mavx512bw -mavx512dq -mavx512vl -mtune=skylake-avx512 -ffp-contract=off)
  target_sources(jshc_unified PRIVATE $<TARGET_OBJECTS:p16_direct_avx512>)
  target_compile_definitions(jshc_unified PRIVATE P16_HAVE_AVX512=1)
  # 合同驱动保持baseline ISA，只有单独对象包含AVX512；运行前检查CPU/OS。
  add_executable(p16_avx512_contract direct_avx512_contract.cpp $<TARGET_OBJECTS:p16_direct_avx512>)
endif()

if(MINGW)
  foreach(dll libgcc_s_seh-1.dll libstdc++-6.dll libwinpthread-1.dll libgomp-1.dll)
    execute_process(COMMAND "${CMAKE_CXX_COMPILER}" "-print-file-name=${dll}"
      OUTPUT_VARIABLE dll_path OUTPUT_STRIP_TRAILING_WHITESPACE)
    if(IS_ABSOLUTE "${dll_path}" AND EXISTS "${dll_path}")
      add_custom_command(TARGET jshc_unified POST_BUILD COMMAND "${CMAKE_COMMAND}" -E copy_if_different
        "${dll_path}" "$<TARGET_FILE_DIR:jshc_unified>" VERBATIM)
    endif()
  endforeach()
endif()
