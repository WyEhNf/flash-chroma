/* 单头运行库合同：检查配置确实控制表示、预算、执行与拒绝行为。
 * 模型采用混合 m 的可复现整数节点；像素参考由同源独立 C 路径执行。
 * C 核本身另由 single_header_c_contract.c 的 u64 oracle 验证。
 */
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace {
void check(bool ok,const char* message) {
    if(!ok) {std::fprintf(stderr,"合同失败：%s\n",message);std::exit(1);}
}
void put32(std::vector<std::uint8_t>& b,std::size_t at,std::uint32_t v) {
    for(unsigned i=0;i<4;++i)b[at+i]=std::uint8_t(v>>(i*8));
}
std::vector<std::uint8_t> model(unsigned m,unsigned mode) {
    const std::size_t nodes=16+12*m+3840;
    std::vector<std::uint8_t> b(nodes+std::size_t(m)*m*m*3);
    b[0]='S';b[1]='L';b[2]='U';b[3]='T';put32(b,4,1);put32(b,8,m);
    for(unsigned axis=0;axis<3;++axis)for(unsigned i=0;i<m;++i) {
        const float f=float(i)*255.0f/float(m-1);std::uint32_t bits;std::memcpy(&bits,&f,4);put32(b,16+(axis*m+i)*4,bits);
    }
    for(unsigned axis=0;axis<3;++axis)for(unsigned i=0;i<256;++i) {
        unsigned cell=i*(m-1)/255;if(cell==m-1)--cell;
        b[16+12*m+axis*256+i]=std::uint8_t(cell);
        const auto fraction=std::uint32_t(((std::uint64_t(i)*(m-1)-std::uint64_t(cell)*255)*65536+127)/255);
        put32(b,16+12*m+768+(axis*256+i)*4,fraction);
    }
    for(unsigned r=0;r<m;++r)for(unsigned g=0;g<m;++g)for(unsigned bl=0;bl<m;++bl) {
        const std::size_t at=nodes+((std::size_t(r)*m+g)*m+bl)*3;
        b[at]=mode==1?17:std::uint8_t((r*255+(m-1)/2)/(m-1));
        b[at+1]=mode==1?73:std::uint8_t((g*255+(m-1)/2)/(m-1));
        b[at+2]=mode==1?209:(mode==2?0:std::uint8_t((bl*255+(m-1)/2)/(m-1)));
    }
    return b;
}
void test_rep(const fc::ModelBundle& bundle,fc::Representation rep,fc::Backend backend,
    const std::vector<std::uint8_t>& input,const std::vector<std::uint8_t>& expected) {
    fc::RuntimeConfig cfg;cfg.representation=rep;cfg.backend=backend;cfg.block_pixels=31;
#if FLASH_CHROMA_ENABLE_OPENMP
    cfg.threads=4;
#endif
    fc::Requirements req;check(fc::Runtime::requirements(bundle,cfg,&req)==fc::Status::Ok,"容量查询");
    cfg.max_workspace_bytes=req.arena_bytes;
    if(req.arena_bytes) {
        fc::RuntimeConfig less=cfg;less.max_workspace_bytes=req.arena_bytes-1;
        check(fc::Runtime::requirements(bundle,less,&req)==fc::Status::Budget,"少一字节预算拒绝");
        check(fc::Runtime::requirements(bundle,cfg,&req)==fc::Status::Ok,"重新查询");
    }
    std::vector<std::uint8_t> arena(req.arena_bytes+2,0xa5);
    fc::Runtime runtime;
    if(req.arena_bytes)check(fc::Runtime::prepare(bundle,cfg,{arena.data()+1,req.arena_bytes-1},&runtime)==fc::Status::Budget,"少一字节工作区拒绝");
    check(fc::Runtime::prepare(bundle,cfg,{arena.data()+1,req.arena_bytes},&runtime)==fc::Status::Ok,"准备");
    check(runtime.ready()&&runtime.selected_backend()==backend,"后端诊断");
    const auto width=input.size()/3;
    std::vector<std::uint8_t> output(input.size()+2,0x5a);
    check(runtime.apply(input.data(),input.size(),input.size(),output.data()+1,input.size(),input.size(),width,1)==fc::Status::Ok,"分离执行");
    check(std::memcmp(output.data()+1,expected.data(),input.size())==0,"分离输出一致");
    check(output.front()==0x5a&&output.back()==0x5a,"输出哨兵");
    auto in_place=input;
    check(runtime.apply(in_place.data(),in_place.size(),in_place.size(),in_place.data(),in_place.size(),in_place.size(),width,1)==fc::Status::Ok,"原地执行");
    check(in_place==expected,"原地输出一致");
    const auto before=output;
    check(runtime.apply(output.data(),input.size(),input.size(),output.data()+1,input.size(),input.size(),width,1)==fc::Status::Overlap,"部分重叠拒绝");
    check(output==before,"拒绝不改输出");
    check(runtime.apply(nullptr,0,0,nullptr,0,0,0,55)==fc::Status::Ok,"空图");
    check(arena.front()==0xa5&&arena.back()==0xa5,"arena哨兵");
    if(rep==fc::Representation::DirectU8)check(runtime.palette_entries()==1,"常量调色板计数");
    if(rep==fc::Representation::DirectU16)check(runtime.palette_entries()>256,"宽调色板资格");
    const std::size_t stride=17*3+7, rows=5;
    std::vector<std::uint8_t> padded(stride*rows,0x9c),target(stride*rows,0x9c),reference(stride*rows,0x9c);
    for(std::size_t y=0;y<rows;++y)std::memcpy(padded.data()+y*stride,input.data()+y*17*3,17*3);
    fc_core::fc_model models[4]{};const fc_core::fc_model* pointers[4];
    for(unsigned i=0;i<4;++i) {check(fc_core::fc_model_init(models+i,bundle.models[i],bundle.sidecars[i])==fc_core::FC_OK,"stride参考模型");pointers[i]=models+i;}
    fc_core::fc_chain chain;check(fc_core::fc_chain_init(&chain,pointers)==fc_core::FC_OK,"stride参考链");
    check(fc_core::fc_apply_rgb8(&chain,padded.data(),padded.size(),stride,reference.data(),reference.size(),stride,17,rows)==fc_core::FC_OK,"stride参考");
    check(runtime.apply(padded.data(),padded.size(),stride,target.data(),target.size(),stride,17,rows)==fc::Status::Ok,"stride执行");
    check(target==reference,"stride及padding一致");
}
}
int main() {
    std::vector<std::uint8_t> blobs[4]={model(17,0),model(18,0),model(25,0),model(33,0)};
    std::vector<std::uint8_t> sidecar(9216);
    for(unsigned c=0;c<3;++c)for(unsigned a=0;a<3;++a)for(unsigned i=0;i<256;++i) {
        const unsigned cell=blobs[0][16+12*17+a*256+i];
        unsigned f=std::uint32_t(((std::uint64_t(i)*16-std::uint64_t(cell)*255)*65536+127)/255);
        f=(c==1&&f<65500)?f+31:f;put32(sidecar,(c*768+a*256+i)*4,f);
    }
    fc::ModelBundle bundle;
    for(unsigned i=0;i<4;++i)bundle.models[i]={blobs[i].data(),blobs[i].size()};
    bundle.sidecars[0]={sidecar.data(),sidecar.size()};
    std::vector<std::uint8_t> input(257*3),expected(input.size());
    for(std::size_t i=0;i<input.size();++i)input[i]=std::uint8_t(i*73+19);
    fc_core::fc_model models[4]{};const fc_core::fc_model* pointers[4];
    for(unsigned i=0;i<4;++i) {check(fc_core::fc_model_init(models+i,bundle.models[i],bundle.sidecars[i])==fc_core::FC_OK,"混合m模型");pointers[i]=models+i;}
    fc_core::fc_chain chain;check(fc_core::fc_chain_init(&chain,pointers)==fc_core::FC_OK,"参考链");
    check(fc_core::fc_apply_rgb8(&chain,input.data(),input.size(),input.size(),expected.data(),expected.size(),expected.size(),257,1)==fc_core::FC_OK,"参考输出");
    test_rep(bundle,fc::Representation::Sparse,fc::Backend::Scalar,input,expected);
    if(fc::available_backends()&2)test_rep(bundle,fc::Representation::Sparse,fc::Backend::Avx2,input,expected);
#if FLASH_CHROMA_ENABLE_DIRECT
    {
        const auto direct_backend=(fc::available_backends()&2)?fc::Backend::Avx2:fc::Backend::Scalar;
        test_rep(bundle,fc::Representation::DirectRGB24,direct_backend,input,expected);
        blobs[3]=model(33,1);bundle.models[3]={blobs[3].data(),blobs[3].size()};
        for(std::size_t i=0;i<expected.size();i+=3){expected[i]=17;expected[i+1]=73;expected[i+2]=209;}
        test_rep(bundle,fc::Representation::DirectU8,direct_backend,input,expected);
        if(direct_backend==fc::Backend::Avx2)test_rep(bundle,fc::Representation::DirectU8,fc::Backend::Scalar,input,expected);
        blobs[3]=model(33,2);bundle.models[3]={blobs[3].data(),blobs[3].size()};
        check(fc_core::fc_model_init(models+3,bundle.models[3],bundle.sidecars[3])==fc_core::FC_OK,"宽模型");
        check(fc_core::fc_apply_rgb8(&chain,input.data(),input.size(),input.size(),expected.data(),expected.size(),expected.size(),257,1)==fc_core::FC_OK,"宽参考");
        test_rep(bundle,fc::Representation::DirectU16,direct_backend,input,expected);
        fc::RuntimeConfig cfg;cfg.representation=fc::Representation::DirectU8;cfg.backend=direct_backend;
        fc::Requirements req;check(fc::Runtime::requirements(bundle,cfg,&req)==fc::Status::Ok,"不适用窄表查询");
        std::vector<std::uint8_t> arena(req.arena_bytes);fc::Runtime fail;
        check(fc::Runtime::prepare(bundle,cfg,{arena.data(),arena.size()},&fail)==fc::Status::Capacity&&!fail.ready(),"超过窄调色板拒绝");
    }
#endif
    fc::RuntimeConfig unsupported;unsupported.backend=fc::Backend::Avx512;fc::Requirements req;
    check(fc::Runtime::requirements(bundle,unsupported,&req)==fc::Status::Unsupported,"AVX512显式拒绝");
    std::puts("单头C++运行库合同通过");return 0;
}
