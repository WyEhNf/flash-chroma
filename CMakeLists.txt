cmake_minimum_required(VERSION 3.20)
project(jshc LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# JSHC_ARCH: "native" (default, fastest on this host), "x86-64-v3" (AVX2/FMA, matches the
# i7-14700 evaluation CPU, portable across modern x86), or "generic" (no SIMD flags).
set(JSHC_ARCH "x86-64-v3" CACHE STRING "native | x86-64-v3 | generic")
if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
  if(JSHC_ARCH STREQUAL "native")
    add_compile_options(-march=native)
  elseif(JSHC_ARCH STREQUAL "x86-64-v3")
    add_compile_options(-march=x86-64-v3)
  endif()
endif()
add_compile_options(-O3 -Wall -Wextra)

find_package(OpenMP)

add_library(jshc_core STATIC cpp/src/lut.cpp)
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
