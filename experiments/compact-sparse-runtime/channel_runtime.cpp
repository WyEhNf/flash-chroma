// 通用冻结稀疏句柄：保留packed节点和必要轴表，逐级校验后释放canonical表示。
#include "channel_runtime.h"
#include "channel_views.hpp"
#include "jshc/lut.hpp"
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <limits>
#include <memory>
#include <stdexcept>
#include <vector>
#if defined(_OPENMP)
#include <omp.h>
#endif

namespace {
struct FrozenTable {
  std::vector<uint32_t> nodes;
  std::vector<uint32_t> axes;
};
struct Handle {
  std::vector<FrozenTable> tables;
  std::vector<jshc_channel::View> views;
  size_t peak_known_bytes=0,loader_peak_known_bytes=0,serialized_bytes=0;
};
size_t resident_bytes(const Handle& h) {
  size_t bytes=sizeof(Handle)+h.tables.capacity()*sizeof(FrozenTable)+h.views.capacity()*sizeof(jshc_channel::View);
  for(const auto& table:h.tables)bytes+=(table.nodes.capacity()+table.axes.capacity())*sizeof(uint32_t);
  return bytes;
}
void message(char* output, size_t size, const char* value) {
  if (output && size) std::snprintf(output, size, "%s", value);
}
std::vector<uint32_t> read_fractions(const char* path) {
  std::unique_ptr<FILE, decltype(&std::fclose)> f(std::fopen(path, "rb"), &std::fclose);
  if (!f) throw std::runtime_error("无法打开分通道坐标侧表");
  std::vector<uint32_t> table(3*3*256);
  if (std::fread(table.data(), sizeof(uint32_t), table.size(), f.get()) != table.size()
      || std::fgetc(f.get()) != EOF) throw std::runtime_error("坐标侧表必须恰为9216字节");
  for (uint32_t value : table) if (value > jshc::kOne) throw std::runtime_error("Q16坐标越界");
  return table;
}
void scalar(const jshc_channel::View* chain, size_t stages, uint8_t* rgb, size_t pixels) {
  for (size_t p=0; p<pixels; ++p) {
    uint8_t colour[3] = {rgb[3*p], rgb[3*p+1], rgb[3*p+2]};
    for (size_t s=0; s<stages; ++s) {
      const auto& v=chain[s];
      const int base=static_cast<int>(v.axes[0][0][colour[0]]>>17)*v.sr
          +static_cast<int>(v.axes[0][1][colour[1]]>>17)*v.sg+static_cast<int>(v.axes[0][2][colour[2]]>>17);
      uint8_t next[3];
      for (int c=0; c<3; ++c) {
        int x=static_cast<int>(v.axes[c][0][colour[0]]&0x1ffff), y=static_cast<int>(v.axes[c][1][colour[1]]&0x1ffff), z=static_cast<int>(v.axes[c][2][colour[2]]&0x1ffff);
        int a=v.sr, b=v.sg, d=1;
        if (x<y) {std::swap(x,y);std::swap(a,b);}
        if (y<z) {std::swap(y,z);std::swap(b,d);}
        if (x<y) {std::swap(x,y);std::swap(a,b);}
        const uint32_t mask=255, shift=8*c;
        const int n0=(v.nodes[base]>>shift)&mask, n1=(v.nodes[base+a]>>shift)&mask;
        const int n2=(v.nodes[base+a+b]>>shift)&mask, n3=(v.nodes[base+v.sr+v.sg+1]>>shift)&mask;
        // 四项凸重心的总和<=255*65536，含舍入仍在int32安全范围。
        const int acc=(65536-x)*n0+(x-y)*n1+(y-z)*n2+z*n3;
        next[c]=static_cast<uint8_t>((acc+32768)>>16);
      }
      std::memcpy(colour,next,3); // 每级先得到全部三个整数输出，再作下一级输入。
    }
    std::memcpy(rgb+3*p,colour,3);
  }
}
void apply(Handle& h,uint8_t* rgb,size_t bytes,int kernel,int threads) {
  if (bytes%3 || (bytes && !rgb) || (kernel!=0 && kernel!=1) || threads<1 || threads>256)
    throw std::runtime_error("需要紧密RGB8、有效后端和1..256线程");
  if (kernel==1 && !(jshc_cc_capabilities()&2)) throw std::runtime_error("本库或CPU/OS不支持AVX2");
  const size_t pixels=bytes/3, blocks=pixels/4096+(pixels%4096!=0);
  if (blocks>static_cast<size_t>(std::numeric_limits<long long>::max())) throw std::runtime_error("块计数溢出");
  if (!blocks) return;
#if defined(_OPENMP)
  const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,static_cast<size_t>(threads)));
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
  for (long long block=0; block<static_cast<long long>(blocks); ++block) {
    const size_t start=static_cast<size_t>(block)*4096, n=std::min(size_t{4096},pixels-start);
    uint8_t* data=rgb+3*start;
    size_t vectorized=0;
#if defined(JSHC_CC_HAVE_AVX2)
    if (kernel==1) {
      vectorized=n&~size_t{7};
      jshc_channel::avx2_chain(h.views.data(),h.views.size(),data,vectorized);
    }
#endif
    scalar(h.views.data(),h.views.size(),data+3*vectorized,n-vectorized);
  }
}
}

extern "C" {
uint32_t jshc_cc_abi_version(void) {return 1;}
uint32_t jshc_cc_revision(void) {return 1001;}
uint32_t jshc_cc_capabilities(void) {
  uint32_t mask=1;
#if defined(JSHC_CC_HAVE_AVX2)
  if (jshc::avx2_available()) mask|=2;
#endif
#if defined(_OPENMP)
  mask|=4;
#endif
  return mask;
}
int jshc_cc_create(const char* const* paths,const char* const* sidecars,size_t stages,void** output,char* error,size_t size) {
  if(output)*output=nullptr;
  try {
    if(!paths || !output || stages<1 || stages>4)throw std::runtime_error("研究链要求1..4个模型");
    auto h=std::make_unique<Handle>();h->tables.resize(stages);h->views.resize(stages);
    for(size_t s=0;s<stages;++s) {
      if(!paths[s])throw std::runtime_error("空模型路径");
      // 逐级加载，校验全部元数据后直接生成唯一运行表示，不先构建第二份packed缓存。
      const auto m=jshc::SparseLut::load(paths[s]);
      if(m.m<17 || m.m>33)throw std::runtime_error("研究阶段m必须17..33");
      const size_t serialized=16+12*size_t(m.m)+sizeof(m.idx)+sizeof(m.frac)+m.nodes.size();
      h->serialized_bytes+=serialized;
      // load内部文件缓冲在返回前释放，此项是已知对象/向量容量上界，不是RSS。
      h->loader_peak_known_bytes=std::max(h->loader_peak_known_bytes,resident_bytes(*h)+m.runtime_bytes()+serialized);
      std::vector<uint32_t> f;
      if(sidecars && sidecars[s] && sidecars[s][0])f=read_fractions(sidecars[s]);
      h->serialized_bytes+=f.size()*sizeof(uint32_t);
      if(!f.empty())for(int c=0;c<3;++c)for(int a=0;a<3;++a) {
        int64_t previous=-1;
        for(int code=0;code<256;++code) {
          const int64_t q=static_cast<int64_t>(m.idx[a][code])*65536+f[c*768+a*256+code];
          if(q<previous || (code==0&&q!=0) || (code==255&&q!=(m.m-1)*65536))throw std::runtime_error("侧表有效坐标非降/端点合同不符");
          previous=q;
        }
      }
      auto& table=h->tables[s];auto& view=h->views[s];
      view.shared=f.empty() || (std::equal(f.begin(),f.begin()+768,f.begin()+768) && std::equal(f.begin(),f.begin()+768,f.begin()+1536));
      const int channels=view.shared?1:3;
      table.axes.resize(size_t(channels)*768);
      for(int c=0;c<channels;++c)for(int a=0;a<3;++a)for(int code=0;code<256;++code)
        table.axes[c*768+a*256+code]=(uint32_t(m.idx[a][code])<<17)|(f.empty()?m.frac[a][code]:f[c*768+a*256+code]);
      table.nodes.resize(m.nodes.size()/3);
      for(size_t i=0;i<table.nodes.size();++i)table.nodes[i]=uint32_t(m.nodes[3*i])|(uint32_t(m.nodes[3*i+1])<<8)|(uint32_t(m.nodes[3*i+2])<<16);
      view.nodes=table.nodes.data();view.sr=m.stride[0];view.sg=m.stride[1];
      for(int c=0;c<3;++c)for(int a=0;a<3;++a)view.axes[c][a]=table.axes.data()+(view.shared?0:c*768)+a*256;
      h->peak_known_bytes=std::max(h->peak_known_bytes,resident_bytes(*h)+m.runtime_bytes()+sizeof(f)+f.capacity()*sizeof(uint32_t));
      // m与原侧表在本级结束时销毁；views只指向已冻结、不会再移动的owned数组。
    }
    *output=h.release();message(error,size,"");return 0;
  }catch(const std::exception& e){message(error,size,e.what());return 1;}
}
void jshc_cc_destroy(void* handle) {delete static_cast<Handle*>(handle);}
size_t jshc_cc_model_bytes(const void* handle) {
  if(!handle)return 0;return resident_bytes(*static_cast<const Handle*>(handle));
}
// 顺序：常驻容量、已知冻结暂态、load文件缓冲上界、序列化输入总量；均不是RSS。
JSHC_CC_API int jshc_cc_frozen_metrics(const void* handle,uint64_t* output,size_t words) {
  if(!handle || !output || words!=4)return 1;
  const auto& h=*static_cast<const Handle*>(handle);
  output[0]=resident_bytes(h);output[1]=h.peak_known_bytes;output[2]=h.loader_peak_known_bytes;output[3]=h.serialized_bytes;return 0;
}
int jshc_cc_apply(void* handle,uint8_t* rgb,size_t bytes,int kernel,int threads,char* error,size_t size) {
  try {if(!handle)throw std::runtime_error("空研究句柄");apply(*static_cast<Handle*>(handle),rgb,bytes,kernel,threads);message(error,size,"");return 0;}
  catch(const std::exception& e) {message(error,size,e.what());return 1;}
}
int jshc_cc_bench(void* handle,const uint8_t* source,uint8_t* work,size_t bytes,int kernel,int threads,size_t repeats,double* apply_seconds,double* total_seconds,char* error,size_t size) {
  try {
    if(!handle || !source || !work || !bytes || source==work || repeats<1 || repeats>100 || !apply_seconds || !total_seconds) throw std::runtime_error("研究基准参数非法");
    const uintptr_t src=reinterpret_cast<uintptr_t>(source),dst=reinterpret_cast<uintptr_t>(work);
    if(bytes>std::numeric_limits<uintptr_t>::max()-src || bytes>std::numeric_limits<uintptr_t>::max()-dst || (src<dst+bytes && dst<src+bytes)) throw std::runtime_error("基准源与工作区重叠或地址溢出");
    for(size_t r=0;r<repeats;++r) {
      const auto start=std::chrono::steady_clock::now();std::memcpy(work,source,bytes);
      const auto copied=std::chrono::steady_clock::now();apply(*static_cast<Handle*>(handle),work,bytes,kernel,threads);
      const auto done=std::chrono::steady_clock::now();
      apply_seconds[r]=std::chrono::duration<double>(done-copied).count();total_seconds[r]=std::chrono::duration<double>(done-start).count();
    }
    message(error,size,"");return 0;
  } catch(const std::exception& e) {message(error,size,e.what());return 1;}
}
}
