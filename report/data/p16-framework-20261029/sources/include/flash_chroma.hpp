/* 自动生成：修改同源 C 核或 src 中的 inc 文件后运行生成脚本。 */
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
/* flash-chroma：四级 RGB8/Q16 单头 C99 运行库。
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
#ifndef FLASH_CHROMA_TARGET
#define FLASH_CHROMA_TARGET FLASH_CHROMA_TARGET_DESKTOP
#endif
#if FLASH_CHROMA_TARGET < 1 || FLASH_CHROMA_TARGET > 4
#error "FLASH_CHROMA_TARGET 必须是支持的部署目标"
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

/* RGB24保留已有gather路线、精确24B图像读写与表尾guard契约。 */
FC_AVX2 inline void direct_rgb24_run(const std::uint8_t* table,const std::uint8_t* src,
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
    if(__get_cpuid(1,&a,&b,&c,&d)&&(c&(1u<<27))&&(c&(1u<<28))) {
        unsigned xlo=0,xhi=0;__asm__ volatile("xgetbv":"=a"(xlo),"=d"(xhi):"c"(0));
        if((xlo&6)==6&&__get_cpuid_count(7,0,&a,&b,&c,&d)&&(b&(1u<<5)))mask|=2;
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
