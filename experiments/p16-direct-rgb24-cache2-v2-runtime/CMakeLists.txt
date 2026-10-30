cmake_minimum_required(VERSION 3.24)
project(p16_direct_rgb24_cache2 LANGUAGES CXX C)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
get_filename_component(JSHC_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(BASE "${JSHC_ROOT}/experiments/skylake-andn-normal-runtime")
add_subdirectory("${BASE}" baseline)
find_package(OpenMP REQUIRED COMPONENTS CXX)
add_library(jshc_direct_rgb24_cache2 SHARED channel_runtime.cpp compile_avx2.cpp direct_rgb24_avx2.cpp linear.cpp andn_inplace.cpp andn_outplace.cpp normal_inplace.cpp
  "${BASE}/outplace_bench.cpp" "${BASE}/channel_avx2.cpp"
  "${BASE}/andn_inplace/channel_avx2.cpp" "${BASE}/andn_outplace/channel_avx2.cpp"
  "${BASE}/normal_inplace/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(jshc_direct_rgb24_cache2 PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_link_libraries(jshc_direct_rgb24_cache2 PRIVATE jshc_core OpenMP::OpenMP_CXX)
target_compile_definitions(jshc_direct_rgb24_cache2 PRIVATE JSHC_CC_HAVE_AVX2=1 P16_PREPARE_SIMD=1)
target_compile_options(jshc_direct_rgb24_cache2 PRIVATE -Wall -Wextra -fvisibility=hidden -fstack-usage)
add_executable(p16_direct_rgb24_cache2_contracts contracts.cpp compile_avx2.cpp direct_rgb24_avx2.cpp linear.cpp andn_inplace.cpp andn_outplace.cpp normal_inplace.cpp)
target_include_directories(p16_direct_rgb24_cache2_contracts PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_compile_options(p16_direct_rgb24_cache2_contracts PRIVATE -Wall -Wextra -fstack-usage)
set_source_files_properties(compile_avx2.cpp direct_rgb24_avx2.cpp linear.cpp andn_inplace.cpp andn_outplace.cpp normal_inplace.cpp "${BASE}/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
set_source_files_properties("${BASE}/andn_inplace/channel_avx2.cpp" "${BASE}/andn_outplace/channel_avx2.cpp"
  "${BASE}/normal_inplace/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off;-mbmi")

set_source_files_properties(linear.cpp PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
set_source_files_properties(andn_inplace.cpp andn_outplace.cpp normal_inplace.cpp PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off;-mbmi")
