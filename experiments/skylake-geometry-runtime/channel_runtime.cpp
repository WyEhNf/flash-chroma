// 对有界坐标差使用无损int16打包；不满足边界时保留原九表，不改变输入文件或像素语义。
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
struct Handle {
  std::vector<jshc::SparseLut> models;
  std::vector<std::vector<uint32_t>> fractions;
  std::vector<jshc_geometry::View> views;
  std::vector<const jshc::SparseLut*> original;
  bool extended = false;
};
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
int fraction(const jshc_geometry::View& view,int c,int axis,int code) {
  if(!view.delta16 || c==0)return int(view.axes[c][axis][code]&0x1ffff);
  const uint32_t word=view.axes[1][axis][code];
  const int bits=int((word>>(16*(c-1)))&65535);
  // 明确符号扩展，不依赖无符号转int16或负数右移的实现定义行为。
  const int difference=bits-((bits&32768)<<1);
  return int(view.axes[0][axis][code]&0x1ffff)+difference;
}
void scalar(const jshc_geometry::View* chain, size_t stages, uint8_t* rgb, size_t pixels) {
  for (size_t p=0; p<pixels; ++p) {
    uint8_t colour[3] = {rgb[3*p], rgb[3*p+1], rgb[3*p+2]};
    for (size_t s=0; s<stages; ++s) {
      const auto& v=chain[s];
      const int base=static_cast<int>(v.axes[0][0][colour[0]]>>17)*v.sr
          +static_cast<int>(v.axes[0][1][colour[1]]>>17)*v.sg+static_cast<int>(v.axes[0][2][colour[2]]>>17);
      uint8_t next[3];
      for (int c=0; c<3; ++c) {
        int x=fraction(v,c,0,colour[0]),y=fraction(v,c,1,colour[1]),z=fraction(v,c,2,colour[2]);
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
  if (!h.extended) {
    jshc::apply_chain(h.original,rgb,bytes/3,kernel==0?jshc::Kernel::TetraScalar:jshc::Kernel::TetraAvx2,threads);
    return;
  }
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
      jshc_geometry::avx2_chain(h.views.data(),h.views.size(),data,vectorized);
    }
#endif
    scalar(h.views.data(),h.views.size(),data+3*vectorized,n-vectorized);
  }
}
}

extern "C" {
uint32_t jshc_cc_abi_version(void) {return 1;}
uint32_t jshc_cc_revision(void) {return 17;}
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
  if (output) *output=nullptr;
  try {
    if (!paths || !output || stages<1 || stages>4) throw std::runtime_error("研究链要求1..4个模型");
    auto h=std::make_unique<Handle>();h->models.reserve(stages);h->fractions.resize(stages);h->views.reserve(stages);h->original.reserve(stages);
    for (size_t s=0;s<stages;++s) {
      if (!paths[s]) throw std::runtime_error("空模型路径");
      h->models.push_back(jshc::SparseLut::load(paths[s]));
      if (h->models.back().m<17 || h->models.back().m>33) throw std::runtime_error("研究阶段m必须17..33");
      if (sidecars && sidecars[s] && sidecars[s][0]) {h->fractions[s]=read_fractions(sidecars[s]);h->extended=true;}
    }
    for (size_t s=0;s<stages;++s) {
      const auto& m=h->models[s];const auto& packed=m.packed_tables();auto& f=h->fractions[s];
      if (!f.empty()) for (int c=0;c<3;++c) for(int a=0;a<3;++a) {
        int64_t previous=-1;
        for(int code=0;code<256;++code) {
          const int64_t q=static_cast<int64_t>(m.idx[a][code])*65536+f[c*768+a*256+code];
          if(q<previous || (code==0&&q!=0) || (code==255&&q!=(m.m-1)*65536)) throw std::runtime_error("侧表有效坐标非降/端点合同不符");
          previous=q;
        }
      }
      jshc_geometry::View view{};view.nodes=packed.nodes.data();view.sr=m.stride[0];view.sg=m.stride[1];
      view.shared=f.empty() || (std::equal(f.begin(),f.begin()+768,f.begin()+768)
          && std::equal(f.begin(),f.begin()+768,f.begin()+1536));
      view.delta16=!view.shared;
      if(view.delta16)for(int a=0;a<3;++a)for(int code=0;code<256;++code)for(int c=1;c<3;++c) {
        const int diff=int(f[c*768+a*256+code])-int(f[a*256+code]);
        if(diff < -32768 || diff > 32767)view.delta16=false;
      }
      if(view.delta16) {
        std::vector<uint32_t> encoded(1536);
        for(int a=0;a<3;++a)for(int code=0;code<256;++code) {
          const int index=a*256+code;
          const int dg=int(f[768+index])-int(f[index]),db=int(f[1536+index])-int(f[index]);
          encoded[index]=(uint32_t(m.idx[a][code])<<17)|f[index];
          encoded[768+index]=uint32_t(uint16_t(dg))|(uint32_t(uint16_t(db))<<16);
        }
        f.swap(encoded);
        for(int a=0;a<3;++a) {
          view.axes[0][a]=f.data()+a*256;view.axes[1][a]=f.data()+768+a*256;
          view.axes[2][a]=nullptr;
        }
      } else {
        // 共享/不合资格模型保持原始九表；相等但不同于base的侧表也不能丢弃。
        if(!f.empty())for(int c=0;c<3;++c)for(int a=0;a<3;++a)for(int code=0;code<256;++code)
          f[c*768+a*256+code]|=uint32_t(m.idx[a][code])<<17;
        for(int a=0;a<3;++a)for(int c=0;c<3;++c)
          view.axes[c][a]=f.empty()?packed.axis.data()+a*256:f.data()+c*768+a*256;
      }
      h->views.push_back(view);
      h->original.push_back(&m);
    }
    *output=h.release();message(error,size,"");return 0;
  } catch (const std::exception& e) {message(error,size,e.what());return 1;}
}
void jshc_cc_destroy(void* handle) {delete static_cast<Handle*>(handle);}
// 只读研究诊断：0原非共享、1共享、2有符号双差值；失败不修改调用者数组。
JSHC_CC_API int jshc_cc_get_layouts(const void* handle,uint32_t* flags,size_t count) {
  if(!handle || !flags)return 1;const auto& h=*static_cast<const Handle*>(handle);
  if(count!=h.views.size())return 1;
  for(size_t s=0;s<count;++s)flags[s]=h.views[s].shared?1u:(h.views[s].delta16?2u:0u);
  return 0;
}
size_t jshc_cc_model_bytes(const void* handle) {
  if(!handle)return 0;const auto& h=*static_cast<const Handle*>(handle);
  size_t bytes=sizeof(Handle)+h.models.capacity()*sizeof(jshc::SparseLut)+h.fractions.capacity()*sizeof(std::vector<uint32_t>)+h.views.capacity()*sizeof(jshc_geometry::View)+h.original.capacity()*sizeof(void*);
  for(const auto& m:h.models)bytes+=m.runtime_bytes()-sizeof(jshc::SparseLut);
  for(const auto& f:h.fractions)bytes+=f.capacity()*sizeof(uint32_t);
  return bytes;
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
