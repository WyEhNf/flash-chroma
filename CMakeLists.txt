cmake_minimum_required(VERSION 3.20)
project(jshc LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

add_compile_options(-O3 -Wall -Wextra)

find_package(OpenMP)
find_program(ZIG_EXECUTABLE zig REQUIRED)
find_program(RUSTC_EXECUTABLE rustc REQUIRED)

set(CPP_SIMD_OBJ "${CMAKE_CURRENT_BINARY_DIR}/lut_simd_cpp26.o")
add_custom_command(
  OUTPUT "${CPP_SIMD_OBJ}"
  COMMAND "${CMAKE_CXX_COMPILER}" -std=c++26 -O3 -fPIC
          -c "${CMAKE_CURRENT_SOURCE_DIR}/cpp/src/lut_simd_cpp26.cpp"
          -o "${CPP_SIMD_OBJ}"
  DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/cpp/src/lut_simd_cpp26.cpp"
  COMMENT "Building C++26 <simd> kernel"
)

set(ZIG_SIMD_OBJ "${CMAKE_CURRENT_BINARY_DIR}/lut_simd_zig.o")
add_custom_command(
  OUTPUT "${ZIG_SIMD_OBJ}"
  COMMAND "${ZIG_EXECUTABLE}" build-obj "${CMAKE_CURRENT_SOURCE_DIR}/zig/lut_simd.zig"
          -O ReleaseFast -fPIC "-femit-bin=${ZIG_SIMD_OBJ}"
  DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/zig/lut_simd.zig"
  COMMENT "Building Zig @Vector SIMD kernel"
)

set(RUST_SIMD_OBJ "${CMAKE_CURRENT_BINARY_DIR}/lut_simd_rust.o")
add_custom_command(
  OUTPUT "${RUST_SIMD_OBJ}"
  COMMAND "${CMAKE_COMMAND}" -E env RUSTC_BOOTSTRAP=1
          "${RUSTC_EXECUTABLE}" --edition 2021 --crate-type=lib --emit=obj
          -C opt-level=3 -C panic=abort -C relocation-model=pic
          "${CMAKE_CURRENT_SOURCE_DIR}/rust/lut_simd.rs"
          -o "${RUST_SIMD_OBJ}"
  DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/rust/lut_simd.rs"
  COMMENT "Building Rust portable_simd kernel"
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
