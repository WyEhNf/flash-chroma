cmake_minimum_required(VERSION 3.24)
project(p16_shared_proven_contract_repair LANGUAGES CXX)
get_filename_component(JSHC_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(BASE "${JSHC_ROOT}/experiments/skylake-andn-normal-runtime")
set(CANDIDATE "${JSHC_ROOT}/experiments/p16-shared-proven-runtime")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
# 只补测试target缺失的通用头路径；复用v1原字节，不重建生产DLL。
add_executable(p16_shared_proven_contract "${CANDIDATE}/finite_contract.cpp"
  "${CANDIDATE}/compile_shared_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
target_include_directories(p16_shared_proven_contract PRIVATE "${BASE}" "${JSHC_ROOT}/experiments/channel-runtime")
target_compile_options(p16_shared_proven_contract PRIVATE -Wall -Wextra -mavx2 -mtune=skylake -ffp-contract=off -fstack-usage)
set_source_files_properties("${CANDIDATE}/compile_shared_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
add_executable(p16_palette_contract "${JSHC_ROOT}/experiments/p16-palette-prepare-runtime/finite_contract.cpp")
target_include_directories(p16_palette_contract PRIVATE "${JSHC_ROOT}/experiments/p16-palette-prepare-runtime")
target_compile_options(p16_palette_contract PRIVATE -Wall -Wextra -fstack-usage)
