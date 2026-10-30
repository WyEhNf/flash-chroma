cmake_minimum_required(VERSION 3.24)
project(jshc_scanline_prepare LANGUAGES CXX C)
find_package(OpenMP REQUIRED COMPONENTS CXX)
get_filename_component(JSHC_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(BASE "${JSHC_ROOT}/experiments/skylake-andn-normal-runtime")
add_subdirectory("${BASE}" baseline)
# 100仅新增固定B批扫描线准备器；原97八对象和公开apply路径保持。
add_library(jshc_scanline_prepare SHARED
  channel_runtime.cpp compile_shared_avx2.cpp compile_scanline_avx2.cpp
  "${BASE}/outplace_bench.cpp" "${BASE}/channel_avx2.cpp"
  "${BASE}/andn_inplace/channel_avx2.cpp" "${BASE}/andn_outplace/channel_avx2.cpp"
  "${BASE}/normal_inplace/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(jshc_scanline_prepare PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_link_libraries(jshc_scanline_prepare PRIVATE jshc_core OpenMP::OpenMP_CXX)
target_compile_definitions(jshc_scanline_prepare PRIVATE JSHC_CC_HAVE_AVX2=1 P16_PREPARE_SIMD=1)
target_compile_options(jshc_scanline_prepare PRIVATE -Wall -Wextra -fvisibility=hidden -fstack-usage)
set_source_files_properties(compile_shared_avx2.cpp compile_scanline_avx2.cpp
  "${BASE}/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
set_source_files_properties("${BASE}/andn_inplace/channel_avx2.cpp"
  "${BASE}/andn_outplace/channel_avx2.cpp" "${BASE}/normal_inplace/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off;-mbmi")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


# 私有有限合同包含原97入口和新扫描线入口，不链接模型核心。
add_executable(p16_scanline_contract finite_contract.cpp compile_shared_avx2.cpp compile_scanline_avx2.cpp)
target_include_directories(p16_scanline_contract PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_compile_options(p16_scanline_contract PRIVATE -Wall -Wextra -mavx2 -mtune=skylake -ffp-contract=off -fstack-usage)
