cmake_minimum_required(VERSION 3.24)
project(jshc_direct_compile LANGUAGES CXX C)
find_package(OpenMP REQUIRED COMPONENTS CXX)
get_filename_component(JSHC_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_subdirectory("${JSHC_ROOT}/experiments/skylake-andn-normal-runtime" baseline)
set(BASE "${JSHC_ROOT}/experiments/skylake-andn-normal-runtime")
add_library(jshc_direct_compile SHARED
  channel_runtime.cpp compile_avx2.cpp
  "${BASE}/outplace_bench.cpp" "${BASE}/channel_avx2.cpp"
  "${BASE}/andn_inplace/channel_avx2.cpp" "${BASE}/andn_outplace/channel_avx2.cpp"
  "${BASE}/normal_inplace/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(jshc_direct_compile PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_link_libraries(jshc_direct_compile PRIVATE jshc_core OpenMP::OpenMP_CXX)
target_compile_definitions(jshc_direct_compile PRIVATE JSHC_CC_HAVE_AVX2=1)
target_compile_options(jshc_direct_compile PRIVATE -Wall -Wextra -fvisibility=hidden)
set_source_files_properties(compile_avx2.cpp "${BASE}/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
set_source_files_properties("${BASE}/andn_inplace/channel_avx2.cpp"
  "${BASE}/andn_outplace/channel_avx2.cpp" "${BASE}/normal_inplace/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off;-mbmi")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 通用分输出坐标路径：一个相同内核，分别比较先复制与直接分离输出。
add_library(jshc_channel_copy SHARED
  "${JSHC_ROOT}/experiments/channel-runtime/channel_runtime.cpp"
  "${JSHC_ROOT}/experiments/channel-runtime-specialized/channel_avx2.cpp"
  "${BASE}/reference_to.cpp" "${BASE}/outplace_bench.cpp")
add_library(jshc_channel_to SHARED channel_to_runtime.cpp channel_to_avx2.cpp "${BASE}/outplace_bench.cpp")
foreach(t jshc_channel_copy jshc_channel_to)
  target_include_directories(${t} PRIVATE "${JSHC_ROOT}/experiments/channel-runtime")
  target_link_libraries(${t} PRIVATE jshc_core OpenMP::OpenMP_CXX)
  target_compile_definitions(${t} PRIVATE JSHC_CC_HAVE_AVX2=1)
  target_compile_options(${t} PRIVATE -Wall -Wextra -fvisibility=hidden)
endforeach()
set_source_files_properties(channel_to_avx2.cpp
  "${JSHC_ROOT}/experiments/channel-runtime-specialized/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
