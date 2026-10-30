cmake_minimum_required(VERSION 3.20)
project(p16_call_boundary LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
# 纯调用边界探针不链接像素实现或OpenMP，调用者传入同一87入口。
add_library(jshc_call_boundary SHARED probe.cpp)
target_compile_options(jshc_call_boundary PRIVATE -Wall -Wextra -fvisibility=hidden)
