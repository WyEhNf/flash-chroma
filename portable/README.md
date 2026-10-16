# Portable RGB8/Q16 C API

This standalone C99 library executes four independent SLUT v1 models. Fitting,
file/image decoding, threading, and device scheduling stay in the host layer.
The pixel path has no heap allocation, I/O, floating-point arithmetic, Python,
OpenMP, CUDA, or x86 instruction requirement. Compiler-generated memory helpers
such as `memcpy`/`memset` may need the target C runtime or board implementation.

The implemented operator is tetrahedral Q16 only. SLUT v1 does not contain an
interpolation-type identifier: a model fitted for `tri_float` requires that
backend, and cannot be made equivalent by passing it to this tetrahedral API.
The host must retain the manifest's operator and source provenance. Parsing bare
SLUT bytes proves structural validity, not that four distinct original LUTs were
independently fitted or that the official image/accuracy contract is satisfied.

```powershell
cmake -S portable -B build-portable-c -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
cmake --build build-portable-c
# Add -DBUILD_SHARED_LIBS=ON for a DLL/shared library.
```

The C API is in [jshc_portable.h](include/jshc_portable.h). Allocate four
`jshc_p_model` objects and one `jshc_p_chain` in caller-owned memory. Keep the
serialized blobs alive and immutable: they are borrowed, not copied. A shared
prepared chain is read-only and may be used by independent caller threads.

```c
#include "jshc_portable.h"

/* ROM blobs, pixel allocation, and error handling are supplied by the host. */
jshc_p_model model[4];
jshc_p_chain chain;
const jshc_p_model *views[4] = { &model[0], &model[1], &model[2], &model[3] };
for (unsigned s = 0; s < 4; ++s) {
    if (jshc_p_model_prepare(&model[s], blob[s], blob_bytes[s]) != JSHC_P_OK)
        return MODEL_ERROR;
}
if (jshc_p_chain_prepare(&chain, views, 0) != JSHC_P_OK) return MODEL_ERROR;
if (jshc_p_apply_rgb8(&chain, pixels, capacity, row_stride,
        pixels, capacity, row_stride, width, height) != JSHC_P_OK)
    return PIXEL_ERROR;
```

Positive row strides, unaligned pixels/model bytes, rectangular tiles, and exact
in-place mapping are supported. The function validates sizes, overflow, overlap,
and model state before writing output. It leaves padding untouched. It rejects
partial overlap, including destination overlap with ROM or prepared workspaces.
The caller must provide actual readable/writable allocations of the stated sizes
and naturally aligned prepared C objects; arbitrary invalid pointers cannot be
validated by a C library. Zero-area calls need no pixel pointers. Callers wanting
the competition image contract must separately enforce RGB8, 1024x768 and the
input container policy; arbitrary tile sizes here do not change that contract.

Serialized indices and Q16 fractions are authoritative. Metadata is validated as
finite, strictly increasing binary32 covering 0..255, using integer bit ordering;
it is not recomputed into different axis tables. All integer and metadata loads
are alignment-safe little-endian byte loads. The parser enforces 17<=m<=33.

Preparation proves the complete stored node array before selecting a shortcut:

- A constant model returns its stored RGB value.
- If each output channel depends on at most one axis, three 256-entry packed
  contribution tables exactly reproduce tetrahedral Q16 interpolation and per
  stage rounding. Channel permutations/shared axes and constant channels work.
- If all fractions are 0/65536, interpolation becomes one stored vertex lookup.
  A later stage may use that same path when every preceding stored vertex hits
  its endpoint tables. This proof belongs to the chain, not the standalone model.
- Otherwise four-node tetrahedral interpolation is used. Nonnegative integer
  weights sum to 65536; adding 32768 keeps the RGB8 sum below 2^24.

Every stage still produces RGB8 before the next stage. There is no full-cube
composition table and no residual target. `JSHC_P_FORCE_GENERIC` disables all
shortcuts for explicit equivalence checks. Prepared tables add 3072 bytes per
model plus metadata; exact ABI sizes are returned by the exported size functions.
The model bytes remain the original m^3 RGB8 nodes and axis metadata.

The staged verifier is `scripts/r30_portable_stage.py`: it compares complete RGB
cubes to frozen native evidence, checks an independent uint64 oracle, exercises
row/tile/in-place/error contracts, rejects malformed sparse fixtures, and records
freestanding target compilation separately from actual execution. Check its
result artifact before claiming verification. Cross-compilation alone is neither
ARM execution nor mobile performance/power evidence. These portability gates
do not measure a speedup; the separate desktop comparison is described below.

## Generate ROM arrays on the development host

The development-host exporter checks the existing cache manifest and preserves
the four model blobs byte for byte. Firmware consumes generated `const uint8_t`
arrays directly; it does not need Python or a model file system.

```powershell
$env:PYTHONPATH = 'python'
python -m lutlab.portable_export --models stage1.slut stage2.slut stage3.slut stage4.slut --output firmware-model
```

Compile generated `flash_chroma.c` with this library and include the generated
header. `flash_chroma_prepare(models, &chain, 0)` uses caller-owned objects and
borrows the const arrays. The sidecar files retain ordered source/model hashes,
the original fitting manifest and explicit `tetra_q16` semantics. Trilinear or
unknown-basis models are rejected; an existing output folder is preserved.

R43 actually compiled and consumed the generated arrays for m17 and m33 models:
both complete RGB cubes matched frozen native results. Their serialized ROM
array payloads are 75,196 and 448,252 bytes; native 64-bit prepared workspace is
12,560 bytes. Linker tables/code/padding are additional, and target ABI sizes may
differ. AArch64 LE/BE, Cortex-M4 and RV32IM object compilation also succeeded;
this does not add physical-device timing evidence. See the
[staged ROM results and row-buffer integration](../docs/r43-rom-export.md).

R39 separately measured the desktop C99/OpenMP bridge against AVX2 on the same
host, models and 100-image cohort. Results vary by model structure; they are not
mobile speed estimates. See [paired desktop results](../docs/r39-structured-performance.md).

R47 also verified a compiled ROM chain with stage sizes `[17,33,17,17]`, using
168,460 bytes of serialized array payload. Generated bundles preserve parent
manifests in `parents/`; keep those files with the host-side provenance sidecars.
Each stage still owns its original SLUT v1 bytes and produces RGB8 before the
next stage. The portable core has not changed. See the
[mixed-capacity search and native gate](../docs/r47-mixed-capacity.md).

R51 also compiled a recovered random/adversarial m33 model into ROM and matched
its complete RGB8 cube against CPU and CUDA output. All four portable paths are
generic. The host measured 448,252 serialized ROM bytes and 12,560 preparation
bytes on a 64-bit build; no physical mobile performance was measured. This model
has poor prediction accuracy and does not replace the case's quality champions.
See [solver recovery and its accuracy boundary](../docs/r51-bounded-cg-recovery.md).
