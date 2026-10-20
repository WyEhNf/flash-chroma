// 有界后缀精确缓存研究：只预计算现有稀疏模型的逐级整数输出，不改变模型。
#include "channel_runtime.h"
#include "channel_views.hpp"
#include "suffix_cache.hpp"
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
  std::vector<jshc_channel::View> views;
  std::vector<const jshc::SparseLut*> original;
  std::vector<uint32_t> cache;
  jshc_channel::SuffixCacheView cache_view;
  jshc_cc_cache_info cache_info{};
  bool extended = false;
  bool domain_proven = false;
};
static_assert(sizeof(Handle)==248, "域证明标志必须使用原Handle尾部填充");
static_assert(sizeof(jshc_cc_domain_info)==48, "只读域证书ABI必须为48字节");
bool domain_fast_enabled(const Handle& h) noexcept {
  return h.domain_proven && !h.views[0].shared && h.views[1].shared && h.views[2].shared && h.views[3].shared;
}
int64_t floor_q16(int64_t x) noexcept {
  return x>=0?x/65536:-((-x+65535)/65536);
}
jshc_cc_domain_info domain_certificate(const Handle& h) {
  jshc_cc_domain_info result{};result.version=1;result.cache_enabled=h.cache_info.enabled;
  if(!result.cache_enabled || h.models.size()!=4)return result;
  const auto& model=h.models[0];const auto& view=h.views[0];const int cells=model.m-1;
  int dmin[2][3][32],dmax[2][3][32],count[3][32]{};
  for(int c=0;c<2;++c)for(int a=0;a<3;++a)for(int i=0;i<cells;++i) {
    dmin[c][a][i]=65536;dmax[c][a][i]=-65536;
  }
  for(int a=0;a<3;++a)for(int code=0;code<256;++code) {
    const int cell=model.idx[a][code];++count[a][cell];
    for(int c=0;c<2;++c) {
      const int delta=int(view.axes[c+1][a][code]&0x1ffff)-int(view.axes[0][a][code]&0x1ffff);
      dmin[c][a][cell]=std::min(dmin[c][a][cell],delta);dmax[c][a][cell]=std::max(dmax[c][a][cell],delta);
    }
  }
  result.dg_min=result.db_min=255;result.dg_max=result.db_max=-255;
  for(int r=0;r<cells;++r)for(int g=0;g<cells;++g)for(int b=0;b<cells;++b) {
    if(!count[0][r] || !count[1][g] || !count[2][b])continue;
    ++result.reachable_cells;int nodes[8][3];const int indices[3]={r,g,b};
    for(int corner=0;corner<8;++corner) {
      const size_t offset=((size_t(r+((corner>>2)&1))*model.m+g+((corner>>1)&1))*model.m+b+(corner&1))*3;
      for(int c=0;c<3;++c)nodes[corner][c]=model.nodes[offset+c];
    }
    bool cell_ok=true;
    for(int c=0;c<2;++c) {
      int nmin=255,nmax=-255;
      for(int corner=0;corner<8;++corner) {
        const int difference=nodes[corner][c+1]-nodes[corner][0];
        nmin=std::min(nmin,difference);nmax=std::max(nmax,difference);
      }
      int64_t lower=0,upper=0;
      for(int a=0;a<3;++a) {
        const int bit=1<<(2-a);int slope_min=255,slope_max=-255;
        for(int corner=0;corner<8;++corner)if(!(corner&bit)) {
          const int slope=nodes[corner|bit][c+1]-nodes[corner][c+1];
          slope_min=std::min(slope_min,slope);slope_max=std::max(slope_max,slope);
        }
        const int lo=dmin[c][a][indices[a]],hi=dmax[c][a][indices[a]];
        const int64_t products[4]={int64_t(slope_min)*lo,int64_t(slope_min)*hi,int64_t(slope_max)*lo,int64_t(slope_max)*hi};
        lower+=*std::min_element(products,products+4);upper+=*std::max_element(products,products+4);
      }
      // 差值的下/上界分别floor/ceil，不能用C++负数除法的向零截断。
      const int lo=std::max(-255,nmin+int(floor_q16(lower)));
      const int hi=std::min(255,nmax-int(floor_q16(-upper)));
      if(c==0) {
        result.dg_min=std::min(result.dg_min,lo);result.dg_max=std::max(result.dg_max,hi);
        cell_ok=cell_ok && lo>=h.cache_info.dg_min && hi<=h.cache_info.dg_max;
      } else {
        result.db_min=std::min(result.db_min,lo);result.db_max=std::max(result.db_max,hi);
        cell_ok=cell_ok && lo>=h.cache_info.db_min && hi<=h.cache_info.db_max;
      }
    }
    if(!cell_ok)++result.unproven_cells;
  }
  result.eligible=result.reachable_cells && !result.unproven_cells;return result;
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
void prepare_cache(Handle& h) {
  const auto started = std::chrono::steady_clock::now();
  auto& info=h.cache_info; info.version=1; info.reason=1;
  if(h.models.size()==4) {
    const auto& nodes=h.models[0].nodes;
    int rmin=255,rmax=0,gmin=255,gmax=-255,bmin=255,bmax=-255;
    for(size_t p=0;p<nodes.size();p+=3) {
      const int r=nodes[p],dg=int(nodes[p+1])-r,db=int(nodes[p+2])-r;
      rmin=std::min(rmin,r);rmax=std::max(rmax,r);
      gmin=std::min(gmin,dg);gmax=std::max(gmax,dg);
      bmin=std::min(bmin,db);bmax=std::max(bmax,db);
    }
    // 差值范围仅是容量启发式，分输出坐标不保证输出差值落在节点范围。
    gmin=std::max(-255,gmin-2);gmax=std::min(255,gmax+2);
    bmin=std::max(-255,bmin-2);bmax=std::min(255,bmax+2);
    const size_t wg=size_t(gmax-gmin+1),wb=size_t(bmax-bmin+1);
    const size_t entries=size_t(rmax-rmin+1)*wg*wb;
    info.r_min=rmin;info.r_max=rmax;info.dg_min=gmin;info.dg_max=gmax;
    info.db_min=bmin;info.db_max=bmax; info.reason=2;
    constexpr size_t budget=1024*1024;
    if(entries<=budget/sizeof(uint32_t)) {
      try {
        std::vector<uint8_t> colours;colours.reserve(entries*3);
        for(int r=rmin;r<=rmax;++r)for(int dg=gmin;dg<=gmax;++dg)for(int db=bmin;db<=bmax;++db)
          if(r+dg>=0 && r+dg<=255 && r+db>=0 && r+db<=255) {
            colours.push_back(uint8_t(r));colours.push_back(uint8_t(r+dg));colours.push_back(uint8_t(r+db));
          }
        info.temporary_capacity_bytes=colours.capacity();
        info.valid_entries=colours.size()/3;info.reason=3;
        if(info.valid_entries) {
          h.cache.assign(entries,0);
          // 复用当前稀疏后三个模型，逐级RGB8 half-up，绝不从完整源LUT生成。
          scalar(h.views.data()+1,3,colours.data(),colours.size()/3);
          size_t next=0,index=0;
          for(int r=rmin;r<=rmax;++r)for(int dg=gmin;dg<=gmax;++dg)for(int db=bmin;db<=bmax;++db,++index)
            if(r+dg>=0 && r+dg<=255 && r+db>=0 && r+db<=255) {
              h.cache[index]=uint32_t(colours[next])|(uint32_t(colours[next+1])<<8)|(uint32_t(colours[next+2])<<16);
              next+=3;
            }
          info.entries=entries;info.table_capacity_bytes=h.cache.capacity()*sizeof(uint32_t);
          info.enabled=1;info.reason=0;
          h.cache_view={h.cache.data(),rmin,rmax,gmin,gmax,bmin,bmax,int32_t(wg),int32_t(wb)};
        }
      } catch(const std::bad_alloc&) {
        std::vector<uint32_t>().swap(h.cache);h.cache_view={};
        info.enabled=0;info.reason=4;info.entries=0;info.table_capacity_bytes=0;
      }
    }
  }
  h.domain_proven=domain_certificate(h).eligible!=0;
  info.prepare_seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
}
void apply(Handle& h,uint8_t* rgb,size_t bytes,int kernel,int threads) {
  if (bytes%3 || (bytes && !rgb) || (kernel!=0 && kernel!=1) || threads<1 || threads>256)
    throw std::runtime_error("需要紧密RGB8、有效后端和1..256线程");
  if (kernel==1 && !(jshc_cc_capabilities()&2)) throw std::runtime_error("本库或CPU/OS不支持AVX2");
  if (!h.extended && (kernel==0 || !h.cache_info.enabled)) {
    jshc::apply_chain(h.original,rgb,bytes/3,kernel==0?jshc::Kernel::TetraScalar:jshc::Kernel::TetraAvx2,threads);
    return;
  }
  const size_t pixels=bytes/3, blocks=pixels/4096+(pixels%4096!=0);
  if (blocks>static_cast<size_t>(std::numeric_limits<long long>::max())) throw std::runtime_error("块计数溢出");
  if (!blocks) return;
  const bool domain_fast=domain_fast_enabled(h);
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
      if(h.cache_info.enabled) {
        if(domain_fast)jshc_channel::avx2_chain_domain(h.views.data(),h.cache_view,data,vectorized);
        else jshc_channel::avx2_chain_cached(h.views.data(),h.cache_view,data,vectorized);
      }
      else jshc_channel::avx2_chain(h.views.data(),h.views.size(),data,vectorized);
    }
#endif
    scalar(h.views.data(),h.views.size(),data+3*vectorized,n-vectorized);
  }
}
}

extern "C" {
uint32_t jshc_cc_abi_version(void) {return 1;}
uint32_t jshc_cc_revision(void) {return 16;}
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
      jshc_channel::View view{};view.nodes=packed.nodes.data();view.sr=m.stride[0];view.sg=m.stride[1];
      view.shared=f.empty() || (std::equal(f.begin(),f.begin()+768,f.begin()+768)
          && std::equal(f.begin(),f.begin()+768,f.begin()+1536));
      // 同一owned侧表原地合并idx，无额外大表；先完成原Q16/单调性验证。
      if(!f.empty())for(int c=0;c<3;++c)for(int a=0;a<3;++a)for(int code=0;code<256;++code)
        f[c*768+a*256+code]|=static_cast<uint32_t>(m.idx[a][code])<<17;
      for(int a=0;a<3;++a)for(int c=0;c<3;++c)
        view.axes[c][a]=f.empty()?packed.axis.data()+a*256:f.data()+c*768+a*256;
      h->views.push_back(view);
      h->original.push_back(&m);
    }
    prepare_cache(*h);
    *output=h.release();message(error,size,"");return 0;
  } catch (const std::exception& e) {message(error,size,e.what());return 1;}
}
void jshc_cc_destroy(void* handle) {delete static_cast<Handle*>(handle);}
size_t jshc_cc_model_bytes(const void* handle) {
  if(!handle)return 0;const auto& h=*static_cast<const Handle*>(handle);
  size_t bytes=sizeof(Handle)+h.models.capacity()*sizeof(jshc::SparseLut)+h.fractions.capacity()*sizeof(std::vector<uint32_t>)+h.views.capacity()*sizeof(jshc_channel::View)+h.original.capacity()*sizeof(void*);
  for(const auto& m:h.models)bytes+=m.runtime_bytes()-sizeof(jshc::SparseLut);
  for(const auto& f:h.fractions)bytes+=f.capacity()*sizeof(uint32_t);
  bytes+=h.cache.capacity()*sizeof(uint32_t);
  return bytes;
}
int jshc_cc_get_cache_info(const void* handle,jshc_cc_cache_info* output,size_t bytes) {
  if(!handle || !output || bytes!=sizeof(jshc_cc_cache_info))return 1;
  *output=static_cast<const Handle*>(handle)->cache_info;return 0;
}
int jshc_cc_copy_cache(const void* handle,uint32_t* output,size_t entries) {
  if(!handle)return 1;const auto& table=static_cast<const Handle*>(handle)->cache;
  if(entries!=table.size() || (entries && !output))return 1;
  if(entries)std::memcpy(output,table.data(),entries*sizeof(uint32_t));return 0;
}
int jshc_cc_get_domain_info(const void* handle,jshc_cc_domain_info* output,size_t bytes) {
  if(!handle || !output || bytes!=sizeof(jshc_cc_domain_info))return 1;
  const auto& h=*static_cast<const Handle*>(handle);const auto info=domain_certificate(h);
  if(bool(info.eligible)!=h.domain_proven)return 1;
  *output=info;return 0;
}
uint32_t jshc_cc_domain_fast_enabled(const void* handle) {
  return handle && domain_fast_enabled(*static_cast<const Handle*>(handle))?1:0;
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
