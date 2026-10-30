/* 准备缓存合同：可证明/不可证明/超预算域及palette超集回退。
 * 与修复统一构建后执行；本文件不把缓存superset颜色数当完整RGB8可达计数。
 */
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
#include <vector>
#include <cstdio>
#include <cstdlib>

namespace {
void check(bool ok,const char* what) {
    if(!ok) {std::fprintf(stderr,"准备缓存合同失败：%s\n",what);std::exit(1);}
}
void put32(std::uint8_t* p,std::uint32_t n) {
    for(unsigned i=0;i<4;++i)p[i]=std::uint8_t(n>>(8*i));
}
std::uint32_t bits(unsigned n) {
    if(!n)return 0;
    unsigned exponent=150;
    while(n<(1u<<23)) {n<<=1;--exponent;}
    return (exponent<<23)|(n&0x7fffffu);
}
unsigned grid(unsigned i,unsigned m) {return i*255/(m-1);}
/* kind：0=恒等、1=首轴灰阶、2=常量、3=RG二维输出。 */
std::vector<std::uint8_t> make(unsigned m,unsigned kind) {
    const std::size_t axis=16+12*m,nodes=axis+3840;
    std::vector<std::uint8_t> bytes(nodes+std::size_t(m)*m*m*3);
    auto* p=bytes.data();p[0]='S';p[1]='L';p[2]='U';p[3]='T';put32(p+4,1);put32(p+8,m);
    for(unsigned a=0;a<3;++a) {
        for(unsigned i=0;i<m;++i)put32(p+16+4*(a*m+i),bits(grid(i,m)));
        for(unsigned x=0;x<256;++x) {
            unsigned cell=0;while(cell<m-2&&grid(cell+1,m)<=x)++cell;
            const auto lo=grid(cell,m),hi=grid(cell+1,m);
            p[axis+a*256+x]=std::uint8_t(cell);
            put32(p+axis+768+4*(a*256+x),((x-lo)*65536+(hi-lo)/2)/(hi-lo));
        }
    }
    for(unsigned r=0;r<m;++r)for(unsigned g=0;g<m;++g)for(unsigned b=0;b<m;++b) {
        const auto i=nodes+((std::size_t(r)*m+g)*m+b)*3;
        p[i]=kind==2?17:std::uint8_t(grid(r,m));
        p[i+1]=kind==2?73:std::uint8_t(grid(kind==1?r:g,m));
        p[i+2]=kind==2?209:(kind==3?0:std::uint8_t(grid(kind==1?r:b,m)));
    }
    return bytes;
}
std::vector<std::uint8_t> side(const std::vector<std::uint8_t>& blob,bool break_domain) {
    const unsigned m=unsigned(blob[8])|(unsigned(blob[9])<<8);
    const auto* fractions=blob.data()+16+12*m+768;
    std::vector<std::uint8_t> value(9216);
    for(unsigned c=0;c<3;++c)for(unsigned a=0;a<3;++a)for(unsigned x=0;x<256;++x) {
        const auto* p=fractions+(a*256+x)*4;
        unsigned f=unsigned(p[0])|(unsigned(p[1])<<8)|(unsigned(p[2])<<16)|(unsigned(p[3])<<24);
        if(break_domain&&a==0&&c==1)f=65536;
        if(break_domain&&a==0&&c==2)f=0;
        put32(value.data()+(c*768+a*256+x)*4,f);
    }
    return value;
}
void exercise(unsigned fixture,unsigned threads,fc::Representation representation=fc::Representation::DirectU8) {
    const unsigned sizes[4]={17,18,25,33};
    std::vector<std::uint8_t> blobs[4],sides[4];
    for(unsigned s=0;s<4;++s)blobs[s]=make(sizes[s],0);
    if(fixture<=2)blobs[0]=make(sizes[0],1);
    if(fixture==0)blobs[3]=make(sizes[3],2);
    if(fixture==3)blobs[3]=make(sizes[3],1);
    if(fixture==0)for(unsigned s=0;s<4;++s)sides[s]=side(blobs[s],false);
    if(fixture==2)sides[0]=side(blobs[0],true);
    fc::ModelBundle bundle;
    fc_core::fc_model views[4]{};const fc_core::fc_model* pointers[4];
    for(unsigned s=0;s<4;++s) {
        bundle.models[s]={blobs[s].data(),blobs[s].size()};
        if(!sides[s].empty())bundle.sidecars[s]={sides[s].data(),sides[s].size()};
        check(fc_core::fc_model_init(views+s,bundle.models[s],bundle.sidecars[s])==fc_core::FC_OK,"参考模型");pointers[s]=views+s;
    }
    fc_core::fc_chain chain;check(fc_core::fc_chain_init(&chain,pointers)==fc_core::FC_OK,"参考链");
    fc::RuntimeConfig config;config.backend=fc::Backend::Avx2;config.representation=representation;
    config.threads=threads;config.block_pixels=31;
    fc::Requirements requirements;
    check(fc::Runtime::requirements(bundle,config,&requirements)==fc::Status::Ok,"资源查询");
    check(requirements.object_bytes==sizeof(fc::Runtime),"诊断字段计入对象容量");
    fc::RuntimeConfig denied=config;denied.max_workspace_bytes=requirements.arena_bytes-1;
    fc::Requirements unchanged;
    check(fc::Runtime::requirements(bundle,denied,&unchanged)==fc::Status::Budget,"少一字节预算拒绝");
    std::vector<std::uint8_t> arena(requirements.arena_bytes+2,0xa7);fc::Runtime runtime;
    check(fc::Runtime::prepare(bundle,config,{arena.data()+1,requirements.arena_bytes-1},&runtime)==fc::Status::Budget,"少一字节工作区拒绝");
    check(fc::Runtime::prepare(bundle,config,{arena.data()+1,requirements.arena_bytes},&runtime)==fc::Status::Ok,"完整准备");
    check(arena.front()==0xa7&&arena.back()==0xa7,"准备不越arena");
#if FLASH_CHROMA_ENABLE_PREPARE_CACHE
    const bool cached=fixture==0||(fixture==1&&representation!=fc::Representation::DirectU8);
    check(runtime.prepared_with_suffix_cache()==cached,"缓存证明/资格及回退选择");
    check((runtime.preparation_cache_entries()!=0)==cached,"缓存槽诊断");
#else
    check(!runtime.prepared_with_suffix_cache()&&!runtime.preparation_cache_entries(),"关闭缓存确实裁剪");
#endif
    const auto palette_count=representation==fc::Representation::DirectRGB24?0u:(fixture==0?1u:256u);
    check(runtime.palette_entries()==palette_count,"实际完整RGB8可达palette计数");
    std::vector<std::uint8_t> input(3*1025),output(input.size()+2,0x5a),truth(input.size());
    for(std::size_t i=0;i<input.size();++i)input[i]=std::uint8_t(i*73+19);
    check(fc_core::fc_apply_rgb8(&chain,input.data(),input.size(),input.size(),truth.data(),truth.size(),truth.size(),1025,1)==fc_core::FC_OK,"独立标量参考");
    check(runtime.apply(input.data(),input.size(),input.size(),output.data()+1,input.size(),input.size(),1025,1)==fc::Status::Ok,"实际direct映射");
    for(std::size_t i=0;i<input.size();++i)check(output[i+1]==truth[i],"direct与四级参考一致");
    check(output.front()==0x5a&&output.back()==0x5a,"映射哨兵");
}
}
int main() {
    if(!(fc::available_backends()&2u)) {std::puts("准备缓存合同：当前构建/CPU无AVX2，未执行快路径");return 0;}
    for(unsigned fixture=0;fixture<4;++fixture)exercise(fixture,1);
    exercise(1,1,fc::Representation::DirectU16);
    exercise(1,1,fc::Representation::DirectRGB24);
#if FLASH_CHROMA_ENABLE_OPENMP
    exercise(0,4);
#endif
    std::puts("准备缓存合同通过：小域、palette超集回退、分输出证明拒绝、域容量回退及完整预算");
    return 0;
}
