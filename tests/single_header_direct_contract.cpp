/* direct 修复的集中边界合同：实际生成三种表示，覆盖64/32/8像素循环及精确尾部。
 * 同源C标量作为执行参考；C核心的数学独立性由另一个u64 oracle合同验证。
 * 本文件不进行性能计时，不要求图像对齐、padding或模型额外guard。
 */
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#elif defined(__unix__) || defined(__APPLE__)
#include <sys/mman.h>
#include <unistd.h>
#endif

#if FLASH_CHROMA_ENABLE_DIRECT
namespace {
std::size_t comparisons = 0;
void require(bool condition, const char* message) {
    if (!condition) { std::fprintf(stderr,"direct合同失败：%s\n",message); std::exit(1); }
}
void put32(std::vector<std::uint8_t>& blob, std::size_t offset, std::uint32_t value) {
    for (unsigned i=0;i<4;++i) blob[offset+i]=std::uint8_t(value>>(8*i));
}
std::vector<std::uint8_t> make_model(unsigned m, unsigned final_mode) {
    const std::size_t node_offset=16+12*m+3840;
    std::vector<std::uint8_t> blob(node_offset+std::size_t(m)*m*m*3,0);
    blob[0]='S';blob[1]='L';blob[2]='U';blob[3]='T';put32(blob,4,1);put32(blob,8,m);
    for (unsigned a=0;a<3;++a) for (unsigned i=0;i<m;++i) {
        float position=float(i)*255.0f/float(m-1);std::uint32_t bits;
        std::memcpy(&bits,&position,4);put32(blob,16+(a*m+i)*4,bits);
    }
    for (unsigned a=0;a<3;++a) for (unsigned x=0;x<256;++x) {
        unsigned cell=x*(m-1)/255;if (cell==m-1)--cell;
        blob[16+12*m+a*256+x]=std::uint8_t(cell);
        const auto f=std::uint32_t(((std::uint64_t(x)*(m-1)-std::uint64_t(cell)*255)*65536+127)/255);
        put32(blob,16+12*m+768+(a*256+x)*4,f);
    }
    for (unsigned r=0;r<m;++r) for(unsigned g=0;g<m;++g) for(unsigned b=0;b<m;++b) {
        const auto at=node_offset+((std::size_t(r)*m+g)*m+b)*3;
        const auto red=std::uint8_t((r*255+(m-1)/2)/(m-1));
        const auto green=std::uint8_t((g*255+(m-1)/2)/(m-1));
        const auto blue=std::uint8_t((b*255+(m-1)/2)/(m-1));
        blob[at]=red;blob[at+1]=final_mode==1?red:green;
        blob[at+2]=final_mode==1?red:(final_mode==2?0:blue);
    }
    return blob;
}
std::vector<std::uint8_t> make_sidecar(const std::vector<std::uint8_t>& blob, unsigned m) {
    std::vector<std::uint8_t> sidecar(9216);
    for (unsigned c=0;c<3;++c) for(unsigned a=0;a<3;++a) for(unsigned x=0;x<256;++x) {
        const unsigned cell=blob[16+12*m+a*256+x];
        std::uint64_t f=((std::uint64_t(x)*(m-1)-std::uint64_t(cell)*255)*65536+127)/255;
        if (c==0) f=(f*f+32768)/65536;
        if (c==2) f=(f*(131072-f)+32768)/65536;
        put32(sidecar,(c*768+a*256+x)*4,std::uint32_t(f));
    }
    return sidecar;
}
void check_window(const std::vector<std::uint8_t>& bytes, std::size_t start,
                  const std::vector<std::uint8_t>& expected, std::size_t count) {
    require(std::memcmp(bytes.data()+start,expected.data(),count)==0,"像素结果与C参考不同");
    for(std::size_t i=0;i<start;++i)require(bytes[i]==0xa5,"写入输出前缀哨兵");
    for(std::size_t i=start+count;i<bytes.size();++i)require(bytes[i]==0xa5,"写入输出后缀哨兵");
}
template<class Executor>
void linear_case(const Executor& runtime,const std::vector<std::uint8_t>& source,
                 const std::vector<std::uint8_t>& expected,std::size_t pixels,unsigned offset) {
    const std::size_t bytes=pixels*3;
    std::vector<std::uint8_t> input(bytes+320,0xa5),output(bytes+320,0xa5);
    const auto input_base=(reinterpret_cast<std::uintptr_t>(input.data()+64)+63u)&~std::uintptr_t{63};
    const auto output_base=(reinterpret_cast<std::uintptr_t>(output.data()+64)+63u)&~std::uintptr_t{63};
    const std::size_t input_at=std::size_t(input_base-reinterpret_cast<std::uintptr_t>(input.data()))+offset;
    const std::size_t output_at=std::size_t(output_base-reinterpret_cast<std::uintptr_t>(output.data()))+((offset*17+13)&63u);
    if(bytes)std::memcpy(input.data()+input_at,source.data(),bytes);
    const auto unchanged=input;
    require(runtime.apply(input.data()+input_at,bytes,bytes,output.data()+output_at,bytes,bytes,pixels,1)==fc::Status::Ok,"分离映射拒绝合法尾部");
    check_window(output,output_at,expected,bytes);
    require(input==unchanged,"分离映射修改源像素或哨兵");
    require(runtime.apply(input.data()+input_at,bytes,bytes,input.data()+input_at,bytes,bytes,pixels,1)==fc::Status::Ok,"原地映射拒绝合法尾部");
    check_window(input,input_at,expected,bytes);
    comparisons+=2;
}
void strided_case(const fc::Runtime& runtime,const fc_core::fc_chain& chain,
                  const std::vector<std::uint8_t>& source,std::size_t width) {
    constexpr std::size_t rows=7;
    const std::size_t row=width*3, src_stride=row+13, dst_stride=row+29;
    const std::size_t src_span=(rows-1)*src_stride+row, dst_span=(rows-1)*dst_stride+row;
    std::vector<std::uint8_t> input(3+src_span+64,0xa5),output(51+dst_span+64,0xa5),reference=output;
    for(std::size_t y=0;y<rows;++y)std::memcpy(input.data()+3+y*src_stride,source.data()+y*row,row);
    const auto before=input;
    require(fc_core::fc_apply_rgb8(&chain,input.data()+3,src_span,src_stride,reference.data()+51,dst_span,dst_stride,width,rows)==fc_core::FC_OK,"stride参考拒绝");
    require(runtime.apply(input.data()+3,src_span,src_stride,output.data()+51,dst_span,dst_stride,width,rows)==fc::Status::Ok,"stride映射拒绝");
    require(output==reference&&input==before,"stride像素、padding或源缓冲不同");
    auto in_place=input,expected=input;
    require(fc_core::fc_apply_rgb8(&chain,expected.data()+3,src_span,src_stride,expected.data()+3,src_span,src_stride,width,rows)==fc_core::FC_OK,"原地stride参考拒绝");
    require(runtime.apply(in_place.data()+3,src_span,src_stride,in_place.data()+3,src_span,src_stride,width,rows)==fc::Status::Ok,"原地stride拒绝");
    require(in_place==expected,"原地stride像素或padding不同");
    comparisons+=2;
}

/* 首尾均为NOACCESS；末端窗口不提供读padding，哨兵之外另检测越界读取。 */
class ProtectedBuffer {
    std::uint8_t* base_=nullptr;
    std::size_t total_=0, page_=0, usable_=0;
public:
    explicit ProtectedBuffer(std::size_t capacity) {
#if defined(_WIN32)
        SYSTEM_INFO info;GetSystemInfo(&info);page_=info.dwPageSize;
        usable_=(capacity+page_-1)/page_*page_;total_=usable_+2*page_;
        base_=static_cast<std::uint8_t*>(VirtualAlloc(nullptr,total_,MEM_RESERVE|MEM_COMMIT,PAGE_NOACCESS));
        require(base_!=nullptr,"无法分配Windows保护页");DWORD previous=0;
        require(VirtualProtect(base_+page_,usable_,PAGE_READWRITE,&previous)!=0,"无法设置Windows可写区");
#elif defined(__unix__) || defined(__APPLE__)
        const long page=sysconf(_SC_PAGESIZE);require(page>0,"无法查询保护页大小");page_=std::size_t(page);
        usable_=(capacity+page_-1)/page_*page_;total_=usable_+2*page_;
        void* mapping=mmap(nullptr,total_,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
        require(mapping!=MAP_FAILED,"无法分配POSIX保护页");base_=static_cast<std::uint8_t*>(mapping);
        require(mprotect(base_+page_,usable_,PROT_READ|PROT_WRITE)==0,"无法设置POSIX可写区");
#else
        (void)capacity;
#endif
    }
    ~ProtectedBuffer() {
#if defined(_WIN32)
        if(base_)VirtualFree(base_,0,MEM_RELEASE);
#elif defined(__unix__) || defined(__APPLE__)
        if(base_)munmap(base_,total_);
#endif
    }
    bool available() const {return base_!=nullptr;}
    std::uint8_t* tail(std::size_t bytes) {require(bytes<=usable_,"保护页容量不足");return base_+page_+usable_-bytes;}
    std::uint8_t* head() {return base_+page_;}
};
template<class Executor>
void protected_cases(const Executor& runtime,const std::vector<std::uint8_t>& source,
                     const std::vector<std::uint8_t>& expected) {
    ProtectedBuffer input(65537*3),output(65537*3);
    if(!input.available()) {std::puts("当前平台没有保护页适配，未执行NOACCESS合同");return;}
    std::vector<std::size_t> counts;
    for(std::size_t n=1;n<=96;++n)counts.push_back(n);
    for(const auto n:{127u,128u,129u,255u,256u,257u,4095u,4096u,4097u,65535u,65536u,65537u})counts.push_back(n);
    for(const auto n:counts) {
        const auto bytes=n*3;
        auto* src=input.tail(bytes);auto* dst=output.tail(bytes);
        std::memcpy(src,source.data(),bytes);std::memset(dst,0xa5,bytes);
        require(runtime.apply(src,bytes,bytes,dst,bytes,bytes,n,1)==fc::Status::Ok,"保护页分离映射拒绝");
        require(std::memcmp(dst,expected.data(),bytes)==0&&std::memcmp(src,source.data(),bytes)==0,"保护页分离输出或源错误");
        require(runtime.apply(src,bytes,bytes,src,bytes,bytes,n,1)==fc::Status::Ok,"保护页原地映射拒绝");
        require(std::memcmp(src,expected.data(),bytes)==0,"保护页原地输出错误");
        /* 另一端紧邻前保护页，检测向前对齐读取或写入。 */
        src=input.head();dst=output.head();std::memcpy(src,source.data(),bytes);
        require(runtime.apply(src,bytes,bytes,dst,bytes,bytes,n,1)==fc::Status::Ok,"前保护页映射拒绝");
        require(std::memcmp(dst,expected.data(),bytes)==0,"前保护页输出错误");
        comparisons+=3;
    }
}
#if FLASH_CHROMA_ENABLE_AVX2
/* 独立解析表覆盖BMI宿主上的非BMI回退，结果由直接标量索引生成。 */
struct ForcedKernel {
    using Function=void(*)(const std::uint8_t*,const std::uint32_t*,const std::uint8_t*,std::uint8_t*,std::size_t);
    Function run;
    const std::uint8_t* table;
    const std::uint32_t* palette;
    fc::Status apply(const std::uint8_t* source,std::size_t,std::size_t source_stride,
                     std::uint8_t* destination,std::size_t,std::size_t destination_stride,
                     std::size_t width,std::size_t height) const {
        for(std::size_t y=0;y<height;++y)run(table,palette,source+y*source_stride,destination+y*destination_stride,width);
        return fc::Status::Ok;
    }
};
template<bool Wide>
void forced_kernel_cases(const std::vector<std::uint8_t>& source) {
    const std::size_t colours=std::size_t{1}<<24;
    std::vector<std::uint8_t> ids8(Wide?0:colours);
    std::vector<std::uint16_t> ids16(Wide?colours:0);
    for(std::size_t code=0;code<colours;++code) {
        if constexpr(Wide)ids16[code]=std::uint16_t(code^(code>>8));
        else ids8[code]=std::uint8_t(code^(code>>8)^(code>>16));
    }
    std::vector<std::uint32_t> palette(Wide?65536:256);
    for(std::size_t id=0;id<palette.size();++id) {
        const std::uint32_t r=std::uint32_t((id*13+17)&255),g=std::uint32_t((id*29+(id>>8))&255),b=std::uint32_t(((id>>8)*73+91)&255);
        palette[id]=r|(g<<8)|(b<<16);
    }
    std::vector<std::uint8_t> expected(source.size());
    for(std::size_t p=0;p<source.size();p+=3) {
        const std::uint32_t code=std::uint32_t(source[p])|(std::uint32_t(source[p+1])<<8)|(std::uint32_t(source[p+2])<<16);
        const std::uint32_t id=Wide?ids16[code]:ids8[code],value=palette[id];
        expected[p]=std::uint8_t(value);expected[p+1]=std::uint8_t(value>>8);expected[p+2]=std::uint8_t(value>>16);
    }
    const auto* table=Wide?reinterpret_cast<const std::uint8_t*>(ids16.data()):ids8.data();
    const ForcedKernel::Function functions[]={fc::detail::direct_palette_run<Wide>
#if defined(__x86_64__)
        ,fc::detail::direct_palette_run_bmi<Wide>
#endif
    };
    for(unsigned path=0;path<sizeof(functions)/sizeof(functions[0]);++path) {
        if(path==1&&!__builtin_cpu_supports("bmi"))continue;
        const ForcedKernel executor{functions[path],table,palette.data()};
        for(std::size_t n=0;n<=257;++n)for(unsigned offset=0;offset<64;++offset)linear_case(executor,source,expected,n,offset);
        for(const auto n:{511u,512u,513u,4095u,4096u,4097u,65535u,65536u,65537u})
            for(unsigned offset=0;offset<64;++offset)linear_case(executor,source,expected,n,offset);
        protected_cases(executor,source,expected);
    }
}
#endif
}
#endif

int main() {
#if !FLASH_CHROMA_ENABLE_DIRECT
    std::puts("本构建关闭direct表示，direct修复合同未执行");return 0;
#else
    const fc::Backend backend=(fc::available_backends()&2u)?fc::Backend::Avx2:fc::Backend::Scalar;
    std::vector<std::uint8_t> blobs[4]={make_model(17,0),make_model(18,0),make_model(25,0),make_model(33,0)};
    const auto sidecar=make_sidecar(blobs[0],17),original_sidecar=sidecar;
    std::vector<std::uint8_t> source(65537*3);std::uint32_t random=0x58314ab9;
    for(auto& byte:source) {random^=random<<13;random^=random>>17;random^=random<<5;byte=std::uint8_t(random);}
    source[0]=source[1]=source[2]=0;source[source.size()-1]=source[source.size()-2]=source[source.size()-3]=255;
    const fc::Representation representations[]={fc::Representation::DirectU8,fc::Representation::DirectU16,fc::Representation::DirectRGB24};
    for(const auto representation:representations) {
        blobs[3]=make_model(33,representation==fc::Representation::DirectU8?1u:(representation==fc::Representation::DirectU16?2u:0u));
        fc::ModelBundle bundle;for(unsigned i=0;i<4;++i)bundle.models[i]={blobs[i].data(),blobs[i].size()};
        bundle.sidecars[0]={sidecar.data(),sidecar.size()};
        const auto original0=blobs[0],original1=blobs[1],original2=blobs[2],original3=blobs[3];
        fc_core::fc_model views[4]{};const fc_core::fc_model* pointers[4];
        for(unsigned i=0;i<4;++i) {require(fc_core::fc_model_init(views+i,bundle.models[i],bundle.sidecars[i])==fc_core::FC_OK,"参考模型初始化");pointers[i]=views+i;}
        fc_core::fc_chain chain;require(fc_core::fc_chain_init(&chain,pointers)==fc_core::FC_OK,"参考链初始化");
        std::vector<std::uint8_t> expected(source.size());
        require(fc_core::fc_apply_rgb8(&chain,source.data(),source.size(),source.size(),expected.data(),expected.size(),expected.size(),source.size()/3,1)==fc_core::FC_OK,"C标量参考输出");
        const unsigned maximum_threads=(fc::compiled_capabilities()&4u)?4u:1u;
        for(unsigned threads=1;threads<=maximum_threads;threads+=3) {
            fc::RuntimeConfig config;config.representation=representation;config.backend=backend;
            config.threads=threads;config.block_pixels=65536;
            fc::Requirements required;require(fc::Runtime::requirements(bundle,config,&required)==fc::Status::Ok,"资源查询");
            config.max_workspace_bytes=required.arena_bytes;
            std::vector<std::uint8_t> arena(required.arena_bytes+128,0xa5);fc::Runtime runtime;
            require(fc::Runtime::prepare(bundle,config,{arena.data()+1,required.arena_bytes},&runtime)==fc::Status::Ok,"direct准备");
            if(representation==fc::Representation::DirectU8)require(runtime.palette_entries()>1&&runtime.palette_entries()<=256,"窄表必须实际具有多个输出颜色");
            if(representation==fc::Representation::DirectU16)require(runtime.palette_entries()>256,"宽表必须实际超过256色");
            for(std::size_t n=0;n<=257;++n)for(unsigned offset=0;offset<64;++offset)linear_case(runtime,source,expected,n,offset);
            for(const auto n:{511u,512u,513u,1023u,1024u,1025u,4095u,4096u,4097u,65535u,65536u,65537u})
                for(unsigned offset=0;offset<64;++offset)linear_case(runtime,source,expected,n,offset);
            for(const auto width:{1u,7u,8u,31u,32u,63u,64u,65u,71u,72u,79u,80u,127u,128u,129u,1024u})strided_case(runtime,chain,source,width);
            protected_cases(runtime,source,expected);
            require(arena.front()==0xa5,"direct准备写入arena前缀");
            for(std::size_t i=required.arena_bytes+1;i<arena.size();++i)require(arena[i]==0xa5,"direct准备写入arena后缀");
            require(blobs[0]==original0&&blobs[1]==original1&&blobs[2]==original2&&blobs[3]==original3,"运行过程中修改借用模型");
            require(sidecar==original_sidecar,"运行过程中修改借用sidecar");
        }
    }
#if FLASH_CHROMA_ENABLE_AVX2
    if(backend==fc::Backend::Avx2) {forced_kernel_cases<false>(source);forced_kernel_cases<true>(source);}
#endif
    std::printf("direct集中边界合同通过：%zu项比较；后端=%u\n",comparisons,unsigned(backend));return 0;
#endif
}
