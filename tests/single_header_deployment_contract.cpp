/* 部署开关与双头包含合同。使用 -DFLASH_CHROMA_TARGET=1/2/3/4 分别构建。
 * -DFC_DEPLOYMENT_C_FIRST=1 先包含 C99 头；默认先包含 C++ 头。
 * 不依赖容器、堆、异常、RTTI、文件或宿主 stdio，失败返回对应源码行号。
 */
#if defined(FC_DEPLOYMENT_C_FIRST) && FC_DEPLOYMENT_C_FIRST
#define FC_C_IMPLEMENTATION
#include "flash_chroma_c.h"
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
#else
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
#define FC_C_IMPLEMENTATION
#include "flash_chroma_c.h"
#endif

#define CHECK(condition) do { if (!(condition)) return __LINE__; } while (false)

static_assert(FLASH_CHROMA_ENABLE_DIRECT == (FLASH_CHROMA_TARGET <= 2), "默认direct裁剪不符");
#if FLASH_CHROMA_TARGET >= 3
static_assert(FLASH_CHROMA_ENABLE_AVX2 == 0, "端侧默认关闭AVX2");
static_assert(FLASH_CHROMA_ENABLE_OPENMP == 0, "端侧默认关闭OpenMP");
#endif

namespace {
constexpr unsigned m = 17;
constexpr std::size_t model_size = 16 + 12*m + 3840 + 3*m*m*m;
std::uint8_t blobs[4][model_size + 1];
std::uint8_t sidecar[FC_C_SIDECAR_BYTES + 1];
std::uint8_t input[3*257 + 2], actual[3*257 + 2], reference[3*257 + 2];

void put32(std::uint8_t* p, std::uint32_t value) {
    for (unsigned i=0; i<4; ++i) p[i]=static_cast<std::uint8_t>(value>>(8*i));
}
std::uint32_t float_bits(std::uint32_t value) {
    std::uint32_t exponent=150;
    if (!value) return 0;
    while (value < (1u<<23)) { value<<=1; --exponent; }
    return (exponent<<23) | (value&0x7fffffu);
}
unsigned grid(unsigned i) { return i*255/(m-1); }
void make_model(std::uint8_t* p, std::uint32_t seed) {
    for (std::size_t i=0; i<model_size; ++i) p[i]=0;
    p[0]='S'; p[1]='L'; p[2]='U'; p[3]='T'; put32(p+4,1); put32(p+8,m);
    const unsigned axis=16+12*m;
    for (unsigned a=0; a<3; ++a) {
        for (unsigned i=0; i<m; ++i) put32(p+16+4*(a*m+i),float_bits(grid(i)));
        for (unsigned x=0; x<256; ++x) {
            unsigned cell=0;
            while (cell<m-2 && grid(cell+1)<=x) ++cell;
            const unsigned lo=grid(cell), hi=grid(cell+1);
            p[axis+a*256+x]=static_cast<std::uint8_t>(cell);
            put32(p+axis+768+4*(a*256+x),((x-lo)*65536+(hi-lo)/2)/(hi-lo));
        }
    }
    for (std::size_t i=axis+3840; i<model_size; ++i) {
        seed=seed*1664525u+1013904223u;
        p[i]=static_cast<std::uint8_t>(seed>>24);
    }
}
}

int main() {
    CHECK((fc::compiled_capabilities()&1u)!=0);
#if FLASH_CHROMA_TARGET >= 3
    CHECK(fc::compiled_capabilities()==1u && fc::available_backends()==1u);
#endif
    for (unsigned s=0; s<4; ++s) make_model(blobs[s]+1,s+37);
    const std::uint32_t fractions[7]={0,1,32767,32768,32769,65535,65536};
    for (unsigned c=0; c<3; ++c) for (unsigned a=0; a<3; ++a) for (unsigned x=0; x<256; ++x)
        put32(sidecar+1+4*((c*3+a)*256+x),fractions[(c+a+x)%7]);
    std::uint32_t seed=20261027;
    for (std::size_t i=0; i<sizeof(input); ++i) {
        seed=seed*1664525u+1013904223u;
        input[i]=static_cast<std::uint8_t>(seed>>24);
    }
    for (unsigned mode=0; mode<2; ++mode) {
        fc::ModelBundle bundle;
        fc_model c_models[4];
        const fc_model* pointers[4];
        for (unsigned s=0; s<4; ++s) {
            bundle.models[s]={blobs[s]+1,model_size};
            if (mode && !s) bundle.sidecars[s]={sidecar+1,FC_C_SIDECAR_BYTES};
            const fc_bytes blob={bundle.models[s].data,bundle.models[s].size};
            const fc_bytes side={bundle.sidecars[s].data,bundle.sidecars[s].size};
            CHECK(fc_model_init(c_models+s,blob,side)==FC_OK);
            pointers[s]=c_models+s;
        }
        fc_chain c_chain;
        CHECK(fc_chain_init(&c_chain,pointers)==FC_OK);
        fc::RuntimeConfig config;
        config.backend=fc::Backend::Scalar;
        config.max_workspace_bytes=0;
        config.block_pixels=13;
        fc::Requirements resources;
        CHECK(fc::Runtime::requirements(bundle,config,&resources)==fc::Status::Ok);
        CHECK(resources.arena_bytes==0 && resources.temporary_bytes==0 && resources.persistent_bytes==0);
        CHECK(resources.model_bytes==4*model_size+(mode ? FC_C_SIDECAR_BYTES : 0));
        fc::Runtime runtime;
        CHECK(fc::Runtime::prepare(bundle,config,{nullptr,0},&runtime)==fc::Status::Ok);
        CHECK(runtime.selected_backend()==fc::Backend::Scalar);
        for (std::size_t n=0; n<=257; ++n) {
            for (std::size_t i=0; i<sizeof(actual); ++i) actual[i]=reference[i]=0x6a;
            CHECK(fc_apply_rgb8(&c_chain,input+1,sizeof(input)-2,n*3,
                reference+1,sizeof(reference)-2,n*3,n,1)==FC_OK);
            CHECK(runtime.apply(input+1,sizeof(input)-2,n*3,actual+1,sizeof(actual)-2,n*3,n,1)==fc::Status::Ok);
            for (std::size_t i=0; i<sizeof(actual); ++i) CHECK(actual[i]==reference[i]);
        }
        const auto selected=runtime.config();
        CHECK(selected.target==static_cast<fc::Target>(FLASH_CHROMA_TARGET));
        fc::RuntimeConfig invalid=config;
        invalid.backend=fc::Backend::Avx512;
        CHECK(fc::Runtime::requirements(bundle,invalid,&resources)==fc::Status::Unsupported);
        invalid=config; invalid.threads=0;
        CHECK(fc::Runtime::requirements(bundle,invalid,&resources)==fc::Status::Range);
        invalid=config; invalid.threads=257;
        CHECK(fc::Runtime::requirements(bundle,invalid,&resources)==fc::Status::Range);
        invalid=config; invalid.target=static_cast<fc::Target>(0);
        CHECK(fc::Runtime::requirements(bundle,invalid,&resources)==fc::Status::Range);
#if FLASH_CHROMA_TARGET >= 3
        invalid=config; invalid.target=fc::Target::Desktop;
        CHECK(fc::Runtime::requirements(bundle,invalid,&resources)==fc::Status::Unsupported);
        invalid=config; invalid.representation=fc::Representation::DirectU8;
        CHECK(fc::Runtime::requirements(bundle,invalid,&resources)==fc::Status::Unsupported);
        invalid=config; invalid.backend=fc::Backend::Avx2;
        CHECK(fc::Runtime::requirements(bundle,invalid,&resources)==fc::Status::Unsupported);
#endif
#if !FLASH_CHROMA_ENABLE_OPENMP
        invalid=config; invalid.threads=2;
        CHECK(fc::Runtime::requirements(bundle,invalid,&resources)==fc::Status::Unsupported);
#endif
    }
    return 0;
}
