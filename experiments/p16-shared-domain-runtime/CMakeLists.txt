cmake_minimum_required(VERSION 3.24)
project(jshc_shared_domain LANGUAGES CXX C)
find_package(OpenMP REQUIRED COMPONENTS CXX)
get_filename_component(JSHC_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(BASE "${JSHC_ROOT}/experiments/skylake-andn-normal-runtime")
add_subdirectory("${BASE}" baseline)
# 仅构造资格扩展；旧87所有像素及精确失败回退TU复用同源。
add_library(jshc_shared_domain SHARED
  channel_runtime.cpp "${JSHC_ROOT}/experiments/p16-direct-compile/compile_avx2.cpp"
  "${BASE}/outplace_bench.cpp" "${BASE}/channel_avx2.cpp"
  "${BASE}/andn_inplace/channel_avx2.cpp" "${BASE}/andn_outplace/channel_avx2.cpp"
  "${BASE}/normal_inplace/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(jshc_shared_domain PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_link_libraries(jshc_shared_domain PRIVATE jshc_core OpenMP::OpenMP_CXX)
target_compile_definitions(jshc_shared_domain PRIVATE JSHC_CC_HAVE_AVX2=1 P16_PREPARE_SIMD=1)
target_compile_options(jshc_shared_domain PRIVATE -Wall -Wextra -fvisibility=hidden)
set_source_files_properties("${JSHC_ROOT}/experiments/p16-direct-compile/compile_avx2.cpp"
  "${BASE}/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
set_source_files_properties("${BASE}/andn_inplace/channel_avx2.cpp"
  "${BASE}/andn_outplace/channel_avx2.cpp" "${BASE}/normal_inplace/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off;-mbmi")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
