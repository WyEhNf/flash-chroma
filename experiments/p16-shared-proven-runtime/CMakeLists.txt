cmake_minimum_required(VERSION 3.24)
project(jshc_shared_proven LANGUAGES CXX C)
find_package(OpenMP REQUIRED COMPONENTS CXX)
get_filename_component(JSHC_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(BASE "${JSHC_ROOT}/experiments/skylake-andn-normal-runtime")
add_subdirectory("${BASE}" baseline)
# 97仅新增隔离shared已证域像素入口；准备/字典/旧checked对象来源保持95。
add_library(jshc_shared_proven SHARED
  channel_runtime.cpp compile_shared_avx2.cpp
  "${BASE}/outplace_bench.cpp" "${BASE}/channel_avx2.cpp"
  "${BASE}/andn_inplace/channel_avx2.cpp" "${BASE}/andn_outplace/channel_avx2.cpp"
  "${BASE}/normal_inplace/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(jshc_shared_proven PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_link_libraries(jshc_shared_proven PRIVATE jshc_core OpenMP::OpenMP_CXX)
target_compile_definitions(jshc_shared_proven PRIVATE JSHC_CC_HAVE_AVX2=1 P16_PREPARE_SIMD=1)
target_compile_options(jshc_shared_proven PRIVATE -Wall -Wextra -fvisibility=hidden -fstack-usage)
set_source_files_properties(compile_shared_avx2.cpp
  "${BASE}/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
set_source_files_properties("${BASE}/andn_inplace/channel_avx2.cpp"
  "${BASE}/andn_outplace/channel_avx2.cpp" "${BASE}/normal_inplace/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off;-mbmi")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 独立有限合同不链接模型核心，不作计时。
add_executable(p16_palette_contract "${JSHC_ROOT}/experiments/p16-palette-prepare-runtime/finite_contract.cpp")
target_include_directories(p16_palette_contract PRIVATE "${JSHC_ROOT}/experiments/p16-palette-prepare-runtime")
target_compile_options(p16_palette_contract PRIVATE -Wall -Wextra -fstack-usage)

# 私有核质量入口显式调用新函数，独立四项凸权重uint64真值，不新增生产C ABI。
add_executable(p16_shared_proven_contract finite_contract.cpp compile_shared_avx2.cpp
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(p16_shared_proven_contract PRIVATE "${BASE}")
target_compile_options(p16_shared_proven_contract PRIVATE -Wall -Wextra -mavx2 -mtune=skylake -ffp-contract=off -fstack-usage)
