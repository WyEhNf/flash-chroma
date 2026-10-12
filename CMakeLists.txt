cmake_minimum_required(VERSION 3.20)
project(jshc LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

option(JSHC_PORTABLE_NATIVE_TARGET
       "Lower portable SIMD (C++26 <simd>, Zig @Vector, Rust std::simd) to host CPU target"
       OFF)

if(JSHC_PORTABLE_NATIVE_TARGET)
  set(CPP_TARGET_FLAG "-march=native")
  set(ZIG_TARGET_FLAG "-mcpu=native")
  set(RUST_TARGET_FLAG "-Ctarget-cpu=native")
else()
  set(CPP_TARGET_FLAG "-march=x86-64")
  set(ZIG_TARGET_FLAG "-mcpu=x86_64")
  set(RUST_TARGET_FLAG "-Ctarget-cpu=x86-64")
endif()

add_compile_options(-O3 -Wall -Wextra ${CPP_TARGET_FLAG})

find_package(OpenMP)
find_program(ZIG_EXECUTABLE zig REQUIRED)
find_program(RUSTC_EXECUTABLE rustc REQUIRED)

# Prefer host GCC 16+ with true C++26 <simd> support if available; fallback to CMAKE_CXX_COMPILER -std=c++23.
if(EXISTS "/usr/bin/g++")
  set(CPP26_SIMD_COMPILER "/usr/bin/g++")
  set(CPP26_SIMD_STD "-std=c++26")
else()
  set(CPP26_SIMD_COMPILER "${CMAKE_CXX_COMPILER}")
  set(CPP26_SIMD_STD "-std=c++23")
endif()

set(CPP_SIMD_OBJ "${CMAKE_CURRENT_BINARY_DIR}/lut_simd_cpp26.o")
add_custom_command(
  OUTPUT "${CPP_SIMD_OBJ}"
  COMMAND "${CPP26_SIMD_COMPILER}" ${CPP26_SIMD_STD} -O3 ${CPP_TARGET_FLAG} -fPIC
          -c "${CMAKE_CURRENT_SOURCE_DIR}/cpp/src/lut_simd_cpp26.cpp"
          -o "${CPP_SIMD_OBJ}"
  DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/cpp/src/lut_simd_cpp26.cpp"
  COMMENT "Building C++26 <simd> kernel (${CPP_TARGET_FLAG})"
)

set(ZIG_SIMD_OBJ "${CMAKE_CURRENT_BINARY_DIR}/lut_simd_zig.o")
add_custom_command(
  OUTPUT "${ZIG_SIMD_OBJ}"
  COMMAND "${ZIG_EXECUTABLE}" build-obj "${CMAKE_CURRENT_SOURCE_DIR}/zig/lut_simd.zig"
          -O ReleaseFast ${ZIG_TARGET_FLAG} -fPIC "-femit-bin=${ZIG_SIMD_OBJ}"
  DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/zig/lut_simd.zig"
  COMMENT "Building Zig @Vector SIMD kernel (${ZIG_TARGET_FLAG})"
)

set(RUST_SIMD_OBJ "${CMAKE_CURRENT_BINARY_DIR}/lut_simd_rust.o")
add_custom_command(
  OUTPUT "${RUST_SIMD_OBJ}"
  COMMAND "${RUSTC_EXECUTABLE}" --edition 2021 --crate-type=lib --emit=obj
          -C opt-level=3 ${RUST_TARGET_FLAG} -C panic=abort -C relocation-model=pic
          "${CMAKE_CURRENT_SOURCE_DIR}/rust/lut_simd.rs"
          -o "${RUST_SIMD_OBJ}"
  DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/rust/lut_simd.rs"
  COMMENT "Building Rust portable_simd kernel (${RUST_TARGET_FLAG})"
)

add_library(jshc_core STATIC
  cpp/src/lut.cpp
  cpp/src/fit_r14.cpp
  "${CPP_SIMD_OBJ}"
  "${ZIG_SIMD_OBJ}"
  "${RUST_SIMD_OBJ}"
)
target_include_directories(jshc_core PUBLIC cpp/include)
if(OpenMP_CXX_FOUND)
  target_link_libraries(jshc_core PUBLIC OpenMP::OpenMP_CXX)
endif()

add_executable(jshc cpp/src/main.cpp)
target_include_directories(jshc PRIVATE cpp/third_party)
target_compile_options(jshc PRIVATE -Wno-unused-function -Wno-missing-field-initializers)
target_link_libraries(jshc PRIVATE jshc_core)

enable_testing()
add_executable(jshc_tests cpp/tests/test_kernels.cpp)
target_link_libraries(jshc_tests PRIVATE jshc_core)
add_test(NAME kernels COMMAND jshc_tests)
