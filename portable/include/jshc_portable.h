/* Allocation-free RGB8/Q16 runtime.
 *
 * Model bytes and prepared objects must remain alive and immutable during use.
 * All buffers/workspaces belong to the caller; the library performs no I/O,
 * heap allocation, threading, floating-point arithmetic, or LUT fitting.
 * This interface consumes SLUT v1, with competition sizes 17 <= m <= 33.
 */
#ifndef JSHC_PORTABLE_H
#define JSHC_PORTABLE_H

#include <stddef.h>
#include <stdint.h>

#if defined(_WIN32) && defined(JSHC_P_SHARED)
# if defined(JSHC_P_BUILD)
#  define JSHC_P_API __declspec(dllexport)
# else
#  define JSHC_P_API __declspec(dllimport)
# endif
#else
# define JSHC_P_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define JSHC_P_ABI_VERSION 1u
#define JSHC_P_STAGES 4u

typedef enum jshc_p_status {
    JSHC_P_OK = 0,
    JSHC_P_NULL = 1,
    JSHC_P_FORMAT = 2,
    JSHC_P_SIZE = 3,
    JSHC_P_RANGE = 4,
    JSHC_P_OVERFLOW = 5,
    JSHC_P_OVERLAP = 6,
    JSHC_P_STATE = 7
} jshc_p_status;

enum {
    JSHC_P_MODEL_ONE_HOT = 1u,
    JSHC_P_MODEL_SEPARABLE = 2u,
    JSHC_P_MODEL_CONSTANT = 4u,
    JSHC_P_FORCE_GENERIC = 1u
};

typedef enum jshc_p_path {
    JSHC_P_TETRA = 0,
    JSHC_P_CURVE = 1,
    JSHC_P_VERTEX = 2,
    JSHC_P_CONSTANT = 3
} jshc_p_path;

/* Public layout enables static allocation and FFI. Members are implementation
 * state, not an editing API. Re-prepare after changing serialized model bytes.
 * curve[] is packed RGB contributions indexed by one input component; it does
 * not replace or modify the m^3 serialized RGB nodes.
 */
typedef struct jshc_p_model {
    uint32_t ready;
    uint32_t m;
    uint32_t flags;
    uint32_t constant_rgb;
    const uint8_t *blob;
    size_t blob_bytes;
    const uint8_t *index;
    const uint8_t *fraction_le;
    const uint8_t *nodes;
    uint32_t curve[3][256];
} jshc_p_model;

typedef struct jshc_p_chain {
    uint32_t ready;
    uint32_t options;
    const jshc_p_model *models[JSHC_P_STAGES];
    uint8_t path[JSHC_P_STAGES];
    uint8_t effective_one_hot[JSHC_P_STAGES];
} jshc_p_chain;

JSHC_P_API uint32_t jshc_p_abi_version(void);
JSHC_P_API size_t jshc_p_model_bytes(void);
JSHC_P_API size_t jshc_p_chain_bytes(void);
JSHC_P_API const char *jshc_p_status_string(jshc_p_status status);

/* Validates the complete exact-length blob, including binary32 grid metadata,
 * indices and Q16 fractions. Input alignment and host byte order are arbitrary.
 * On error, *out is untouched. out must not overlap the borrowed blob.
 */
JSHC_P_API jshc_p_status jshc_p_model_prepare(
    jshc_p_model *out, const void *blob, size_t bytes);

/* Exactly four independently prepared models; no composition or skipped stage.
 * FORCE_GENERIC disables shortcuts to support explicit equivalence comparisons.
 * A vertex shortcut may depend on this chain's preceding output palette proof.
 * On error, *out is untouched; chain must not overlap models or their blobs.
 */
JSHC_P_API jshc_p_status jshc_p_chain_prepare(
    jshc_p_chain *out, const jshc_p_model *const models[JSHC_P_STAGES],
    uint32_t options);

/* Byte counts describe accessible spans starting at src/dst. Positive strides
 * must cover width*3 bytes. Padding is untouched. Exact in-place operation is
 * supported when pointers and strides match; other intersecting spans reject.
 * Zero width or height is a no-op (NULL pixels allowed) for a valid chain.
 * All errors are detected before any output write. Destination cannot overlap
 * model bytes, prepared models, or the chain. Tile by calling with row/column
 * offsets and appropriately reduced spans; every call still applies four LUTs.
 */
JSHC_P_API jshc_p_status jshc_p_apply_rgb8(
    const jshc_p_chain *chain,
    const uint8_t *src, size_t src_bytes, size_t src_stride,
    uint8_t *dst, size_t dst_bytes, size_t dst_stride,
    size_t width, size_t height);

#ifdef __cplusplus
}
#endif
#endif
