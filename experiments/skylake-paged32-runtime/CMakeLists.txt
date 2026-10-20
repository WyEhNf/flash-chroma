cmake_minimum_required(VERSION 3.24)
project(jshc_skylake_paged32 LANGUAGES CXX C)
set(SKYLAKE_CANDIDATE_TARGET jshc_skylake_paged32)
set(SKYLAKE_RUNTIME_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/channel_runtime.cpp")
# 新候选共用构建骨架；既有两个候选的独立CMake保留原执行身份。
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
if(MSVC)
  message(FATAL_ERROR "当前研究验证GNU兼容编译器，未验收MSVC")
endif()
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "构建模式" FORCE)
endif()
get_filename_component(JSHC_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(BUILD_TESTING OFF CACHE BOOL "独立研究库不重复全仓门禁" FORCE)
set(JSHC_ENABLE_EMBEDDED OFF CACHE BOOL "研究库不构建嵌入式目标" FORCE)
set(JSHC_ENABLE_CHANNEL_RESEARCH OFF CACHE BOOL "另建显式参考与候选" FORCE)
set(JSHC_ENABLE_FULL_FIT OFF CACHE BOOL "不构建离线拟合库" FORCE)
set(JSHC_ENABLE_AVX2 ON CACHE BOOL "显式分派AVX2" FORCE)
set(JSHC_ENABLE_OPENMP ON CACHE BOOL "显式OpenMP" FORCE)
add_subdirectory("${JSHC_ROOT}" "${CMAKE_BINARY_DIR}/core" EXCLUDE_FROM_ALL)
find_package(OpenMP REQUIRED COMPONENTS CXX)
if(NOT DEFINED SKYLAKE_RUNTIME_SOURCE)
  set(SKYLAKE_RUNTIME_SOURCE "${JSHC_ROOT}/experiments/channel-runtime/channel_runtime.cpp")
endif()
add_library(jshc_skylake_reference SHARED
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_runtime.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-domain-isolated-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
add_library(${SKYLAKE_CANDIDATE_TARGET} SHARED "${SKYLAKE_RUNTIME_SOURCE}"
  "${CMAKE_CURRENT_SOURCE_DIR}/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-domain-isolated-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp")
foreach(target jshc_skylake_reference ${SKYLAKE_CANDIDATE_TARGET})
  target_link_libraries(${target} PRIVATE jshc_core OpenMP::OpenMP_CXX)
  target_include_directories(${target} PRIVATE "${JSHC_ROOT}/experiments/channel-runtime")
  target_compile_definitions(${target} PRIVATE JSHC_CC_HAVE_AVX2=1)
  target_compile_options(${target} PRIVATE -Wall -Wextra -fvisibility=hidden)
endforeach()
set_source_files_properties(
  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-palette-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-domain-isolated-runtime/channel_avx2.cpp"
  "${JSHC_ROOT}/experiments/skylake-suffix-cache-runtime/channel_avx2.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/channel_avx2.cpp"
  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")
set_property(SOURCE "${JSHC_ROOT}/cpp/src/lut_simd_avx2.cpp" DIRECTORY "${JSHC_ROOT}"
  APPEND PROPERTY COMPILE_OPTIONS -mtune=skylake -ffp-contract=off)
if(MINGW)
  foreach(target jshc_skylake_reference ${SKYLAKE_CANDIDATE_TARGET})
    foreach(dll libgcc_s_seh-1.dll libstdc++-6.dll libwinpthread-1.dll libgomp-1.dll)
      execute_process(COMMAND "${CMAKE_CXX_COMPILER}" "-print-file-name=${dll}"
        OUTPUT_VARIABLE dll_path OUTPUT_STRIP_TRAILING_WHITESPACE)
      if(IS_ABSOLUTE "${dll_path}" AND EXISTS "${dll_path}")
        add_custom_command(TARGET ${target} POST_BUILD COMMAND "${CMAKE_COMMAND}" -E copy_if_different
          "${dll_path}" "$<TARGET_FILE_DIR:${target}>" VERBATIM)
      endif()
    endforeach()
  endforeach()
endif()
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/libraries-$<CONFIG>.json" CONTENT
  "{\n  \"reference\": \"$<TARGET_FILE:jshc_skylake_reference>\",\n  \"candidate\": \"$<TARGET_FILE:${SKYLAKE_CANDIDATE_TARGET}>\"\n}\n")
