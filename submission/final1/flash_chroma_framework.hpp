// 来源：final_pipeline.hpp
// final1：既有前中层精度算法与既有Direct运行内核的组合；不读取图像进行准备。
#ifndef ZMX_FINAL1_PIPELINE_HPP
#define ZMX_FINAL1_PIPELINE_HPP
// 来源：candidate.hpp
/* 前中层真实整数搜索与末层重拟合；预算预先固定，输入只包含原 LUT。 */
#ifndef ZMX_PREFIX_JOINT_CANDIDATE_HPP
#define ZMX_PREFIX_JOINT_CANDIDATE_HPP
// 来源：precision_pipeline.hpp
/* 有界历史能力迁移：候选在读图前确定，所有接收判定基于原四LUT完整域。 */
#ifndef FLASH_CHROMA_FRAMEWORK_PRECISION_PIPELINE_HPP
#define FLASH_CHROMA_FRAMEWORK_PRECISION_PIPELINE_HPP
// 来源：precision_fit.hpp
/* 完整LUT联合质量加权的box-QP、Lp IRLS与尾部再加权。 */
#ifndef FLASH_CHROMA_FRAMEWORK_PRECISION_FIT_HPP
#define FLASH_CHROMA_FRAMEWORK_PRECISION_FIT_HPP
// 来源：precision_search.hpp
/* 完整LUT域的联合支撑、真实整数后缀重放与固定锚点门控；不接受照片频数。 */
#ifndef FLASH_CHROMA_FRAMEWORK_PRECISION_SEARCH_HPP
#define FLASH_CHROMA_FRAMEWORK_PRECISION_SEARCH_HPP
// 来源：precision_geometry.hpp
/* 历史非均匀轴及分输出几何的LUT-only原生入口。所有预算在读图前固定。 */
#ifndef FLASH_CHROMA_FRAMEWORK_PRECISION_GEOMETRY_HPP
#define FLASH_CHROMA_FRAMEWORK_PRECISION_GEOMETRY_HPP
// 来源：fit_chain_experiment.hpp
// 完整RGB域链拟合：固定前三层，以原始四层链输出拟合第四层。
#ifndef FLASH_CHROMA_FRAMEWORK_FIT_CHAIN_EXPERIMENT_HPP
#define FLASH_CHROMA_FRAMEWORK_FIT_CHAIN_EXPERIMENT_HPP
// 来源：fit_experiment.hpp
/* 图像无关的完整RGB域Q16四面体最小二乘实验。
 * 只修改Stage的m³节点；轴表、执行库及精确曲线证明保持原样。
 * 此文件目前是独立候选，不自动替换比赛适配器的采样路径。
 */
#ifndef FLASH_CHROMA_FRAMEWORK_FIT_EXPERIMENT_HPP
#define FLASH_CHROMA_FRAMEWORK_FIT_EXPERIMENT_HPP
// 来源：flash_chroma_adapter.hpp
/* 比赛框架的单线程适配：只用原始LUT做准备，不读取任何图像。
 * 一个翻译单元须在包含本文件前定义FLASH_CHROMA_IMPLEMENTATION。
 * Stage在Chain使用期间必须保持有效、地址稳定且内容不变。
 */
#ifndef FLASH_CHROMA_FRAMEWORK_ADAPTER_HPP
#define FLASH_CHROMA_FRAMEWORK_ADAPTER_HPP

#if defined(FLASH_CHROMA_ENABLE_OPENMP) && FLASH_CHROMA_ENABLE_OPENMP
#error "比赛框架禁止多线程；本适配不得启用OpenMP"
#endif
#ifndef FLASH_CHROMA_ENABLE_OPENMP
#define FLASH_CHROMA_ENABLE_OPENMP 0
#endif
// 来源：flash_chroma.hpp
/* 独立C++17单头；维护时由同源标量核心及src片段生成，部署不依赖.c/.h或生成脚本。 */
#ifndef FLASH_CHROMA_HPP
#define FLASH_CHROMA_HPP
#if !defined(__cplusplus) || __cplusplus < 201703L
#error "flash_chroma.hpp 要求 C++17"
#endif
#include <stddef.h>
#include <stdint.h>
#define FC_CPP_CORE_STATIC
#define FC_CPP_CORE_IMPLEMENTATION
namespace fc_core {
/* flash-chroma：四级 RGB8/Q16 C++内部标量核心，与独立C99头共享数值语义。
 * 在一个翻译单元定义 FC_CPP_CORE_IMPLEMENTATION 后包含本文件以生成实现。
 * 定义 FC_CPP_CORE_STATIC 可生成文件内联接口，适合嵌入独立的 C++ 单头文件。
 * 模型与可选侧表均只读借用；不申请堆、不执行 I/O、浮点或线程操作。
 */
#ifndef FLASH_CHROMA_CPP_C_CORE_H
#define FLASH_CHROMA_CPP_C_CORE_H

#include <stddef.h>
#include <stdint.h>

#ifdef FC_CPP_CORE_STATIC
#define FC_CPP_CORE_API static inline
#else
#define FC_CPP_CORE_API extern
#endif



#define FC_CPP_CORE_VERSION 1u
#define FC_CPP_CORE_STAGES 4u
#define FC_CPP_CORE_SIDECAR_BYTES 9216u

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
    const fc_model *models[FC_CPP_CORE_STAGES];
} fc_chain;

FC_CPP_CORE_API const char *fc_status_string(fc_status status);

/* m 限定 17..33；严格验证格式、完整长度、轴元数据、idx 和全部 Q16。
 * 不存在侧表用 {NULL,0} 表示。允许任意字节对齐与宿主字节序。
 * 失败时不改变 out；out 不得覆盖输入模型或侧表。
 */
FC_CPP_CORE_API fc_status fc_model_init(fc_model *out, fc_bytes blob, fc_bytes sidecar);
FC_CPP_CORE_API fc_status fc_chain_init(fc_chain *out, const fc_model *const models[4]);

/* 低层单像素入口：chain 必须已成功初始化，三个指针须有效。
 * 支持 input==output；output 不得覆盖模型、侧表、视图或链。
 * 每级完整得到三个 RGB8 输出后再进入下一级。
 * 供已验证的内部像素循环或等价派生表准备器使用，不重复检查参数。
 */
FC_CPP_CORE_API void fc_map_pixel(const fc_chain *chain, const uint8_t input[3], uint8_t output[3]);

/* 对每行 width*3 字节执行四级映射，行尾 padding 保持不变。
 * src_bytes/dst_bytes 为从各指针开始可访问的容量，stride 为正向行跨度。
 * 支持精确原地（指针及 stride 相同），其他相交区间拒绝；dst 不得覆盖
 * 链、模型视图、SLUT 或侧表。先完成所有检查，再写入任一像素。
 * 有效链上 width==0 或 height==0 为无操作，此时图像指针允许 NULL。
 */
FC_CPP_CORE_API fc_status fc_apply_rgb8(const fc_chain *chain,
    const uint8_t *src, size_t src_bytes, size_t src_stride,
    uint8_t *dst, size_t dst_bytes, size_t dst_stride,
    size_t width, size_t height);

/* 与 apply 相同的完整参数检查，只读且不执行映射；供已准备的 SIMD 路径复用。 */
FC_CPP_CORE_API fc_status fc_validate_rgb8(const fc_chain *chain,
    const uint8_t *src, size_t src_bytes, size_t src_stride,
    uint8_t *dst, size_t dst_bytes, size_t dst_stride,
    size_t width, size_t height);


#endif

#if defined(FC_CPP_CORE_IMPLEMENTATION) && !defined(FLASH_CHROMA_CPP_C_CORE_IMPLEMENTED)
#define FLASH_CHROMA_CPP_C_CORE_IMPLEMENTED

#define FC_CPP_DETAIL_MODEL_READY UINT32_C(0x46434d31)
#define FC_CPP_DETAIL_CHAIN_READY UINT32_C(0x46434331)



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
        m->ready == FC_CPP_DETAIL_MODEL_READY && m->m >= 17 && m->m <= 33 &&
        m->blob.data && m->index && m->fraction_le && m->nodes &&
        fc_detail_span_valid(m->blob.data, m->blob.size) &&
        ((!m->sidecar.data && !m->sidecar.size) ||
         (m->sidecar.data && m->sidecar.size == FC_CPP_CORE_SIDECAR_BYTES &&
          fc_detail_span_valid(m->sidecar.data, m->sidecar.size)));
}

FC_CPP_CORE_API const char *fc_status_string(fc_status status)
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

FC_CPP_CORE_API fc_status fc_model_init(fc_model *out, fc_bytes blob, fc_bytes sidecar)
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
    if (sidecar.data && sidecar.size != FC_CPP_CORE_SIDECAR_BYTES) return FC_SIZE;
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
    temporary.ready = FC_CPP_DETAIL_MODEL_READY;
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

FC_CPP_CORE_API fc_status fc_chain_init(fc_chain *out, const fc_model *const models[4])
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
    temporary.ready = FC_CPP_DETAIL_CHAIN_READY;
    *out = temporary;
    return FC_OK;
}

FC_CPP_CORE_API void fc_map_pixel(const fc_chain *chain, const uint8_t input[3], uint8_t output[3])
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

FC_CPP_CORE_API fc_status fc_validate_rgb8(const fc_chain *chain,
    const uint8_t *src, size_t src_bytes, size_t src_stride,
    uint8_t *dst, size_t dst_bytes, size_t dst_stride, size_t width, size_t height)
{
    size_t row, input_span, output_span;
    fc_status status;
    unsigned s;
    if (!chain) return FC_NULL;
    if (!fc_detail_span_valid(chain, sizeof(*chain))) return FC_OVERFLOW;
    if (chain->ready != FC_CPP_DETAIL_CHAIN_READY) return FC_STATE;
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

FC_CPP_CORE_API fc_status fc_apply_rgb8(const fc_chain *chain,
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


#endif

}
#undef FC_CPP_CORE_IMPLEMENTATION
#undef FC_CPP_CORE_STATIC
#undef FC_CPP_CORE_API
/* C++17 部分；由 generate_flash_chroma_header.py 与同源 C 核合并交付。
 * 图像、源模型和工作区均由调用者持有，初始化后映射不申请内存。
 */
#ifndef FLASH_CHROMA_CPP_API
#define FLASH_CHROMA_CPP_API
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>

#define FLASH_CHROMA_TARGET_DESKTOP 1
#define FLASH_CHROMA_TARGET_MOBILE 2
#define FLASH_CHROMA_TARGET_EMBEDDED 3
#define FLASH_CHROMA_TARGET_PORTABLE 4
#if (defined(__STDC_HOSTED__) && __STDC_HOSTED__ == 0) || \
    ((defined(__arm__) || defined(__aarch64__) || defined(__riscv)) && \
     !defined(__linux__) && !defined(__ANDROID__) && !defined(__APPLE__) && !defined(_WIN32) && !defined(__unix__))
#define FC_DETECTED_EMBEDDED 1
#else
#define FC_DETECTED_EMBEDDED 0
#endif
#ifndef FLASH_CHROMA_TARGET
#if defined(FLASH_CHROMA_EMBEDDED)
#if FLASH_CHROMA_EMBEDDED
#define FLASH_CHROMA_TARGET FLASH_CHROMA_TARGET_EMBEDDED
#else
#define FLASH_CHROMA_TARGET FLASH_CHROMA_TARGET_DESKTOP
#endif
#elif FC_DETECTED_EMBEDDED
#define FLASH_CHROMA_TARGET FLASH_CHROMA_TARGET_EMBEDDED
#elif defined(__ANDROID__)
#define FLASH_CHROMA_TARGET FLASH_CHROMA_TARGET_MOBILE
#else
#define FLASH_CHROMA_TARGET FLASH_CHROMA_TARGET_DESKTOP
#endif
#endif
#if FLASH_CHROMA_TARGET < 1 || FLASH_CHROMA_TARGET > 4
#error "FLASH_CHROMA_TARGET 必须是支持的部署目标"
#endif
#ifndef FLASH_CHROMA_EMBEDDED
#define FLASH_CHROMA_EMBEDDED (FLASH_CHROMA_TARGET == FLASH_CHROMA_TARGET_EMBEDDED)
#endif
#if (FLASH_CHROMA_EMBEDDED != 0 && FLASH_CHROMA_EMBEDDED != 1)
#error "FLASH_CHROMA_EMBEDDED 必须为0或1"
#endif
#if FLASH_CHROMA_EMBEDDED != (FLASH_CHROMA_TARGET == FLASH_CHROMA_TARGET_EMBEDDED)
#error "FLASH_CHROMA_EMBEDDED 与 FLASH_CHROMA_TARGET 冲突"
#endif
#ifndef FLASH_CHROMA_ENABLE_DIRECT
#define FLASH_CHROMA_ENABLE_DIRECT (FLASH_CHROMA_TARGET <= 2)
#endif
#ifndef FLASH_CHROMA_ENABLE_AVX2
#if (defined(__GNUC__) || defined(__clang__)) && (defined(__x86_64__) || defined(__i386__)) && FLASH_CHROMA_TARGET <= 2
#define FLASH_CHROMA_ENABLE_AVX2 1
#else
#define FLASH_CHROMA_ENABLE_AVX2 0
#endif
#endif
#ifndef FLASH_CHROMA_ENABLE_OPENMP
#if defined(_OPENMP) && FLASH_CHROMA_TARGET <= 2
#define FLASH_CHROMA_ENABLE_OPENMP 1
#else
#define FLASH_CHROMA_ENABLE_OPENMP 0
#endif
#endif
#ifndef FLASH_CHROMA_ENABLE_PREPARE_CACHE
#define FLASH_CHROMA_ENABLE_PREPARE_CACHE (FLASH_CHROMA_ENABLE_DIRECT && FLASH_CHROMA_ENABLE_AVX2)
#endif
#if FLASH_CHROMA_EMBEDDED && (FLASH_CHROMA_ENABLE_DIRECT || FLASH_CHROMA_ENABLE_AVX2 || FLASH_CHROMA_ENABLE_OPENMP || FLASH_CHROMA_ENABLE_PREPARE_CACHE)
#error "嵌入式模式必须关闭direct、AVX2、OpenMP和准备缓存"
#endif
#if FLASH_CHROMA_ENABLE_PREPARE_CACHE && (!FLASH_CHROMA_ENABLE_DIRECT || !FLASH_CHROMA_ENABLE_AVX2)
#error "准备缓存快路径需要direct与AVX2；可关闭FLASH_CHROMA_ENABLE_PREPARE_CACHE"
#endif
#if FLASH_CHROMA_ENABLE_OPENMP && !defined(_OPENMP)
#error "启用 OpenMP 需由编译器提供 _OPENMP"
#endif
#if FLASH_CHROMA_ENABLE_AVX2
#if !(defined(__GNUC__) || defined(__clang__)) || !(defined(__x86_64__) || defined(__i386__))
#error "当前单头 AVX2 隔离只支持 x86 GCC/Clang；其他组合请关闭该后端"
#endif
#include <immintrin.h>
#include <cpuid.h>
#define FC_AVX2 __attribute__((target("avx2")))
#endif
#if FLASH_CHROMA_ENABLE_OPENMP
#include <omp.h>
#endif

namespace fc {
// 默认识别编译目标，显式配置可覆盖；具体指令集还须经CPU及OS运行时探测。
constexpr bool is_embedded() noexcept { return FLASH_CHROMA_EMBEDDED != 0; }
using Bytes = fc_core::fc_bytes;
constexpr std::size_t MiB = std::size_t{1024} * 1024;
enum class Status : unsigned {
    Ok=0, Null=1, Format=2, Size=3, Range=4, Overflow=5, Overlap=6, State=7,
    Unsupported=8, Budget=9, Capacity=10
};
enum class Target : unsigned { Desktop=1, Mobile=2, Embedded=3, Portable=4 };
enum class Backend : unsigned { Auto=0, Scalar=1, Avx2=2, Avx512=8 };
enum class Representation : unsigned { Sparse=0, DirectU8=1, DirectU16=2, DirectRGB24=3 };
struct RuntimeConfig {
    Target target = static_cast<Target>(FLASH_CHROMA_TARGET);
    Backend backend = Backend::Auto;
    Representation representation = Representation::Sparse;
    unsigned threads = 1;
    std::size_t block_pixels = 65536;
    std::size_t max_workspace_bytes = (std::numeric_limits<std::size_t>::max)();
};
struct ModelBundle { Bytes models[4]{}; Bytes sidecars[4]{}; };
struct Workspace { void* data=nullptr; std::size_t bytes=0; };
/* arena 包含 63B 最坏对齐余量；model_bytes 是借用源模型总长。
 * object_bytes 是 Runtime 对象，不含调用者图像、OS 线程栈或 OpenMP 运行库。
 * temporary 是准备时借用的 arena 尾段，prepare 后可由调用者释放该尾段。
 */
struct Requirements {
    std::size_t persistent_bytes=0, temporary_bytes=0, arena_bytes=0;
    std::size_t model_bytes=0, alignment=64, object_bytes=0;
};
std::uint32_t compiled_capabilities() noexcept;
std::uint32_t available_backends() noexcept;
const char* status_string(Status) noexcept;

namespace detail {
// 纯特性门控也供合同验证；不能仅凭CPU型号或AVX2位执行YMM指令。
constexpr bool avx2_state_supported(std::uint32_t cpuid1_ecx, std::uint32_t xcr0,
                                     std::uint32_t leaf7_ebx) noexcept {
    constexpr std::uint32_t prerequisite = (1u << 26) | (1u << 27) | (1u << 28);
    return (cpuid1_ecx & prerequisite) == prerequisite && (xcr0 & 6u) == 6u &&
           (leaf7_ebx & (1u << 5)) != 0;
}
struct PackedView {
    const std::uint32_t* axes[3][3]{};
    const std::uint32_t* nodes=nullptr;
    std::int32_t sr=0, sg=0;
    bool shared=true;
};
}

class Runtime {
public:
    Runtime() noexcept = default;
    Runtime(const Runtime&) = delete;
    Runtime& operator=(const Runtime&) = delete;
    Runtime(Runtime&&) = delete;
    Runtime& operator=(Runtime&&) = delete;
    static Status requirements(const ModelBundle&, const RuntimeConfig&, Requirements*) noexcept;
    static Status prepare(const ModelBundle&, const RuntimeConfig&, Workspace, Runtime*) noexcept;
    /* 借用与bundle四级整数输出逐字节对应的预计算RGB24表（含4B零guard）。
     * 调用者保证来源对应性、不可变性与生命周期；此接口验证格式/容量/别名，
     * 不再次遍历色域重算。用于已完整评估的拟合输出直接发布。 */
    static Status prepare_precomputed_rgb24(const ModelBundle&, const RuntimeConfig&, Bytes, Runtime*) noexcept;
    Status apply(const std::uint8_t*, std::size_t, std::size_t,
                 std::uint8_t*, std::size_t, std::size_t, std::size_t, std::size_t) const noexcept;
    const RuntimeConfig& config() const noexcept { return config_; }
    const Requirements& resources() const noexcept { return resources_; }
    Backend selected_backend() const noexcept { return backend_; }
    std::uint32_t palette_entries() const noexcept { return palette_count_; }
    bool prepared_with_suffix_cache() const noexcept { return prepared_cache_; }
    std::size_t preparation_cache_entries() const noexcept { return prepared_cache_entries_; }
    bool ready() const noexcept { return ready_; }
private:
    RuntimeConfig config_{};
    Requirements resources_{};
    Backend backend_=Backend::Scalar;
    fc_core::fc_model models_[4]{};
    fc_core::fc_chain chain_{};
#if FLASH_CHROMA_ENABLE_AVX2
    detail::PackedView packed_[4]{};
#endif
    const std::uint8_t* direct_=nullptr;
    const std::uint32_t* palette_=nullptr;
    std::uint32_t palette_count_=0;
    const std::uint8_t* arena_=nullptr;
    std::size_t prepared_cache_entries_=0;
    bool prepared_cache_=false;
    bool ready_=false;
};
}
#endif

#if defined(FLASH_CHROMA_IMPLEMENTATION) && !defined(FLASH_CHROMA_CPP_IMPLEMENTED)
#define FLASH_CHROMA_CPP_IMPLEMENTED
namespace fc {
namespace detail {
constexpr std::size_t colours = std::size_t{1} << 24;
inline std::size_t aligned(std::size_t n) noexcept { return (n+63u)&~std::size_t{63}; }
inline bool add(std::size_t& value,std::size_t n) noexcept {
    if(value > (std::numeric_limits<std::size_t>::max)()-n)return false;
    value+=n;return true;
}
inline std::uint32_t read32(const std::uint8_t* p) noexcept {
    return std::uint32_t(p[0])|(std::uint32_t(p[1])<<8)|(std::uint32_t(p[2])<<16)|(std::uint32_t(p[3])<<24);
}
inline std::uint32_t rgb32(const std::uint8_t* p) noexcept {
    return std::uint32_t(p[0])|(std::uint32_t(p[1])<<8)|(std::uint32_t(p[2])<<16);
}
inline void store_rgb(std::uint8_t* p,std::uint32_t v) noexcept {
    p[0]=std::uint8_t(v);p[1]=std::uint8_t(v>>8);p[2]=std::uint8_t(v>>16);
}
#if FLASH_CHROMA_ENABLE_AVX2
inline std::size_t packed_bytes(const fc_core::fc_model (&models)[4]) noexcept {
    std::size_t bytes=0;
    for(const auto& m:models)bytes+=aligned(std::size_t(m.m)*m.m*m.m*4)+aligned(m.sidecar.data?9216:3072);
    return bytes;
}
inline void pack_views(const fc_core::fc_model (&models)[4], std::uint8_t* p,PackedView* views) noexcept {
    for(unsigned s=0;s<4;++s) {
        const auto& m=models[s];auto& v=views[s];const std::size_t count=std::size_t(m.m)*m.m*m.m;
        auto* nodes=reinterpret_cast<std::uint32_t*>(p);p+=aligned(count*4);
        for(std::size_t i=0;i<count;++i)nodes[i]=rgb32(m.nodes+i*3);
        v.nodes=nodes;v.sr=std::int32_t(m.m*m.m);v.sg=std::int32_t(m.m);v.shared=!m.sidecar.data;
        auto* axes=reinterpret_cast<std::uint32_t*>(p);p+=aligned(v.shared?3072:9216);
        for(unsigned c=0;c<(v.shared?1u:3u);++c)for(unsigned a=0;a<3;++a)for(unsigned i=0;i<256;++i) {
            const auto* fraction=m.sidecar.data?m.sidecar.data+(c*768+a*256+i)*4:m.fraction_le+(a*256+i)*4;
            axes[c*768+a*256+i]=(std::uint32_t(m.index[a*256+i])<<17)|read32(fraction);
        }
        for(unsigned c=0;c<3;++c)for(unsigned a=0;a<3;++a)v.axes[c][a]=axes+(v.shared?0:c*768)+a*256;
    }
}
#endif
inline Status resolve(const RuntimeConfig& c,Backend* backend) noexcept {
    const unsigned target=static_cast<unsigned>(c.target);
    const unsigned rep=static_cast<unsigned>(c.representation);
    if(target<1||target>4||rep>3||!c.threads||c.threads>256||!c.block_pixels)return Status::Range;
    if(c.block_pixels>(std::numeric_limits<std::size_t>::max)()/3)return Status::Overflow;
    if((FLASH_CHROMA_TARGET>=3 && target<=2) ||
       (target>=3 && (rep!=0||c.threads!=1|| (c.backend!=Backend::Scalar&&c.backend!=Backend::Auto))))return Status::Unsupported;
#if !FLASH_CHROMA_ENABLE_DIRECT
    if(rep)return Status::Unsupported;
#endif
#if !FLASH_CHROMA_ENABLE_OPENMP
    if(c.threads!=1)return Status::Unsupported;
#endif
    Backend selected=c.backend;
    if(selected==Backend::Auto)selected=(target<=2&&(available_backends()&2))?Backend::Avx2:Backend::Scalar;
    if(selected!=Backend::Scalar&&selected!=Backend::Avx2)return Status::Unsupported;
    if(selected==Backend::Avx2&&!(available_backends()&2))return Status::Unsupported;
    *backend=selected;return Status::Ok;
}

#if FLASH_CHROMA_ENABLE_AVX2
struct Rgb { __m256i r,g,b; };
FC_AVX2 inline void load8(const std::uint8_t* p,Rgb& rgb) noexcept {
    const __m128i lo=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
    const __m128i last=_mm_loadl_epi64(reinterpret_cast<const __m128i*>(p+16));
    const __m128i hi=_mm_alignr_epi8(last,lo,12);
    const __m256i raw=_mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
    const __m256i shuffle=_mm256_setr_epi8(0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1,0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1);
    const __m256i packed=_mm256_shuffle_epi8(raw,shuffle), mask=_mm256_set1_epi32(255);
    rgb.r=_mm256_and_si256(packed,mask);rgb.g=_mm256_and_si256(_mm256_srli_epi32(packed,8),mask);rgb.b=_mm256_srli_epi32(packed,16);
}
FC_AVX2 inline void store8(std::uint8_t* p,const Rgb& rgb) noexcept {
    const __m256i packed=_mm256_or_si256(rgb.r,_mm256_or_si256(_mm256_slli_epi32(rgb.g,8),_mm256_slli_epi32(rgb.b,16)));
    const __m256i shuffle=_mm256_setr_epi8(0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1);
    const __m256i bytes=_mm256_shuffle_epi8(packed,shuffle);
    const __m128i lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
    _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(hi,4));
}
FC_AVX2 inline __m256i gather(const std::uint32_t* data,const __m256i& index) noexcept {
    return _mm256_i32gather_epi32(reinterpret_cast<const int*>(data),index,4);
}
template<int C>
FC_AVX2 inline __m256i interpolate(const __m256i& v0,const __m256i& v1,const __m256i& v2,const __m256i& v3,
    const __m256i& x,const __m256i& y,const __m256i& z) noexcept {
    const __m256i mask=_mm256_set1_epi32(255);
    const __m256i n0=_mm256_and_si256(_mm256_srli_epi32(v0,8*C),mask),n1=_mm256_and_si256(_mm256_srli_epi32(v1,8*C),mask);
    const __m256i n2=_mm256_and_si256(_mm256_srli_epi32(v2,8*C),mask),n3=_mm256_and_si256(_mm256_srli_epi32(v3,8*C),mask);
    const __m256i acc=_mm256_add_epi32(_mm256_slli_epi32(n0,16),_mm256_add_epi32(
      _mm256_mullo_epi32(_mm256_sub_epi32(n1,n0),x),_mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(n2,n1),y),_mm256_mullo_epi32(_mm256_sub_epi32(n3,n2),z))));
    return _mm256_srli_epi32(_mm256_add_epi32(acc,_mm256_set1_epi32(32768)),16);
}
FC_AVX2 inline void geometry(const PackedView& v,const __m256i& x,const __m256i& y,const __m256i& z,
    __m256i& high,__m256i& middle,__m256i& low,__m256i& first,__m256i& last) noexcept {
    const __m256i sr=_mm256_set1_epi32(v.sr),sg=_mm256_set1_epi32(v.sg),one=_mm256_set1_epi32(1);
    first=_mm256_blendv_epi8(sr,sg,_mm256_cmpgt_epi32(y,x));high=_mm256_max_epi32(x,y);
    first=_mm256_blendv_epi8(first,one,_mm256_cmpgt_epi32(z,high));high=_mm256_max_epi32(high,z);
    last=_mm256_blendv_epi8(sr,sg,_mm256_cmpgt_epi32(x,y));low=_mm256_min_epi32(x,y);
    last=_mm256_blendv_epi8(last,one,_mm256_cmpgt_epi32(low,z));low=_mm256_min_epi32(low,z);
    middle=_mm256_sub_epi32(_mm256_add_epi32(_mm256_add_epi32(x,y),z),_mm256_add_epi32(high,low));
}
template<int C>
FC_AVX2 inline __m256i channel(const PackedView& v,const __m256i& base,const __m256i& n0,const __m256i& n3,
    const __m256i& x,const __m256i& y,const __m256i& z) noexcept {
    __m256i high,middle,low,first,last;geometry(v,x,y,z,high,middle,low,first,last);
    const __m256i n1=gather(v.nodes,_mm256_add_epi32(base,first));
    const __m256i n2=gather(v.nodes,_mm256_add_epi32(base,_mm256_sub_epi32(_mm256_set1_epi32(v.sr+v.sg+1),last)));
    return interpolate<C>(n0,n1,n2,n3,high,middle,low);
}
FC_AVX2 inline void transform(const PackedView& v,Rgb& rgb) noexcept {
    const __m256i ar=gather(v.axes[0][0],rgb.r),ag=gather(v.axes[0][1],rgb.g),ab=gather(v.axes[0][2],rgb.b);
    const __m256i base=_mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ar,17),_mm256_set1_epi32(v.sr)),
      _mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ag,17),_mm256_set1_epi32(v.sg)),_mm256_srli_epi32(ab,17)));
    const __m256i mask=_mm256_set1_epi32(0x1ffff),x=_mm256_and_si256(ar,mask),y=_mm256_and_si256(ag,mask),z=_mm256_and_si256(ab,mask);
    const __m256i n0=gather(v.nodes,base),n3=gather(v.nodes,_mm256_add_epi32(base,_mm256_set1_epi32(v.sr+v.sg+1)));
    if(v.shared) {
        __m256i high,middle,low,first,last;geometry(v,x,y,z,high,middle,low,first,last);
        const __m256i n1=gather(v.nodes,_mm256_add_epi32(base,first));
        const __m256i n2=gather(v.nodes,_mm256_add_epi32(base,_mm256_sub_epi32(_mm256_set1_epi32(v.sr+v.sg+1),last)));
        rgb.r=interpolate<0>(n0,n1,n2,n3,high,middle,low);rgb.g=interpolate<1>(n0,n1,n2,n3,high,middle,low);rgb.b=interpolate<2>(n0,n1,n2,n3,high,middle,low);return;
    }
    const __m256i r=channel<0>(v,base,n0,n3,x,y,z);
    const __m256i g=channel<1>(v,base,n0,n3,_mm256_and_si256(gather(v.axes[1][0],rgb.r),mask),_mm256_and_si256(gather(v.axes[1][1],rgb.g),mask),_mm256_and_si256(gather(v.axes[1][2],rgb.b),mask));
    const __m256i b=channel<2>(v,base,n0,n3,_mm256_and_si256(gather(v.axes[2][0],rgb.r),mask),_mm256_and_si256(gather(v.axes[2][1],rgb.g),mask),_mm256_and_si256(gather(v.axes[2][2],rgb.b),mask));
    rgb.r=r;rgb.g=g;rgb.b=b;
}
FC_AVX2 inline void sparse8(const PackedView* views,const std::uint8_t* src,std::uint8_t* dst,std::size_t n) noexcept {
    for(std::size_t i=0;i<n;i+=8) {Rgb rgb;load8(src+3*i,rgb);for(unsigned s=0;s<4;++s)transform(views[s],rgb);store8(dst+3*i,rgb);}
}
#if FLASH_CHROMA_ENABLE_DIRECT
/* 精确 direct 热核：从成熟 adaptive-linear 路径迁移的标量 ILP 查表与 AVX2 打包。
 * 本片段由生成器嵌入 fc::detail；调用者先检查 AVX2，输入/输出只能同址或分离。
 * U8/U16 表不要求 guard；RGB24 沿用原有的四字节尾部容量契约。
 * 基础路径不依赖 BMI；可选强目标函数由每块一次的 CPU 能力检测保护。
 * 不申请堆，不使用可变全局状态，也不改变任何模型或四级整数结果。
 */

template<bool Wide>
inline std::uint32_t direct_palette_id(const std::uint8_t* table,std::uint32_t code) noexcept {
    if constexpr(Wide)return reinterpret_cast<const std::uint16_t*>(table)[code];
    else return table[code];
}

template<bool Wide>
inline std::uint32_t direct_palette_value(const std::uint8_t* table,
    const std::uint32_t* palette,std::uint32_t code) noexcept {
    return palette[direct_palette_id<Wide>(table,code)];
}

/* 仅宽循环使用；第四字节只用于机器读取，随后掩掉，不参与颜色地址。 */
inline std::uint32_t direct_code_wide(const std::uint8_t* p) noexcept {
    std::uint32_t value;std::memcpy(&value,p,4);return value&0xffffffu;
}

/* 精确读取八个像素的24B，不依赖下一个像素或图像 padding。 */
template<bool Wide>
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_read_exact(
    const std::uint8_t* table,const std::uint32_t* palette,const std::uint8_t* p) noexcept {
    std::uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
    return _mm256_setr_epi32(
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t(a&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t((a>>24)&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t(((a>>48)|(b<<16))&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t((b>>8)&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t((b>>32)&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t(((b>>56)|(c<<8))&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t((c>>16)&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t(c>>40))));
}

/* 八路ID读取按两组提前发出；其后再读取小调色板，保留成熟内核的ILP组织。 */
template<bool Wide>
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_read_wide(
    const std::uint8_t* table,const std::uint32_t* palette,const std::uint8_t* p) noexcept {
    const auto i0=direct_palette_id<Wide>(table,direct_code_wide(p));
    const auto i1=direct_palette_id<Wide>(table,direct_code_wide(p+3));
    const auto i2=direct_palette_id<Wide>(table,direct_code_wide(p+6));
    const auto i3=direct_palette_id<Wide>(table,direct_code_wide(p+9));
    __asm__ volatile("" : : "r"(i0),"r"(i1),"r"(i2),"r"(i3) : "memory");
    const __m128i lo=_mm_setr_epi32(static_cast<int>(palette[i0]),static_cast<int>(palette[i1]),
        static_cast<int>(palette[i2]),static_cast<int>(palette[i3]));
    const auto i4=direct_palette_id<Wide>(table,direct_code_wide(p+12));
    const auto i5=direct_palette_id<Wide>(table,direct_code_wide(p+15));
    const auto i6=direct_palette_id<Wide>(table,direct_code_wide(p+18));
    const auto i7=direct_palette_id<Wide>(table,direct_code_wide(p+21));
    __asm__ volatile("" : : "r"(i4),"r"(i5),"r"(i6),"r"(i7) : "memory");
    const __m128i hi=_mm_setr_epi32(static_cast<int>(palette[i4]),static_cast<int>(palette[i5]),
        static_cast<int>(palette[i6]),static_cast<int>(palette[i7]));
    return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
}

/* 保持强目标只进入独立 BMI 主模板，不内联到仅支持 AVX2 的分派函数。 */
#if defined(__x86_64__)
#define FC_DIRECT_BMI __attribute__((target("avx2,bmi")))

FC_DIRECT_BMI inline __attribute__((always_inline)) std::uint64_t direct_pair48_input(
    const std::uint8_t* p) noexcept {
    typedef std::uint64_t unaligned_alias_u64 __attribute__((aligned(1),may_alias));
    const std::uint64_t high_mask=0xffff000000000000ULL;
    std::uint64_t packed;
    /* AT&T顺序为内存、取反掩码、目标，结果精确保留低48位的两个RGB像素。 */
    __asm__("andn %1, %q2, %q0" : "=r"(packed)
        : "m"(*reinterpret_cast<const unaligned_alias_u64*>(p)),"r"(high_mask) : "cc");
    return packed;
}

template<bool Wide>
FC_DIRECT_BMI inline __attribute__((always_inline)) __m256i direct_read_pair48(
    const std::uint8_t* table,const std::uint32_t* palette,const std::uint8_t* p) noexcept {
    const auto q0=direct_pair48_input(p);
    const auto i0=direct_palette_id<Wide>(table,std::uint32_t(q0&0xffffffu));
    const auto i1=direct_palette_id<Wide>(table,std::uint32_t(q0>>24));
    const auto q1=direct_pair48_input(p+6);
    const auto i2=direct_palette_id<Wide>(table,std::uint32_t(q1&0xffffffu));
    const auto i3=direct_palette_id<Wide>(table,std::uint32_t(q1>>24));
    __asm__ volatile("" : : "r"(i0),"r"(i1),"r"(i2),"r"(i3) : "memory");
    const auto lo=_mm_setr_epi32(static_cast<int>(palette[i0]),static_cast<int>(palette[i1]),
        static_cast<int>(palette[i2]),static_cast<int>(palette[i3]));
    const auto q2=direct_pair48_input(p+12);
    const auto i4=direct_palette_id<Wide>(table,std::uint32_t(q2&0xffffffu));
    const auto i5=direct_palette_id<Wide>(table,std::uint32_t(q2>>24));
    const auto q3=direct_pair48_input(p+18);
    const auto i6=direct_palette_id<Wide>(table,std::uint32_t(q3&0xffffffu));
    const auto i7=direct_palette_id<Wide>(table,std::uint32_t(q3>>24));
    __asm__ volatile("" : : "r"(i4),"r"(i5),"r"(i6),"r"(i7) : "memory");
    const auto hi=_mm_setr_epi32(static_cast<int>(palette[i4]),static_cast<int>(palette[i5]),
        static_cast<int>(palette[i6]),static_cast<int>(palette[i7]));
    return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
}
#endif

FC_AVX2 inline __attribute__((always_inline)) void direct_output8(
    std::uint8_t* p,__m256i value) noexcept {
    const auto bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(
        0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,
        0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
    const auto lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
    _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(hi,4));
}

template<int Phase>
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_pack(__m256i value) noexcept {
    const auto bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(
        0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,
        0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
    if constexpr(Phase==0)return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(0,1,2,4,5,6,3,7));
    else if constexpr(Phase==1)return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(2,4,5,6,3,7,0,1));
    else if constexpr(Phase==2)return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(5,6,3,7,0,1,2,4));
    else return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(3,7,0,1,2,4,5,6));
}

FC_AVX2 inline __attribute__((always_inline)) void direct_output32_stream(
    std::uint8_t* p,__m256i v0,__m256i v1,__m256i v2,__m256i v3) noexcept {
    const auto s0=_mm256_blend_epi32(v0,v1,0xc0);
    const auto s1=_mm256_permute2x128_si256(v1,v2,0x30);
    const auto s2=_mm256_blend_epi32(v3,v2,0x03);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(p),s0);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(p+32),s1);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(p+64),s2);
}

FC_AVX2 inline __attribute__((always_inline)) void direct_output32(
    std::uint8_t* p,__m256i v0,__m256i v1,__m256i v2,__m256i v3) noexcept {
    const auto a=_mm256_castsi256_si128(v0),b=_mm256_extracti128_si256(v0,1);
    const auto c=_mm256_castsi256_si128(v1),d=_mm256_extracti128_si256(v1,1);
    const auto e=_mm256_castsi256_si128(v2),f=_mm256_extracti128_si256(v2,1);
    const auto g=_mm256_castsi256_si128(v3),h=_mm256_extracti128_si256(v3,1);
    const auto s0=_mm256_inserti128_si256(_mm256_castsi128_si256(a),_mm_unpacklo_epi64(b,c),1);
    const auto s1=_mm256_inserti128_si256(_mm256_castsi128_si256(_mm_alignr_epi8(d,c,8)),e,1);
    const auto s2=_mm256_inserti128_si256(_mm256_castsi128_si256(_mm_unpacklo_epi64(f,g)),_mm_alignr_epi8(h,g,8),1);
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(p),s0);
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(p+32),s1);
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(p+64),s2);
}

template<bool Wide>
inline void direct_palette_scalar(const std::uint8_t* table,const std::uint32_t* palette,
    const std::uint8_t* src,std::uint8_t* dst) noexcept {
    store_rgb(dst,direct_palette_value<Wide>(table,palette,rgb32(src)));
}

template<bool Wide>
FC_AVX2 inline void direct_palette_run(const std::uint8_t* table,const std::uint32_t* palette,
    const std::uint8_t* source,std::uint8_t* destination,std::size_t remaining) noexcept {
    const std::size_t initial=remaining>341?1024:remaining*3;
    for(std::size_t offset=0;offset<initial;offset+=64)
        _mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_NTA);
    /* 3与64互质；最多63个像素后到达缓存行边界，且不写入范围外。 */
    for(;remaining&&(reinterpret_cast<std::uintptr_t>(destination)&63);source+=3,destination+=3,--remaining)
        direct_palette_scalar<Wide>(table,palette,source,destination);
    bool streamed=false;
    for(;remaining>=72;source+=192,destination+=192,remaining-=64) {
        /* 最大提示地址为source+1215；remaining>=406保证它仍在当前输入块内。 */
        if(remaining>=406) {
            const auto* future=source+1024;
            _mm_prefetch(reinterpret_cast<const char*>(future),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+64),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+128),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+191),_MM_HINT_NTA);
        }
        /* 宽读末端多出的1B位于剩余块内；先读取64像素，再写精确192B。 */
        const auto r0=direct_pack<0>(direct_read_wide<Wide>(table,palette,source));
        const auto r1=direct_pack<1>(direct_read_wide<Wide>(table,palette,source+24));
        const auto r2=direct_pack<2>(direct_read_wide<Wide>(table,palette,source+48));
        const auto r3=direct_pack<3>(direct_read_wide<Wide>(table,palette,source+72));
        const auto r4=direct_pack<0>(direct_read_wide<Wide>(table,palette,source+96));
        const auto r5=direct_pack<1>(direct_read_wide<Wide>(table,palette,source+120));
        const auto r6=direct_pack<2>(direct_read_wide<Wide>(table,palette,source+144));
        const auto r7=direct_pack<3>(direct_read_wide<Wide>(table,palette,source+168));
        direct_output32_stream(destination,r0,r1,r2,r3);
        direct_output32_stream(destination+96,r4,r5,r6,r7);
        streamed=true;
    }
    /* 在普通尾部、调用方读取和OpenMP barrier前发布NT写入。 */
    if(streamed)_mm_sfence();
    for(;remaining>=40;source+=96,destination+=96,remaining-=32) {
        const auto r0=direct_pack<0>(direct_read_wide<Wide>(table,palette,source));
        const auto r1=direct_pack<0>(direct_read_wide<Wide>(table,palette,source+24));
        const auto r2=direct_pack<0>(direct_read_wide<Wide>(table,palette,source+48));
        const auto r3=direct_pack<0>(direct_read_wide<Wide>(table,palette,source+72));
        direct_output32(destination,r0,r1,r2,r3);
    }
    for(;remaining>=8;source+=24,destination+=24,remaining-=8)
        direct_output8(destination,direct_read_exact<Wide>(table,palette,source));
    for(;remaining;source+=3,destination+=3,--remaining)
        direct_palette_scalar<Wide>(table,palette,source,destination);
}

/* 与基础模板保持同一写入、预取和短尾协议；只替换宽循环的双像素读取。 */
#if defined(__x86_64__)
template<bool Wide>
FC_DIRECT_BMI inline void direct_palette_run_bmi(const std::uint8_t* table,const std::uint32_t* palette,
    const std::uint8_t* source,std::uint8_t* destination,std::size_t remaining) noexcept {
    const std::size_t initial=remaining>341?1024:remaining*3;
    for(std::size_t offset=0;offset<initial;offset+=64)
        _mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_NTA);
    for(;remaining&&(reinterpret_cast<std::uintptr_t>(destination)&63);source+=3,destination+=3,--remaining)
        direct_palette_scalar<Wide>(table,palette,source,destination);
    bool streamed=false;
    for(;remaining>=72;source+=192,destination+=192,remaining-=64) {
        if(remaining>=406) {
            const auto* future=source+1024;
            _mm_prefetch(reinterpret_cast<const char*>(future),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+64),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+128),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+191),_MM_HINT_NTA);
        }
        /* 最后一次8B读取起于source+186，末端194B仍在72像素的216B内。 */
        const auto r0=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source));
        const auto r1=direct_pack<1>(direct_read_pair48<Wide>(table,palette,source+24));
        const auto r2=direct_pack<2>(direct_read_pair48<Wide>(table,palette,source+48));
        const auto r3=direct_pack<3>(direct_read_pair48<Wide>(table,palette,source+72));
        const auto r4=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source+96));
        const auto r5=direct_pack<1>(direct_read_pair48<Wide>(table,palette,source+120));
        const auto r6=direct_pack<2>(direct_read_pair48<Wide>(table,palette,source+144));
        const auto r7=direct_pack<3>(direct_read_pair48<Wide>(table,palette,source+168));
        direct_output32_stream(destination,r0,r1,r2,r3);
        direct_output32_stream(destination+96,r4,r5,r6,r7);
        streamed=true;
    }
    if(streamed)_mm_sfence();
    for(;remaining>=40;source+=96,destination+=96,remaining-=32) {
        /* 最后一次8B读取起于source+90，末端98B仍在40像素的120B内。 */
        const auto r0=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source));
        const auto r1=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source+24));
        const auto r2=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source+48));
        const auto r3=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source+72));
        direct_output32(destination,r0,r1,r2,r3);
    }
    for(;remaining>=8;source+=24,destination+=24,remaining-=8)
        direct_output8(destination,direct_read_exact<Wide>(table,palette,source));
    for(;remaining;source+=3,destination+=3,--remaining)
        direct_palette_scalar<Wide>(table,palette,source,destination);
}
#endif

/* 保留旧gather作为可复测基线，表尾guard与精确24B图像读写契约不变。 */
FC_AVX2 inline void direct_rgb24_gather_run(const std::uint8_t* table,const std::uint8_t* src,
    std::uint8_t* dst,std::size_t pixels) noexcept {
    const auto mask=_mm256_set1_epi32(255);
    std::size_t i=0;
    for(;pixels-i>=8;i+=8) {
        Rgb rgb;load8(src+3*i,rgb);
        const auto code=_mm256_or_si256(rgb.r,_mm256_or_si256(_mm256_slli_epi32(rgb.g,8),_mm256_slli_epi32(rgb.b,16)));
        const auto offset=_mm256_add_epi32(code,_mm256_slli_epi32(code,1));
        const auto value=_mm256_i32gather_epi32(reinterpret_cast<const int*>(table),offset,1);
        rgb.r=_mm256_and_si256(value,mask);rgb.g=_mm256_and_si256(_mm256_srli_epi32(value,8),mask);
        rgb.b=_mm256_and_si256(_mm256_srli_epi32(value,16),mask);store8(dst+3*i,rgb);
    }
    for(;i<pixels;++i)store_rgb(dst+3*i,rgb32(table+std::size_t(rgb32(src+3*i))*3));
}

/* RGB24节点只有3B；读取第4B由既有表尾guard保证，打包时明确丢弃。 */
inline std::uint32_t direct_rgb24_value(const std::uint8_t* table,std::uint32_t code) noexcept {
    std::uint32_t value;std::memcpy(&value,table+std::size_t(code)*3,4);return value;
}

/* 输入只读精确24B，用于最后的8像素及保护页边界。 */
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_rgb24_read_exact(
    const std::uint8_t* table,const std::uint8_t* p) noexcept {
    std::uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
    return _mm256_setr_epi32(
        static_cast<int>(direct_rgb24_value(table,std::uint32_t(a&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t((a>>24)&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t(((a>>48)|(b<<16))&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t((b>>8)&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t((b>>32)&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t(((b>>56)|(c<<8))&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t((c>>16)&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t(c>>40))));
}

/* 八个独立节点读取分组发出，减少单条gather内部的串行等待。 */
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_rgb24_read_wide(
    const std::uint8_t* table,const std::uint8_t* p) noexcept {
    const auto v0=direct_rgb24_value(table,direct_code_wide(p));
    const auto v1=direct_rgb24_value(table,direct_code_wide(p+3));
    const auto v2=direct_rgb24_value(table,direct_code_wide(p+6));
    const auto v3=direct_rgb24_value(table,direct_code_wide(p+9));
    __asm__ volatile("" : : "r"(v0),"r"(v1),"r"(v2),"r"(v3) : "memory");
    const auto lo=_mm_setr_epi32(static_cast<int>(v0),static_cast<int>(v1),static_cast<int>(v2),static_cast<int>(v3));
    const auto v4=direct_rgb24_value(table,direct_code_wide(p+12));
    const auto v5=direct_rgb24_value(table,direct_code_wide(p+15));
    const auto v6=direct_rgb24_value(table,direct_code_wide(p+18));
    const auto v7=direct_rgb24_value(table,direct_code_wide(p+21));
    __asm__ volatile("" : : "r"(v4),"r"(v5),"r"(v6),"r"(v7) : "memory");
    const auto hi=_mm_setr_epi32(static_cast<int>(v4),static_cast<int>(v5),static_cast<int>(v6),static_cast<int>(v7));
    return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
}

template<bool Stream>
FC_AVX2 inline void direct_rgb24_block_run(const std::uint8_t* table,const std::uint8_t* source,
    std::uint8_t* destination,std::size_t remaining) noexcept {
    const std::size_t initial=remaining>341?1024:remaining*3;
    for(std::size_t offset=0;offset<initial;offset+=64)
        _mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_NTA);
    for(;remaining&&(reinterpret_cast<std::uintptr_t>(destination)&63);source+=3,destination+=3,--remaining)
        store_rgb(destination,rgb32(table+std::size_t(rgb32(source))*3));
    bool streamed=false;
    for(;remaining>=72;source+=192,destination+=192,remaining-=64) {
        if(remaining>=406) {
            const auto* future=source+1024;
            _mm_prefetch(reinterpret_cast<const char*>(future),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+64),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+128),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+191),_MM_HINT_NTA);
        }
        /* 最后一个宽输入读取末端为193B，始终在至少216B的剩余输入内。 */
        const auto r0=direct_pack<0>(direct_rgb24_read_wide(table,source));
        const auto r1=direct_pack<1>(direct_rgb24_read_wide(table,source+24));
        const auto r2=direct_pack<2>(direct_rgb24_read_wide(table,source+48));
        const auto r3=direct_pack<3>(direct_rgb24_read_wide(table,source+72));
        const auto r4=direct_pack<0>(direct_rgb24_read_wide(table,source+96));
        const auto r5=direct_pack<1>(direct_rgb24_read_wide(table,source+120));
        const auto r6=direct_pack<2>(direct_rgb24_read_wide(table,source+144));
        const auto r7=direct_pack<3>(direct_rgb24_read_wide(table,source+168));
        if constexpr(Stream) {
            direct_output32_stream(destination,r0,r1,r2,r3);
            direct_output32_stream(destination+96,r4,r5,r6,r7);
            streamed=true;
        } else {
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination),_mm256_blend_epi32(r0,r1,0xc0));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+32),_mm256_permute2x128_si256(r1,r2,0x30));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+64),_mm256_blend_epi32(r3,r2,0x03));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+96),_mm256_blend_epi32(r4,r5,0xc0));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+128),_mm256_permute2x128_si256(r5,r6,0x30));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+160),_mm256_blend_epi32(r7,r6,0x03));
        }
    }
    if(streamed)_mm_sfence();
    for(;remaining>=40;source+=96,destination+=96,remaining-=32) {
        const auto r0=direct_pack<0>(direct_rgb24_read_wide(table,source));
        const auto r1=direct_pack<0>(direct_rgb24_read_wide(table,source+24));
        const auto r2=direct_pack<0>(direct_rgb24_read_wide(table,source+48));
        const auto r3=direct_pack<0>(direct_rgb24_read_wide(table,source+72));
        direct_output32(destination,r0,r1,r2,r3);
    }
    for(;remaining>=8;source+=24,destination+=24,remaining-=8)
        direct_output8(destination,direct_rgb24_read_exact(table,source));
    for(;remaining;source+=3,destination+=3,--remaining)
        store_rgb(destination,rgb32(table+std::size_t(rgb32(source))*3));
}

/* 常数优化候选与基线并存；模板参数只在构建时确定，不根据待测图片选核。
 * Input=0沿用8次u32，1为4次u64双像素，2为精确3次u64。
 * Fence=0不限制调度，1只约束四个值，2保留旧memory屏障。
 */
template<unsigned Fence>
FC_AVX2 inline __attribute__((always_inline)) void direct_rgb24_fence4(
    std::uint32_t a,std::uint32_t b,std::uint32_t c,std::uint32_t d) noexcept {
    static_assert(Fence<=2,"RGB24屏障选项非法");
    if constexpr(Fence==2)__asm__ volatile("" : : "r"(a),"r"(b),"r"(c),"r"(d) : "memory");
    else if constexpr(Fence==1)__asm__ volatile("" : : "r"(a),"r"(b),"r"(c),"r"(d));
}

template<unsigned Fence>
FC_AVX2 inline __attribute__((always_inline)) __m128i direct_rgb24_lookup4(
    const std::uint8_t* table,std::uint32_t c0,std::uint32_t c1,std::uint32_t c2,std::uint32_t c3) noexcept {
    const auto v0=direct_rgb24_value(table,c0),v1=direct_rgb24_value(table,c1);
    const auto v2=direct_rgb24_value(table,c2),v3=direct_rgb24_value(table,c3);
    direct_rgb24_fence4<Fence>(v0,v1,v2,v3);
    return _mm_setr_epi32(static_cast<int>(v0),static_cast<int>(v1),static_cast<int>(v2),static_cast<int>(v3));
}

template<unsigned Input,unsigned Fence>
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_rgb24_read_candidate(
    const std::uint8_t* table,const std::uint8_t* p) noexcept {
    static_assert(Input<=2,"RGB24输入选项非法");
    __m128i lo,hi;
    if constexpr(Input==1) {
        // 末对读到p+25；仅在至少多一个像素的宽块中使用，尾部另走精确读取。
        std::uint64_t a,b;
        std::memcpy(&a,p,8);std::memcpy(&b,p+6,8);
        lo=direct_rgb24_lookup4<Fence>(table,std::uint32_t(a)&0xffffffu,std::uint32_t(a>>24)&0xffffffu,
            std::uint32_t(b)&0xffffffu,std::uint32_t(b>>24)&0xffffffu);
        std::uint64_t c,d;
        std::memcpy(&c,p+12,8);std::memcpy(&d,p+18,8);
        hi=direct_rgb24_lookup4<Fence>(table,std::uint32_t(c)&0xffffffu,std::uint32_t(c>>24)&0xffffffu,
            std::uint32_t(d)&0xffffffu,std::uint32_t(d>>24)&0xffffffu);
    } else if constexpr(Input==2) {
        std::uint64_t a,b,c;
        std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
        lo=direct_rgb24_lookup4<Fence>(table,std::uint32_t(a)&0xffffffu,std::uint32_t(a>>24)&0xffffffu,
            std::uint32_t((a>>48)|(b<<16))&0xffffffu,std::uint32_t(b>>8)&0xffffffu);
        hi=direct_rgb24_lookup4<Fence>(table,std::uint32_t(b>>32)&0xffffffu,
            std::uint32_t((b>>56)|(c<<8))&0xffffffu,std::uint32_t(c>>16)&0xffffffu,std::uint32_t(c>>40));
    } else {
        lo=direct_rgb24_lookup4<Fence>(table,direct_code_wide(p),direct_code_wide(p+3),
            direct_code_wide(p+6),direct_code_wide(p+9));
        hi=direct_rgb24_lookup4<Fence>(table,direct_code_wide(p+12),direct_code_wide(p+15),
            direct_code_wide(p+18),direct_code_wide(p+21));
    }
    return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
}

FC_AVX2 inline __attribute__((always_inline)) void direct_rgb24_store_prepacked32(
    std::uint8_t* destination,__m256i r0,__m256i r1,__m256i r2,__m256i r3) noexcept {
    _mm256_store_si256(reinterpret_cast<__m256i*>(destination),_mm256_blend_epi32(r0,r1,0xc0));
    _mm256_store_si256(reinterpret_cast<__m256i*>(destination+32),_mm256_permute2x128_si256(r1,r2,0x30));
    _mm256_store_si256(reinterpret_cast<__m256i*>(destination+64),_mm256_blend_epi32(r3,r2,0x03));
}

template<unsigned Input,unsigned Fence>
FC_AVX2 inline __attribute__((always_inline)) void direct_rgb24_pipeline32(
    const std::uint8_t* table,const std::uint8_t* source,std::uint8_t* destination) noexcept {
    // 下一组查询先于上一组打包；32像素即写出，避免同时保留8组YMM结果。
    const auto v0=direct_rgb24_read_candidate<Input,Fence>(table,source);
    const auto v1=direct_rgb24_read_candidate<Input,Fence>(table,source+24);
    const auto r0=direct_pack<0>(v0);
    const auto v2=direct_rgb24_read_candidate<Input,Fence>(table,source+48);
    const auto r1=direct_pack<1>(v1);
    const auto v3=direct_rgb24_read_candidate<Input,Fence>(table,source+72);
    const auto r2=direct_pack<2>(v2),r3=direct_pack<3>(v3);
    direct_rgb24_store_prepacked32(destination,r0,r1,r2,r3);
}

template<unsigned Input,unsigned Fence,bool Pipeline,unsigned BlockPixels>
FC_AVX2 inline __attribute__((always_inline)) void direct_rgb24_candidate_body(
    const std::uint8_t* table,const std::uint8_t* source,std::uint8_t* destination,
    std::size_t remaining) noexcept {
    static_assert(BlockPixels==32||BlockPixels==64,"RGB24块长必须为32或64");
    const std::size_t initial=remaining>341?1024:remaining*3;
    for(std::size_t offset=0;offset<initial;offset+=64)
        _mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_NTA);
    for(;remaining&&(reinterpret_cast<std::uintptr_t>(destination)&63);source+=3,destination+=3,--remaining)
        store_rgb(destination,rgb32(table+std::size_t(rgb32(source))*3));
    for(;remaining>=BlockPixels+8;source+=3*BlockPixels,destination+=3*BlockPixels,remaining-=BlockPixels) {
        if(remaining>=406) {
            const auto* future=source+1024;
            _mm_prefetch(reinterpret_cast<const char*>(future),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+64),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+128),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+191),_MM_HINT_NTA);
        }
        if constexpr(Pipeline) {
            direct_rgb24_pipeline32<Input,Fence>(table,source,destination);
            if constexpr(BlockPixels==64)direct_rgb24_pipeline32<Input,Fence>(table,source+96,destination+96);
        } else {
            const auto r0=direct_pack<0>(direct_rgb24_read_candidate<Input,Fence>(table,source));
            const auto r1=direct_pack<1>(direct_rgb24_read_candidate<Input,Fence>(table,source+24));
            const auto r2=direct_pack<2>(direct_rgb24_read_candidate<Input,Fence>(table,source+48));
            const auto r3=direct_pack<3>(direct_rgb24_read_candidate<Input,Fence>(table,source+72));
            if constexpr(BlockPixels==64) {
                const auto r4=direct_pack<0>(direct_rgb24_read_candidate<Input,Fence>(table,source+96));
                const auto r5=direct_pack<1>(direct_rgb24_read_candidate<Input,Fence>(table,source+120));
                const auto r6=direct_pack<2>(direct_rgb24_read_candidate<Input,Fence>(table,source+144));
                const auto r7=direct_pack<3>(direct_rgb24_read_candidate<Input,Fence>(table,source+168));
                direct_rgb24_store_prepacked32(destination,r0,r1,r2,r3);
                direct_rgb24_store_prepacked32(destination+96,r4,r5,r6,r7);
            } else direct_rgb24_store_prepacked32(destination,r0,r1,r2,r3);
        }
    }
    // 剩余最多71像素，只读精确24B；无需图像padding，也不使用重叠写。
    for(;remaining>=8;source+=24,destination+=24,remaining-=8)
        direct_output8(destination,direct_rgb24_read_exact(table,source));
    for(;remaining;source+=3,destination+=3,--remaining)
        store_rgb(destination,rgb32(table+std::size_t(rgb32(source))*3));
}

template<unsigned Input,unsigned Fence,bool Pipeline,unsigned BlockPixels>
FC_AVX2 inline void direct_rgb24_candidate_noalias(
    const std::uint8_t* table,const std::uint8_t* __restrict__ source,
    std::uint8_t* __restrict__ destination,std::size_t pixels) noexcept {
    // 仅由下方已核对地址区间的入口调用；body强制内联以传递不别名承诺。
    direct_rgb24_candidate_body<Input,Fence,Pipeline,BlockPixels>(table,source,destination,pixels);
}

inline bool direct_rgb24_separate(const std::uint8_t* source,const std::uint8_t* destination,
    std::size_t pixels) noexcept {
    if(pixels>(std::numeric_limits<std::size_t>::max)()/3)return false;
    const auto bytes=pixels*3,a=reinterpret_cast<std::uintptr_t>(source),b=reinterpret_cast<std::uintptr_t>(destination);
    return a<b?b-a>=bytes:b<a&&a-b>=bytes;
}

template<unsigned Input,unsigned Fence,bool Pipeline,unsigned BlockPixels,bool NoAlias>
FC_AVX2 inline void direct_rgb24_candidate_run(const std::uint8_t* table,const std::uint8_t* source,
    std::uint8_t* destination,std::size_t pixels) noexcept {
    if(!pixels)return;
    if constexpr(NoAlias) {
        if(direct_rgb24_separate(source,destination,pixels)) {
            direct_rgb24_candidate_noalias<Input,Fence,Pipeline,BlockPixels>(table,source,destination,pixels);
            return;
        }
    }
    // 公共Runtime已拒绝部分重叠；原地保持不带restrict的相同数值路径。
    direct_rgb24_candidate_body<Input,Fence,Pipeline,BlockPixels>(table,source,destination,pixels);
}

/* 同步huangrui的main_merged.cpp（2026-10-30，来源哈希见阶段报告）。
 * 四组精确24B读取先于写出，逐组输出24B；不要求64B对齐，也无需图像padding。
 * 原地时32个输入先全部读取，写入区间不越过该32像素；尾部保持同一契约。
 */
FC_AVX2 inline void direct_rgb24_exact32_run(const std::uint8_t* table,const std::uint8_t* source,
    std::uint8_t* destination,std::size_t remaining) noexcept {
    for(;remaining>=32;source+=96,destination+=96,remaining-=32) {
        const auto r0=direct_rgb24_read_exact(table,source);
        const auto r1=direct_rgb24_read_exact(table,source+24);
        const auto r2=direct_rgb24_read_exact(table,source+48);
        const auto r3=direct_rgb24_read_exact(table,source+72);
        direct_output8(destination,r0);
        direct_output8(destination+24,r1);
        direct_output8(destination+48,r2);
        direct_output8(destination+72,r3);
    }
    for(;remaining>=8;source+=24,destination+=24,remaining-=8)
        direct_output8(destination,direct_rgb24_read_exact(table,source));
    for(;remaining;source+=3,destination+=3,--remaining)
        store_rgb(destination,rgb32(table+std::size_t(rgb32(source))*3));
}

#ifndef FLASH_CHROMA_RGB24_EXACT32
#define FLASH_CHROMA_RGB24_EXACT32 0
#endif
#ifndef FLASH_CHROMA_RGB24_HOT_OPTIMIZED
#define FLASH_CHROMA_RGB24_HOT_OPTIMIZED 1
#endif
#ifndef FLASH_CHROMA_RGB24_HOT_INPUT
#define FLASH_CHROMA_RGB24_HOT_INPUT 1
#endif
#ifndef FLASH_CHROMA_RGB24_HOT_FENCE
#define FLASH_CHROMA_RGB24_HOT_FENCE 0
#endif
#ifndef FLASH_CHROMA_RGB24_HOT_PIPELINE
#define FLASH_CHROMA_RGB24_HOT_PIPELINE 1
#endif
#ifndef FLASH_CHROMA_RGB24_HOT_BLOCK
#define FLASH_CHROMA_RGB24_HOT_BLOCK 32
#endif
#ifndef FLASH_CHROMA_RGB24_HOT_NOALIAS
#define FLASH_CHROMA_RGB24_HOT_NOALIAS 1
#endif

/* 回归复测可显式重放旧核；候选共享模型/表格式与资源需求。 */
FC_AVX2 inline void direct_rgb24_run(const std::uint8_t* table,const std::uint8_t* src,
    std::uint8_t* dst,std::size_t pixels) noexcept {
#if defined(FLASH_CHROMA_RGB24_LEGACY) && FLASH_CHROMA_RGB24_LEGACY
    direct_rgb24_gather_run(table,src,dst,pixels);
#elif defined(FLASH_CHROMA_RGB24_STREAMING) && FLASH_CHROMA_RGB24_STREAMING
    direct_rgb24_block_run<true>(table,src,dst,pixels);
#elif FLASH_CHROMA_RGB24_EXACT32
    direct_rgb24_exact32_run(table,src,dst,pixels);
#elif FLASH_CHROMA_RGB24_HOT_OPTIMIZED
    direct_rgb24_candidate_run<FLASH_CHROMA_RGB24_HOT_INPUT,FLASH_CHROMA_RGB24_HOT_FENCE,
        FLASH_CHROMA_RGB24_HOT_PIPELINE!=0,FLASH_CHROMA_RGB24_HOT_BLOCK,FLASH_CHROMA_RGB24_HOT_NOALIAS!=0>(table,src,dst,pixels);
#else
    direct_rgb24_block_run<false>(table,src,dst,pixels);
#endif
}

FC_AVX2 inline void direct8(const std::uint8_t* table,const std::uint32_t* palette,Representation rep,
    const std::uint8_t* src,std::uint8_t* dst,std::size_t pixels) noexcept {
    if(rep==Representation::DirectRGB24) {direct_rgb24_run(table,src,dst,pixels);return;}
    /* GCC/Clang已初始化的CPU能力位：每块检查一次，不在八像素循环里做CPUID。 */
#if defined(__x86_64__)
    if(__builtin_cpu_supports("bmi")) {
        if(rep==Representation::DirectU8)direct_palette_run_bmi<false>(table,palette,src,dst,pixels);
        else direct_palette_run_bmi<true>(table,palette,src,dst,pixels);
        return;
    }
#endif
    if(rep==Representation::DirectU8)direct_palette_run<false>(table,palette,src,dst,pixels);
    else direct_palette_run<true>(table,palette,src,dst,pixels);
}

#undef FC_DIRECT_BMI

#endif
#endif
/* direct准备专用：证明首层到达域，精确编译后三层，再并行扫描首层。
 * 注入点位于 fc::detail 内、AVX2原语之后。关闭开关时只留下空域描述。
 */
struct PrepareDomain {
    int r_min=0, r_max=-1, dg_min=0, dg_max=-1, db_min=0, db_max=-1;
    int width_g=0, width_b=0;
    std::size_t entries=0;
    bool proven=false;
};

#if FLASH_CHROMA_ENABLE_PREPARE_CACHE
inline int prepare_min(int a,int b) noexcept { return a<b?a:b; }
inline int prepare_max(int a,int b) noexcept { return a>b?a:b; }
inline std::int64_t prepare_floor_q16(std::int64_t n) noexcept {
    return n>=0?n/65536:-((-n+65535)/65536);
}
inline std::uint32_t prepare_fraction(const fc_core::fc_model& m,unsigned channel,unsigned axis,unsigned code) noexcept {
    const auto* p=m.sidecar.data?m.sidecar.data+(channel*768u+axis*256u+code)*4u:
        m.fraction_le+(axis*256u+code)*4u;
    return read32(p);
}

/* 与旧域证书相同的逐cell界：同坐标时通道差在八角点差的凸包内；
 * 分输出坐标的每轴扰动以该cell四条平行边斜率的最小/最大值包围。
 * 对负下界取floor、正上界取ceil，覆盖每级half-up后的整数差。
 * 固定局部数组1920B，八角点96B；它们是有界栈，不属于arena账单。
 */
inline PrepareDomain prepare_domain(const fc_core::fc_model& first) noexcept {
    PrepareDomain d;
    int rmin=255,rmax=0,gmin=255,gmax=-255,bmin=255,bmax=-255;
    const std::size_t nodes=std::size_t(first.m)*first.m*first.m;
    for(std::size_t i=0;i<nodes;++i) {
        const int r=first.nodes[i*3],g=int(first.nodes[i*3+1])-r,b=int(first.nodes[i*3+2])-r;
        rmin=prepare_min(rmin,r);rmax=prepare_max(rmax,r);
        gmin=prepare_min(gmin,g);gmax=prepare_max(gmax,g);
        bmin=prepare_min(bmin,b);bmax=prepare_max(bmax,b);
    }
    d.r_min=rmin;d.r_max=rmax;
    d.dg_min=prepare_max(-255,gmin-2);d.dg_max=prepare_min(255,gmax+2);
    d.db_min=prepare_max(-255,bmin-2);d.db_max=prepare_min(255,bmax+2);
    d.width_g=d.dg_max-d.dg_min+1;d.width_b=d.db_max-d.db_min+1;
    d.entries=std::size_t(rmax-rmin+1)*std::size_t(d.width_g)*std::size_t(d.width_b);
    if(d.entries>2u*MiB/sizeof(std::uint32_t)) {d.entries=0;return d;}
    const unsigned cells=first.m-1;
    int low[2][3][32],high[2][3][32],count[3][32]{};
    for(unsigned c=0;c<2;++c)for(unsigned a=0;a<3;++a)for(unsigned i=0;i<cells;++i) {
        low[c][a][i]=65536;high[c][a][i]=-65536;
    }
    for(unsigned a=0;a<3;++a)for(unsigned x=0;x<256;++x) {
        const unsigned cell=first.index[a*256u+x];++count[a][cell];
        const int red=int(prepare_fraction(first,0,a,x));
        for(unsigned c=0;c<2;++c) {
            const int delta=int(prepare_fraction(first,c+1,a,x))-red;
            low[c][a][cell]=prepare_min(low[c][a][cell],delta);
            high[c][a][cell]=prepare_max(high[c][a][cell],delta);
        }
    }
    bool reachable=false;
    for(unsigned r=0;r<cells;++r)for(unsigned g=0;g<cells;++g)for(unsigned b=0;b<cells;++b) {
        if(!count[0][r]||!count[1][g]||!count[2][b])continue;
        reachable=true;
        const unsigned indices[3]={r,g,b};int corner[8][3];
        for(unsigned k=0;k<8;++k) {
            const auto at=((std::size_t(r+((k>>2)&1))*first.m+g+((k>>1)&1))*first.m+b+(k&1))*3;
            for(unsigned c=0;c<3;++c)corner[k][c]=first.nodes[at+c];
        }
        for(unsigned c=0;c<2;++c) {
            int nmin=255,nmax=-255;
            for(unsigned k=0;k<8;++k) {
                const int diff=corner[k][c+1]-corner[k][0];
                nmin=prepare_min(nmin,diff);nmax=prepare_max(nmax,diff);
            }
            std::int64_t lower=0,upper=0;
            for(unsigned a=0;a<3;++a) {
                const unsigned bit=1u<<(2-a);int smin=255,smax=-255;
                for(unsigned k=0;k<8;++k)if(!(k&bit)) {
                    const int slope=corner[k|bit][c+1]-corner[k][c+1];
                    smin=prepare_min(smin,slope);smax=prepare_max(smax,slope);
                }
                const int lo=low[c][a][indices[a]],hi=high[c][a][indices[a]];
                const std::int64_t products[4]={std::int64_t(smin)*lo,std::int64_t(smin)*hi,
                    std::int64_t(smax)*lo,std::int64_t(smax)*hi};
                auto pmin=products[0],pmax=products[0];
                for(unsigned k=1;k<4;++k) {if(products[k]<pmin)pmin=products[k];if(products[k]>pmax)pmax=products[k];}
                lower+=pmin;upper+=pmax;
            }
            const int lo=prepare_max(-255,nmin+int(prepare_floor_q16(lower)));
            const int hi=prepare_min(255,nmax-int(prepare_floor_q16(-upper)));
            if(lo<(c?d.db_min:d.dg_min)||hi>(c?d.db_max:d.dg_max)) {d.entries=0;return d;}
        }
    }
    d.proven=reachable;
    if(!reachable)d.entries=0;
    return d;
}

constexpr std::size_t prepare_chunk_pixels=4096;
constexpr std::size_t prepare_chunk_bytes=prepare_chunk_pixels*3;
inline unsigned prepare_cache_workers(const PrepareDomain& d,const RuntimeConfig& config) noexcept {
    const auto blocks=d.entries/prepare_chunk_pixels+(d.entries%prepare_chunk_pixels!=0);
    return blocks<config.threads?static_cast<unsigned>(blocks):config.threads;
}
inline std::size_t prepare_cache_scratch(const PrepareDomain& d,const RuntimeConfig& config) noexcept {
    if(!d.proven)return 0;
    const bool rgb=config.representation==Representation::DirectRGB24;
    const bool narrow=config.representation==Representation::DirectU8;
    const auto cache_bytes=aligned(d.entries*4);
    const auto used_stride=aligned((narrow?256u:65536u)/8u);
    return cache_bytes+(rgb?0:cache_bytes+(narrow?1024u:131072u)*8u+std::size_t(config.threads)*used_stride)+
        std::size_t(prepare_cache_workers(d,config))*prepare_chunk_bytes;
}

/* 一次只处理有界RGB块；失效域槽存UINT32_MAX，不参与palette资格。
 * 末块按8像素补零，cache自身按64B预留，因此向量末写仍在arena内。
 */
FC_AVX2 inline void prepare_suffix_block(const PackedView* views,const PrepareDomain& d,
    std::size_t begin,std::size_t n,std::uint8_t* colours,std::uint32_t* cache) noexcept {
    const std::size_t rounded=(n+7u)&~std::size_t{7};
    const std::size_t plane=std::size_t(d.width_g)*d.width_b;
    for(std::size_t i=0;i<rounded;++i) {
        const auto index=begin+i;
        const int r=d.r_min+int(index/plane);
        const int g=r+d.dg_min+int((index/std::size_t(d.width_b))%std::size_t(d.width_g));
        const int b=r+d.db_min+int(index%std::size_t(d.width_b));
        const bool valid=i<n&&g>=0&&g<=255&&b>=0&&b<=255;
        auto* p=colours+i*3;
        p[0]=valid?std::uint8_t(r):0;p[1]=valid?std::uint8_t(g):0;p[2]=valid?std::uint8_t(b):0;
        cache[index]=valid?0:0xffffffffu;
    }
    for(std::size_t i=0;i<rounded;i+=8) {
        Rgb value;load8(colours+i*3,value);
        for(unsigned s=1;s<4;++s)transform(views[s],value);
        const auto packed=_mm256_or_si256(value.r,_mm256_or_si256(_mm256_slli_epi32(value.g,8),_mm256_slli_epi32(value.b,16)));
        const auto invalid=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(cache+begin+i));
        _mm256_storeu_si256(reinterpret_cast<__m256i*>(cache+begin+i),_mm256_or_si256(packed,invalid));
    }
}

/* R连续加载、G/B广播；分输出侧表分别计算自己的分数与顶点排序。 */
template<bool Shared>
FC_AVX2 inline void prepare_first8(const PackedView& v,unsigned red,
    const std::uint32_t* green,const std::uint32_t* blue,Rgb& rgb) noexcept {
    const auto ar=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(v.axes[0][0]+red));
    const auto ag=_mm256_set1_epi32(static_cast<int>(green[0])),ab=_mm256_set1_epi32(static_cast<int>(blue[0]));
    const auto base=_mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ar,17),_mm256_set1_epi32(v.sr)),
        _mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ag,17),_mm256_set1_epi32(v.sg)),_mm256_srli_epi32(ab,17)));
    const auto mask=_mm256_set1_epi32(0x1ffff),x=_mm256_and_si256(ar,mask),y=_mm256_and_si256(ag,mask),z=_mm256_and_si256(ab,mask);
    const auto n0=gather(v.nodes,base),n3=gather(v.nodes,_mm256_add_epi32(base,_mm256_set1_epi32(v.sr+v.sg+1)));
    if constexpr(Shared) {
        __m256i high,middle,low,first,last;geometry(v,x,y,z,high,middle,low,first,last);
        const auto n1=gather(v.nodes,_mm256_add_epi32(base,first));
        const auto n2=gather(v.nodes,_mm256_add_epi32(base,_mm256_sub_epi32(_mm256_set1_epi32(v.sr+v.sg+1),last)));
        rgb.r=interpolate<0>(n0,n1,n2,n3,high,middle,low);
        rgb.g=interpolate<1>(n0,n1,n2,n3,high,middle,low);
        rgb.b=interpolate<2>(n0,n1,n2,n3,high,middle,low);
    } else {
        rgb.r=channel<0>(v,base,n0,n3,x,y,z);
        rgb.g=channel<1>(v,base,n0,n3,
            _mm256_and_si256(_mm256_loadu_si256(reinterpret_cast<const __m256i*>(v.axes[1][0]+red)),mask),
            _mm256_and_si256(_mm256_set1_epi32(static_cast<int>(green[1])),mask),
            _mm256_and_si256(_mm256_set1_epi32(static_cast<int>(blue[1])),mask));
        rgb.b=channel<2>(v,base,n0,n3,
            _mm256_and_si256(_mm256_loadu_si256(reinterpret_cast<const __m256i*>(v.axes[2][0]+red)),mask),
            _mm256_and_si256(_mm256_set1_epi32(static_cast<int>(green[2])),mask),
            _mm256_and_si256(_mm256_set1_epi32(static_cast<int>(blue[2])),mask));
    }
}

template<unsigned Format,bool Shared>
FC_AVX2 inline void prepare_direct_blue(const PackedView& first,const PrepareDomain& d,
    const std::uint32_t* table,std::uint8_t* destination,unsigned blue_code,std::uint8_t* used) noexcept {
    std::uint32_t blues[Shared?1:3];
    for(unsigned c=0;c<(Shared?1u:3u);++c)blues[c]=first.axes[c][2][blue_code];
    const auto bytes8=_mm_setr_epi8(0,4,8,12,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1);
    const auto words8=_mm_setr_epi8(0,1,4,5,8,9,12,13,-1,-1,-1,-1,-1,-1,-1,-1);
    for(unsigned green_code=0;green_code<256;++green_code) {
        std::uint32_t greens[Shared?1:3];
        for(unsigned c=0;c<(Shared?1u:3u);++c)greens[c]=first.axes[c][1][green_code];
        for(unsigned red_code=0;red_code<256;red_code+=8) {
            Rgb rgb;prepare_first8<Shared>(first,red_code,greens,blues,rgb);
            const auto dg=_mm256_sub_epi32(rgb.g,rgb.r),db=_mm256_sub_epi32(rgb.b,rgb.r);
            const auto index=_mm256_add_epi32(
                _mm256_mullo_epi32(_mm256_sub_epi32(rgb.r,_mm256_set1_epi32(d.r_min)),_mm256_set1_epi32(d.width_g*d.width_b)),
                _mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(dg,_mm256_set1_epi32(d.dg_min)),_mm256_set1_epi32(d.width_b)),
                    _mm256_sub_epi32(db,_mm256_set1_epi32(d.db_min))));
            const auto value=gather(table,index);
            auto* out=destination+(std::size_t(green_code)*256+red_code)*Format;
            if constexpr(Format==3) {
                const auto mask=_mm256_set1_epi32(255);
                rgb.r=_mm256_and_si256(value,mask);rgb.g=_mm256_and_si256(_mm256_srli_epi32(value,8),mask);rgb.b=_mm256_srli_epi32(value,16);
                store8(out,rgb);
            } else {
                /* worker私有位图只记录实际完整RGB8到达的ID；缓存超集不能冒充可达palette。 */
                alignas(32) std::uint32_t reached[8];
                _mm256_store_si256(reinterpret_cast<__m256i*>(reached),value);
                for(unsigned i=0;i<8;++i)used[reached[i]>>3]|=std::uint8_t(1u<<(reached[i]&7));
                const auto lo=_mm256_castsi256_si128(value),hi=_mm256_extracti128_si256(value,1);
                if constexpr(Format==1) {
                    _mm_storel_epi64(reinterpret_cast<__m128i*>(out),_mm_unpacklo_epi32(_mm_shuffle_epi8(lo,bytes8),_mm_shuffle_epi8(hi,bytes8)));
                } else {
                    _mm_storeu_si128(reinterpret_cast<__m128i*>(out),_mm_unpacklo_epi64(_mm_shuffle_epi8(lo,words8),_mm_shuffle_epi8(hi,words8)));
                }
            }
        }
    }
}

inline bool prepare_cached_direct(const PackedView* views,const PrepareDomain& d,
    const RuntimeConfig& config,std::uint8_t* destination,std::uint8_t* temporary,
    std::uint32_t* palette,std::uint32_t* palette_count) noexcept {
    if(!d.proven)return false;
    const bool rgb=config.representation==Representation::DirectRGB24;
    const bool narrow=config.representation==Representation::DirectU8;
    const std::size_t cache_bytes=aligned(d.entries*4),slots=narrow?1024:131072,limit=narrow?256:65536;
    auto* cache=reinterpret_cast<std::uint32_t*>(temporary);
    auto* ids=rgb?nullptr:reinterpret_cast<std::uint32_t*>(temporary+cache_bytes);
    auto* keys=rgb?nullptr:reinterpret_cast<std::uint32_t*>(temporary+2*cache_bytes);
    auto* values=rgb?nullptr:keys+slots;
    const auto used_stride=aligned(limit/8u);
    auto* used=rgb?nullptr:reinterpret_cast<std::uint8_t*>(values+slots);
    auto* scratch=rgb?temporary+cache_bytes:used+std::size_t(config.threads)*used_stride;
    const std::size_t blocks=d.entries/prepare_chunk_pixels+(d.entries%prepare_chunk_pixels!=0);
#if FLASH_CHROMA_ENABLE_OPENMP
    const int workers=omp_in_parallel()?1:static_cast<int>(prepare_cache_workers(d,config));
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
    for(long long task=0;task<static_cast<long long>(blocks);++task) {
        const std::size_t begin=std::size_t(task)*prepare_chunk_pixels;
        const std::size_t n=d.entries-begin<prepare_chunk_pixels?d.entries-begin:prepare_chunk_pixels;
        std::size_t worker=0;
#if FLASH_CHROMA_ENABLE_OPENMP
        worker=static_cast<std::size_t>(omp_get_thread_num());
#endif
        prepare_suffix_block(views,d,begin,n,scratch+worker*prepare_chunk_bytes,cache);
    }
    if(!rgb) {
        for(std::size_t i=0;i<slots;++i)keys[i]=0xffffffffu;
        for(std::size_t i=0;i<limit;++i)palette[i]=0;
        std::uint32_t count=0;
        for(std::size_t i=0;i<d.entries;++i) {
            const auto colour=cache[i];
            if(colour==0xffffffffu) {ids[i]=0;continue;}
            std::size_t slot=(std::uint32_t(colour*2654435761u))>>(narrow?22:15);
            while(keys[slot]!=0xffffffffu&&keys[slot]!=colour)slot=(slot+1)&(slots-1);
            if(keys[slot]==0xffffffffu) {
                /* 超集palette过大不等于实际全RGB8过大，必须走通用资格回退。 */
                if(count==limit)return false;
                keys[slot]=colour;values[slot]=count;palette[count++]=colour;
            }
            ids[i]=values[slot];
        }
        if(!count)return false;
        *palette_count=count;
    } else *palette_count=0;
    if(!rgb)for(std::size_t i=0;i<std::size_t(config.threads)*used_stride;++i)used[i]=0;
#if FLASH_CHROMA_ENABLE_OPENMP
    const int direct_workers=omp_in_parallel()?1:static_cast<int>(config.threads);
#pragma omp parallel for schedule(static) num_threads(direct_workers)
#endif
    for(int blue=0;blue<256;++blue) {
        const auto* lookup=rgb?cache:ids;
        const auto offset=std::size_t(blue)*65536u*(rgb?3u:(narrow?1u:2u));
        std::size_t worker=0;
#if FLASH_CHROMA_ENABLE_OPENMP
        worker=static_cast<std::size_t>(omp_get_thread_num());
#endif
        auto* reached=rgb?nullptr:used+worker*used_stride;
        if(rgb) {
            if(views[0].shared)prepare_direct_blue<3,true>(views[0],d,lookup,destination+offset,unsigned(blue),nullptr);
            else prepare_direct_blue<3,false>(views[0],d,lookup,destination+offset,unsigned(blue),nullptr);
        } else if(narrow) {
            if(views[0].shared)prepare_direct_blue<1,true>(views[0],d,lookup,destination+offset,unsigned(blue),reached);
            else prepare_direct_blue<1,false>(views[0],d,lookup,destination+offset,unsigned(blue),reached);
        } else {
            if(views[0].shared)prepare_direct_blue<2,true>(views[0],d,lookup,destination+offset,unsigned(blue),reached);
            else prepare_direct_blue<2,false>(views[0],d,lookup,destination+offset,unsigned(blue),reached);
        }
    }
    if(!rgb) {
        /* 合并worker位图，只报告完整RGB8实际可达颜色数。
         * 私有palette仍保留超集ID及未用槽；热核只按固定容量访问，不把该计数当ID上界。
         * 这样无需为了只读诊断再读写整张16/32MiB direct表。
         */
        for(unsigned worker=1;worker<config.threads;++worker)
            for(std::size_t i=0;i<used_stride;++i)used[i]|=used[std::size_t(worker)*used_stride+i];
        const auto old_count=*palette_count;
        std::uint32_t actual=0;
        for(std::uint32_t i=0;i<old_count;++i)if(used[i>>3]&(1u<<(i&7)))++actual;
        *palette_count=actual;
    }
    if(rgb)for(unsigned i=0;i<4;++i)destination[colours*3+i]=0;
    return true;
}
#endif

}

std::uint32_t compiled_capabilities() noexcept {
    return 1u
#if FLASH_CHROMA_ENABLE_AVX2
        |2u
#endif
#if FLASH_CHROMA_ENABLE_OPENMP
        |4u
#endif
        ;
}
std::uint32_t available_backends() noexcept {
    std::uint32_t mask=1;
#if FLASH_CHROMA_ENABLE_AVX2
    unsigned a=0,b=0,c=0,d=0;
    constexpr unsigned prerequisites=(1u<<26)|(1u<<27)|(1u<<28);
    if(__get_cpuid(1,&a,&b,&c,&d)&&(c&prerequisites)==prerequisites) {
        const unsigned leaf1_ecx=c;
        unsigned xlo=0,xhi=0;__asm__ volatile("xgetbv":"=a"(xlo),"=d"(xhi):"c"(0));
        if(__get_cpuid_count(7,0,&a,&b,&c,&d)&&detail::avx2_state_supported(leaf1_ecx,xlo,b))mask|=2;
    }
#endif
#if FLASH_CHROMA_ENABLE_OPENMP
    mask|=4;
#endif
    return mask;
}
const char* status_string(Status status) noexcept {
    if(static_cast<unsigned>(status)<=7)return fc_core::fc_status_string(static_cast<fc_core::fc_status>(status));
    switch(status) {case Status::Unsupported:return "当前目标、编译能力或CPU不支持配置";case Status::Budget:return "工作区预算或容量不足";case Status::Capacity:return "完整色域的调色板超过所选索引容量";default:return "未知状态";}
}

namespace detail {
inline Status runtime_requirements(const ModelBundle& bundle,const RuntimeConfig& config,
    Requirements* out,PrepareDomain* domain) noexcept {
    (void)domain;
    if(!out)return Status::Null;
    if(!fc_core::fc_detail_span_valid(out,sizeof(*out)))return Status::Overflow;
    if(fc_core::fc_detail_intersects(out,sizeof(*out),&bundle,sizeof(bundle))||fc_core::fc_detail_intersects(out,sizeof(*out),&config,sizeof(config)))return Status::Overlap;
    Backend backend;const auto resolved=detail::resolve(config,&backend);if(resolved!=Status::Ok)return resolved;
    fc_core::fc_model models[4]{};Requirements r{};r.object_bytes=sizeof(Runtime);
    for(unsigned s=0;s<4;++s) {
        const auto st=fc_core::fc_model_init(models+s,bundle.models[s],bundle.sidecars[s]);
        if(st!=fc_core::FC_OK)return static_cast<Status>(st);
        if(fc_core::fc_detail_intersects(out,sizeof(*out),bundle.models[s].data,bundle.models[s].size)||fc_core::fc_detail_intersects(out,sizeof(*out),bundle.sidecars[s].data,bundle.sidecars[s].size))return Status::Overlap;
        if(!detail::add(r.model_bytes,bundle.models[s].size)||!detail::add(r.model_bytes,bundle.sidecars[s].size))return Status::Overflow;
    }
    const std::size_t packed=
#if FLASH_CHROMA_ENABLE_AVX2
        backend==Backend::Avx2?detail::packed_bytes(models):0;
#else
        0;
#endif
    if(config.representation==Representation::Sparse)r.persistent_bytes=packed;
#if FLASH_CHROMA_ENABLE_DIRECT
    else if(config.representation==Representation::DirectRGB24) {
        r.persistent_bytes=detail::aligned(detail::colours*3+4);r.temporary_bytes=packed;
    } else {
        const bool narrow=config.representation==Representation::DirectU8;
        r.persistent_bytes=detail::colours*(narrow?1:2)+(narrow?256:65536)*4;
        r.temporary_bytes=packed+(narrow?1024:131072)*8+detail::aligned(4096*3);
    }
#if FLASH_CHROMA_ENABLE_PREPARE_CACHE
    if(config.representation!=Representation::Sparse&&backend==Backend::Avx2) {
        const auto proven=detail::prepare_domain(models[0]);
        const auto fast=detail::prepare_cache_scratch(proven,config);
        if(fast&&packed+fast>r.temporary_bytes)r.temporary_bytes=packed+fast;
        if(domain)*domain=proven;
    }
#endif
#endif
    r.arena_bytes=r.persistent_bytes+r.temporary_bytes;
    if(r.arena_bytes&&!detail::add(r.arena_bytes,63))return Status::Overflow;
    if(r.arena_bytes>config.max_workspace_bytes)return Status::Budget;
    *out=r;return Status::Ok;
}
}

Status Runtime::requirements(const ModelBundle& bundle,const RuntimeConfig& config,Requirements* out) noexcept {
    return detail::runtime_requirements(bundle,config,out,nullptr);
}

Status Runtime::prepare_precomputed_rgb24(const ModelBundle& bundle,const RuntimeConfig& config,
    Bytes table,Runtime* out) noexcept {
#if !FLASH_CHROMA_ENABLE_DIRECT
    (void)bundle;(void)config;(void)table;(void)out;
    return Status::Unsupported;
#else
    if(!out||!table.data)return Status::Null;
    if(!fc_core::fc_detail_span_valid(out,sizeof(*out))||
       !fc_core::fc_detail_span_valid(table.data,table.size))return Status::Overflow;
    if(config.representation!=Representation::DirectRGB24)return Status::Range;
    if(table.size!=detail::colours*3+4)return Status::Size;
    if(table.size>config.max_workspace_bytes)return Status::Budget;
    Backend backend;const auto resolved=detail::resolve(config,&backend);
    if(resolved!=Status::Ok)return resolved;
    for(std::size_t i=detail::colours*3;i<table.size;++i)if(table.data[i])return Status::Format;
    if(fc_core::fc_detail_intersects(out,sizeof(*out),&bundle,sizeof(bundle))||
       fc_core::fc_detail_intersects(out,sizeof(*out),&config,sizeof(config))||
       fc_core::fc_detail_intersects(out,sizeof(*out),table.data,table.size)||
       fc_core::fc_detail_intersects(table.data,table.size,&bundle,sizeof(bundle))||
       fc_core::fc_detail_intersects(table.data,table.size,&config,sizeof(config)))return Status::Overlap;
    fc_core::fc_model checked[4]{};
    Requirements resources{};resources.object_bytes=sizeof(Runtime);
    resources.persistent_bytes=table.size;resources.arena_bytes=table.size;resources.alignment=1;
    for(unsigned s=0;s<4;++s) {
        const auto status=fc_core::fc_model_init(checked+s,bundle.models[s],bundle.sidecars[s]);
        if(status!=fc_core::FC_OK)return static_cast<Status>(status);
        const Bytes inputs[2]={bundle.models[s],bundle.sidecars[s]};
        for(const auto input:inputs) {
            if(fc_core::fc_detail_intersects(out,sizeof(*out),input.data,input.size)||
               fc_core::fc_detail_intersects(table.data,table.size,input.data,input.size))return Status::Overlap;
            if(!detail::add(resources.model_bytes,input.size))return Status::Overflow;
        }
    }
    out->ready_=false;out->config_=config;out->resources_=resources;out->backend_=backend;
    for(unsigned s=0;s<4;++s)out->models_[s]=checked[s];
    const fc_core::fc_model* pointers[4]={out->models_,out->models_+1,out->models_+2,out->models_+3};
    const auto chained=fc_core::fc_chain_init(&out->chain_,pointers);
    if(chained!=fc_core::FC_OK)return static_cast<Status>(chained);
    out->arena_=table.data;out->direct_=table.data;out->palette_=nullptr;out->palette_count_=0;
    out->prepared_cache_=false;out->prepared_cache_entries_=0;out->ready_=true;
    return Status::Ok;
#endif
}

Status Runtime::prepare(const ModelBundle& bundle,const RuntimeConfig& config,Workspace workspace,Runtime* out) noexcept {
    if(!out)return Status::Null;
    if(!fc_core::fc_detail_span_valid(out,sizeof(*out)))return Status::Overflow;
    Requirements r;detail::PrepareDomain domain;
    const auto st=detail::runtime_requirements(bundle,config,&r,&domain);if(st!=Status::Ok)return st;
    if(r.arena_bytes&&(!workspace.data||workspace.bytes<r.arena_bytes))return Status::Budget;
    if(workspace.bytes&&!workspace.data)return Status::Null;
    if(workspace.data&&!fc_core::fc_detail_span_valid(workspace.data,workspace.bytes))return Status::Overflow;
    if(fc_core::fc_detail_intersects(out,sizeof(*out),&bundle,sizeof(bundle))||fc_core::fc_detail_intersects(out,sizeof(*out),&config,sizeof(config))||
       fc_core::fc_detail_intersects(workspace.data,workspace.bytes,&bundle,sizeof(bundle))||fc_core::fc_detail_intersects(workspace.data,workspace.bytes,&config,sizeof(config)))return Status::Overlap;
    if(fc_core::fc_detail_intersects(out,sizeof(*out),workspace.data,workspace.bytes))return Status::Overlap;
    for(unsigned s=0;s<4;++s) {
        const Bytes inputs[2]={bundle.models[s],bundle.sidecars[s]};
        for(const auto bytes:inputs)if(fc_core::fc_detail_intersects(out,sizeof(*out),bytes.data,bytes.size)||fc_core::fc_detail_intersects(workspace.data,workspace.bytes,bytes.data,bytes.size))return Status::Overlap;
    }
    out->ready_=false;out->prepared_cache_=false;out->prepared_cache_entries_=0;
    out->config_=config;out->resources_=r;
    detail::resolve(config,&out->backend_);
    for(unsigned s=0;s<4;++s)fc_core::fc_model_init(out->models_+s,bundle.models[s],bundle.sidecars[s]);
    const fc_core::fc_model* ptrs[4]={out->models_,out->models_+1,out->models_+2,out->models_+3};
    fc_core::fc_chain_init(&out->chain_,ptrs);
    auto address=reinterpret_cast<std::uintptr_t>(workspace.data);
    auto* arena=r.arena_bytes?reinterpret_cast<std::uint8_t*>((address+63u)&~std::uintptr_t{63}):nullptr;
    out->arena_=arena;out->direct_=nullptr;out->palette_=nullptr;out->palette_count_=0;
#if FLASH_CHROMA_ENABLE_AVX2
    const std::size_t packed=out->backend_==Backend::Avx2?detail::packed_bytes(out->models_):0;
#elif FLASH_CHROMA_ENABLE_DIRECT
    const std::size_t packed=0;
#endif
    if(config.representation==Representation::Sparse) {
#if FLASH_CHROMA_ENABLE_AVX2
        if(packed)detail::pack_views(out->models_,arena,out->packed_);
#endif
        out->ready_=true;return Status::Ok;
    }
#if FLASH_CHROMA_ENABLE_DIRECT
    auto* temporary=arena+r.persistent_bytes;
#if FLASH_CHROMA_ENABLE_AVX2
    if(packed)detail::pack_views(out->models_,temporary,out->packed_);
#endif
    out->direct_=arena;
#if FLASH_CHROMA_ENABLE_PREPARE_CACHE
    if(domain.proven&&out->backend_==Backend::Avx2) {
        const bool rgb=config.representation==Representation::DirectRGB24;
        const bool narrow=config.representation==Representation::DirectU8;
        auto* palette=rgb?nullptr:reinterpret_cast<std::uint32_t*>(arena+detail::colours*(narrow?1:2));
        if(detail::prepare_cached_direct(out->packed_,domain,config,arena,temporary+packed,palette,&out->palette_count_)) {
            out->palette_=palette;out->prepared_cache_=true;out->prepared_cache_entries_=domain.entries;
            out->ready_=true;return Status::Ok;
        }
    }
#endif
    if(config.representation==Representation::DirectRGB24) {
        const std::size_t blocks=detail::colours/config.block_pixels+(detail::colours%config.block_pixels!=0);
#if FLASH_CHROMA_ENABLE_OPENMP
        const int workers=omp_in_parallel()?1:static_cast<int>(config.threads);
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
        for(long long block=0;block<static_cast<long long>(blocks);++block) {
            const std::size_t begin=std::size_t(block)*config.block_pixels;
            const std::size_t n=(detail::colours-begin<config.block_pixels)?detail::colours-begin:config.block_pixels;
            auto* p=arena+begin*3;
            for(std::size_t i=0;i<n;++i)detail::store_rgb(p+i*3,std::uint32_t(begin+i));
            std::size_t done=0;
#if FLASH_CHROMA_ENABLE_AVX2
            if(out->backend_==Backend::Avx2) {done=n&~std::size_t{7};detail::sparse8(out->packed_,p,p,done);}
#endif
            for(;done<n;++done)fc_core::fc_map_pixel(&out->chain_,p+3*done,p+3*done);
        }
        for(unsigned i=0;i<4;++i)arena[detail::colours*3+i]=0;
        out->ready_=true;return Status::Ok;
    }
    const bool narrow=config.representation==Representation::DirectU8;
    const std::size_t limit=narrow?256:65536, slots=narrow?1024:131072;
    auto* palette=reinterpret_cast<std::uint32_t*>(arena+detail::colours*(narrow?1:2));
    auto* keys=reinterpret_cast<std::uint32_t*>(temporary+packed);
    auto* values=keys+slots;auto* colours=reinterpret_cast<std::uint8_t*>(values+slots);
    for(std::size_t i=0;i<slots;++i)keys[i]=0xffffffffu;
    for(std::size_t i=0;i<limit;++i)palette[i]=0;
    std::uint32_t count=0;
    for(std::size_t begin=0;begin<detail::colours;begin+=4096) {
        for(std::size_t i=0;i<4096;++i)detail::store_rgb(colours+i*3,std::uint32_t(begin+i));
#if FLASH_CHROMA_ENABLE_AVX2
        if(out->backend_==Backend::Avx2)detail::sparse8(out->packed_,colours,colours,4096);
        else
#endif
        for(std::size_t i=0;i<4096;++i)fc_core::fc_map_pixel(&out->chain_,colours+i*3,colours+i*3);
        for(std::size_t i=0;i<4096;++i) {
            const auto colour=detail::rgb32(colours+i*3);
            std::size_t slot=(std::uint32_t(colour*2654435761u))>>(narrow?22:15);
            while(keys[slot]!=0xffffffffu&&keys[slot]!=colour)slot=(slot+1)&(slots-1);
            if(keys[slot]==0xffffffffu) {
                if(count==limit)return Status::Capacity;
                keys[slot]=colour;values[slot]=count;palette[count++]=colour;
            }
            const std::uint32_t id=values[slot];
            if(narrow)arena[begin+i]=std::uint8_t(id);
            else reinterpret_cast<std::uint16_t*>(arena)[begin+i]=std::uint16_t(id);
        }
    }
    out->palette_=palette;out->palette_count_=count;out->ready_=true;return Status::Ok;
#else
    return Status::Unsupported;
#endif
}

Status Runtime::apply(const std::uint8_t* src,std::size_t src_bytes,std::size_t src_stride,
    std::uint8_t* dst,std::size_t dst_bytes,std::size_t dst_stride,std::size_t width,std::size_t height) const noexcept {
    if(!ready_)return Status::State;
    const auto checked=fc_core::fc_validate_rgb8(&chain_,src,src_bytes,src_stride,dst,dst_bytes,dst_stride,width,height);
    if(checked!=fc_core::FC_OK)return static_cast<Status>(checked);
    if(!width||!height)return Status::Ok;
    const std::size_t source_span=(height-1)*src_stride+width*3,destination_span=(height-1)*dst_stride+width*3;
    if(fc_core::fc_detail_intersects(src,source_span,this,sizeof(*this))||fc_core::fc_detail_intersects(dst,destination_span,this,sizeof(*this))||
       fc_core::fc_detail_intersects(src,source_span,arena_,resources_.persistent_bytes)||fc_core::fc_detail_intersects(dst,destination_span,arena_,resources_.persistent_bytes))return Status::Overlap;
    const std::size_t row_blocks=width/config_.block_pixels+(width%config_.block_pixels!=0);
    if(height>(std::numeric_limits<std::size_t>::max)()/row_blocks)return Status::Overflow;
    const std::size_t blocks=height*row_blocks;
    if(blocks>static_cast<std::size_t>((std::numeric_limits<long long>::max)()))return Status::Overflow;
#if FLASH_CHROMA_ENABLE_OPENMP
    const int workers=omp_in_parallel()?1:static_cast<int>(config_.threads);
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
    for(long long task=0;task<static_cast<long long>(blocks);++task) {
        const std::size_t row=std::size_t(task)/row_blocks,first=(std::size_t(task)%row_blocks)*config_.block_pixels;
        const std::size_t n=(width-first<config_.block_pixels)?width-first:config_.block_pixels;
        const auto* input=src+row*src_stride+first*3;auto* output=dst+row*dst_stride+first*3;
        std::size_t done=0;
#if FLASH_CHROMA_ENABLE_AVX2
        if(backend_==Backend::Avx2) {
            done=n&~std::size_t{7};
            if(config_.representation==Representation::Sparse)detail::sparse8(packed_,input,output,done);
#if FLASH_CHROMA_ENABLE_DIRECT
            else detail::direct8(direct_,palette_,config_.representation,input,output,done);
#endif
        }
#endif
        for(;done<n;++done) {
            const auto* p=input+done*3;auto* q=output+done*3;
            if(config_.representation==Representation::Sparse)fc_core::fc_map_pixel(&chain_,p,q);
#if FLASH_CHROMA_ENABLE_DIRECT
            else {const auto code=detail::rgb32(p);std::uint32_t value;
                if(config_.representation==Representation::DirectRGB24)value=detail::rgb32(direct_+std::size_t(code)*3);
                else if(config_.representation==Representation::DirectU8)value=palette_[direct_[code]];
                else value=palette_[reinterpret_cast<const std::uint16_t*>(direct_)[code]];
                detail::store_rgb(q,value);
            }
#endif
        }
    }
    return Status::Ok;
}
}
#endif

/* 连续目标到离散执行计划的无堆选择器；所有误差及时间结论仅属于绑定的验证上下文。 */
#ifndef FLASH_CHROMA_SELECTION_INCLUDED
#define FLASH_CHROMA_SELECTION_INCLUDED
#include <limits>

namespace fc {

enum class Goal { Balanced, Fastest, Accurate, Compact };
enum class SelectionStatus { Ok, InvalidRequest, InvalidCandidate, NoFeasible, BufferTooSmall };

struct Preference {
    double accuracy = 1.0;
    double speed = 1.0;
    double compactness = 1.0;
};

struct Candidate {
    const char* id = nullptr;
    const char* context = nullptr;
    const char* model_id = nullptr;
    const char* evidence = nullptr;
    RuntimeConfig config{};
    double mean_error = std::numeric_limits<double>::quiet_NaN();
    double worst_image_mean = std::numeric_limits<double>::quiet_NaN();
    double batch_ms = std::numeric_limits<double>::quiet_NaN();
    std::size_t runtime_bytes = 0;
    std::size_t workspace_bytes = 0;
    bool correctness_verified = false;
    bool accuracy_verified = false;
    bool resources_verified = false;
    bool time_verified = false;
    bool time_stable = false;
};

struct Request {
    const char* context = nullptr;
    Target target = RuntimeConfig{}.target;
    Goal goal = Goal::Balanced;
    Preference preference{};
    unsigned backend_mask = available_backends() & 3u;
    unsigned max_threads = (compiled_capabilities() & 4u) ? 256u : 1u;
    bool use_time = true;
    bool require_stable_time = true;
    bool has_error_limit = false;
    double max_image_mean_error = 0;
    bool has_time_limit = false;
    double max_batch_ms = 0;
    std::size_t max_runtime_bytes = (std::numeric_limits<std::size_t>::max)();
    std::size_t max_workspace_bytes = (std::numeric_limits<std::size_t>::max)();
};

struct RejectionCounts {
    std::size_t context = 0, target = 0, capability = 0;
    std::size_t unverified = 0, unstable_time = 0, budget = 0;
};

struct SelectionView {
    std::size_t index = (std::numeric_limits<std::size_t>::max)();
    double score = 0;
    bool provisional = false;
    std::size_t eligible = 0;
    std::size_t frontier_size = 0;
    RejectionCounts rejected{};
};

namespace selection_detail {
inline bool text(const char* value) { return value && *value; }
inline bool number(double value) {
    return value >= 0 && value <= (std::numeric_limits<double>::max)();
}
inline int compare(const char* a, const char* b) {
    while (*a && *a == *b) { ++a; ++b; }
    const unsigned char x = static_cast<unsigned char>(*a), y = static_cast<unsigned char>(*b);
    return x < y ? -1 : (x > y ? 1 : 0);
}
inline bool valid_target(Target value) {
    return value == Target::Desktop || value == Target::Mobile ||
           value == Target::Embedded || value == Target::Portable;
}
inline bool valid_request(const Request& r) {
    const auto& w = r.preference;
    if (!text(r.context) || !valid_target(r.target) || !r.backend_mask || (r.backend_mask & ~3u) ||
        !r.max_threads || r.max_threads > 256 ||
        !number(w.accuracy) || !number(w.speed) || !number(w.compactness) ||
        w.accuracy > 1 || w.speed > 1 || w.compactness > 1 ||
        !(w.accuracy + w.speed + w.compactness > 0) ||
        (r.has_error_limit && !number(r.max_image_mean_error)) ||
        (r.has_time_limit && !number(r.max_batch_ms))) return false;
    if (r.goal != Goal::Balanced && r.goal != Goal::Fastest &&
        r.goal != Goal::Accurate && r.goal != Goal::Compact) return false;
    return r.use_time || (r.goal != Goal::Fastest && !r.has_time_limit &&
                         (r.goal != Goal::Balanced || w.speed == 0));
}
inline bool valid_candidate(const Candidate& c) {
    if (!text(c.id) || !text(c.context) || !text(c.model_id) || !text(c.evidence) ||
        !valid_target(c.config.target) || !c.config.threads || c.config.threads > 256 ||
        !c.config.block_pixels || (c.config.backend != Backend::Scalar && c.config.backend != Backend::Avx2) ||
        (c.config.representation != Representation::Sparse && c.config.representation != Representation::DirectU8 &&
         c.config.representation != Representation::DirectU16 && c.config.representation != Representation::DirectRGB24)) return false;
    if (c.accuracy_verified && (!number(c.mean_error) || !number(c.worst_image_mean) ||
                               c.worst_image_mean < c.mean_error)) return false;
    if (c.time_verified && (!number(c.batch_ms) || c.batch_ms == 0)) return false;
    if (c.time_stable && !c.time_verified) return false;
    if (c.resources_verified && (c.workspace_bytes > c.runtime_bytes ||
                                c.workspace_bytes > c.config.max_workspace_bytes)) return false;
    if ((c.config.target == Target::Embedded || c.config.target == Target::Portable) &&
        (c.config.backend != Backend::Scalar || c.config.representation != Representation::Sparse ||
         c.config.threads != 1)) return false;
    return true;
}
inline bool eligible(const Candidate& c, const Request& r, RejectionCounts* counts = nullptr) {
    if (compare(c.context, r.context)) { if (counts) ++counts->context; return false; }
    if (c.config.target != r.target) { if (counts) ++counts->target; return false; }
    const unsigned bit = c.config.backend == Backend::Avx2 ? 2u : 1u;
    bool compiled_plan = true;
#if FLASH_CHROMA_TARGET >= 3
    if (c.config.target == Target::Desktop || c.config.target == Target::Mobile) compiled_plan = false;
#endif
#if !FLASH_CHROMA_ENABLE_DIRECT
    if (c.config.representation != Representation::Sparse) compiled_plan = false;
#endif
    if (c.config.block_pixels > (std::numeric_limits<std::size_t>::max)()/3) compiled_plan = false;
    if (!compiled_plan || !(bit & r.backend_mask & available_backends()) || c.config.threads > r.max_threads ||
        (c.config.threads > 1 && !(compiled_capabilities() & 4u))) {
        if (counts) ++counts->capability;
        return false;
    }
    if (!c.correctness_verified || !c.accuracy_verified || !c.resources_verified ||
        (r.use_time && !c.time_verified)) { if (counts) ++counts->unverified; return false; }
    if (r.use_time && r.require_stable_time && !c.time_stable) {
        if (counts) ++counts->unstable_time;
        return false;
    }
    if ((r.has_error_limit && !(c.worst_image_mean < r.max_image_mean_error)) ||
        (r.has_time_limit && c.batch_ms > r.max_batch_ms) ||
        c.runtime_bytes > r.max_runtime_bytes || c.workspace_bytes > r.max_workspace_bytes) {
        if (counts) ++counts->budget;
        return false;
    }
    return true;
}
inline bool dominates(const Candidate& a, const Candidate& b, const Request& r) {
    /* 先应用逐图/工作区预算，再计算三维前沿；原catalog须保留所有候选以便改变预算重选。 */
    return a.mean_error <= b.mean_error && (!r.use_time || a.batch_ms <= b.batch_ms) &&
           a.runtime_bytes <= b.runtime_bytes &&
           (a.mean_error < b.mean_error || (r.use_time && a.batch_ms < b.batch_ms) ||
            a.runtime_bytes < b.runtime_bytes);
}
inline bool on_frontier(const Candidate* c, std::size_t count, std::size_t index, const Request& r) {
    if (!eligible(c[index], r)) return false;
    for (std::size_t j = 0; j < count; ++j)
        if (j != index && eligible(c[j], r) && dominates(c[j], c[index], r)) return false;
    return true;
}
inline SelectionStatus validate(const Candidate* c, std::size_t n, const Request& r) {
    if (!valid_request(r) || (n && !c)) return SelectionStatus::InvalidRequest;
    for (std::size_t i = 0; i < n; ++i) {
        if (!valid_candidate(c[i])) return SelectionStatus::InvalidCandidate;
        for (std::size_t j = 0; j < i; ++j)
            if (!compare(c[j].id, c[i].id)) return SelectionStatus::InvalidCandidate;
    }
    return SelectionStatus::Ok;
}
inline double normalized(double value, double minimum, double maximum) {
    if (!(maximum > minimum)) return 0;
    /* 所有量非负，因此差值不溢出；直接相减还能保留相邻浮点数的尺度。 */
    return (value - minimum) / (maximum - minimum);
}
inline bool tie_less(const Candidate& a, const Candidate& b, const Request& r) {
    if (a.mean_error != b.mean_error) return a.mean_error < b.mean_error;
    if (a.worst_image_mean != b.worst_image_mean) return a.worst_image_mean < b.worst_image_mean;
    if (r.use_time && a.batch_ms != b.batch_ms) return a.batch_ms < b.batch_ms;
    if (a.runtime_bytes != b.runtime_bytes) return a.runtime_bytes < b.runtime_bytes;
    if (a.workspace_bytes != b.workspace_bytes) return a.workspace_bytes < b.workspace_bytes;
    return compare(a.id, b.id) < 0;
}
} // namespace selection_detail

/* 查询需要容量时可传nullptr/0；容量不足不修改indices。 */
inline SelectionStatus frontier(const Candidate* candidates, std::size_t count, const Request& request,
                                std::size_t* indices, std::size_t capacity, std::size_t* required) {
    if (!required || (capacity && !indices)) return SelectionStatus::InvalidRequest;
    const auto status = selection_detail::validate(candidates, count, request);
    if (status != SelectionStatus::Ok) return status;
    std::size_t needed = 0;
    for (std::size_t i = 0; i < count; ++i)
        if (selection_detail::on_frontier(candidates, count, i, request)) ++needed;
    *required = needed;
    if (!needed) return SelectionStatus::NoFeasible;
    if (capacity < needed) return SelectionStatus::BufferTooSmall;
    std::size_t out = 0;
    for (std::size_t i = 0; i < count; ++i)
        if (selection_detail::on_frontier(candidates, count, i, request)) indices[out++] = i;
    return SelectionStatus::Ok;
}

inline SelectionStatus select(const Candidate* candidates, std::size_t count,
                              const Request& request, SelectionView* output) {
    if (!output) return SelectionStatus::InvalidRequest;
    const auto status = selection_detail::validate(candidates, count, request);
    if (status != SelectionStatus::Ok) return status;
    SelectionView result;
    double min_e = (std::numeric_limits<double>::max)(), max_e = 0;
    double min_t = min_e, max_t = 0;
    std::size_t min_m = (std::numeric_limits<std::size_t>::max)(), max_m = 0;
    for (std::size_t i = 0; i < count; ++i) {
        const auto& c = candidates[i];
        if (!selection_detail::eligible(c, request, &result.rejected)) continue;
        ++result.eligible;
        if (c.mean_error < min_e) min_e = c.mean_error;
        if (c.mean_error > max_e) max_e = c.mean_error;
        if (request.use_time && c.batch_ms < min_t) min_t = c.batch_ms;
        if (request.use_time && c.batch_ms > max_t) max_t = c.batch_ms;
        if (c.runtime_bytes < min_m) min_m = c.runtime_bytes;
        if (c.runtime_bytes > max_m) max_m = c.runtime_bytes;
    }
    if (!result.eligible) { *output = result; return SelectionStatus::NoFeasible; }
    Preference weights = request.preference;
    if (request.goal == Goal::Fastest) weights = {0, 1, 0};
    else if (request.goal == Goal::Accurate) weights = {1, 0, 0};
    else if (request.goal == Goal::Compact) weights = {0, 0, 1};
    const double sum = weights.accuracy + weights.speed + weights.compactness;
    double best = (std::numeric_limits<double>::max)();
    for (std::size_t i = 0; i < count; ++i) {
        if (!selection_detail::on_frontier(candidates, count, i, request)) continue;
        ++result.frontier_size;
        const auto& c = candidates[i];
        const double error = selection_detail::normalized(c.mean_error, min_e, max_e);
        const double time = request.use_time ? selection_detail::normalized(c.batch_ms, min_t, max_t) : 0;
        const double memory = max_m > min_m ? double(c.runtime_bytes - min_m) / double(max_m - min_m) : 0;
        const double score = (weights.accuracy * error + weights.speed * time + weights.compactness * memory) / sum;
        if (score < best || (score == best && selection_detail::tie_less(c, candidates[result.index], request))) {
            best = score; result.index = i;
        }
    }
    result.score = best;
    result.provisional = !request.use_time || !candidates[result.index].time_stable;
    *output = result;
    return SelectionStatus::Ok;
}

inline const char* selection_status_string(SelectionStatus status) {
    switch (status) {
    case SelectionStatus::Ok: return "已选择绑定上下文的可执行配置";
    case SelectionStatus::InvalidRequest: return "请求非法：检查连续权重、上下文、目标与预算";
    case SelectionStatus::InvalidCandidate: return "候选记录非法：检查唯一身份、指标及执行配置";
    case SelectionStatus::NoFeasible: return "无满足验证、能力和预算要求的候选";
    case SelectionStatus::BufferTooSmall: return "前沿输出容量不足，未写入索引";
    }
    return "未知选择状态";
}
} // namespace fc
#endif

#endif

#include <array>
#include <algorithm>
#include <limits>
#include <stdexcept>
#include <vector>

namespace fc_framework {

constexpr std::size_t dense_nodes = std::size_t{256} * 256 * 256;
constexpr std::size_t dense_values = dense_nodes * 3;
enum class Grid { FrameworkStep, UniformRounded };
enum class Interpolation { TetraQ16, TrilinearQ16 };
struct FitOptions {
    Grid grid = Grid::UniformRounded;
    bool prove_structure = true;
    // 自定义三轴只由LUT预处理生成；空数组保持原来的固定网格。
    std::array<std::vector<unsigned>, 3> axes{};
};

struct Stage {
    unsigned m = 0;
    std::vector<std::uint8_t> blob;
    std::vector<std::uint8_t> fractions;
    Interpolation interpolation = Interpolation::TetraQ16;
    bool separable_proven = false;
    std::array<std::array<std::uint8_t, 256>, 3> curves{};
    std::size_t proof_nodes = 0;
    std::size_t model_bytes() const noexcept { return blob.size() + fractions.size(); }
    std::size_t sidecar_bytes() const noexcept { return fractions.size() + (separable_proven ? 3u * 256u : 0u); }
    const std::uint8_t* nodes_data() const noexcept {
        return blob.empty() ? nullptr : blob.data() + 16u + 12u * m + 3840u;
    }
    std::size_t node_bytes() const noexcept { return std::size_t(m) * m * m * 3; }
};

namespace detail {
inline void put32(std::vector<std::uint8_t>& bytes, std::size_t at, std::uint32_t value) {
    for (unsigned i = 0; i != 4; ++i) bytes[at + i] = static_cast<std::uint8_t>(value >> (8 * i));
}
inline std::uint8_t source(const std::vector<std::uint16_t>& raw,
                           unsigned r, unsigned g, unsigned b, unsigned channel) noexcept {
    const std::size_t at = ((std::size_t(b) * 256 + g) * 256 + r) * 3 + 2 - channel;
    return static_cast<std::uint8_t>(raw[at] / 16);
}
inline bool overlaps(const void* a, std::size_t an, const void* b, std::size_t bn) noexcept {
    return fc_core::fc_detail_intersects(a, an, b, bn) != 0;
}
} // namespace detail

inline Stage prepare_stage(const std::vector<std::uint16_t>& raw, unsigned m,
                           FitOptions options = {}) {
    if (raw.size() != dense_values) throw std::invalid_argument("原始LUT必须含256³个三通道节点");
    if (m < 17 || m > 33) throw std::invalid_argument("每级稀疏尺寸必须在17..33内");
    if (options.grid != Grid::FrameworkStep && options.grid != Grid::UniformRounded)
        throw std::invalid_argument("未知网格策略");
    Stage result;
    result.m = m;
    result.separable_proven = options.prove_structure;
    if (options.prove_structure) {
        for (unsigned code = 0; code != 256; ++code) {
            result.curves[0][code] = detail::source(raw, code, 0, 0, 0);
            result.curves[1][code] = detail::source(raw, 0, code, 0, 1);
            result.curves[2][code] = detail::source(raw, 0, 0, code, 2);
        }
    }
    // 检查每个原节点，不以采样、文件名或样图代替结构证明。
    // 忠实保留框架的uint16除16再转uint8语义，包括大于4095时的回绕。
    if (options.prove_structure) for (unsigned b = 0; b != 256; ++b) for (unsigned g = 0; g != 256; ++g) {
        const auto* row = raw.data() + ((std::size_t(b) * 256 + g) * 256) * 3;
        for (unsigned r = 0; r != 256; ++r) {
            const auto v0 = static_cast<std::uint8_t>(row[r * 3] / 16);
            const auto v1 = static_cast<std::uint8_t>(row[r * 3 + 1] / 16);
            const auto v2 = static_cast<std::uint8_t>(row[r * 3 + 2] / 16);
            ++result.proof_nodes;
            if (v2 != result.curves[0][r] || v1 != result.curves[1][g] || v0 != result.curves[2][b])
                result.separable_proven = false;
        }
    }
    std::array<std::array<unsigned, 33>, 3> grids{};
    const bool custom = !options.axes[0].empty() || !options.axes[1].empty() || !options.axes[2].empty();
    for (unsigned a = 0; a != 3; ++a) {
        if (custom) {
            const auto& axis = options.axes[a];
            if (axis.size() != m || axis.front() != 0 || axis.back() != 255)
                throw std::invalid_argument("自定义轴必须有m个整数节点并包含0和255");
            for (unsigned i = 1; i != m; ++i) if (axis[i] <= axis[i-1] || axis[i] > 255)
                throw std::invalid_argument("自定义轴必须严格递增且在RGB8域内");
            std::copy(axis.begin(), axis.end(), grids[a].begin());
        } else {
            for (unsigned i = 0; i != m; ++i)
                grids[a][i] = options.grid == Grid::FrameworkStep ? i * (256 / (m - 1))
                    : (i * 255 + (m - 1) / 2) / (m - 1);
            grids[a][m - 1] = 255;
        }
    }
    const std::size_t nodes_at = 16u + 12u * m + 3840u;
    result.blob.resize(nodes_at + std::size_t(m) * m * m * 3);
    auto& bytes = result.blob;
    bytes[0] = 'S'; bytes[1] = 'L'; bytes[2] = 'U'; bytes[3] = 'T';
    detail::put32(bytes, 4, 1); detail::put32(bytes, 8, m);
    for (unsigned axis = 0; axis != 3; ++axis) {
        const auto& grid = grids[axis];
        for (unsigned i = 0; i != m; ++i) {
            const float value = static_cast<float>(grid[i]);
            std::uint32_t bits; std::memcpy(&bits, &value, 4);
            detail::put32(bytes, 16 + (axis * m + i) * 4, bits);
        }
        unsigned cell = 0;
        for (unsigned code = 0; code != 256; ++code) {
            while (cell + 1 < m - 1 && code >= grid[cell + 1]) ++cell;
            const unsigned span = grid[cell + 1] - grid[cell];
            const unsigned fraction = ((code - grid[cell]) * 65536u + span / 2) / span;
            bytes[16 + 12 * m + axis * 256 + code] = static_cast<std::uint8_t>(cell);
            detail::put32(bytes, 16 + 12 * m + 768 + (axis * 256 + code) * 4, fraction);
        }
    }
    for (unsigned r = 0; r != m; ++r) for (unsigned g = 0; g != m; ++g)
        for (unsigned b = 0; b != m; ++b) for (unsigned c = 0; c != 3; ++c)
            bytes[nodes_at + ((std::size_t(r) * m + g) * m + b) * 3 + c] =
                detail::source(raw, grids[0][r], grids[1][g], grids[2][b], c);
    fc_core::fc_model checked{};
    if (fc_core::fc_model_init(&checked, {bytes.data(), bytes.size()}, {nullptr, 0}) != fc_core::FC_OK)
        throw std::runtime_error("稀疏模型序列化未通过运行库校验");
    return result;
}

namespace detail {
inline fc_core::fc_bytes sidecar(const Stage& stage) noexcept {
    return {stage.fractions.empty() ? nullptr : stage.fractions.data(), stage.fractions.size()};
}
inline fc_core::fc_model view(const Stage& stage) {
    fc_core::fc_model result{};
    if ((stage.interpolation != Interpolation::TetraQ16 && stage.interpolation != Interpolation::TrilinearQ16) ||
        fc_core::fc_model_init(&result, {stage.blob.data(), stage.blob.size()}, sidecar(stage)) != fc_core::FC_OK || result.m != stage.m)
        throw std::invalid_argument("精度模型的节点、坐标或插值类型非法");
    return result;
}
inline std::uint32_t code(const std::uint8_t* c) noexcept {
    return std::uint32_t(c[0]) | (std::uint32_t(c[1]) << 8) | (std::uint32_t(c[2]) << 16);
}
// 两种插值都在每一级末尾只舍入一次；三线性使用精确48位权重。
inline std::uint32_t map(const fc_core::fc_model& m, Interpolation kind, std::uint32_t input) noexcept {
    const unsigned colour[3] = {input & 255u, (input >> 8) & 255u, input >> 16};
    const std::size_t stride[3] = {std::size_t(m.m)*m.m, m.m, 1};
    const std::size_t base = m.index[colour[0]]*stride[0] + m.index[256+colour[1]]*stride[1] + m.index[512+colour[2]];
    std::uint32_t output = 0;
    for (unsigned c = 0; c != 3; ++c) {
        const auto* table = m.sidecar.data ? m.sidecar.data + c*3072 : m.fraction_le;
        std::uint32_t f[3];
        for (unsigned a = 0; a != 3; ++a) f[a] = fc_core::fc_detail_read32(table + (a*256+colour[a])*4);
        std::uint64_t sum = 0;
        if (kind == Interpolation::TrilinearQ16) {
            for (unsigned mask = 0; mask != 8; ++mask) {
                std::size_t node = base; std::uint64_t weight = 1;
                for (unsigned a = 0; a != 3; ++a) {
                    const bool hi = (mask & (4u >> a)) != 0;
                    node += hi ? stride[a] : 0; weight *= hi ? f[a] : 65536u-f[a];
                }
                sum += weight*m.nodes[node*3+c];
            }
            output |= std::uint32_t((sum+(std::uint64_t{1}<<47))>>48) << (c*8);
        } else {
            std::size_t d[3] = {stride[0],stride[1],1};
            if(f[0]<f[1]){std::swap(f[0],f[1]);std::swap(d[0],d[1]);}
            if(f[1]<f[2]){std::swap(f[1],f[2]);std::swap(d[1],d[2]);}
            if(f[0]<f[1]){std::swap(f[0],f[1]);std::swap(d[0],d[1]);}
            sum = std::uint64_t(65536-f[0])*m.nodes[base*3+c] + std::uint64_t(f[0]-f[1])*m.nodes[(base+d[0])*3+c]
                + std::uint64_t(f[1]-f[2])*m.nodes[(base+d[0]+d[1])*3+c] + std::uint64_t(f[2])*m.nodes[(base+stride[0]+stride[1]+1)*3+c];
            output |= std::uint32_t((sum+32768)>>16) << (c*8);
        }
    }
    return output;
}
} // namespace detail

struct Options {
    fc::Backend backend = fc::Backend::Auto;
    fc::Representation representation = fc::Representation::Sparse;
    bool structure = true;
    unsigned threads = 1;
    std::size_t block_pixels = 65536;
    std::size_t max_workspace_bytes = 64 * fc::MiB;
};
struct Info {
    bool structured = false;
    fc::Backend backend = fc::Backend::Scalar;
    fc::Representation representation = fc::Representation::Sparse;
    unsigned threads = 1;
    std::size_t model_bytes = 0, sidecar_bytes = 0, arena_bytes = 0, object_bytes = 0;
    std::size_t proof_nodes = 0;
    std::uint32_t palette_entries = 0;
    // sidecar_bytes含model_bytes中的分输出坐标及object_bytes内曲线，不重复相加。
};

class Chain {
public:
    Chain() = default;
    Chain(const Chain&) = delete;
    Chain& operator=(const Chain&) = delete;
    Chain(Chain&&) = delete;
    Chain& operator=(Chain&&) = delete;

    fc::Status prepare(const std::array<const Stage*, 4>& stages, Options options = {}) {
        ready_ = false; info_ = {}; stages_ = {};
        mixed_ = false;
        std::vector<std::uint8_t>().swap(arena_);
        if (options.threads != 1) return fc::Status::Unsupported;
        if (!options.block_pixels) return fc::Status::Range;
        if (options.backend != fc::Backend::Auto && options.backend != fc::Backend::Scalar &&
            options.backend != fc::Backend::Avx2) return fc::Status::Unsupported;
        if (options.backend == fc::Backend::Avx2 && !(fc::available_backends() & 2u))
            return fc::Status::Unsupported;
        if (options.representation != fc::Representation::Sparse &&
            options.representation != fc::Representation::DirectU8 &&
            options.representation != fc::Representation::DirectU16 &&
            options.representation != fc::Representation::DirectRGB24) return fc::Status::Range;
        fc::ModelBundle bundle{};
        const fc_core::fc_model* pointers[4]{};
        bool structured = options.structure;
        for (unsigned i = 0; i != 4; ++i) {
            if (!stages[i]) return fc::Status::Null;
            const auto& stage = *stages[i];
            bundle.models[i] = {stage.blob.data(), stage.blob.size()};
            bundle.sidecars[i] = detail::sidecar(stage);
            const auto status = fc_core::fc_model_init(models_.data() + i, bundle.models[i], bundle.sidecars[i]);
            if (status != fc_core::FC_OK) return static_cast<fc::Status>(status);
            if (stage.m != models_[i].m) return fc::Status::Format;
            if (stage.interpolation != Interpolation::TetraQ16 && stage.interpolation != Interpolation::TrilinearQ16) return fc::Status::Format;
            mixed_ = mixed_ || stage.interpolation == Interpolation::TrilinearQ16;
            pointers[i] = models_.data() + i;
            structured = structured && stage.separable_proven && stage.proof_nodes == dense_nodes;
            info_.model_bytes += stage.model_bytes();
            info_.sidecar_bytes += stage.sidecar_bytes();
            info_.proof_nodes += stage.proof_nodes;
        }
        const auto status = fc_core::fc_chain_init(&validation_chain_, pointers);
        if (status != fc_core::FC_OK) return static_cast<fc::Status>(status);
        stages_ = stages;
        info_.object_bytes = sizeof(Chain) + 4 * sizeof(Stage);
        if (structured) {
            for (unsigned c = 0; c != 3; ++c) for (unsigned code = 0; code != 256; ++code) {
                unsigned value = code;
                for (const auto* stage : stages) value = stage->curves[c][value];
                composed_[c][code] = static_cast<std::uint8_t>(value);
            }
            info_.structured = true;
            info_.backend = fc::Backend::Scalar;
            info_.representation = fc::Representation::Sparse;
            info_.sidecar_bytes += 3 * 256;
            ready_ = true;
            return fc::Status::Ok;
        }
        if (mixed_) {
            if (options.representation != fc::Representation::Sparse && options.representation != fc::Representation::DirectRGB24)
                return fc::Status::Unsupported;
            info_.representation = options.representation;
            info_.backend = fc::Backend::Scalar;
            if (options.representation == fc::Representation::DirectRGB24) {
                const std::size_t bytes = dense_values + 4;
                if (bytes > options.max_workspace_bytes) return fc::Status::Budget;
                arena_.resize(bytes);
                for (std::uint32_t input = 0; input != dense_nodes; ++input) {
                    auto value = input;
                    for (unsigned s = 0; s != 4; ++s) value = detail::map(models_[s],stages_[s]->interpolation,value);
                    for(unsigned c=0;c!=3;++c)arena_[std::size_t(input)*3+c]=std::uint8_t(value>>(c*8));
                }
#if FLASH_CHROMA_ENABLE_AVX2
                if (options.backend != fc::Backend::Scalar && (fc::available_backends() & 2u)) info_.backend=fc::Backend::Avx2;
#endif
                info_.arena_bytes=arena_.size();
            }
            ready_=true;return fc::Status::Ok;
        }
        fc::RuntimeConfig config;
        config.threads = 1; config.backend = options.backend;
        config.representation = options.representation; config.block_pixels = options.block_pixels;
        config.max_workspace_bytes = options.max_workspace_bytes;
        fc::Requirements requirements;
        auto runtime_status = fc::Runtime::requirements(bundle, config, &requirements);
        if (runtime_status != fc::Status::Ok) return runtime_status;
        arena_.resize(requirements.arena_bytes);
        runtime_status = fc::Runtime::prepare(bundle, config, {arena_.data(), arena_.size()}, &runtime_);
        if (runtime_status != fc::Status::Ok) { std::vector<std::uint8_t>().swap(arena_); return runtime_status; }
        info_.backend = runtime_.selected_backend();
        info_.representation = config.representation;
        info_.arena_bytes = requirements.arena_bytes;
        info_.palette_entries = runtime_.palette_entries();
        ready_ = true;
        return fc::Status::Ok;
    }

    fc::Status apply(const std::uint8_t* input, std::uint8_t* output, std::size_t pixels) const noexcept {
        if (!ready_) return fc::Status::State;
        if (pixels > (std::numeric_limits<std::size_t>::max)() / 3) return fc::Status::Overflow;
        const std::size_t bytes = pixels * 3;
        const auto validation = fc_core::fc_validate_rgb8(&validation_chain_, input, bytes, bytes,
                                                         output, bytes, bytes, pixels, 1);
        if (validation != fc_core::FC_OK) return static_cast<fc::Status>(validation);
        if (!pixels) return fc::Status::Ok;
        if (detail::overlaps(output, bytes, this, sizeof(*this))) return fc::Status::Overlap;
        for (const Stage* stage : stages_)
            if (detail::overlaps(output, bytes, stage, sizeof(*stage))) return fc::Status::Overlap;
        if (!info_.structured && mixed_) {
            if(detail::overlaps(output,bytes,arena_.data(),arena_.size()))return fc::Status::Overlap;
#if FLASH_CHROMA_ENABLE_AVX2
            if(info_.representation==fc::Representation::DirectRGB24 && info_.backend==fc::Backend::Avx2){
                fc::detail::direct_rgb24_run(arena_.data(),input,output,pixels);return fc::Status::Ok;
            }
#endif
            for(std::size_t i=0;i<pixels;++i){
                auto value=detail::code(input+3*i);
                if(info_.representation==fc::Representation::DirectRGB24)value=detail::code(arena_.data()+std::size_t(value)*3);
                else for(unsigned s=0;s<4;++s)value=detail::map(models_[s],stages_[s]->interpolation,value);
                for(unsigned c=0;c<3;++c)output[3*i+c]=std::uint8_t(value>>(8*c));
            }
            return fc::Status::Ok;
        }
        if (!info_.structured)
            return runtime_.apply(input, bytes, bytes, output, bytes, bytes, pixels, 1);
        const auto* r = composed_[0].data();
        const auto* g = composed_[1].data();
        const auto* b = composed_[2].data();
        for (std::size_t i = 0; i != pixels; ++i) {
            output[i * 3] = r[input[i * 3]];
            output[i * 3 + 1] = g[input[i * 3 + 1]];
            output[i * 3 + 2] = b[input[i * 3 + 2]];
        }
        return fc::Status::Ok;
    }
    const Info& info() const noexcept { return info_; }
    bool ready() const noexcept { return ready_; }
private:
    bool ready_ = false;
    bool mixed_ = false;
    Info info_{};
    std::array<const Stage*, 4> stages_{};
    std::array<fc_core::fc_model, 4> models_{};
    fc_core::fc_chain validation_chain_{};
    std::array<std::array<std::uint8_t, 256>, 3> composed_{};
    std::vector<std::uint8_t> arena_;
    fc::Runtime runtime_;
};

} // namespace fc_framework
#endif

#include <cmath>
#include <chrono>

namespace fc_framework {
struct FitExperimentOptions {
    unsigned cg_max_iterations = 160;
    unsigned integer_sweeps = 8;
    double relative_tolerance = 1e-8;
    double regularization = 1e-5;
    bool guard_full_domain = true;
};
struct FitChannelReport {
    unsigned iterations = 0;
    double relative_residual = 0;
    bool converged = false;
};
struct FitError {
    std::uint64_t sse = 0;
    double mean = 0, linear_sse = 0;
    unsigned max_squared = 0;
};
struct FitReport {
    unsigned m = 0;
    std::size_t samples = 0, matrix_bytes = 0, temporary_bytes = 0;
    unsigned integer_sweeps = 0;
    std::size_t changed_nodes = 0;
    bool source_separable_skipped = false, candidate_used = false;
    std::array<FitChannelReport, 3> channels{};
    FitError baseline{}, candidate{};
    double linear_sse_before = 0, linear_sse_after = 0;
    double assembly_seconds = 0, solve_seconds = 0, evaluation_seconds = 0;
};

namespace fit_detail {
inline double seconds() {
    return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
inline std::uint32_t u32(const std::uint8_t* p) {
    return std::uint32_t(p[0]) | (std::uint32_t(p[1]) << 8) |
           (std::uint32_t(p[2]) << 16) | (std::uint32_t(p[3]) << 24);
}
struct Geometry {
    std::size_t node[4]{};
    unsigned mask[4]{};
    std::uint32_t weight[4]{};
};
struct Coordinates {
    std::array<std::array<unsigned, 256>, 3> index{};
    std::array<std::array<std::uint32_t, 256>, 3> fraction{};
    std::array<std::size_t, 8> delta{};
    unsigned m = 0;
    explicit Coordinates(const Stage& stage) : m(stage.m) {
        if(stage.interpolation!=Interpolation::TetraQ16||!stage.fractions.empty())
            throw std::invalid_argument("原始LS仅支持共享坐标四面体；分输出/三线性须使用precision拟合器");
        fc_core::fc_model checked{};
        if (fc_core::fc_model_init(&checked, {stage.blob.data(), stage.blob.size()}, {nullptr, 0}) != fc_core::FC_OK || checked.m != stage.m)
            throw std::invalid_argument("完整域拟合的初始Stage非法");
        for (unsigned a = 0; a != 3; ++a) for (unsigned v = 0; v != 256; ++v) {
            index[a][v] = checked.index[a * 256 + v];
            fraction[a][v] = u32(checked.fraction_le + (a * 256 + v) * 4);
        }
        for (unsigned mask = 0; mask != 8; ++mask)
            delta[mask] = ((mask & 4) ? std::size_t(m) * m : 0) + ((mask & 2) ? m : 0) + ((mask & 1) ? 1 : 0);
    }
    Geometry at(unsigned r, unsigned g, unsigned b) const {
        const std::size_t base = (std::size_t(index[0][r]) * m + index[1][g]) * m + index[2][b];
        std::uint32_t f[3] = {fraction[0][r], fraction[1][g], fraction[2][b]};
        unsigned mask[3] = {4, 2, 1};
        if (f[0] < f[1]) { std::swap(f[0], f[1]); std::swap(mask[0], mask[1]); }
        if (f[1] < f[2]) { std::swap(f[1], f[2]); std::swap(mask[1], mask[2]); }
        if (f[0] < f[1]) { std::swap(f[0], f[1]); std::swap(mask[0], mask[1]); }
        Geometry result;
        result.mask[0] = 0; result.mask[1] = mask[0]; result.mask[2] = mask[0] | mask[1]; result.mask[3] = 7;
        for (unsigned i = 0; i != 4; ++i) result.node[i] = base + delta[result.mask[i]];
        result.weight[0] = 65536 - f[0]; result.weight[1] = f[0] - f[1];
        result.weight[2] = f[1] - f[2]; result.weight[3] = f[2];
        return result;
    }
};

// 同一四面体任意两个顶点的位移仅含同号的轴步长，故每行只需15个邻居。
// 只存对角及7个正向邻居，上三角总量m³*8，矩阵乘法对称更新另半边。
struct Normal {
    std::size_t count;
    std::array<std::size_t, 8> delta;
    std::vector<std::array<double, 8>> h;
    std::vector<std::array<double, 3>> rhs;
    double target_squared_sum = 0;
    explicit Normal(const Coordinates& coordinates)
        : count(std::size_t(coordinates.m) * coordinates.m * coordinates.m), delta(coordinates.delta), h(count), rhs(count) {}
    void multiply(const std::vector<double>& x, std::vector<double>& out,
                  const std::vector<double>& regularizer) const {
        out.resize(count);
        for (std::size_t i = 0; i != count; ++i) out[i] = (h[i][0] + regularizer[i]) * x[i];
        for (std::size_t i = 0; i != count; ++i) for (unsigned k = 1; k != 8; ++k) {
            const double value = h[i][k];
            if (value == 0) continue;
            const std::size_t j = i + delta[k];
            if (j >= count) throw std::runtime_error("正规矩阵邻接越界");
            out[i] += value * x[j]; out[j] += value * x[i];
        }
    }
    double row_off_diagonal(std::size_t i, const std::vector<std::array<double, 3>>& x, unsigned channel) const {
        double sum = 0;
        for (unsigned k = 1; k != 8; ++k) {
            const std::size_t step = delta[k];
            if (i + step < count) sum += h[i][k] * x[i + step][channel];
            if (i >= step) sum += h[i - step][k] * x[i - step][channel];
        }
        return sum;
    }
    double sse(const std::vector<std::array<double, 3>>& x) const {
        double result = target_squared_sum;
        for (std::size_t i = 0; i != count; ++i) for (unsigned c = 0; c != 3; ++c) {
            result += h[i][0] * x[i][c] * x[i][c] - 2 * rhs[i][c] * x[i][c];
            for (unsigned k = 1; k != 8; ++k) if (i + delta[k] < count)
                result += 2 * h[i][k] * x[i][c] * x[i + delta[k]][c];
        }
        return result;
    }
};

inline void assemble(const std::vector<std::uint16_t>& raw, const Coordinates& coordinates, Normal& matrix) {
    constexpr double inverse = 1.0 / 65536.0;
    for (unsigned b = 0; b != 256; ++b) for (unsigned g = 0; g != 256; ++g) {
        const auto* row = raw.data() + ((std::size_t(b) * 256 + g) * 256) * 3;
        for (unsigned r = 0; r != 256; ++r) {
            const auto geometry = coordinates.at(r, g, b);
            const unsigned target[3] = {static_cast<std::uint8_t>(row[r * 3 + 2] / 16),
                                        static_cast<std::uint8_t>(row[r * 3 + 1] / 16),
                                        static_cast<std::uint8_t>(row[r * 3] / 16)};
            for (unsigned c = 0; c != 3; ++c) matrix.target_squared_sum += double(target[c]) * target[c];
            for (unsigned i = 0; i != 4; ++i) {
                const double own = geometry.weight[i] * inverse;
                if (own == 0) continue;
                for (unsigned c = 0; c != 3; ++c) matrix.rhs[geometry.node[i]][c] += own * target[c];
                for (unsigned j = i; j != 4; ++j) {
                    const unsigned edge = geometry.mask[i] ^ geometry.mask[j];
                    matrix.h[geometry.node[i]][edge] += own * (geometry.weight[j] * inverse);
                }
            }
        }
    }
}

inline double dot(const std::vector<double>& a, const std::vector<double>& b) {
    double value = 0;
    for (std::size_t i = 0; i != a.size(); ++i) value += a[i] * b[i];
    return value;
}
inline std::vector<double> solve_channel(const Normal& matrix, unsigned channel,
                                        const std::vector<std::array<double, 3>>& initial,
                                        const FitExperimentOptions& options, FitChannelReport& report) {
    const auto n = matrix.count;
    std::vector<double> x(n), rhs(n), reg(n), r(n), z(n), direction(n), product(n);
    for (std::size_t i = 0; i != n; ++i) {
        x[i] = initial[i][channel]; reg[i] = options.regularization * (matrix.h[i][0] + 1);
        rhs[i] = matrix.rhs[i][channel] + reg[i] * x[i];
    }
    matrix.multiply(x, product, reg);
    for (std::size_t i = 0; i != n; ++i) {
        r[i] = rhs[i] - product[i];
        z[i] = r[i] / (matrix.h[i][0] + reg[i]); direction[i] = z[i];
    }
    const double rhs_squared = dot(rhs, rhs);
    const double target = options.relative_tolerance * options.relative_tolerance * (std::max)(rhs_squared, 1e-60);
    double rz = dot(r, z);
    for (unsigned step = 0; step != options.cg_max_iterations && dot(r, r) > target; ++step) {
        matrix.multiply(direction, product, reg);
        const double denominator = dot(direction, product);
        if (!(denominator > 0) || !std::isfinite(denominator) || !std::isfinite(rz))
            throw std::runtime_error("完整域CG遇到非正或非有限方向");
        const double alpha = rz / denominator;
        for (std::size_t i = 0; i != n; ++i) { x[i] += alpha * direction[i]; r[i] -= alpha * product[i]; }
        ++report.iterations;
        if (dot(r, r) <= target) break;
        for (std::size_t i = 0; i != n; ++i) z[i] = r[i] / (matrix.h[i][0] + reg[i]);
        const double next = dot(r, z), beta = next / rz;
        for (std::size_t i = 0; i != n; ++i) direction[i] = z[i] + beta * direction[i];
        rz = next;
    }
    // 最终残差用原矩阵重新计算，不能只信递推残差或迭代退出。
    matrix.multiply(x, product, reg);
    for (std::size_t i = 0; i != n; ++i) r[i] = rhs[i] - product[i];
    report.relative_residual = std::sqrt(dot(r, r) / (std::max)(rhs_squared, 1e-60));
    report.converged = std::isfinite(report.relative_residual) && report.relative_residual <= options.relative_tolerance * 2;
    if (!report.converged) throw std::runtime_error("完整域CG未达到预设残差阈值，候选不发布");
    return x;
}
inline unsigned integer(double value) {
    if (!std::isfinite(value)) throw std::runtime_error("拟合节点非有限");
    return static_cast<unsigned>((std::max)(0.0, (std::min)(255.0, std::floor(value + .5))));
}
inline void evaluate(const std::vector<std::uint16_t>& raw, const Coordinates& coordinates,
                     const std::uint8_t* baseline, const std::uint8_t* candidate,
                     FitError& before, FitError& after) {
    for (unsigned b = 0; b != 256; ++b) for (unsigned g = 0; g != 256; ++g) {
        const auto* row = raw.data() + ((std::size_t(b) * 256 + g) * 256) * 3;
        for (unsigned r = 0; r != 256; ++r) {
            const auto geometry = coordinates.at(r, g, b);
            unsigned squared[2]{};
            double linear_squared[2]{};
            for (unsigned c = 0; c != 3; ++c) {
                std::uint64_t sums[2] = {32768, 32768};
                for (unsigned i = 0; i != 4; ++i) {
                    sums[0] += std::uint64_t(geometry.weight[i]) * baseline[geometry.node[i] * 3 + c];
                    sums[1] += std::uint64_t(geometry.weight[i]) * candidate[geometry.node[i] * 3 + c];
                }
                const int target = static_cast<std::uint8_t>(row[r * 3 + 2 - c] / 16);
                for (unsigned variant = 0; variant != 2; ++variant) {
                    const int error = static_cast<int>(sums[variant] >> 16) - target;
                    squared[variant] += static_cast<unsigned>(error * error);
                    const double linear_error = double(sums[variant] - 32768) / 65536 - target;
                    linear_squared[variant] += linear_error * linear_error;
                }
            }
            before.sse += squared[0]; after.sse += squared[1];
            before.linear_sse += linear_squared[0]; after.linear_sse += linear_squared[1];
            before.mean += std::sqrt(double(squared[0])); after.mean += std::sqrt(double(squared[1]));
            before.max_squared = (std::max)(before.max_squared, squared[0]);
            after.max_squared = (std::max)(after.max_squared, squared[1]);
        }
    }
    before.mean /= dense_nodes; after.mean /= dense_nodes;
}
} // namespace fit_detail

inline Stage fit_full(const std::vector<std::uint16_t>& raw, const Stage& initial, FitReport& report,
                      FitExperimentOptions options = {}) {
    report = {}; report.m = initial.m;
    if (raw.size() != dense_values) throw std::invalid_argument("完整域拟合要求256³三通道uint16源");
    if (!options.cg_max_iterations || options.cg_max_iterations > 1000 || options.integer_sweeps > 64 ||
        !std::isfinite(options.regularization) || options.regularization <= 0 ||
        !std::isfinite(options.relative_tolerance) || options.relative_tolerance <= 0 || options.relative_tolerance >= 1)
        throw std::invalid_argument("完整域拟合参数非法");
    const fit_detail::Coordinates coordinates(initial);
    if (initial.separable_proven && initial.proof_nodes == dense_nodes) {
        report.source_separable_skipped = true;
        return initial;
    }
    Stage result = initial;
    const double start = fit_detail::seconds();
    fit_detail::Normal matrix(coordinates);
    fit_detail::assemble(raw, coordinates, matrix);
    report.samples = dense_nodes;
    report.matrix_bytes = matrix.h.size() * sizeof(matrix.h[0]);
    report.temporary_bytes = report.matrix_bytes + matrix.rhs.size() * sizeof(matrix.rhs[0]) +
                             matrix.count * (3 * 2 + 7) * sizeof(double) + sizeof(coordinates);
    report.assembly_seconds = fit_detail::seconds() - start;
    std::vector<std::array<double, 3>> first(matrix.count), solution(matrix.count);
    for (std::size_t i = 0; i != matrix.count; ++i) for (unsigned c = 0; c != 3; ++c)
        first[i][c] = initial.nodes_data()[i * 3 + c];
    report.linear_sse_before = matrix.sse(first);
    const double solve_start = fit_detail::seconds();
    for (unsigned c = 0; c != 3; ++c) {
        const auto channel = fit_detail::solve_channel(matrix, c, first, options, report.channels[c]);
        for (std::size_t i = 0; i != matrix.count; ++i) solution[i][c] = fit_detail::integer(channel[i]);
    }
    // 固定最大次数的整数坐标下降，目标是同一个完整域正规方程，不看图像。
    for (unsigned sweep = 0; sweep != options.integer_sweeps; ++sweep) {
        std::size_t changed = 0;
        for (std::size_t i = 0; i != matrix.count; ++i) for (unsigned c = 0; c != 3; ++c) {
            const double reg = options.regularization * (matrix.h[i][0] + 1);
            const double next = fit_detail::integer((matrix.rhs[i][c] + reg * first[i][c] -
                    matrix.row_off_diagonal(i, solution, c)) / (matrix.h[i][0] + reg));
            changed += next != solution[i][c]; solution[i][c] = next;
        }
        ++report.integer_sweeps;
        if (!changed) break;
    }
    report.linear_sse_after = matrix.sse(solution);
    auto* nodes = result.blob.data() + (result.nodes_data() - result.blob.data());
    for (std::size_t i = 0; i != matrix.count; ++i) {
        bool changed = false;
        for (unsigned c = 0; c != 3; ++c) {
            nodes[i * 3 + c] = static_cast<std::uint8_t>(solution[i][c]);
            changed = changed || nodes[i * 3 + c] != initial.nodes_data()[i * 3 + c];
        }
        report.changed_nodes += changed;
    }
    report.solve_seconds = fit_detail::seconds() - solve_start;
    const double evaluate_start = fit_detail::seconds();
    fit_detail::evaluate(raw, coordinates, initial.nodes_data(), result.nodes_data(), report.baseline, report.candidate);
    // 独立逐点线性误差应与正规矩阵二次型一致，用来审计稀疏邻接装配。
    const auto matches = [](double direct, double matrix_value) {
        return std::abs(direct - matrix_value) <= (std::max)(1.0, direct * 1e-8);
    };
    if (!matches(report.baseline.linear_sse, report.linear_sse_before) ||
        !matches(report.candidate.linear_sse, report.linear_sse_after))
        throw std::runtime_error("完整域逐点误差与正规矩阵二次型不一致，候选不发布");
    report.evaluation_seconds = fit_detail::seconds() - evaluate_start;
    report.candidate_used = !options.guard_full_domain ||
        (report.candidate.sse <= report.baseline.sse && report.candidate.mean <= report.baseline.mean);
    return report.candidate_used ? result : initial;
}
} // namespace fc_framework
#endif

namespace fc_framework {
namespace fit_chain_detail {
using Color = std::array<unsigned, 3>;
inline Color apply_nodes(const fit_detail::Coordinates& coordinates, const Stage& stage, const Color& color) {
    const auto geometry = coordinates.at(color[0], color[1], color[2]);
    Color result{};
    for (unsigned c = 0; c != 3; ++c) {
        std::uint64_t sum = 32768;
        for (unsigned i = 0; i != 4; ++i) sum += std::uint64_t(geometry.weight[i]) * stage.nodes_data()[geometry.node[i] * 3 + c];
        result[c] = static_cast<unsigned>(sum >> 16);
    }
    return result;
}
inline Color target(const std::array<std::vector<std::uint16_t>, 4>& raw, Color color) {
    for (const auto& table : raw) {
        const auto at = ((std::size_t(color[2]) * 256 + color[1]) * 256 + color[0]) * 3;
        color = {static_cast<std::uint8_t>(table[at + 2] / 16), static_cast<std::uint8_t>(table[at + 1] / 16),
                 static_cast<std::uint8_t>(table[at] / 16)};
    }
    return color;
}
} // namespace fit_chain_detail

inline Stage fit_chain_last(const std::array<std::vector<std::uint16_t>, 4>& raw,
                            const std::array<Stage, 4>& sampled, FitReport& report,
                            FitExperimentOptions options = {}) {
    for (const auto& table : raw) if (table.size() != dense_values) throw std::invalid_argument("链拟合要求完整四级LUT");
    if (!options.cg_max_iterations || options.cg_max_iterations > 1000 || options.integer_sweeps > 64 ||
        !std::isfinite(options.regularization) || options.regularization <= 0 ||
        !std::isfinite(options.relative_tolerance) || options.relative_tolerance <= 0 || options.relative_tolerance >= 1)
        throw std::invalid_argument("链拟合参数非法");
    report = {}; report.m = sampled[3].m; report.samples = dense_nodes;
    const std::array<fit_detail::Coordinates, 4> coordinates = {
        fit_detail::Coordinates(sampled[0]), fit_detail::Coordinates(sampled[1]),
        fit_detail::Coordinates(sampled[2]), fit_detail::Coordinates(sampled[3])};
    fit_detail::Normal matrix(coordinates[3]);
    auto result = sampled[3];
    const double start = fit_detail::seconds();
    // 输入均为算法枚举的完整RGB域；这里不存在图片、直方图或抽样权重。
    for (unsigned r = 0; r != 256; ++r) for (unsigned g = 0; g != 256; ++g) for (unsigned b = 0; b != 256; ++b) {
        const fit_chain_detail::Color input = {r, g, b};
        const auto expected = fit_chain_detail::target(raw, input);
        auto prefix = input;
        for (unsigned i = 0; i != 3; ++i) prefix = fit_chain_detail::apply_nodes(coordinates[i], sampled[i], prefix);
        const auto geometry = coordinates[3].at(prefix[0], prefix[1], prefix[2]);
        for (unsigned c = 0; c != 3; ++c) matrix.target_squared_sum += double(expected[c]) * expected[c];
        for (unsigned i = 0; i != 4; ++i) {
            const double own = double(geometry.weight[i]) / 65536;
            if (!own) continue;
            for (unsigned c = 0; c != 3; ++c) matrix.rhs[geometry.node[i]][c] += own * expected[c];
            for (unsigned j = i; j != 4; ++j)
                matrix.h[geometry.node[i]][geometry.mask[i] ^ geometry.mask[j]] += own * (double(geometry.weight[j]) / 65536);
        }
    }
    report.assembly_seconds = fit_detail::seconds() - start;
    report.matrix_bytes = matrix.h.size() * sizeof(matrix.h[0]);
    report.temporary_bytes = report.matrix_bytes + matrix.rhs.size() * sizeof(matrix.rhs[0]) +
                             matrix.count * (3 * 2 + 7) * sizeof(double) + sizeof(coordinates);
    std::vector<std::array<double, 3>> first(matrix.count), solution(matrix.count);
    for (std::size_t i = 0; i != matrix.count; ++i) for (unsigned c = 0; c != 3; ++c) first[i][c] = sampled[3].nodes_data()[i * 3 + c];
    report.linear_sse_before = matrix.sse(first);
    const double solve_start = fit_detail::seconds();
    for (unsigned c = 0; c != 3; ++c) {
        const auto solved = fit_detail::solve_channel(matrix, c, first, options, report.channels[c]);
        for (std::size_t i = 0; i != matrix.count; ++i) solution[i][c] = fit_detail::integer(solved[i]);
    }
    for (unsigned sweep = 0; sweep != options.integer_sweeps; ++sweep) {
        std::size_t changed = 0;
        for (std::size_t i = 0; i != matrix.count; ++i) for (unsigned c = 0; c != 3; ++c) {
            const double reg = options.regularization * (matrix.h[i][0] + 1);
            const double next = fit_detail::integer((matrix.rhs[i][c] + reg * first[i][c] - matrix.row_off_diagonal(i, solution, c)) / (matrix.h[i][0] + reg));
            changed += next != solution[i][c]; solution[i][c] = next;
        }
        ++report.integer_sweeps; if (!changed) break;
    }
    report.linear_sse_after = matrix.sse(solution);
    auto* nodes = result.blob.data() + (result.nodes_data() - result.blob.data());
    for (std::size_t i = 0; i != matrix.count; ++i) {
        bool changed = false;
        for (unsigned c = 0; c != 3; ++c) { nodes[i * 3 + c] = static_cast<std::uint8_t>(solution[i][c]); changed = changed || nodes[i * 3 + c] != sampled[3].nodes_data()[i * 3 + c]; }
        report.changed_nodes += changed;
    }
    report.solve_seconds = fit_detail::seconds() - solve_start;
    const double evaluate_start = fit_detail::seconds();
    for (unsigned r = 0; r != 256; ++r) for (unsigned g = 0; g != 256; ++g) for (unsigned b = 0; b != 256; ++b) {
        const fit_chain_detail::Color input = {r, g, b};
        const auto expected = fit_chain_detail::target(raw, input);
        auto prefix = input;
        for (unsigned i = 0; i != 3; ++i) prefix = fit_chain_detail::apply_nodes(coordinates[i], sampled[i], prefix);
        const auto geometry = coordinates[3].at(prefix[0], prefix[1], prefix[2]);
        unsigned squared[2]{}; double linear_squared[2]{};
        for (unsigned c = 0; c != 3; ++c) {
            std::uint64_t sums[2] = {32768, 32768};
            for (unsigned i = 0; i != 4; ++i) {
                sums[0] += std::uint64_t(geometry.weight[i]) * sampled[3].nodes_data()[geometry.node[i] * 3 + c];
                sums[1] += std::uint64_t(geometry.weight[i]) * result.nodes_data()[geometry.node[i] * 3 + c];
            }
            for (unsigned v = 0; v != 2; ++v) {
                const int error = int(sums[v] >> 16) - int(expected[c]); squared[v] += unsigned(error * error);
                const double linear_error = double(sums[v] - 32768) / 65536 - expected[c]; linear_squared[v] += linear_error * linear_error;
            }
        }
        report.baseline.sse += squared[0]; report.candidate.sse += squared[1];
        report.baseline.mean += std::sqrt(double(squared[0])); report.candidate.mean += std::sqrt(double(squared[1]));
        report.baseline.linear_sse += linear_squared[0]; report.candidate.linear_sse += linear_squared[1];
        report.baseline.max_squared = (std::max)(report.baseline.max_squared, squared[0]);
        report.candidate.max_squared = (std::max)(report.candidate.max_squared, squared[1]);
    }
    report.baseline.mean /= dense_nodes; report.candidate.mean /= dense_nodes;
    const auto matches = [](double direct, double quadratic) { return std::abs(direct - quadratic) <= (std::max)(1.0, direct * 1e-8); };
    if (!matches(report.baseline.linear_sse, report.linear_sse_before) || !matches(report.candidate.linear_sse, report.linear_sse_after))
        throw std::runtime_error("链拟合逐点误差与正规矩阵二次型不同");
    report.evaluation_seconds = fit_detail::seconds() - evaluate_start;
    report.candidate_used = !options.guard_full_domain ||
        (report.candidate.sse <= report.baseline.sse && report.candidate.mean <= report.baseline.mean);
    // 链目标与原末层函数不同，修改后不得沿用原曲线资格绕过拟合节点。
    if (report.candidate_used && report.changed_nodes) {
        result.separable_proven = false; result.proof_nodes = 0; result.curves = {};
    }
    return report.candidate_used ? result : sampled[3];
}
} // namespace fc_framework
#endif

#include <numeric>
#include <string>

namespace fc_framework {
namespace precision {
using Models = std::array<Stage, 4>;
using Sources = std::array<std::vector<std::uint16_t>, 4>;
using Axes = std::array<std::vector<unsigned>, 3>;
inline unsigned component(std::uint32_t rgb, unsigned c) { return (rgb >> (8 * c)) & 255u; }
inline std::uint32_t source_color(const std::vector<std::uint16_t> &raw, std::uint32_t rgb) {
    const auto at =
        ((std::size_t(component(rgb, 2)) * 256 + component(rgb, 1)) * 256 + component(rgb, 0)) * 3;
    return std::uint32_t(std::uint8_t(raw[at + 2] / 16)) |
           (std::uint32_t(std::uint8_t(raw[at + 1] / 16)) << 8) |
           (std::uint32_t(std::uint8_t(raw[at] / 16)) << 16);
}
struct Evaluator {
    std::array<fc_core::fc_model, 4> views;
    std::array<Interpolation, 4> kinds;
    explicit Evaluator(const Models &models) {
        for (unsigned i = 0; i < 4; ++i) {
            views[i] = detail::view(models[i]);
            kinds[i] = models[i].interpolation;
        }
    }
    std::uint32_t map(std::uint32_t rgb, unsigned begin = 0, unsigned end = 4) const {
        for (unsigned i = begin; i < end; ++i)
            rgb = detail::map(views[i], kinds[i], rgb);
        return rgb;
    }
};
struct Geometry {
    std::array<std::size_t, 8> node{};
    std::array<std::uint64_t, 8> weight{};
    unsigned count = 0, shift = 16;
};
inline Geometry geometry(const fc_core::fc_model &m, Interpolation kind, std::uint32_t rgb,
                         unsigned channel) {
    Geometry g;
    const unsigned v[3] = {component(rgb, 0), component(rgb, 1), component(rgb, 2)};
    const std::size_t d[3] = {std::size_t(m.m) * m.m, m.m, 1};
    const std::size_t base = m.index[v[0]] * d[0] + m.index[256 + v[1]] * d[1] + m.index[512 + v[2]];
    const auto *fractions = m.sidecar.data ? m.sidecar.data + channel * 3072 : m.fraction_le;
    std::uint32_t f[3];
    for (unsigned a = 0; a < 3; ++a)
        f[a] = fc_core::fc_detail_read32(fractions + (a * 256 + v[a]) * 4);
    if (kind == Interpolation::TrilinearQ16) {
        g.count = 8;
        g.shift = 48;
        for (unsigned mask = 0; mask < 8; ++mask) {
            g.node[mask] = base;
            g.weight[mask] = 1;
            for (unsigned a = 0; a < 3; ++a) {
                const bool hi = (mask & (4u >> a)) != 0;
                g.node[mask] += hi ? d[a] : 0;
                g.weight[mask] *= hi ? f[a] : 65536 - f[a];
            }
        }
    } else {
        unsigned order[3] = {0, 1, 2};
        if (f[order[0]] < f[order[1]])
            std::swap(order[0], order[1]);
        if (f[order[1]] < f[order[2]])
            std::swap(order[1], order[2]);
        if (f[order[0]] < f[order[1]])
            std::swap(order[0], order[1]);
        g.count = 4;
        g.node[0] = base;
        g.node[1] = base + d[order[0]];
        g.node[2] = g.node[1] + d[order[1]];
        g.node[3] = base + d[0] + d[1] + 1;
        g.weight[0] = 65536 - f[order[0]];
        g.weight[1] = f[order[0]] - f[order[1]];
        g.weight[2] = f[order[1]] - f[order[2]];
        g.weight[3] = f[order[2]];
    }
    return g;
}
inline void clear_proof(Stage &stage) {
    stage.separable_proven = false;
    stage.proof_nodes = 0;
}
inline Axes fixed_axes(unsigned m, Grid kind) {
    if (m < 17 || m > 33)
        throw std::invalid_argument("节点尺寸须在17..33");
    Axes axes;
    for (auto &a : axes) {
        a.resize(m);
        for (unsigned i = 0; i < m; ++i)
            a[i] = kind == Grid::FrameworkStep ? i * (256 / (m - 1)) : (i * 255 + (m - 1) / 2) / (m - 1);
        a.back() = 255;
    }
    return axes;
}
inline Axes curvature_axes(const std::vector<std::uint16_t> &raw, unsigned m) {
    if (raw.size() != dense_values)
        throw std::invalid_argument("非均匀网格要求完整LUT");
    Axes axes = fixed_axes(m, Grid::UniformRounded);
    for (unsigned a = 0; a < 3; ++a) {
        std::array<double, 256> density{}, cdf{};
        unsigned coord[3]{};
        for (unsigned u = 0; u < 256; u += 4)
            for (unsigned v = 0; v < 256; v += 4) {
                coord[(a + 1) % 3] = u;
                coord[(a + 2) % 3] = v;
                for (unsigned x = 1; x < 255; ++x)
                    for (unsigned c = 0; c < 3; ++c) {
                        coord[a] = x - 1;
                        const int left = detail::source(raw, coord[0], coord[1], coord[2], c);
                        coord[a] = x;
                        const int middle = detail::source(raw, coord[0], coord[1], coord[2], c);
                        coord[a] = x + 1;
                        const int right = detail::source(raw, coord[0], coord[1], coord[2], c);
                        density[x] += std::abs(left - 2 * middle + right);
                    }
            }
        density[0] = density[1];
        density[255] = density[254];
        double average = 0;
        for (auto &d : density) {
            d = std::pow(d / (64.0 * 64 * 3), .4);
            average += d / 256;
        }
        for (auto &d : density)
            d = .5 + .5 * d / (average + 1e-8);
        for (unsigned x = 1; x < 256; ++x)
            cdf[x] = cdf[x - 1] + (density[x - 1] + density[x]) * .5;
        for (unsigned i = 1; i < m - 1; ++i) {
            const double q = cdf.back() * i / (m - 1);
            unsigned x = 1;
            while (cdf[x] < q)
                ++x;
            const double value = x - 1 + (q - cdf[x - 1]) / (cdf[x] - cdf[x - 1]);
            axes[a][i] = (std::min)(255 - 2 * (m - 1 - i),
                                    (std::max)(axes[a][i - 1] + 2, unsigned(std::floor(value + .5))));
        }
    }
    return axes;
}
// 与历史轴弦SSE动态规划相同：所有256个轴位置、固定垂直LUT探针、间距2..ceil(2*ideal)。
inline Axes dp_axes(const std::vector<std::uint16_t> &raw, unsigned m, unsigned probes = 24) {
    if (raw.size() != dense_values || probes < 2 || probes > 64)
        throw std::invalid_argument("DP源或探针数非法");
    Axes axes = fixed_axes(m, Grid::UniformRounded);
    const unsigned width = probes * probes * 3;
    const double ideal = 255.0 / (m - 1);
    const unsigned max_step = unsigned(std::ceil(2 * ideal));
    for (unsigned a = 0; a < 3; ++a) {
        std::vector<double> y(256 * width), gram(256 * 256), prefix(256 * 257), weighted(256 * 257),
            norm(257), cost(256 * 256, INFINITY);
        unsigned coord[3]{};
        for (unsigned x = 0; x < 256; ++x) {
            coord[a] = x;
            for (unsigned u = 0; u < probes; ++u)
                for (unsigned v = 0; v < probes; ++v) {
                    coord[(a + 1) % 3] = (u * 255 + (probes - 1) / 2) / (probes - 1);
                    coord[(a + 2) % 3] = (v * 255 + (probes - 1) / 2) / (probes - 1);
                    for (unsigned c = 0; c < 3; ++c)
                        y[x * width + (u * probes + v) * 3 + c] =
                            detail::source(raw, coord[0], coord[1], coord[2], c);
                }
        }
        for (unsigned x = 0; x < 256; ++x)
            for (unsigned z = 0; z <= x; ++z) {
                double value = 0;
                for (unsigned k = 0; k < width; ++k)
                    value += y[x * width + k] * y[z * width + k];
                gram[x * 256 + z] = gram[z * 256 + x] = value / width;
            }
        for (unsigned x = 0; x < 256; ++x) {
            norm[x + 1] = norm[x] + gram[x * 256 + x];
            for (unsigned z = 0; z < 256; ++z) {
                prefix[x * 257 + z + 1] = prefix[x * 257 + z] + gram[x * 256 + z];
                weighted[x * 257 + z + 1] = weighted[x * 257 + z] + z * gram[x * 256 + z];
            }
        }
        for (unsigned x = 0; x < 254; ++x)
            for (unsigned z = x + 2; z < 256 && z <= x + max_step; ++z) {
                const double w = z - x, sa = prefix[x * 257 + z + 1] - prefix[x * 257 + x],
                             sb = prefix[z * 257 + z + 1] - prefix[z * 257 + x];
                const double xa = weighted[x * 257 + z + 1] - weighted[x * 257 + x],
                             xb = weighted[z * 257 + z + 1] - weighted[z * 257 + x];
                const double cross = 2 * (z * sa - xa + xb - x * sb) / w;
                const double predicted =
                    (w + 1) * (2 * w + 1) / (6 * w) * (gram[x * 256 + x] + gram[z * 256 + z]) +
                    (w + 1) * (w - 1) / (3 * w) * gram[x * 256 + z];
                cost[x * 256 + z] = (std::max)(0.0, norm[z + 1] - norm[x] - cross + predicted) +
                                    1e-6 * (w - ideal) * (w - ideal);
            }
        std::vector<double> dp(m * 256, INFINITY);
        std::vector<unsigned> parent(m * 256, 256);
        dp[0] = 0;
        for (unsigned s = 1; s < m; ++s)
            for (unsigned end = 2 * s; end < 256 && end <= max_step * s; ++end) {
                const unsigned start = (std::max)(2 * (s - 1), end > max_step ? end - max_step : 0u);
                for (unsigned begin = start; begin + 2 <= end; ++begin) {
                    const double value = dp[(s - 1) * 256 + begin] + cost[begin * 256 + end];
                    if (value < dp[s * 256 + end]) {
                        dp[s * 256 + end] = value;
                        parent[s * 256 + end] = begin;
                    }
                }
            }
        if (!std::isfinite(dp[(m - 1) * 256 + 255]))
            throw std::runtime_error("DP没有可行端点路径");
        unsigned end = 255;
        for (unsigned s = m - 1; s > 0; --s) {
            axes[a][s] = end;
            end = parent[s * 256 + end];
        }
        axes[a][0] = 0;
    }
    return axes;
}
inline void initialize_sidecar(Stage &stage) {
    if (!stage.fractions.empty())
        return;
    const auto m = detail::view(stage);
    stage.fractions.resize(9216);
    for (unsigned c = 0; c < 3; ++c)
        std::copy(m.fraction_le, m.fraction_le + 3072, stage.fractions.begin() + c * 3072);
}
inline Axes error_axes(const std::vector<std::uint16_t> &raw, unsigned m) {
    FitOptions f;
    f.prove_structure = false;
    f.grid = Grid::UniformRounded;
    const auto pilot = prepare_stage(raw, m, f);
    const auto view = detail::view(pilot);
    std::array<std::array<double, 32>, 3> profile{};
    std::array<unsigned, 32> code{};
    for (unsigned i = 0; i < 32; ++i)
        code[i] = (i * 255 + 15) / 31;
    for (unsigned r = 0; r < 32; ++r)
        for (unsigned g = 0; g < 32; ++g)
            for (unsigned b = 0; b < 32; ++b) {
                const auto rgb = code[r] | code[g] << 8 | code[b] << 16;
                const auto predicted = detail::map(view, Interpolation::TetraQ16, rgb),
                           target = source_color(raw, rgb);
                double error = 0;
                for (unsigned c = 0; c < 3; ++c) {
                    const int d = int(component(predicted, c)) - int(component(target, c));
                    error += d * d;
                }
                error = std::sqrt(error);
                profile[0][r] += error / 1024;
                profile[1][g] += error / 1024;
                profile[2][b] += error / 1024;
            }
    auto axes = fixed_axes(m, Grid::UniformRounded);
    for (unsigned a = 0; a < 3; ++a) {
        double average = 0;
        for (auto x : profile[a])
            average += x / 32;
        std::array<double, 32> density{}, cdf{};
        for (unsigned x = 0; x < 32; ++x)
            density[x] = .5 + .5 * (profile[a][x] + .25) / (average + .25);
        for (unsigned x = 1; x < 32; ++x)
            cdf[x] = cdf[x - 1] + (density[x] + density[x - 1]) * .5;
        for (unsigned i = 1; i < m - 1; ++i) {
            const double q = cdf.back() * i / (m - 1);
            unsigned x = 1;
            while (cdf[x] < q)
                ++x;
            const double value =
                code[x - 1] + (code[x] - code[x - 1]) * (q - cdf[x - 1]) / (cdf[x] - cdf[x - 1]);
            axes[a][i] = (std::min)(255 - 2 * (m - 1 - i),
                                    (std::max)(axes[a][i - 1] + 2, unsigned(std::floor(value + .5))));
        }
    }
    return axes;
}
struct MonotoneReport {
    bool source_proven = false, nodes_proven = false, feasible = false;
    std::array<unsigned, 3> axes{};
};
// 轴置换/共享均可；完整原表和节点张量逐值证明后，交舍入区间及单调域。
inline Stage exact_monotone(const std::vector<std::uint16_t> &raw, const Stage &initial,
                            MonotoneReport &report, unsigned max_shift = 4096) {
    if (raw.size() != dense_values || max_shift > 65536 || !initial.fractions.empty())
        throw std::invalid_argument("精确单调校准源、偏移或共享坐标非法");
    report = {};
    std::array<std::array<std::array<std::uint8_t, 256>, 3>, 3> curves{};
    bool possible[3][3];
    for (unsigned c = 0; c < 3; ++c)
        for (unsigned a = 0; a < 3; ++a) {
            possible[c][a] = true;
            for (unsigned v = 0; v < 256; ++v) {
                unsigned xyz[3]{};
                xyz[a] = v;
                curves[c][a][v] = detail::source(raw, xyz[0], xyz[1], xyz[2], c);
            }
        }
    for (std::uint32_t rgb = 0; rgb < dense_nodes; ++rgb) {
        const auto target = source_color(raw, rgb);
        for (unsigned c = 0; c < 3; ++c)
            for (unsigned a = 0; a < 3; ++a)
                possible[c][a] = possible[c][a] && (component(target, c) == curves[c][a][component(rgb, a)]);
    }
    for (unsigned c = 0; c < 3; ++c) {
        unsigned a = 0;
        while (a < 3 && !possible[c][a])
            ++a;
        if (a == 3)
            return initial;
        report.axes[c] = a;
    }
    report.source_proven = true;
    const auto view = detail::view(initial);
    const unsigned m = initial.m;
    const std::size_t stride[3] = {std::size_t(m) * m, m, 1};
    for (std::size_t i = 0; i < initial.node_bytes() / 3; ++i)
        for (unsigned c = 0; c < 3; ++c) {
            const auto a = report.axes[c];
            const auto at = (i / stride[a]) % m;
            if (initial.nodes_data()[3 * i + c] != initial.nodes_data()[3 * at * stride[a] + c])
                return initial;
        }
    report.nodes_proven = true;
    std::array<std::array<int, 256>, 3> lower{}, upper{}, original{};
    for (unsigned a = 0; a < 3; ++a)
        for (unsigned v = 0; v < 256; ++v) {
            const int f = int(fc_core::fc_detail_read32(view.fraction_le + 4 * (a * 256 + v)));
            original[a][v] = f;
            lower[a][v] = (std::max)(0, f - int(max_shift));
            upper[a][v] = (std::min)(65536, f + int(max_shift));
            if (v == 0 || v == 255)
                lower[a][v] = upper[a][v] = f;
        }
    for (unsigned c = 0; c < 3; ++c) {
        const auto a = report.axes[c];
        for (unsigned v = 0; v < 256; ++v) {
            const unsigned cell = view.index[a * 256 + v];
            const int left = initial.nodes_data()[3 * cell * stride[a] + c],
                      right = initial.nodes_data()[3 * (cell + 1) * stride[a] + c], target = curves[c][a][v];
            // 二分找到全部能舍入到target的Q16整数，递减曲线统一翻转坐标。
            const bool reverse = right < left;
            const int lo = (std::min)(left, right), hi = (std::max)(left, right);
            auto first = [&](int threshold) {
                int l = 0, h = 65537;
                while (l < h) {
                    const int mid = l + (h - l) / 2;
                    const int value = (lo * 65536 + (hi - lo) * mid + 32768) >> 16;
                    if (value >= threshold)
                        h = mid;
                    else
                        l = mid + 1;
                }
                return l;
            };
            int l = first(target), h = first(target + 1) - 1;
            if (reverse) {
                const int old = l;
                l = 65536 - h;
                h = 65536 - old;
            }
            lower[a][v] = (std::max)(lower[a][v], l);
            upper[a][v] = (std::min)(upper[a][v], h);
        }
    }
    Stage result = initial;
    for (unsigned a = 0; a < 3; ++a) {
        std::array<int, 256> low{}, high{};
        for (unsigned v = 0; v < 256; ++v) {
            const int offset = int(view.index[a * 256 + v]) * 65536;
            low[v] = lower[a][v] + offset;
            high[v] = upper[a][v] + offset;
            if (v && original[a][v] + offset < original[a][v - 1] + int(view.index[a * 256 + v - 1]) * 65536)
                return initial;
            if (v)
                low[v] = (std::max)(low[v], low[v - 1]);
        }
        for (int v = 254; v >= 0; --v)
            high[v] = (std::min)(high[v], high[v + 1]);
        for (unsigned v = 0; v < 256; ++v) {
            if (low[v] > high[v])
                return initial;
            const int offset = int(view.index[a * 256 + v]) * 65536;
            const int q = (std::min)(high[v], (std::max)(low[v], offset + original[a][v]));
            detail::put32(result.blob, 16 + 12 * m + 768 + 4 * (a * 256 + v), q - offset);
        }
    }
    // 原表证明只支持源函数，清除可绕过当前稀疏节点的旧资格。
    clear_proof(result);
    report.feasible = true;
    return result;
}
} // namespace precision
} // namespace fc_framework
#endif

#include <functional>

namespace fc_framework {
namespace precision {
constexpr unsigned max_error_squared = 3 * 255 * 255;
struct Roots {
    std::vector<double> value;
    std::vector<std::uint64_t> lower, upper;
    Roots() : value(max_error_squared + 1), lower(value.size()), upper(value.size()) {
        for (unsigned d = 0; d < value.size(); ++d) {
            value[d] = std::sqrt(double(d));
            // 逐二进制数位开方；d*2^48需66位，余数及根始终装入64位。
            std::uint64_t q = 0, remainder = 0;
            for (int bit = 32; bit >= 0; --bit) {
                remainder = (remainder << 2) | (bit >= 24 ? ((d >> (2 * (bit - 24))) & 3u) : 0u);
                q <<= 1;
                const auto trial = (q << 1) | 1u;
                if (remainder >= trial) {
                    remainder -= trial;
                    ++q;
                }
            }
            lower[d] = q;
            upper[d] = q + (remainder != 0);
        }
    }
};
inline const Roots &roots() {
    static const Roots r;
    return r;
}
struct Quality {
    std::uint64_t pixels = 0, sse = 0;
    double mean = 0, rms = 0, p99 = 0, max = 0, cvar = 0;
    unsigned p99_squared = 0, p99_upper_squared = 0, p99_weight = 0, max_squared = 0;
};
struct Histogram {
    std::vector<std::uint64_t> count;
    std::uint64_t total = 0, sse = 0;
    unsigned largest = 0;
    Histogram() : count(max_error_squared + 1) {}
    void add(unsigned d, std::uint64_t n) {
        count.at(d) += n;
        total += n;
        sse += std::uint64_t(d) * n;
        largest = (std::max)(largest, d);
    }
    void remove(unsigned d, std::uint64_t n) {
        if (d >= count.size() || count[d] < n)
            throw std::runtime_error("误差直方图增量下溢");
        count[d] -= n;
        total -= n;
        sse -= std::uint64_t(d) * n;
        while (largest && count[largest] == 0)
            --largest;
    }
    Quality quality() const {
        Quality q;
        q.pixels = total;
        q.sse = sse;
        if (!total)
            return q;
        long double sum = 0, tail = 0;
        std::uint64_t accumulated = 0, remaining = (total + 99) / 100;
        const std::uint64_t rank = 99 * (total - 1) / 100;
        q.p99_weight = unsigned(99 * (total - 1) % 100);
        bool low = false, high = false;
        for (unsigned d = 0; d <= largest; ++d) {
            sum += static_cast<long double>(count[d]) * roots().value[d];
            accumulated += count[d];
            if (!low && accumulated > rank) {
                q.p99_squared = d;
                low = true;
            }
            if (!high && accumulated > rank + (q.p99_weight != 0)) {
                q.p99_upper_squared = d;
                high = true;
            }
        }
        for (unsigned d = largest;; --d) {
            const auto n = (std::min)(remaining, count[d]);
            tail += static_cast<long double>(n) * roots().value[d];
            remaining -= n;
            if (!remaining || !d)
                break;
        }
        q.mean = double(sum / total);
        q.rms = std::sqrt(double(sse) / total);
        q.p99 = (roots().value[q.p99_squared] * (100 - q.p99_weight) +
                 roots().value[q.p99_upper_squared] * q.p99_weight) /
                100;
        q.max_squared = largest;
        q.max = roots().value[largest];
        q.cvar = double(tail / ((total + 99) / 100));
        return q;
    }
};
// 用相同误差桶抵消后再作Q24上下界比较，避免依赖浮点mean最后一位。
inline bool certified_mean_leq(const Histogram &a, const Histogram &b) {
    if (a.total != b.total)
        return false;
    std::int64_t upper = 0;
    for (unsigned d = 0; d <= (std::max)(a.largest, b.largest); ++d) {
        const auto delta = std::int64_t(a.count[d]) - std::int64_t(b.count[d]);
        upper += delta * std::int64_t(delta >= 0 ? roots().upper[d] : roots().lower[d]);
    }
    return upper <= 0;
}
enum class Objective { Mean, Maximum, P99, CVaR, Lp };
struct Guard {
    bool mean = true, sse = true, maximum = true, p99 = true, cvar = true, pointwise = false;
};
inline bool certified_tail_leq(const Histogram &a, const Histogram &b) {
    if (a.total != b.total)
        return false;
    std::uint64_t left = (a.total + 99) / 100, right = left;
    std::int64_t upper = 0;
    for (int d = int((std::max)(a.largest, b.largest)); d >= 0 && (left || right); --d) {
        const auto na = (std::min)(left, a.count[d]), nb = (std::min)(right, b.count[d]);
        left -= na;
        right -= nb;
        const auto delta = std::int64_t(na) - std::int64_t(nb);
        upper += delta * std::int64_t(delta >= 0 ? roots().upper[d] : roots().lower[d]);
    }
    return upper <= 0;
}
inline bool accepts(const Histogram &candidate, const Histogram &anchor, const Guard &guard) {
    if (candidate.total != anchor.total || !candidate.total)
        return false;
    if (guard.mean && !certified_mean_leq(candidate, anchor))
        return false;
    if (guard.sse && candidate.sse > anchor.sse)
        return false;
    if (guard.maximum && candidate.largest > anchor.largest)
        return false;
    if (guard.p99 || guard.cvar) {
        const auto c = candidate.quality(), a = anchor.quality();
        if (guard.p99) {
            if (c.p99_squared > a.p99_squared || c.p99_upper_squared > a.p99_upper_squared) {
                Histogram ch, ah;
                ch.add(c.p99_squared, 100 - c.p99_weight);
                ch.add(c.p99_upper_squared, c.p99_weight);
                ah.add(a.p99_squared, 100 - a.p99_weight);
                ah.add(a.p99_upper_squared, a.p99_weight);
                if (!certified_mean_leq(ch, ah))
                    return false;
            }
        }
        if (guard.cvar && !certified_tail_leq(candidate, anchor))
            return false;
    }
    return true;
}
inline long double lp(const Histogram &h) {
    long double value = 0;
    for (unsigned i = 0; i <= h.largest; ++i)
        value += static_cast<long double>(h.count[i]) * i * i * i;
    return value;
}
inline bool better(const Histogram &a, const Histogram &b, Objective objective) {
    const auto x = a.quality(), y = b.quality();
    if (objective == Objective::Maximum && x.max_squared != y.max_squared)
        return x.max_squared < y.max_squared;
    if (objective == Objective::P99 && x.p99 != y.p99)
        return x.p99 < y.p99;
    if (objective == Objective::CVaR && std::abs(x.cvar - y.cvar) > 1e-12)
        return x.cvar < y.cvar;
    if (objective == Objective::Lp) {
        const auto l = lp(a), r = lp(b);
        if (l != r)
            return l < r;
    }
    if (x.mean < y.mean - 1e-12)
        return certified_mean_leq(a, b);
    return std::abs(x.mean - y.mean) <= 1e-12 && a.sse < b.sse;
}
inline unsigned distance(std::uint32_t a, std::uint32_t b) {
    unsigned d = 0;
    for (unsigned c = 0; c < 3; ++c) {
        const int e = int(component(a, c)) - int(component(b, c));
        d += unsigned(e * e);
    }
    return d;
}
inline std::vector<std::uint32_t> truth(const Sources &raw) {
    for (const auto &s : raw)
        if (s.size() != dense_values)
            throw std::invalid_argument("精度准备需要四张完整LUT");
    std::vector<std::uint32_t> result(dense_nodes);
    for (std::uint32_t i = 0; i < dense_nodes; ++i) {
        auto v = i;
        for (const auto &s : raw)
            v = source_color(s, v);
        result[i] = v;
    }
    return result;
}
inline Histogram evaluate(const Models &models, const std::vector<std::uint32_t> &gold) {
    if (gold.size() != dense_nodes)
        throw std::invalid_argument("完整域参考长度不符");
    const Evaluator evaluator(models);
    Histogram h;
    for (std::uint32_t i = 0; i < dense_nodes; ++i)
        h.add(distance(evaluator.map(i), gold[i]), 1);
    return h;
}
struct Point {
    std::uint32_t rgb, target, mass, error, local_error = 0;
};
struct Support {
    std::vector<Point> points;
    std::vector<std::uint32_t> suffix;
    Histogram histogram;
    unsigned stage = 0;
    const std::vector<std::uint16_t> *local_source = nullptr;
    double local_weight = 0;
    Support(const Models &models, const std::vector<std::uint32_t> &gold, unsigned stage_index,
            const std::vector<std::uint16_t> *source = nullptr, double weight = 0)
        : stage(stage_index), local_source(source), local_weight(weight) {
        if (stage >= 4 || gold.size() != dense_nodes)
            throw std::invalid_argument("联合支撑阶段或参考非法");
        if (!std::isfinite(weight) || weight < 0 || (weight && (!source || source->size() != dense_values)))
            throw std::invalid_argument("本级加后缀双目标参数非法");
        Evaluator e(models);
        std::vector<std::uint64_t> pairs(dense_nodes);
        for (std::uint32_t i = 0; i < dense_nodes; ++i)
            pairs[i] = std::uint64_t(e.map(i, 0, stage)) | (std::uint64_t(gold[i]) << 24);
        std::sort(pairs.begin(), pairs.end());
        for (std::size_t i = 0; i < pairs.size();) {
            std::size_t j = i + 1;
            while (j < pairs.size() && pairs[j] == pairs[i])
                ++j;
            points.push_back({std::uint32_t(pairs[i] & 0xffffffu), std::uint32_t(pairs[i] >> 24),
                              std::uint32_t(j - i), 0});
            i = j;
        }
        std::vector<std::uint64_t>().swap(pairs);
        if (stage != 3) {
            suffix.resize(dense_nodes);
            for (std::uint32_t i = 0; i < dense_nodes; ++i)
                suffix[i] = e.map(i, stage + 1);
        }
        const auto view = detail::view(models[stage]);
        for (auto &p : points) {
            auto output = detail::map(view, models[stage].interpolation, p.rgb);
            if (local_weight)
                p.local_error = distance(output, source_color(*local_source, p.rgb));
            if (!suffix.empty())
                output = suffix[output];
            p.error = distance(output, p.target);
            histogram.add(p.error, p.mass);
        }
        if (histogram.total != dense_nodes)
            throw std::runtime_error("联合支撑丢失完整域质量");
    }
    unsigned error(const Stage &model, const Point &point) const {
        const auto m = detail::view(model);
        auto output = detail::map(m, model.interpolation, point.rgb);
        if (!suffix.empty())
            output = suffix[output];
        return distance(output, point.target);
    }
};
struct SearchReport {
    std::uint64_t support_rows = 0, proposals = 0, accepted = 0;
    Quality before{}, after{};
};
// 同一候选先计算全部受影响支撑，再事务式更新直方图；拒绝时逐项恢复。
inline bool trial(Stage &model, Support &support, const std::vector<std::uint32_t> &affected,
                  const Histogram &anchor, const std::vector<unsigned> &caps, const Guard &guard,
                  Objective objective, std::vector<unsigned> &errors) {
    errors.clear();
    errors.reserve(affected.size());
    const auto view = detail::view(model);
    std::vector<unsigned> local_errors;
    long double joint_delta = 0;
    for (auto i : affected) {
        const auto &p = support.points[i];
        auto output = detail::map(view, model.interpolation, p.rgb);
        if (support.local_weight) {
            const auto d = distance(output, source_color(*support.local_source, p.rgb));
            local_errors.push_back(d);
            joint_delta += p.mass * support.local_weight * (roots().value[d] - roots().value[p.local_error]);
        }
        if (!support.suffix.empty())
            output = support.suffix[output];
        const unsigned d = distance(output, p.target);
        if (guard.pointwise && d > caps[i])
            return false;
        errors.push_back(d);
        joint_delta += p.mass * (roots().value[d] - roots().value[p.error]);
    }
    if (support.local_weight && joint_delta > 0)
        return false;
    Histogram before = support.histogram;
    for (std::size_t k = 0; k < affected.size(); ++k) {
        const auto &p = support.points[affected[k]];
        support.histogram.remove(p.error, p.mass);
        support.histogram.add(errors[k], p.mass);
    }
    const bool take =
        accepts(support.histogram, anchor, guard) && better(support.histogram, before, objective);
    if (take) {
        for (std::size_t k = 0; k < affected.size(); ++k) {
            support.points[affected[k]].error = errors[k];
            if (support.local_weight)
                support.points[affected[k]].local_error = local_errors[k];
        }
    } else
        support.histogram = std::move(before);
    return take;
}
inline SearchReport optimize_nodes(Models &models, const std::vector<std::uint32_t> &gold, unsigned stage,
                                   const Histogram &anchor, const Guard &guard, Objective objective,
                                   unsigned budget = 128, unsigned sweeps = 1,
                                   const std::vector<std::uint16_t> *source = nullptr,
                                   double local_weight = 0) {
    Support support(models, gold, stage, source, local_weight);
    SearchReport report;
    report.support_rows = support.points.size();
    report.before = support.histogram.quality();
    auto &model = models[stage];
    auto view = detail::view(model);
    const auto nodes = model.node_bytes() / 3;
    std::vector<long double> score(nodes);
    std::vector<unsigned> caps;
    caps.reserve(support.points.size());
    for (const auto &p : support.points) {
        caps.push_back(p.error);
        for (unsigned c = 0; c < 3; ++c) {
            const auto g = geometry(view, model.interpolation, p.rgb, c);
            for (unsigned k = 0; k < g.count; ++k)
                if (g.weight[k])
                    score[g.node[k]] += static_cast<long double>(p.mass) * p.error * double(g.weight[k]) /
                                        double(std::uint64_t{1} << g.shift);
        }
    }
    std::vector<std::size_t> order(nodes);
    std::iota(order.begin(), order.end(), 0);
    std::stable_sort(order.begin(), order.end(), [&](auto a, auto b) { return score[a] > score[b]; });
    order.resize((std::min)(std::size_t(budget), nodes));
    while (!order.empty() && score[order.back()] == 0)
        order.pop_back();
    std::vector<int> selected(nodes, -1);
    for (std::size_t i = 0; i < order.size(); ++i)
        selected[order[i]] = int(i);
    std::vector<std::vector<std::uint32_t>> links(order.size());
    for (std::uint32_t i = 0; i < support.points.size(); ++i) {
        std::array<std::size_t, 24> seen{};
        unsigned n = 0;
        for (unsigned c = 0; c < 3; ++c) {
            const auto g = geometry(view, model.interpolation, support.points[i].rgb, c);
            for (unsigned k = 0; k < g.count; ++k)
                if (g.weight[k] && selected[g.node[k]] >= 0) {
                    if (std::find(seen.begin(), seen.begin() + n, g.node[k]) == seen.begin() + n) {
                        seen[n++] = g.node[k];
                        links[selected[g.node[k]]].push_back(i);
                    }
                }
        }
    }
    std::vector<unsigned> errors;
    auto *bytes = model.blob.data() + (model.nodes_data() - model.blob.data());
    for (unsigned sweep = 0; sweep < sweeps; ++sweep)
        for (std::size_t k = 0; k < order.size(); ++k) {
            const auto node = order[k];
            for (int step : {1, 2, 4})
                for (int r = -1; r <= 1; ++r)
                    for (int g = -1; g <= 1; ++g)
                        for (int b = -1; b <= 1; ++b) {
                            if (!r && !g && !b)
                                continue;
                            const int delta[3] = {r * step, g * step, b * step};
                            std::array<std::uint8_t, 3> old;
                            bool valid = true;
                            for (unsigned c = 0; c < 3; ++c) {
                                old[c] = bytes[node * 3 + c];
                                const int value = int(old[c]) + delta[c];
                                if (value < 0 || value > 255)
                                    valid = false;
                            }
                            if (!valid)
                                continue;
                            for (unsigned c = 0; c < 3; ++c)
                                bytes[node * 3 + c] = std::uint8_t(int(old[c]) + delta[c]);
                            ++report.proposals;
                            if (trial(model, support, links[k], anchor, caps, guard, objective, errors)) {
                                ++report.accepted;
                                clear_proof(model);
                            } else
                                for (unsigned c = 0; c < 3; ++c)
                                    bytes[node * 3 + c] = old[c];
                        }
        }
    report.after = support.histogram.quality();
    return report;
}
inline SearchReport calibrate_coordinates(Models &models, const std::vector<std::uint32_t> &gold,
                                          unsigned stage, const Histogram &anchor, const Guard &guard,
                                          Objective objective, unsigned budget = 64, bool per_output = true,
                                          const std::vector<std::uint16_t> *source = nullptr,
                                          double local_weight = 0) {
    auto &model = models[stage];
    if (!per_output && !model.fractions.empty())
        throw std::invalid_argument("共享坐标校准须在分输出坐标之前");
    if (per_output)
        initialize_sidecar(model);
    Support support(models, gold, stage, source, local_weight);
    SearchReport report;
    report.support_rows = support.points.size();
    report.before = support.histogram.quality();
    const unsigned channels = per_output ? 3 : 1;
    const auto view = detail::view(model);
    std::vector<long double> score(channels * 768);
    std::vector<unsigned> caps;
    caps.reserve(support.points.size());
    for (const auto &p : support.points) {
        caps.push_back(p.error);
        for (unsigned c = 0; c < channels; ++c)
            for (unsigned a = 0; a < 3; ++a)
                score[c * 768 + a * 256 + component(p.rgb, a)] += static_cast<long double>(p.error) * p.mass;
    }
    std::vector<unsigned> order(score.size());
    std::iota(order.begin(), order.end(), 0);
    std::stable_sort(order.begin(), order.end(), [&](unsigned a, unsigned b) { return score[a] > score[b]; });
    order.resize((std::min)(order.size(), std::size_t(budget)));
    std::vector<unsigned> errors;
    std::vector<std::uint32_t> affected;
    for (auto coordinate : order) {
        if (score[coordinate] == 0)
            continue;
        const unsigned c = coordinate / 768, a = coordinate / 256 % 3, v = coordinate % 256;
        affected.clear();
        for (std::uint32_t i = 0; i < support.points.size(); ++i)
            if (component(support.points[i].rgb, a) == v)
                affected.push_back(i);
        const unsigned cell = view.index[a * 256 + v];
        auto *f =
            per_output ? model.fractions.data() + c * 3072 : model.blob.data() + 16 + 12 * model.m + 768;
        const auto read = [&](unsigned x) { return fc_core::fc_detail_read32(f + (a * 256 + x) * 4); };
        const unsigned low = v && view.index[a * 256 + v - 1] == cell ? read(v - 1) : 0;
        const unsigned high = v < 255 && view.index[a * 256 + v + 1] == cell ? read(v + 1) : 65536;
        for (int magnitude : {4096, 1024, 256, 64, 16, 4, 1})
            for (int sign : {-1, 1}) {
                const auto old = read(v);
                const int proposed = int(old) + sign * magnitude;
                if (proposed < int(low) || proposed > int(high))
                    continue;
                auto &bytes = per_output ? model.fractions : model.blob;
                const std::size_t offset =
                    per_output ? c * 3072 + (a * 256 + v) * 4 : 16 + 12 * model.m + 768 + (a * 256 + v) * 4;
                detail::put32(bytes, offset, unsigned(proposed));
                ++report.proposals;
                if (trial(model, support, affected, anchor, caps, guard, objective, errors)) {
                    ++report.accepted;
                    clear_proof(model);
                } else
                    detail::put32(bytes, offset, old);
            }
    }
    report.after = support.histogram.quality();
    return report;
}
struct BoxVariable {
    std::size_t node;
    unsigned channel;
    int radius;
};
// 穷举冻结整数箱；预算不足直接拒绝，不把局部搜索冒称箱内最优。
inline SearchReport exact_integer_box(Models &models, const std::vector<std::uint32_t> &gold, unsigned stage,
                                      const std::vector<BoxVariable> &variables, const Histogram &anchor,
                                      const Guard &guard, Objective objective,
                                      std::uint64_t max_assignments = 100000) {
    if (stage >= 4 || variables.empty())
        throw std::invalid_argument("整数箱必须非空且指定合法级");
    auto &model = models[stage];
    auto *bytes = model.blob.data() + (model.nodes_data() - model.blob.data());
    std::vector<int> low, high;
    std::vector<std::size_t> offsets;
    std::uint64_t assignments = 1;
    for (const auto &v : variables) {
        if (v.node >= model.node_bytes() / 3 || v.channel >= 3 || v.radius < 0 || v.radius > 255)
            throw std::invalid_argument("整数箱变量越界");
        const auto offset = v.node * 3 + v.channel;
        if (std::find(offsets.begin(), offsets.end(), offset) != offsets.end())
            throw std::invalid_argument("整数箱变量重复");
        offsets.push_back(offset);
        low.push_back((std::max)(0, int(bytes[offset]) - v.radius));
        high.push_back((std::min)(255, int(bytes[offset]) + v.radius));
        const auto width = std::uint64_t(high.back() - low.back() + 1);
        if (assignments > max_assignments / width)
            throw std::invalid_argument("整数箱超过完整穷举预算");
        assignments *= width;
    }
    Support support(models, gold, stage);
    SearchReport report;
    report.before = support.histogram.quality();
    report.support_rows = support.points.size();
    const auto view = detail::view(model);
    std::vector<std::uint32_t> affected;
    std::vector<unsigned> caps, errors;
    for (std::uint32_t i = 0; i < support.points.size(); ++i) {
        const auto &p = support.points[i];
        caps.push_back(p.error);
        bool touches = false;
        for (const auto &v : variables) {
            const auto g = geometry(view, model.interpolation, p.rgb, v.channel);
            for (unsigned k = 0; k < g.count; ++k)
                touches = touches || (g.node[k] == v.node && g.weight[k]);
        }
        if (touches)
            affected.push_back(i);
    }
    std::vector<std::uint8_t> best;
    for (auto i : offsets)
        best.push_back(bytes[i]);
    for (std::uint64_t key = 0; key < assignments; ++key) {
        auto code = key;
        for (std::size_t i = 0; i < offsets.size(); ++i) {
            const auto width = high[i] - low[i] + 1;
            bytes[offsets[i]] = std::uint8_t(low[i] + code % width);
            code /= width;
        }
        ++report.proposals;
        if (trial(model, support, affected, anchor, caps, guard, objective, errors)) {
            ++report.accepted;
            for (std::size_t i = 0; i < offsets.size(); ++i)
                best[i] = bytes[offsets[i]];
        }
    }
    for (std::size_t i = 0; i < offsets.size(); ++i)
        bytes[offsets[i]] = best[i];
    if (report.accepted)
        clear_proof(model);
    report.after = support.histogram.quality();
    return report;
}
} // namespace precision
} // namespace fc_framework
#endif

namespace fc_framework {
namespace precision {
enum class Weight { Uniform, Lp6, Tail };
struct BoxReport {
    unsigned sweeps = 0;
    double kkt = 0;
    bool converged = false;
    std::size_t changed = 0;
};
// 每一行保留3×3×3邻居，因此三线性和分输出坐标无需降格成四面体。
inline Stage box_fit(const Stage &initial, const std::vector<Point> &points, Weight weighting,
                     BoxReport &report, unsigned max_sweeps = 320, double tolerance = 1e-7) {
    if (points.empty() || !max_sweeps || !(tolerance > 0))
        throw std::invalid_argument("box拟合参数非法");
    const auto model = detail::view(initial);
    const unsigned m = model.m;
    const auto n = initial.node_bytes() / 3;
    Histogram h;
    for (const auto &p : points)
        h.add(p.error, p.mass);
    const unsigned threshold = h.quality().p99_squared;
    Stage result = initial;
    auto *output = result.blob.data() + (result.nodes_data() - result.blob.data());
    std::array<std::ptrdiff_t, 27> delta{};
    for (int r = -1; r <= 1; ++r)
        for (int g = -1; g <= 1; ++g)
            for (int b = -1; b <= 1; ++b)
                delta[(r + 1) * 9 + (g + 1) * 3 + b + 1] = r * int(m * m) + g * int(m) + b;
    report = {};
    bool all = true;
    for (unsigned c = 0; c < 3; ++c) {
        std::vector<std::array<double, 27>> matrix(n);
        std::vector<double> rhs(n), x(n), reg(n);
        for (const auto &p : points) {
            const auto geometry_ = geometry(model, initial.interpolation, p.rgb, c);
            double mass = p.mass;
            if (weighting == Weight::Lp6)
                mass *= std::pow(1.0 + p.error / (1.0 + threshold), 2);
            if (weighting == Weight::Tail && p.error >= threshold)
                mass *= 32;
            const double scale = 1.0 / double(std::uint64_t{1} << geometry_.shift);
            for (unsigned i = 0; i < geometry_.count; ++i) {
                if (!geometry_.weight[i])
                    continue;
                const auto a = geometry_.node[i];
                const double wi = geometry_.weight[i] * scale;
                rhs[a] += mass * wi * component(p.target, c);
                for (unsigned j = 0; j < geometry_.count; ++j) {
                    const auto b = geometry_.node[j];
                    const int dr = int(b / (m * m)) - int(a / (m * m)), dg = int(b / m % m) - int(a / m % m),
                              db = int(b % m) - int(a % m);
                    matrix[a][(dr + 1) * 9 + (dg + 1) * 3 + db + 1] +=
                        mass * wi * (geometry_.weight[j] * scale);
                }
            }
        }
        for (std::size_t i = 0; i < n; ++i) {
            x[i] = initial.nodes_data()[3 * i + c];
            reg[i] = 1e-5 * (matrix[i][13] + 1);
            rhs[i] += reg[i] * x[i];
            matrix[i][13] += reg[i];
        }
        double residual = INFINITY;
        unsigned sweeps = 0;
        for (; sweeps < max_sweeps; ++sweeps) {
            for (std::size_t i = 0; i < n; ++i) {
                double off = 0;
                for (unsigned k = 0; k < 27; ++k)
                    if (k != 13 && matrix[i][k])
                        off += matrix[i][k] * x[std::size_t(std::ptrdiff_t(i) + delta[k])];
                x[i] = (std::max)(0.0, (std::min)(255.0, (rhs[i] - off) / matrix[i][13]));
            }
            residual = 0;
            for (std::size_t i = 0; i < n; ++i) {
                double gradient = -rhs[i];
                for (unsigned k = 0; k < 27; ++k)
                    if (matrix[i][k])
                        gradient += matrix[i][k] * x[std::size_t(std::ptrdiff_t(i) + delta[k])];
                const double projected =
                    x[i] - (std::max)(0.0, (std::min)(255.0, x[i] - gradient / matrix[i][13]));
                residual = (std::max)(residual, std::abs(projected));
            }
            if (residual <= tolerance) {
                ++sweeps;
                break;
            }
        }
        report.sweeps = (std::max)(report.sweeps, sweeps);
        report.kkt = (std::max)(report.kkt, residual);
        all = all && residual <= tolerance;
        for (std::size_t i = 0; i < n; ++i)
            output[3 * i + c] = std::uint8_t(fit_detail::integer(x[i]));
    }
    report.converged = all;
    for (std::size_t i = 0; i < n; ++i)
        for (unsigned c = 0; c < 3; ++c)
            report.changed += output[3 * i + c] != initial.nodes_data()[3 * i + c];
    if (report.changed)
        clear_proof(result);
    return result;
}
inline Stage fit_source_box(const std::vector<std::uint16_t> &raw, const Stage &stage, Weight weight,
                            BoxReport &report) {
    if (raw.size() != dense_values)
        throw std::invalid_argument("独立box拟合需要完整LUT");
    const auto view = detail::view(stage);
    std::vector<Point> points(dense_nodes);
    for (std::uint32_t i = 0; i < dense_nodes; ++i) {
        const auto target = source_color(raw, i);
        points[i] = {i, target, 1, distance(detail::map(view, stage.interpolation, i), target)};
    }
    return box_fit(stage, points, weight, report);
}
} // namespace precision
} // namespace fc_framework
#endif

#include <sstream>
#include <iomanip>
namespace fc_framework {
namespace precision {
struct Options {
    bool grids = true, independent = true, matched_basis = true, box = true, irls = true, tail_fit = true;
    bool integer_chain = true, shared_coordinates = true, output_coordinates = true, tail_search = true;
    bool separable_calibration = true, finite_box = true;
    unsigned node_budget = 32, coordinate_budget = 12, sweeps = 1, dp_probes = 24, irls_rounds = 2;
    double local_fidelity_weight = 0;
    // 混合容量由调用者给出候选，空列表只保持输入容量。不得按测试图改预算。
    std::vector<std::array<unsigned, 4>> capacities;
    Guard guard{};
    Objective objective = Objective::Mean;
    std::function<void(const std::string &)> progress;
};
struct Record {
    std::string name, error;
    bool accepted = false;
    Quality quality{};
    std::uint64_t proposals = 0, updates = 0;
    double seconds = 0, kkt = 0;
    bool converged = true;
};
struct Report {
    Quality baseline{}, result{};
    std::vector<Record> records;
    std::string configuration = "{}";
};
inline std::string quality_json(const Quality &q) {
    std::ostringstream s;
    s << std::setprecision(17) << "{\"pixels\":" << q.pixels << ",\"mean\":" << q.mean << ",\"sse\":" << q.sse
      << ",\"rms\":" << q.rms << ",\"p99\":" << q.p99 << ",\"max\":" << q.max << ",\"cvar01\":" << q.cvar
      << '}';
    return s.str();
}
inline std::string json(const Report &r) {
    std::ostringstream s;
    s << std::setprecision(17) << "{\"schema\":\"lut-history-v2\",\"configuration\":" << r.configuration
      << ",\"baseline\":" << quality_json(r.baseline) << ",\"result\":" << quality_json(r.result)
      << ",\"steps\":[";
    for (std::size_t i = 0; i < r.records.size(); ++i) {
        if (i)
            s << ',';
        const auto &x = r.records[i];
        s << "{\"name\":" << std::quoted(x.name) << ",\"accepted\":" << (x.accepted ? "true" : "false")
          << ",\"quality\":" << quality_json(x.quality) << ",\"proposals\":" << x.proposals
          << ",\"updates\":" << x.updates << ",\"seconds\":" << x.seconds << ",\"kkt\":" << x.kkt
          << ",\"converged\":" << (x.converged ? "true" : "false") << ",\"error\":" << std::quoted(x.error)
          << '}';
    }
    s << "]}";
    return s.str();
}
inline Models migrate(const Sources &raw, const Models &sampled, Report &report,
                      const Options &options = {}) {
    if (!options.sweeps || options.dp_probes < 2 || options.dp_probes > 64 || options.irls_rounds > 8 ||
        !std::isfinite(options.local_fidelity_weight) || options.local_fidelity_weight < 0)
        throw std::invalid_argument("历史迁移预算非法");
    const auto gold = truth(raw);
    Models best = sampled;
    FitReport baseline_fit;
    best[3] = fit_chain_last(raw, best, baseline_fit);
    Histogram anchor = evaluate(best, gold), current = anchor;
    report = {};
    report.baseline = anchor.quality();
    {
        std::ostringstream c;
        c << std::setprecision(17) << "{\"node_budget\":" << options.node_budget
          << ",\"coordinate_budget\":" << options.coordinate_budget << ",\"sweeps\":" << options.sweeps
          << ",\"dp_probes\":" << options.dp_probes << ",\"irls_rounds\":" << options.irls_rounds
          << ",\"local_fidelity_weight\":" << options.local_fidelity_weight
          << ",\"objective\":" << unsigned(options.objective) << ",\"grids\":" << options.grids
          << ",\"independent\":" << options.independent << ",\"matched_basis\":" << options.matched_basis
          << ",\"box\":" << options.box << ",\"irls\":" << options.irls
          << ",\"tail_fit\":" << options.tail_fit << ",\"integer_chain\":" << options.integer_chain
          << ",\"shared_coordinates\":" << options.shared_coordinates
          << ",\"output_coordinates\":" << options.output_coordinates
          << ",\"tail_search\":" << options.tail_search
          << ",\"separable_calibration\":" << options.separable_calibration
          << ",\"finite_box\":" << options.finite_box << ",\"guard\":[" << options.guard.mean << ','
          << options.guard.sse << ',' << options.guard.maximum << ',' << options.guard.p99 << ','
          << options.guard.cvar << ',' << options.guard.pointwise << "],\"capacities\":[";
        for (std::size_t i = 0; i < options.capacities.size(); ++i) {
            if (i)
                c << ',';
            const auto &m = options.capacities[i];
            c << '[' << m[0] << ',' << m[1] << ',' << m[2] << ',' << m[3] << ']';
        }
        c << "]}";
        report.configuration = c.str();
        report.result = anchor.quality();
    }
    auto attempt = [&](const std::string &name, const std::function<void(Models &, Record &)> &operation) {
        if (options.progress)
            options.progress(name);
        Models candidate = best;
        Record r;
        r.name = name;
        const double start = fit_detail::seconds();
        try {
            operation(candidate, r);
        } catch (const std::runtime_error &e) {
            r.error = e.what();
            r.converged = false;
            r.quality = current.quality();
            r.seconds = fit_detail::seconds() - start;
            report.records.push_back(std::move(r));
            return;
        }
        const auto measured = evaluate(candidate, gold);
        r.quality = measured.quality();
        r.accepted = r.converged && accepts(measured, anchor, options.guard) &&
                     better(measured, current, options.objective);
        if (r.accepted && options.guard.pointwise) {
            Evaluator a(best), b(candidate);
            for (std::uint32_t i = 0; i < dense_nodes; ++i)
                if (distance(b.map(i), gold[i]) > distance(a.map(i), gold[i])) {
                    r.accepted = false;
                    break;
                }
        }
        if (r.accepted) {
            best = std::move(candidate);
            current = measured;
        }
        r.seconds = fit_detail::seconds() - start;
        report.records.push_back(std::move(r));
        report.result = current.quality();
    };
    // 固定保护锚点是已有chain_ls基线；任何新能力均不能放松其尾部上限。
    if (options.independent)
        attempt("independent_ls", [&](Models &m, Record &) {
            m = sampled;
            for (unsigned s = 0; s < 4; ++s) {
                FitReport f;
                m[s] = fit_full(raw[s], m[s], f);
            }
            FitReport f;
            m[3] = fit_chain_last(raw, m, f);
        });
    auto grid_candidate = [&](const std::array<unsigned, 4> &sizes, const std::string &grid) {
        std::string id = grid;
        for (auto m : sizes)
            id += '-' + std::to_string(m);
        attempt(id, [&](Models &m, Record &) {
            for (unsigned s = 0; s < 4; ++s) {
                bool reused = false;
                for (unsigned k = 0; k < s; ++k)
                    if (sizes[k] == sizes[s] && raw[k] == raw[s]) {
                        m[s] = m[k];
                        reused = true;
                        break;
                    }
                if (reused)
                    continue;
                FitOptions f;
                f.prove_structure = true;
                if (grid == "curvature")
                    f.axes = curvature_axes(raw[s], sizes[s]);
                else if (grid == "dp")
                    f.axes = dp_axes(raw[s], sizes[s], options.dp_probes);
                else if (grid == "error")
                    f.axes = error_axes(raw[s], sizes[s]);
                else
                    f.grid = grid == "framework" ? Grid::FrameworkStep : Grid::UniformRounded;
                m[s] = prepare_stage(raw[s], sizes[s], f);
            }
            FitReport f;
            m[3] = fit_chain_last(raw, m, f);
        });
    };
    std::array<unsigned, 4> sizes;
    for (unsigned s = 0; s < 4; ++s)
        sizes[s] = sampled[s].m;
    if (options.grids)
        for (const char *name : {"uniform", "framework", "curvature", "dp", "error"})
            grid_candidate(sizes, name);
    for (const auto &capacity : options.capacities) {
        for (auto m : capacity)
            if (m < 17 || m > 33)
                throw std::invalid_argument("混合容量越界");
        grid_candidate(capacity, "dp");
    }
    if (options.separable_calibration)
        for (unsigned s = 0; s < 4; ++s)
            attempt("exact_monotone_" + std::to_string(s), [&](Models &m, Record &r) {
                MonotoneReport proof;
                m[s] = exact_monotone(raw[s], m[s], proof);
                if (!proof.feasible)
                    r.error = "源结构、节点或单调舍入区间不满足，保留原候选";
            });
    if (options.matched_basis)
        for (unsigned stage = 0; stage < 4; ++stage)
            attempt("matched_trilinear_" + std::to_string(stage), [&](Models &m, Record &r) {
                m[stage].interpolation = Interpolation::TrilinearQ16;
                clear_proof(m[stage]);
                BoxReport b;
                if (stage == 3) {
                    Support support(m, gold, 3);
                    m[3] = box_fit(m[3], support.points, Weight::Uniform, b);
                } else
                    m[stage] = fit_source_box(raw[stage], m[stage], Weight::Uniform, b);
                r.kkt = b.kkt;
                r.converged = b.converged;
            });
    auto weighted = [&](Weight weight, const std::string &name) {
        attempt(name, [&](Models &m, Record &r) {
            Support support(m, gold, 3);
            BoxReport b;
            m[3] = box_fit(m[3], support.points, weight, b);
            r.kkt = b.kkt;
            r.converged = b.converged;
        });
    };
    if (options.box)
        weighted(Weight::Uniform, "chain_box");
    if (options.irls)
        for (unsigned i = 0; i < options.irls_rounds; ++i)
            weighted(Weight::Lp6, "chain_irls_" + std::to_string(i));
    if (options.tail_fit)
        weighted(Weight::Tail, "chain_tail_weight");
    auto nodes = [&](Objective objective, const std::string &name) {
        for (unsigned stage : {3u, 2u, 1u, 0u})
            attempt(name + '_' + std::to_string(stage), [&](Models &m, Record &r) {
                const auto x =
                    optimize_nodes(m, gold, stage, anchor, options.guard, objective, options.node_budget,
                                   options.sweeps, &raw[stage], options.local_fidelity_weight);
                r.proposals = x.proposals;
                r.updates = x.accepted;
            });
    };
    if (options.integer_chain)
        nodes(options.objective, "integer_rgb_joint");
    if (options.shared_coordinates)
        for (unsigned s = 0; s < 4; ++s)
            attempt("shared_coordinate_" + std::to_string(s), [&](Models &m, Record &r) {
                const auto x = calibrate_coordinates(m, gold, s, anchor, options.guard, options.objective,
                                                     options.coordinate_budget, false, &raw[s],
                                                     options.local_fidelity_weight);
                r.proposals = x.proposals;
                r.updates = x.accepted;
            });
    if (options.output_coordinates)
        for (unsigned s = 0; s < 4; ++s)
            attempt("output_coordinate_" + std::to_string(s), [&](Models &m, Record &r) {
                const auto x = calibrate_coordinates(m, gold, s, anchor, options.guard, options.objective,
                                                     options.coordinate_budget, true, &raw[s],
                                                     options.local_fidelity_weight);
                r.proposals = x.proposals;
                r.updates = x.accepted;
            });
    if (options.tail_search) {
        nodes(Objective::Maximum, "minimax");
        nodes(Objective::P99, "p99");
        nodes(Objective::CVaR, "cvar");
    }
    if (options.finite_box)
        attempt("frozen_integer_box", [&](Models &m, Record &r) {
            Support support(m, gold, 3);
            const auto found =
                std::max_element(support.points.begin(), support.points.end(),
                                 [](const Point &a, const Point &b) { return a.error < b.error; });
            const auto g = geometry(detail::view(m[3]), m[3].interpolation, found->rgb, 0);
            const auto node =
                g.node[std::max_element(g.weight.begin(), g.weight.begin() + g.count) - g.weight.begin()];
            const auto x = exact_integer_box(m, gold, 3, {{node, 0, 1}, {node, 1, 1}, {node, 2, 1}}, anchor,
                                             options.guard, options.objective, 27);
            r.proposals = x.proposals;
            r.updates = x.accepted;
        });
    report.result = current.quality();
    return best;
}
} // namespace precision
} // namespace fc_framework
#endif

#include <iostream>

namespace candidate {
using namespace fc_framework;
using namespace fc_framework::precision;

inline std::vector<std::string> variants() {
    return {"prefix_nodes", "prefix_nodes_refit"};
}

struct PrefixSummary {
    std::uint64_t distinct = 0, minimum_integer_sse = 0;
};

// 固定前三层后，每个到达颜色允许选择任意 RGB8 输出，给出末层 SSE 的宽松下界。
inline PrefixSummary prefix_summary(const Models& models,
                                    const std::vector<std::uint32_t>& gold) {
    struct Aggregate {
        std::uint32_t count = 0;
        std::array<std::uint32_t, 3> sum{};
    };
    static_assert(sizeof(Aggregate) == 16, "聚合内存预算变化");
    std::vector<Aggregate> groups(dense_nodes);
    Evaluator evaluator(models);
    std::int64_t total_squared = 0;
    for (std::uint32_t input = 0; input < dense_nodes; ++input) {
        auto& group = groups[evaluator.map(input, 0, 3)];
        ++group.count;
        for (unsigned c = 0; c < 3; ++c) {
            const auto value = component(gold[input], c);
            group.sum[c] += value;
            total_squared += value * value;
        }
    }
    PrefixSummary result;
    for (const auto& group : groups) {
        if (!group.count) continue;
        ++result.distinct;
        for (unsigned c = 0; c < 3; ++c) {
            const std::int64_t mass = group.count, sum = group.sum[c];
            const std::int64_t best = (2 * sum + mass) / (2 * mass);
            total_squared += mass * best * best - 2 * best * sum;
        }
    }
    if (total_squared < 0) throw std::runtime_error("前缀下界计算出现负 SSE");
    result.minimum_integer_sse = std::uint64_t(total_squared);
    return result;
}

inline Models run(const Sources& raw, const Models& baseline,
                  const std::vector<std::uint32_t>& gold, const std::string& variant,
                  std::string& details_json) {
    if (variant != "prefix_nodes" && variant != "prefix_nodes_refit")
        throw std::invalid_argument("未知前中层实验变体");
    if (gold.size() != dense_nodes) throw std::invalid_argument("完整域参考长度不符");
    for (unsigned s = 0; s < 4; ++s) {
        if (raw[s].size() != dense_values || baseline[s].m != 33 ||
            !baseline[s].fractions.empty() || baseline[s].interpolation != Interpolation::TetraQ16)
            throw std::invalid_argument("本实验仅接受四级33立方共享坐标四面体基线");
    }
    const Guard guard{};
    const Histogram anchor = evaluate(baseline, gold);
    Histogram current = anchor;
    Models best = baseline;
    Report report;
    report.baseline = anchor.quality();
    report.result = report.baseline;
    report.configuration = "{\"variant\":\"" + variant +
        "\",\"stage_order_zero_based\":[2,1],\"nodes_per_stage\":32,\"sweeps\":1,"
        "\"rgb_directions\":26,\"steps\":[1,2,4],\"all_five_guards\":true,"
        "\"reads_photos\":false,\"prefix_diagnostic_peak_bytes\":268435456}";
    std::vector<std::uint64_t> support_rows;

    for (const unsigned stage : {2u, 1u}) {
        std::cerr << "前中层节点搜索：第" << stage + 1 << "级" << std::endl;
        Record row;
        row.name = "prefix_stage_" + std::to_string(stage + 1);
        const auto start = fit_detail::seconds();
        Models proposed = best;
        const auto search = optimize_nodes(proposed, gold, stage, anchor, guard,
                                            Objective::Mean, 32, 1);
        support_rows.push_back(search.support_rows);
        const auto measured = evaluate(proposed, gold);
        if (measured.sse != search.after.sse ||
            std::abs(measured.quality().mean - search.after.mean) > 1e-12)
            throw std::runtime_error("前中层增量评估与完整色域重放不符");
        row.proposals = search.proposals;
        row.updates = search.accepted;
        row.quality = measured.quality();
        row.accepted = accepts(measured, anchor, guard) && better(measured, current, Objective::Mean);
        if (row.accepted) { best = std::move(proposed); current = measured; }
        row.seconds = fit_detail::seconds() - start;
        report.records.push_back(row);
        report.result = current.quality();
    }

    FitReport fit;
    bool refit_attempted = false;
    if (variant == "prefix_nodes_refit") {
        std::cerr << "冻结更新后前三层，重拟合第4级" << std::endl;
        refit_attempted = true;
        Record row;
        row.name = "refit_stage_4";
        const auto start = fit_detail::seconds();
        Models proposed = best;
        FitExperimentOptions options;
        // 返回原始提议，由下方完整五项门控裁决，以保留被拒绝结果的指标。
        options.guard_full_domain = false;
        proposed[3] = fit_chain_last(raw, best, fit, options);
        row.converged = true;
        for (const auto& channel : fit.channels) row.converged &= channel.converged;
        const auto measured = evaluate(proposed, gold);
        row.quality = measured.quality();
        row.updates = fit.changed_nodes;
        row.proposals = 1;
        row.accepted = row.converged && accepts(measured, anchor, guard) &&
                       better(measured, current, Objective::Mean);
        if (!row.converged) row.error = "末级拟合未达到既定CG收敛阈值，保留重拟合前候选";
        if (row.accepted) { best = std::move(proposed); current = measured; }
        row.seconds = fit_detail::seconds() - start;
        report.records.push_back(row);
        report.result = current.quality();
    }
    std::cerr << "计算基线和候选的固定前缀下界" << std::endl;
    const auto before_prefix = prefix_summary(baseline, gold);
    const auto after_prefix = prefix_summary(best, gold);
    std::ostringstream extra;
    extra << std::setprecision(17) << "{\"report\":" << json(report)
          << ",\"support_rows\":[" << support_rows[0] << ',' << support_rows[1] << ']'
          << ",\"prefix_before\":{\"distinct\":" << before_prefix.distinct
          << ",\"minimum_integer_sse\":" << before_prefix.minimum_integer_sse << '}'
          << ",\"prefix_after\":{\"distinct\":" << after_prefix.distinct
          << ",\"minimum_integer_sse\":" << after_prefix.minimum_integer_sse << '}'
          << ",\"refit_attempted\":" << (refit_attempted ? "true" : "false")
          << ",\"refit_channels\":[";
    for (unsigned c = 0; c < 3; ++c) {
        if (c) extra << ',';
        extra << "{\"iterations\":" << fit.channels[c].iterations
              << ",\"relative_residual\":" << fit.channels[c].relative_residual
              << ",\"converged\":" << (fit.channels[c].converged ? "true" : "false") << '}';
    }
    extra << "],\"photos_used_for_selection\":false}";
    details_json = extra.str();
    return best;
}
} // namespace candidate
#endif

#include <cstdio>

namespace fc_delivery {
inline fc_framework::FitOptions sampling_options() {
    fc_framework::FitOptions o; o.grid=fc_framework::Grid::FrameworkStep; o.prove_structure=false; return o;
}
template<class Lut>
bool sample(const std::vector<std::uint16_t>& raw,int size,Lut& output) {
    try { const auto s=fc_framework::prepare_stage(raw,unsigned(size),sampling_options());
        output.data.assign(s.nodes_data(),s.nodes_data()+s.node_bytes());output.size=int(s.m);return true;
    } catch(const std::exception& e){std::fprintf(stderr,"采样失败：%s\n",e.what());return false;}
}
template<class Lut>
class Pipeline {
    fc_framework::precision::Models stages_{};
    std::array<const Lut*,4> bindings_{};
    fc_framework::Chain chain_;
    fc_framework::FitReport fit_{};
    bool ready_=false;
    double fit_seconds_=0,search_seconds_=0,prepare_seconds_=0;
    std::string search_report_="{}";
public:
    bool prepare(const fc_framework::precision::Sources& raw,std::array<Lut,4>& models) {
        ready_=false; bindings_={};search_report_="{}";
        try {
            for(unsigned i=0;i<4;++i){
                stages_[i]=fc_framework::prepare_stage(raw[i],unsigned(models[i].size),sampling_options());
                if(models[i].data.size()!=stages_[i].node_bytes() || !std::equal(models[i].data.begin(),models[i].data.end(),stages_[i].nodes_data()))return false;
            }
            auto t=fc_framework::fit_detail::seconds();
            fc_framework::FitExperimentOptions fit_options;
            stages_[3]=fc_framework::fit_chain_last(raw,stages_,fit_,fit_options);
            fit_seconds_=fc_framework::fit_detail::seconds()-t;
            t=fc_framework::fit_detail::seconds();
            bool all33=true;for(const auto& s:stages_)all33&=s.m==33;
            if(all33){const auto gold=fc_framework::precision::truth(raw);
                stages_=candidate::run(raw,stages_,gold,"prefix_nodes",search_report_);}
            search_seconds_=fc_framework::fit_detail::seconds()-t;
            for(unsigned i=0;i<4;++i)models[i].data.assign(stages_[i].nodes_data(),stages_[i].nodes_data()+stages_[i].node_bytes());
            std::array<const fc_framework::Stage*,4> pointers{{&stages_[0],&stages_[1],&stages_[2],&stages_[3]}};
            fc_framework::Options o;o.backend=fc::Backend::Auto;o.structure=false;o.threads=1;
            o.representation=FLASH_CHROMA_ENABLE_DIRECT?fc::Representation::DirectRGB24:fc::Representation::Sparse;
            o.block_pixels=65536;o.max_workspace_bytes=64*fc::MiB;
            t=fc_framework::fit_detail::seconds();
            auto status=chain_.prepare(pointers,o);
            if(status!=fc::Status::Ok && o.representation==fc::Representation::DirectRGB24){o.representation=fc::Representation::Sparse;status=chain_.prepare(pointers,o);}
            prepare_seconds_=fc_framework::fit_detail::seconds()-t;
            if(status!=fc::Status::Ok)return false;
            for(unsigned i=0;i<4;++i)bindings_[i]=&models[i];ready_=true;return true;
        }catch(const std::exception& e){std::fprintf(stderr,"final1准备失败：%s\n",e.what());return false;}
    }
    template<class Image>
    bool apply(const Image& source,const Lut& l1,const Lut& l2,const Lut& l3,const Lut& l4,Image& output)const{
        if(!ready_||source.C!=3||source.H<=0||source.W<=0||bindings_!=std::array<const Lut*,4>{{&l1,&l2,&l3,&l4}}||
           output.H!=source.H||output.W!=source.W||output.C!=source.C||source.data.size()!=source.size()||output.data.size()!=source.size())return false;
        return chain_.apply(source.ptr(),output.ptr(),std::size_t(source.H)*source.W)==fc::Status::Ok;
    }
    const auto& stages()const noexcept{return stages_;}
    const auto& info()const noexcept{return chain_.info();}
    const auto& fit_report()const noexcept{return fit_;}
    const auto& search_report()const noexcept{return search_report_;}
    double fit_seconds()const noexcept{return fit_seconds_;}
    double search_seconds()const noexcept{return search_seconds_;}
    double prepare_seconds()const noexcept{return prepare_seconds_;}
};
}
#endif
