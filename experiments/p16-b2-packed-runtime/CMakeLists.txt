cmake_minimum_required(VERSION 3.24)
project(jshc_b2_packed LANGUAGES CXX C)
find_package(OpenMP REQUIRED COMPONENTS CXX)
get_filename_component(JSHC_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(BASE "${JSHC_ROOT}/experiments/skylake-andn-normal-runtime")
add_subdirectory("${BASE}" baseline)
# 97仅新增隔离shared已证域像素入口；准备/字典/旧checked对象来源保持95。
add_library(jshc_b2_packed SHARED
  channel_runtime.cpp compile_shared_avx2.cpp b2_shared_avx2.cpp
  "${BASE}/outplace_bench.cpp" "${BASE}/channel_avx2.cpp"
  "${BASE}/andn_inplace/channel_avx2.cpp" "${BASE}/andn_outplace/channel_avx2.cpp"
  "${BASE}/normal_inplace/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(jshc_b2_packed PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_link_libraries(jshc_b2_packed PRIVATE jshc_core OpenMP::OpenMP_CXX)
target_compile_definitions(jshc_b2_packed PRIVATE JSHC_CC_HAVE_AVX2=1 P16_PREPARE_SIMD=1)
target_compile_options(jshc_b2_packed PRIVATE -Wall -Wextra -fvisibility=hidden -fstack-usage)
set_source_files_properties(compile_shared_avx2.cpp b2_shared_avx2.cpp
  "${BASE}/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
set_source_files_properties("${BASE}/andn_inplace/channel_avx2.cpp"
  "${BASE}/andn_outplace/channel_avx2.cpp" "${BASE}/normal_inplace/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off;-mbmi")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


target_compile_features(jshc_b2_packed PRIVATE cxx_std_17)

# 私有首级质量入口单独目标，生产库不定义该宏、不扩C ABI。
add_executable(p16_b2_packed_contract finite_contract.cpp b2_shared_avx2.cpp)
target_include_directories(p16_b2_packed_contract PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_compile_features(p16_b2_packed_contract PRIVATE cxx_std_17)
target_compile_definitions(p16_b2_packed_contract PRIVATE P16_B2_CONTRACT=1)
target_compile_options(p16_b2_packed_contract PRIVATE -Wall -Wextra -mavx2 -mtune=skylake -ffp-contract=off -fstack-usage)
