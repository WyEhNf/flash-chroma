// Optional offline full-domain Q16 normal-equation assembly, C ABI version 1.
// All arrays are caller-owned, contiguous, native-endian and non-overlapping.
// Inputs stay immutable during the call. No memory or exception crosses the ABI.
#pragma once
#include <stdint.h>

#if defined(_WIN32)
#if defined(JSHC_FULL_FIT_BUILD)
#define JSHC_FULL_API __declspec(dllexport)
#else
#define JSHC_FULL_API __declspec(dllimport)
#endif
#else
#define JSHC_FULL_API __attribute__((visibility("default")))
#endif
#ifdef __cplusplus
extern "C" {
#define JSHC_FULL_NOEXCEPT noexcept
#else
#define JSHC_FULL_NOEXCEPT
#endif

JSHC_FULL_API uint32_t jshc_full_normals_abi_v1(void) JSHC_FULL_NOEXCEPT;
JSHC_FULL_API uint32_t jshc_full_normals_openmp_v1(void) JSHC_FULL_NOEXCEPT;
// SHA256 of "<cpp SHA256>:<header SHA256>", embedded by the CMake target.
JSHC_FULL_API const char* jshc_full_normals_source_v1(void) JSHC_FULL_NOEXCEPT;

// RGB input: 256^3*3 bytes, B-fastest. Axis arrays each contain 3*256 entries.
// Outputs before normalisation: diag=sum(w_q^2), upper=sum(w_q*w'_q),
// rhs=sum(w_q*y). Upper slots are positive offsets {1,m,m+1,m^2,m^2+1,
// m^2+m,m^2+m+1}. Divide H by 2^38 and rhs by 2^22 to use weight 1/64.
// Metadata: {visited colors, actual threads, R cells, ABI, sum(y_R^2),
// sum(y_G^2), sum(y_B^2)}. A nonzero return writes a bounded error message.
JSHC_FULL_API int jshc_full_normals_v1(
    const uint8_t* rgb, uint64_t rgb_bytes,
    const uint8_t* indices, const uint32_t* fractions, uint32_t m, uint32_t threads,
    uint64_t* diagonal, uint64_t diagonal_count,
    uint64_t* upper, uint64_t upper_count,
    uint64_t* rhs, uint64_t rhs_count,
    uint64_t* metadata, uint64_t metadata_count,
    char* error, uint64_t error_capacity) JSHC_FULL_NOEXCEPT;

#ifdef __cplusplus
}
#endif
