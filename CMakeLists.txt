cmake_minimum_required(VERSION 3.20)
project(jshc LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

option(JSHC_ENABLE_OPENMP "Enable OpenMP pixel-block parallelism" ON)
option(JSHC_ENABLE_AVX2 "Build the runtime-dispatched x86 AVX2 kernel" ON)
option(JSHC_ENABLE_CPP_SIMD "Build optional C++26/experimental SIMD backend" OFF)
option(JSHC_ENABLE_ZIG "Build optional Zig SIMD backend (requires Zig)" OFF)
option(JSHC_ENABLE_RUST "Build optional Rust portable_simd backend" OFF)

add_library(jshc_core STATIC cpp/src/lut.cpp cpp/src/fit_r14.cpp)
target_include_directories(jshc_core PUBLIC cpp/include)
if(MSVC)
  target_compile_options(jshc_core PRIVATE /W4)
else()
  target_compile_options(jshc_core PRIVATE -Wall -Wextra)
endif()
if(JSHC_ENABLE_OPENMP)
  find_package(OpenMP QUIET)
  if(OpenMP_CXX_FOUND)
    target_link_libraries(jshc_core PUBLIC OpenMP::OpenMP_CXX)
  endif()
endif()

# Only this translation unit may contain AVX2 instructions. lut.cpp (including
# CPUID/XGETBV dispatch) and every fallback retain the compiler's baseline ISA.
include(CheckCXXSourceCompiles)
check_cxx_source_compiles("#if !defined(__x86_64__) && !defined(__i386__) && !defined(_M_X64) && !defined(_M_IX86)\n#error not_x86\n#endif\nint main() { return 0; }" JSHC_TARGET_X86)
if(JSHC_ENABLE_AVX2 AND JSHC_TARGET_X86)
  include(CheckCXXCompilerFlag)
  if(MSVC)
    set(JSHC_AVX2_FLAG /arch:AVX2)
  else()
    set(JSHC_AVX2_FLAG -mavx2)
  endif()
  check_cxx_compiler_flag("${JSHC_AVX2_FLAG}" JSHC_COMPILER_HAS_AVX2)
  if(JSHC_COMPILER_HAS_AVX2)
    target_sources(jshc_core PRIVATE cpp/src/lut_simd_avx2.cpp)
    set_source_files_properties(cpp/src/lut_simd_avx2.cpp PROPERTIES COMPILE_OPTIONS "${JSHC_AVX2_FLAG}")
    target_compile_definitions(jshc_core PRIVATE JSHC_HAVE_AVX2=1)
  endif()
endif()

if(JSHC_ENABLE_CPP_SIMD)
  add_library(jshc_cpp_simd OBJECT cpp/src/lut_simd_cpp26.cpp)
  if("cxx_std_26" IN_LIST CMAKE_CXX_COMPILE_FEATURES)
    target_compile_features(jshc_cpp_simd PRIVATE cxx_std_26)
  endif()
  target_sources(jshc_core PRIVATE $<TARGET_OBJECTS:jshc_cpp_simd>)
  target_compile_definitions(jshc_core PRIVATE JSHC_HAVE_CPP_SIMD=1)
endif()

if(JSHC_ENABLE_ZIG)
  find_program(ZIG_EXECUTABLE zig REQUIRED)
  set(ZIG_SIMD_OBJ "${CMAKE_CURRENT_BINARY_DIR}/lut_simd_zig${CMAKE_CXX_OUTPUT_EXTENSION}")
  add_custom_command(
    OUTPUT "${ZIG_SIMD_OBJ}"
    COMMAND "${ZIG_EXECUTABLE}" build-obj "${CMAKE_CURRENT_SOURCE_DIR}/zig/lut_simd.zig"
            -O ReleaseFast -fPIC "-femit-bin=${ZIG_SIMD_OBJ}"
    DEPENDS zig/lut_simd.zig
    VERBATIM COMMENT "Building optional Zig SIMD kernel")
  target_sources(jshc_core PRIVATE "${ZIG_SIMD_OBJ}")
  target_compile_definitions(jshc_core PRIVATE JSHC_HAVE_ZIG=1)
endif()

if(JSHC_ENABLE_RUST)
  find_program(RUSTC_EXECUTABLE rustc REQUIRED)
  set(RUST_SIMD_OBJ "${CMAKE_CURRENT_BINARY_DIR}/lut_simd_rust${CMAKE_CXX_OUTPUT_EXTENSION}")
  add_custom_command(
    OUTPUT "${RUST_SIMD_OBJ}"
    COMMAND "${CMAKE_COMMAND}" -E env RUSTC_BOOTSTRAP=1
            "${RUSTC_EXECUTABLE}" --edition 2021 --crate-type=lib --emit=obj
            -C opt-level=3 -C panic=abort -C relocation-model=pic
            "${CMAKE_CURRENT_SOURCE_DIR}/rust/lut_simd.rs" -o "${RUST_SIMD_OBJ}"
    DEPENDS rust/lut_simd.rs
    VERBATIM COMMENT "Building optional Rust portable_simd kernel")
  target_sources(jshc_core PRIVATE "${RUST_SIMD_OBJ}")
  target_compile_definitions(jshc_core PRIVATE JSHC_HAVE_RUST=1)
endif()

add_executable(jshc cpp/src/main.cpp)
target_include_directories(jshc PRIVATE cpp/third_party)
if(NOT MSVC)
  target_compile_options(jshc PRIVATE -Wno-unused-function -Wno-missing-field-initializers)
endif()
target_link_libraries(jshc PRIVATE jshc_core)

enable_testing()
add_executable(jshc_tests cpp/tests/test_kernels.cpp)
target_link_libraries(jshc_tests PRIVATE jshc_core)
add_test(NAME kernels COMMAND jshc_tests --full)

message(STATUS "jshc: C++17 portable baseline; AVX2=${JSHC_COMPILER_HAS_AVX2}; OpenMP=${OpenMP_CXX_FOUND}")
message(STATUS "jshc optional backends: C++ SIMD=${JSHC_ENABLE_CPP_SIMD}; Zig=${JSHC_ENABLE_ZIG}; Rust=${JSHC_ENABLE_RUST}")
