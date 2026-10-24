#include "jshc_portable.h"

#define MODEL_READY UINT32_C(0x4a504d31)
#define CHAIN_READY UINT32_C(0x4a504331)
#define ONE UINT32_C(65536)
#define HALF UINT32_C(32768)

/* Byte loads are defined even for unaligned ROM and big-endian hosts. */
static uint32_t read32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static int span_valid(const void *p, size_t bytes) {
#if SIZE_MAX > UINTPTR_MAX
    if (bytes > UINTPTR_MAX) return 0;
#endif
    return (uintptr_t)p <= UINTPTR_MAX - bytes;
}

/* The callers validate both integer intervals before comparing them. */
static int intersects(const void *a, size_t an, const void *b, size_t bn) {
    return an && bn && (uintptr_t)a < (uintptr_t)b + bn &&
                      (uintptr_t)b < (uintptr_t)a + an;
}

static uint32_t float_order_key(uint32_t bits) {
    if ((bits & UINT32_C(0x7fffffff)) == 0) bits = 0; /* equal signed zeros */
    return bits & UINT32_C(0x80000000) ? ~bits : bits ^ UINT32_C(0x80000000);
}

static uint32_t fraction(const jshc_p_model *m, unsigned axis, unsigned value) {
    return read32(m->fraction_le + 4u * (axis * 256u + value));
}

static uint32_t packed(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16);
}

static int endpoints_at_rgb(const jshc_p_model *m, const uint8_t rgb[3]) {
    unsigned a;
    for (a = 0; a < 3; ++a) {
        uint32_t f = fraction(m, a, rgb[a]);
        if (f != 0 && f != ONE) return 0;
    }
    return 1;
}

/* Proves the entire stored m^3 node array, not a few sampled lines. When each
 * output component depends on at most one input axis, barycentric weights on
 * that axis telescope to the exact two-endpoint Q16 interpolation. Different
 * output components may depend on the same axis, or permute the input axes.
 */
static int prepare_curves(jshc_p_model *out) {
    uint32_t strides[3], count = out->m * out->m * out->m;
    unsigned c, a, x;
    int constant = 1;
    strides[0] = out->m * out->m; strides[1] = out->m; strides[2] = 1;
    for (c = 0; c < 3; ++c) {
        int found = 0;
        for (a = 0; a < 3; ++a) {
            uint32_t n;
            for (n = 0; n < count; ++n) {
                uint32_t coordinate = (n / strides[a]) % out->m;
                if (out->nodes[3u*n+c] != out->nodes[3u*coordinate*strides[a]+c]) break;
            }
            if (n == count) { found = 1; break; }
        }
        if (!found) return 0;
        for (x = 1; x < out->m; ++x)
            if (out->nodes[3u*x*strides[a]+c] != out->nodes[c]) break;
        if (x == out->m) {
            out->constant_rgb |= (uint32_t)out->nodes[c] << (8u*c);
            continue;
        }
        constant = 0;
        for (x = 0; x < 256; ++x) {
            uint32_t i = out->index[a*256u+x], f = fraction(out,a,x);
            uint32_t lo = out->nodes[3u*i*strides[a]+c];
            uint32_t hi = out->nodes[3u*(i+1u)*strides[a]+c];
            uint32_t value = ((ONE-f)*lo + f*hi + HALF) >> 16;
            out->curve[a][x] |= value << (8u*c);
        }
    }
    if (constant) out->flags |= JSHC_P_MODEL_CONSTANT;
    return 1;
}

uint32_t jshc_p_abi_version(void) { return JSHC_P_ABI_VERSION; }
size_t jshc_p_model_bytes(void) { return sizeof(jshc_p_model); }
size_t jshc_p_chain_bytes(void) { return sizeof(jshc_p_chain); }

const char *jshc_p_status_string(jshc_p_status status) {
    switch (status) {
    case JSHC_P_OK: return "ok";
    case JSHC_P_NULL: return "null argument";
    case JSHC_P_FORMAT: return "invalid SLUT v1 format";
    case JSHC_P_SIZE: return "incorrect buffer size or stride";
    case JSHC_P_RANGE: return "model value or option out of range";
    case JSHC_P_OVERFLOW: return "address or size overflow";
    case JSHC_P_OVERLAP: return "unsupported buffer overlap";
    case JSHC_P_STATE: return "unprepared model or chain";
    default: return "unknown status";
    }
}

jshc_p_status jshc_p_model_prepare(jshc_p_model *out, const void *blob, size_t bytes) {
    const uint8_t *p = (const uint8_t *)blob;
    uint32_t m, expected, a, i;
    int one_hot = 1;
    jshc_p_model temporary = {0};
    if (!out || !blob) return JSHC_P_NULL;
    if (!span_valid(out,sizeof(*out)) || !span_valid(blob,bytes)) return JSHC_P_OVERFLOW;
    if (intersects(out,sizeof(*out),blob,bytes)) return JSHC_P_OVERLAP;
    if (bytes < 16) return JSHC_P_SIZE;
    if (p[0]!='S' || p[1]!='L' || p[2]!='U' || p[3]!='T' ||
        read32(p+4)!=1 || read32(p+12)!=0) return JSHC_P_FORMAT;
    m = read32(p+8);
    if (m < 17 || m > 33) return JSHC_P_RANGE;
    expected = 16u + 12u*m + 768u + 3072u + 3u*m*m*m;
    if (bytes != expected) return JSHC_P_SIZE;
    for (a = 0; a < 3; ++a) {
        uint32_t previous = 0;
        for (i = 0; i < m; ++i) {
            uint32_t bits = read32(p+16u+4u*(a*m+i));
            uint32_t key = float_order_key(bits);
            if ((bits & UINT32_C(0x7f800000)) == UINT32_C(0x7f800000) ||
                (i && key <= previous) || (!i && key > UINT32_C(0x80000000)) ||
                (i==m-1u && key < UINT32_C(0xc37f0000))) return JSHC_P_FORMAT;
            previous = key;
        }
    }
    temporary.m = m; temporary.blob = p; temporary.blob_bytes = bytes;
    temporary.index = p + 16u + 12u*m;
    temporary.fraction_le = temporary.index + 768u;
    temporary.nodes = temporary.fraction_le + 3072u;
    for (i = 0; i < 768; ++i) {
        uint32_t f = read32(temporary.fraction_le + 4u*i);
        if (temporary.index[i] > m-2u || f > ONE) return JSHC_P_RANGE;
        if (f != 0 && f != ONE) one_hot = 0;
    }
    if (one_hot) temporary.flags |= JSHC_P_MODEL_ONE_HOT;
    if (prepare_curves(&temporary)) temporary.flags |= JSHC_P_MODEL_SEPARABLE;
    temporary.ready = MODEL_READY;
    *out = temporary;
    return JSHC_P_OK;
}

jshc_p_status jshc_p_chain_prepare(jshc_p_chain *out,
    const jshc_p_model *const models[JSHC_P_STAGES], uint32_t options) {
    jshc_p_chain temporary = {0};
    unsigned s;
    if (!out || !models) return JSHC_P_NULL;
    if (options & ~(uint32_t)JSHC_P_FORCE_GENERIC) return JSHC_P_RANGE;
    if (!span_valid(out,sizeof(*out))) return JSHC_P_OVERFLOW;
    for (s = 0; s < JSHC_P_STAGES; ++s) {
        const jshc_p_model *m = models[s];
        int one_hot;
        if (!m) return JSHC_P_NULL;
        if (m->ready != MODEL_READY) return JSHC_P_STATE;
        if (intersects(out,sizeof(*out),m,sizeof(*m)) ||
            intersects(out,sizeof(*out),m->blob,m->blob_bytes)) return JSHC_P_OVERLAP;
        temporary.models[s] = m;
        one_hot = (m->flags & JSHC_P_MODEL_ONE_HOT) != 0;
        if (!one_hot && s && temporary.effective_one_hot[s-1]) {
            const jshc_p_model *previous = models[s-1];
            uint32_t n, count = previous->m * previous->m * previous->m;
            for (n = 0; n < count; ++n)
                if (!endpoints_at_rgb(m,previous->nodes+3u*n)) break;
            one_hot = n == count;
        }
        temporary.effective_one_hot[s] = (uint8_t)one_hot;
        if (options & JSHC_P_FORCE_GENERIC) temporary.path[s] = JSHC_P_TETRA;
        else if (m->flags & JSHC_P_MODEL_CONSTANT) temporary.path[s] = JSHC_P_CONSTANT;
        else if (m->flags & JSHC_P_MODEL_SEPARABLE) temporary.path[s] = JSHC_P_CURVE;
        else if (one_hot) temporary.path[s] = JSHC_P_VERTEX;
        else temporary.path[s] = JSHC_P_TETRA;
    }
    temporary.options = options; temporary.ready = CHAIN_READY;
    *out = temporary;
    return JSHC_P_OK;
}

static uint32_t vertex(const jshc_p_model *m, const uint8_t rgb[3]) {
    uint32_t i = (uint32_t)m->index[rgb[0]] + (fraction(m,0,rgb[0]) == ONE ? 1u : 0u);
    uint32_t j = (uint32_t)m->index[256u+rgb[1]] + (fraction(m,1,rgb[1]) == ONE ? 1u : 0u);
    uint32_t k = (uint32_t)m->index[512u+rgb[2]] + (fraction(m,2,rgb[2]) == ONE ? 1u : 0u);
    return packed(m->nodes + 3u*((i*m->m+j)*m->m+k));
}

static uint32_t tetra(const jshc_p_model *m, const uint8_t rgb[3]) {
    uint32_t sr = m->m*m->m, sg = m->m, strides[3], f[3], swap;
    uint32_t n = m->index[rgb[0]]*sr + m->index[256u+rgb[1]]*sg + m->index[512u+rgb[2]];
    uint32_t offsets[4], weights[4], result = 0;
    unsigned a, b, c;
    strides[0] = sr; strides[1] = sg; strides[2] = 1;
    for (a = 0; a < 3; ++a) f[a] = fraction(m,a,rgb[a]);
    /* Fractions and strides move together; equal-fraction faces have zero
     * weight on any vertex whose ordering could differ. */
    for (a = 0; a < 2; ++a) for (b = a+1; b < 3; ++b) if (f[b] > f[a]) {
        swap=f[a]; f[a]=f[b]; f[b]=swap;
        swap=strides[a]; strides[a]=strides[b]; strides[b]=swap;
    }
    offsets[0]=n; offsets[1]=n+strides[0]; offsets[2]=n+strides[0]+strides[1]; offsets[3]=n+sr+sg+1;
    weights[0]=ONE-f[0]; weights[1]=f[0]-f[1]; weights[2]=f[1]-f[2]; weights[3]=f[2];
    for (c = 0; c < 3; ++c) {
        uint32_t sum = HALF;
        for (a = 0; a < 4; ++a) sum += weights[a]*m->nodes[3u*offsets[a]+c];
        result |= (sum >> 16) << (8u*c);
    }
    return result;
}

static jshc_p_status image_span(size_t row, size_t stride, size_t height,
                              size_t available, size_t *span) {
    if (stride < row) return JSHC_P_SIZE;
    if (height-1 > (SIZE_MAX-row)/stride) return JSHC_P_OVERFLOW;
    *span = (height-1)*stride+row;
    return available < *span ? JSHC_P_SIZE : JSHC_P_OK;
}

jshc_p_status jshc_p_apply_rgb8(const jshc_p_chain *chain,
    const uint8_t *src, size_t src_bytes, size_t src_stride,
    uint8_t *dst, size_t dst_bytes, size_t dst_stride, size_t width, size_t height) {
    size_t row_bytes, input_span, output_span, y, x;
    jshc_p_status status;
    unsigned s;
    if (!chain) return JSHC_P_NULL;
    if (chain->ready != CHAIN_READY) return JSHC_P_STATE;
    for (s = 0; s < JSHC_P_STAGES; ++s)
        if (!chain->models[s] || chain->models[s]->ready != MODEL_READY || chain->path[s] > JSHC_P_CONSTANT) return JSHC_P_STATE;
    if (!width || !height) return JSHC_P_OK;
    if (!src || !dst) return JSHC_P_NULL;
    if (width > SIZE_MAX/3u) return JSHC_P_OVERFLOW;
    row_bytes=width*3u;
    status=image_span(row_bytes,src_stride,height,src_bytes,&input_span);
    if (status != JSHC_P_OK) return status;
    status=image_span(row_bytes,dst_stride,height,dst_bytes,&output_span);
    if (status != JSHC_P_OK) return status;
    if (!span_valid(src,input_span) || !span_valid(dst,output_span)) return JSHC_P_OVERFLOW;
    if ((src != dst || src_stride != dst_stride) && intersects(src,input_span,dst,output_span)) return JSHC_P_OVERLAP;
    if (intersects(dst,output_span,chain,sizeof(*chain))) return JSHC_P_OVERLAP;
    for (s = 0; s < JSHC_P_STAGES; ++s) {
        const jshc_p_model *m = chain->models[s];
        if (intersects(dst,output_span,m,sizeof(*m)) || intersects(dst,output_span,m->blob,m->blob_bytes)) return JSHC_P_OVERLAP;
    }
    for (y = 0; y < height; ++y) {
        const uint8_t *input = src+y*src_stride;
        uint8_t *output = dst+y*dst_stride;
        for (x = 0; x < width; ++x) {
            uint8_t rgb[3];
            rgb[0]=input[3*x]; rgb[1]=input[3*x+1]; rgb[2]=input[3*x+2];
            for (s = 0; s < JSHC_P_STAGES; ++s) {
                const jshc_p_model *m = chain->models[s];
                uint32_t value;
                if (chain->path[s] == JSHC_P_CONSTANT) value=m->constant_rgb;
                else if (chain->path[s] == JSHC_P_CURVE)
                    value=m->constant_rgb | m->curve[0][rgb[0]] | m->curve[1][rgb[1]] | m->curve[2][rgb[2]];
                else if (chain->path[s] == JSHC_P_VERTEX) value=vertex(m,rgb);
                else value=tetra(m,rgb);
                rgb[0]=(uint8_t)value; rgb[1]=(uint8_t)(value>>8); rgb[2]=(uint8_t)(value>>16);
            }
            output[3*x]=rgb[0]; output[3*x+1]=rgb[1]; output[3*x+2]=rgb[2];
        }
    }
    return JSHC_P_OK;
}
