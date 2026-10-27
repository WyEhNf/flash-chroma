/* flash-chroma：四级 RGB8/Q16 单头 C99 运行库。
 * 在一个翻译单元定义 FC_C_IMPLEMENTATION 后包含本文件以生成实现。
 * 定义 FC_C_STATIC 可生成文件内联接口，适合嵌入独立的 C++ 单头文件。
 * 模型与可选侧表均只读借用；不申请堆、不执行 I/O、浮点或线程操作。
 */
#ifndef FLASH_CHROMA_C_H
#define FLASH_CHROMA_C_H

#include <stddef.h>
#include <stdint.h>

#ifdef FC_C_STATIC
#define FC_C_API static inline
#else
#define FC_C_API extern
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define FC_C_VERSION 1u
#define FC_C_STAGES 4u
#define FC_C_SIDECAR_BYTES 9216u

typedef enum fc_status {
    FC_OK = 0, FC_NULL = 1, FC_FORMAT = 2, FC_SIZE = 3,
    FC_RANGE = 4, FC_OVERFLOW = 5, FC_OVERLAP = 6, FC_STATE = 7
} fc_status;

typedef struct fc_bytes {
    const uint8_t *data;
    size_t size;
} fc_bytes;

/* 由 fc_model_init 初始化；调用者不得修改字段。模型与侧表必须保持有效且不变。
 * SLUT v1 的 idx 由三个输出通道共享；可选 sidecar 是 [通道][轴][RGB码]
 * 排列的 3*3*256 个 little-endian u32 Q16 分数，每项允许 0..65536。
 * 不带 sidecar 时，三个输出使用 SLUT 内相同的三轴分数。
 */
typedef struct fc_model {
    uint32_t ready;
    uint32_t m;
    fc_bytes blob;
    fc_bytes sidecar;
    const uint8_t *index;
    const uint8_t *fraction_le;
    const uint8_t *nodes;
} fc_model;

/* 链恰好包含四个借用模型。可被多任务共享，各任务的可写图像须互不重叠。 */
typedef struct fc_chain {
    uint32_t ready;
    const fc_model *models[FC_C_STAGES];
} fc_chain;

FC_C_API const char *fc_status_string(fc_status status);

/* m 限定 17..33；严格验证格式、完整长度、轴元数据、idx 和全部 Q16。
 * 不存在侧表用 {NULL,0} 表示。允许任意字节对齐与宿主字节序。
 * 失败时不改变 out；out 不得覆盖输入模型或侧表。
 */
FC_C_API fc_status fc_model_init(fc_model *out, fc_bytes blob, fc_bytes sidecar);
FC_C_API fc_status fc_chain_init(fc_chain *out, const fc_model *const models[4]);

/* 低层单像素入口：chain 必须已成功初始化，三个指针须有效。
 * 支持 input==output；output 不得覆盖模型、侧表、视图或链。
 * 每级完整得到三个 RGB8 输出后再进入下一级。
 * 供已验证的内部像素循环或等价派生表准备器使用，不重复检查参数。
 */
FC_C_API void fc_map_pixel(const fc_chain *chain, const uint8_t input[3], uint8_t output[3]);

/* 对每行 width*3 字节执行四级映射，行尾 padding 保持不变。
 * src_bytes/dst_bytes 为从各指针开始可访问的容量，stride 为正向行跨度。
 * 支持精确原地（指针及 stride 相同），其他相交区间拒绝；dst 不得覆盖
 * 链、模型视图、SLUT 或侧表。先完成所有检查，再写入任一像素。
 * 有效链上 width==0 或 height==0 为无操作，此时图像指针允许 NULL。
 */
FC_C_API fc_status fc_apply_rgb8(const fc_chain *chain,
    const uint8_t *src, size_t src_bytes, size_t src_stride,
    uint8_t *dst, size_t dst_bytes, size_t dst_stride,
    size_t width, size_t height);

/* 与 apply 相同的完整参数检查，只读且不执行映射；供已准备的 SIMD 路径复用。 */
FC_C_API fc_status fc_validate_rgb8(const fc_chain *chain,
    const uint8_t *src, size_t src_bytes, size_t src_stride,
    uint8_t *dst, size_t dst_bytes, size_t dst_stride,
    size_t width, size_t height);

#ifdef __cplusplus
}
#endif
#endif

#if defined(FC_C_IMPLEMENTATION) && !defined(FLASH_CHROMA_C_IMPLEMENTED)
#define FLASH_CHROMA_C_IMPLEMENTED

#define FC_DETAIL_MODEL_READY UINT32_C(0x46434d31)
#define FC_DETAIL_CHAIN_READY UINT32_C(0x46434331)

#ifdef __cplusplus
extern "C" {
#endif

static uint32_t fc_detail_read32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static int fc_detail_span_valid(const void *p, size_t bytes)
{
#if SIZE_MAX > UINTPTR_MAX
    if (bytes > UINTPTR_MAX) return 0;
#endif
    return (uintptr_t)p <= UINTPTR_MAX - bytes;
}

/* 两个区间先通过 span_valid，避免端点加法溢出。 */
static int fc_detail_intersects(const void *a, size_t an, const void *b, size_t bn)
{
    return an && bn && (uintptr_t)a < (uintptr_t)b + bn &&
           (uintptr_t)b < (uintptr_t)a + an;
}

/* 按 binary32 位模式比较有限值，无需目标具备浮点运算。 */
static uint32_t fc_detail_float_key(uint32_t bits)
{
    if ((bits & UINT32_C(0x7fffffff)) == 0) bits = 0;
    return bits & UINT32_C(0x80000000) ? ~bits : bits ^ UINT32_C(0x80000000);
}

static int fc_detail_model_valid(const fc_model *m)
{
    return m && fc_detail_span_valid(m, sizeof(*m)) &&
        m->ready == FC_DETAIL_MODEL_READY && m->m >= 17 && m->m <= 33 &&
        m->blob.data && m->index && m->fraction_le && m->nodes &&
        fc_detail_span_valid(m->blob.data, m->blob.size) &&
        ((!m->sidecar.data && !m->sidecar.size) ||
         (m->sidecar.data && m->sidecar.size == FC_C_SIDECAR_BYTES &&
          fc_detail_span_valid(m->sidecar.data, m->sidecar.size)));
}

FC_C_API const char *fc_status_string(fc_status status)
{
    switch (status) {
    case FC_OK: return "成功";
    case FC_NULL: return "空指针参数";
    case FC_FORMAT: return "模型格式无效";
    case FC_SIZE: return "容量或行跨度不符";
    case FC_RANGE: return "模型值越界";
    case FC_OVERFLOW: return "尺寸或地址溢出";
    case FC_OVERLAP: return "不支持的内存重叠";
    case FC_STATE: return "模型或链未初始化";
    default: return "未知状态";
    }
}

FC_C_API fc_status fc_model_init(fc_model *out, fc_bytes blob, fc_bytes sidecar)
{
    fc_model temporary;
    const uint8_t *p = blob.data;
    uint32_t m, a, i;
    size_t expected;
    if (!out || !p || (!sidecar.data && sidecar.size)) return FC_NULL;
    if (!fc_detail_span_valid(out, sizeof(*out)) ||
        !fc_detail_span_valid(p, blob.size) ||
        (sidecar.data && !fc_detail_span_valid(sidecar.data, sidecar.size))) return FC_OVERFLOW;
    if (fc_detail_intersects(out, sizeof(*out), p, blob.size) ||
        fc_detail_intersects(out, sizeof(*out), sidecar.data, sidecar.size)) return FC_OVERLAP;
    if (sidecar.data && sidecar.size != FC_C_SIDECAR_BYTES) return FC_SIZE;
    if (blob.size < 16) return FC_SIZE;
    if (p[0] != 'S' || p[1] != 'L' || p[2] != 'U' || p[3] != 'T' ||
        fc_detail_read32(p + 4) != 1 || fc_detail_read32(p + 12) != 0) return FC_FORMAT;
    m = fc_detail_read32(p + 8);
    if (m < 17 || m > 33) return FC_RANGE;
    expected = 16u + (size_t)12u*m + 3840u + (size_t)3u*m*m*m;
    if (blob.size != expected) return FC_SIZE;
    for (a = 0; a < 3; ++a) {
        uint32_t previous = 0;
        for (i = 0; i < m; ++i) {
            const uint32_t bits = fc_detail_read32(p + 16u + 4u*(a*m + i));
            const uint32_t key = fc_detail_float_key(bits);
            if ((bits & UINT32_C(0x7f800000)) == UINT32_C(0x7f800000) ||
                (i && key <= previous) || (!i && key > UINT32_C(0x80000000)) ||
                (i == m-1 && key < UINT32_C(0xc37f0000))) return FC_FORMAT;
            previous = key;
        }
    }
    temporary.ready = FC_DETAIL_MODEL_READY;
    temporary.m = m;
    temporary.blob = blob;
    temporary.sidecar = sidecar;
    temporary.index = p + 16u + 12u*m;
    temporary.fraction_le = temporary.index + 768u;
    temporary.nodes = temporary.fraction_le + 3072u;
    for (i = 0; i < 768; ++i) {
        if (temporary.index[i] > m-2 ||
            fc_detail_read32(temporary.fraction_le + 4u*i) > 65536u) return FC_RANGE;
    }
    if (sidecar.data) {
        for (i = 0; i < 2304; ++i)
            if (fc_detail_read32(sidecar.data + 4u*i) > 65536u) return FC_RANGE;
    }
    *out = temporary;
    return FC_OK;
}

FC_C_API fc_status fc_chain_init(fc_chain *out, const fc_model *const models[4])
{
    fc_chain temporary;
    unsigned s;
    if (!out || !models) return FC_NULL;
    if (!fc_detail_span_valid(out, sizeof(*out)) ||
        !fc_detail_span_valid(models, 4u*sizeof(*models))) return FC_OVERFLOW;
    if (fc_detail_intersects(out, sizeof(*out), models, 4u*sizeof(*models))) return FC_OVERLAP;
    for (s = 0; s < 4; ++s) {
        const fc_model *m = models[s];
        if (!m) return FC_NULL;
        if (!fc_detail_model_valid(m)) return FC_STATE;
        if (fc_detail_intersects(out, sizeof(*out), m, sizeof(*m)) ||
            fc_detail_intersects(out, sizeof(*out), m->blob.data, m->blob.size) ||
            fc_detail_intersects(out, sizeof(*out), m->sidecar.data, m->sidecar.size)) return FC_OVERLAP;
        temporary.models[s] = m;
    }
    temporary.ready = FC_DETAIL_CHAIN_READY;
    *out = temporary;
    return FC_OK;
}

FC_C_API void fc_map_pixel(const fc_chain *chain, const uint8_t input[3], uint8_t output[3])
{
    uint8_t colour[3];
    unsigned s;
    colour[0] = input[0]; colour[1] = input[1]; colour[2] = input[2];
    for (s = 0; s < 4; ++s) {
        const fc_model *m = chain->models[s];
        const size_t sr = (size_t)m->m*m->m, sg = m->m;
        const size_t base = (size_t)m->index[colour[0]]*sr +
            (size_t)m->index[256u + colour[1]]*sg + m->index[512u + colour[2]];
        uint8_t next[3];
        unsigned c;
        for (c = 0; c < 3; ++c) {
            const uint8_t *f = m->sidecar.data ? m->sidecar.data + (size_t)c*3072u : m->fraction_le;
            uint32_t x = fc_detail_read32(f + (size_t)colour[0]*4u);
            uint32_t y = fc_detail_read32(f + (256u + (size_t)colour[1])*4u);
            uint32_t z = fc_detail_read32(f + (512u + (size_t)colour[2])*4u);
            size_t a = sr, b = sg, d = 1, st;
            uint32_t ft, sum;
            if (x < y) { ft=x; x=y; y=ft; st=a; a=b; b=st; }
            if (y < z) { ft=y; y=z; z=ft; st=b; b=d; d=st; }
            if (x < y) { ft=x; x=y; y=ft; st=a; a=b; b=st; }
            /* 非负重心和为65536，分子加半值小于2^24，u32精确。 */
            sum = (65536u-x)*m->nodes[3u*base+c] +
                (x-y)*m->nodes[3u*(base+a)+c] +
                (y-z)*m->nodes[3u*(base+a+b)+c] +
                z*m->nodes[3u*(base+sr+sg+1u)+c] + 32768u;
            next[c] = (uint8_t)(sum >> 16);
        }
        colour[0]=next[0]; colour[1]=next[1]; colour[2]=next[2];
    }
    output[0]=colour[0]; output[1]=colour[1]; output[2]=colour[2];
}

static fc_status fc_detail_image_span(size_t row, size_t stride, size_t height,
                                     size_t capacity, size_t *span)
{
    if (stride < row) return FC_SIZE;
    if (height-1u > (SIZE_MAX-row)/stride) return FC_OVERFLOW;
    *span = (height-1u)*stride + row;
    return capacity < *span ? FC_SIZE : FC_OK;
}

FC_C_API fc_status fc_validate_rgb8(const fc_chain *chain,
    const uint8_t *src, size_t src_bytes, size_t src_stride,
    uint8_t *dst, size_t dst_bytes, size_t dst_stride, size_t width, size_t height)
{
    size_t row, input_span, output_span;
    fc_status status;
    unsigned s;
    if (!chain) return FC_NULL;
    if (!fc_detail_span_valid(chain, sizeof(*chain))) return FC_OVERFLOW;
    if (chain->ready != FC_DETAIL_CHAIN_READY) return FC_STATE;
    for (s = 0; s < 4; ++s)
        if (!fc_detail_model_valid(chain->models[s])) return FC_STATE;
    if (!width || !height) return FC_OK;
    if (!src || !dst) return FC_NULL;
    if (width > SIZE_MAX/3u) return FC_OVERFLOW;
    row = width*3u;
    status = fc_detail_image_span(row, src_stride, height, src_bytes, &input_span);
    if (status != FC_OK) return status;
    status = fc_detail_image_span(row, dst_stride, height, dst_bytes, &output_span);
    if (status != FC_OK) return status;
    if (!fc_detail_span_valid(src, input_span) || !fc_detail_span_valid(dst, output_span)) return FC_OVERFLOW;
    if ((src != dst || src_stride != dst_stride) &&
        fc_detail_intersects(src, input_span, dst, output_span)) return FC_OVERLAP;
    if (fc_detail_intersects(dst, output_span, chain, sizeof(*chain))) return FC_OVERLAP;
    for (s = 0; s < 4; ++s) {
        const fc_model *m = chain->models[s];
        if (fc_detail_intersects(dst, output_span, m, sizeof(*m)) ||
            fc_detail_intersects(dst, output_span, m->blob.data, m->blob.size) ||
            fc_detail_intersects(dst, output_span, m->sidecar.data, m->sidecar.size)) return FC_OVERLAP;
    }
    return FC_OK;
}

FC_C_API fc_status fc_apply_rgb8(const fc_chain *chain,
    const uint8_t *src, size_t src_bytes, size_t src_stride,
    uint8_t *dst, size_t dst_bytes, size_t dst_stride, size_t width, size_t height)
{
    size_t y, x;
    const fc_status status=fc_validate_rgb8(chain,src,src_bytes,src_stride,dst,dst_bytes,dst_stride,width,height);
    if (status!=FC_OK || !width || !height) return status;
    for (y = 0; y < height; ++y) {
        const uint8_t *input = src+y*src_stride;
        uint8_t *output = dst+y*dst_stride;
        for (x = 0; x < width; ++x) fc_map_pixel(chain, input+3u*x, output+3u*x);
    }
    return FC_OK;
}

#ifdef __cplusplus
}
#endif
#endif
