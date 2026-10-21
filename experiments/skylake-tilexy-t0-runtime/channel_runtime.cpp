// 有界后缀精确缓存研究：只预计算现有稀疏模型的逐级整数输出，不改变模型。
#include "channel_runtime.h"
#include "channel_views.hpp"
#include "suffix_cache.hpp"
#include "aligned_table.hpp"
#include "jshc/lut.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
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
  std::vector<uint32_t> compiled;
  std::vector<uint32_t> exceptions;
  jshc_channel::AlignedTable direct_index;
  jshc_channel::AlignedTable tilexy_index;
  std::array<uint32_t,256> output_palette{};
  jshc_cc_palette_info palette_info{};
};
static_assert(sizeof(jshc_cc_palette_info)==56, "调色板诊断ABI固定为56字节");
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
  const size_t pixels=bytes/3, blocks=pixels/65536+(pixels%65536!=0);
  if (blocks>static_cast<size_t>(std::numeric_limits<long long>::max())) throw std::runtime_error("块计数溢出");
  if (!blocks) return;
  const bool domain_fast=domain_fast_enabled(h);
#if defined(_OPENMP)
  const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,static_cast<size_t>(threads)));
#pragma omp parallel for schedule(static) num_threads(workers)
#else
  const int workers=1;
#endif
  for (long long block=0; block<static_cast<long long>(blocks); ++block) {
    const size_t start=static_cast<size_t>(block)*65536, n=std::min(size_t{65536},pixels-start);
    uint8_t* data=rgb+3*start;
    size_t vectorized=0;
#if defined(JSHC_CC_HAVE_AVX2)
    if (kernel==1) {
      vectorized=n&~size_t{7};
      if(h.cache_info.enabled) {
        if(workers>1 && !h.tilexy_index.empty())jshc_channel::avx2_chain_tilexy_t0(h.tilexy_index.data(),h.output_palette.data(),data,vectorized);
        else if(!h.direct_index.empty())jshc_channel::avx2_chain_adaptive_linear(h.direct_index.data(),h.output_palette.data(),data,vectorized);
        else if(!h.compiled.empty())jshc_channel::avx2_chain_exception(h.compiled.data(),h.exceptions.data(),h.output_palette.data(),data,vectorized);
        else if(domain_fast)jshc_channel::avx2_chain_domain(h.views.data(),h.cache_view,data,vectorized);
        else jshc_channel::avx2_chain_cached(h.views.data(),h.cache_view,data,vectorized);
      }
      else jshc_channel::avx2_chain(h.views.data(),h.views.size(),data,vectorized);
    }
#endif
    scalar(h.views.data(),h.views.size(),data+3*vectorized,n-vectorized);
  }
}
void apply_to(Handle& h,const uint8_t* source,uint8_t* destination,size_t bytes,int kernel,int threads) {
  apply(h,nullptr,0,kernel,threads); // 先验证后端/线程，不写任何目标。
  if(!bytes)return;
  if(bytes%3 || !source || !destination)throw std::runtime_error("需要有效紧密RGB8输入/输出");
  const uintptr_t src=reinterpret_cast<uintptr_t>(source),dst=reinterpret_cast<uintptr_t>(destination);
  if(bytes>std::numeric_limits<uintptr_t>::max()-src || bytes>std::numeric_limits<uintptr_t>::max()-dst)throw std::runtime_error("RGB范围溢出");
  if(source==destination) {apply(h,destination,bytes,kernel,threads);return;}
  if(src<dst+bytes && dst<src+bytes)throw std::runtime_error("分离输入/输出不得部分重叠");
  const size_t pixels=bytes/3,blocks=pixels/65536+(pixels%65536!=0);
  if(blocks>size_t(std::numeric_limits<long long>::max()))throw std::runtime_error("块计数溢出");
#if defined(_OPENMP)
  const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,size_t(threads)));
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
  for(long long block=0;block<static_cast<long long>(blocks);++block) {
    const size_t start=size_t(block)*65536,n=std::min(size_t{65536},pixels-start);
    const uint8_t* in=source+3*start;uint8_t* target=destination+3*start;
#if defined(JSHC_CC_HAVE_AVX2)
    if(kernel==1 && !h.direct_index.empty()) {
      const size_t vectorized=n&~size_t{7};
      jshc_channel::avx2_chain_adaptive_linear_to(h.direct_index.data(),h.output_palette.data(),in,target,vectorized);
      if(n!=vectorized) {
        std::memcpy(target+3*vectorized,in+3*vectorized,3*(n-vectorized));
        scalar(h.views.data(),h.views.size(),target+3*vectorized,n-vectorized);
      }
      continue;
    }
#endif
    std::memcpy(target,in,n*3);apply(h,target,n*3,kernel,1);
  }
}
void prepare_palette(Handle& h) {
  auto& info=h.palette_info;info.version=1;info.reason=1;
  if(!domain_fast_enabled(h) || !(jshc_cc_capabilities()&2))return;
  const auto start=std::chrono::steady_clock::now();
  try {
    std::vector<uint32_t> values=h.cache;
    std::sort(values.begin(),values.end());values.erase(std::unique(values.begin(),values.end()),values.end());
    info.palette_size=uint32_t(values.size());info.reason=2;
    if(values.size()>255)return;
    // 原四模型和每级RGB8构成唯一标签，不读取完整源LUT、照片或历史输出流。
    std::vector<uint8_t> rgb(size_t{256}*256*256*3),lookup(size_t{1}<<24,255);
    for(size_t i=0;i<values.size();++i) {h.output_palette[i]=values[i];lookup[values[i]]=uint8_t(i);}
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(4)
#endif
    for(long long i=0;i<256LL*256*256;++i) {
      rgb[3*i]=uint8_t(i>>16);rgb[3*i+1]=uint8_t(i>>8);rgb[3*i+2]=uint8_t(i);
    }
    // 此时compiled为空，所以必定调用原修订16；四核准备成本单列并计入准备+100图。
    apply(h,rgb.data(),rgb.size(),1,4);
    std::vector<uint32_t> packed(size_t{1}<<21,255);
    size_t good=0,bad=0;
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(4) reduction(+:good,bad)
#endif
    for(long long block=0;block<(1LL<<21);++block) {
      unsigned ids[8],lo=255,hi=0;
      for(unsigned k=0;k<8;++k) {
        const size_t i=size_t(block)*8+k;
        const uint32_t value=uint32_t(rgb[3*i])|(uint32_t(rgb[3*i+1])<<8)|(uint32_t(rgb[3*i+2])<<16);
        ids[k]=lookup[value];lo=std::min(lo,ids[k]);hi=std::max(hi,ids[k]);
      }
      if(hi==255) {++bad;continue;}
      if(hi-lo<=7) {
        uint32_t word=lo;
        for(unsigned k=0;k<8;++k)word|=uint32_t(ids[k]-lo)<<(8+3*k);
        packed[size_t(block)]=word;++good;
      }
    }
    if(bad)throw std::runtime_error("域证明输出未包含在原缓存调色板");
    // 两个零词保护混合包中的非例外lane；其索引固定落在0或1。
    std::vector<uint32_t> exception_words;
    exception_words.reserve(2+(packed.size()-good)*2);
    exception_words.push_back(0);exception_words.push_back(0);
    for(size_t block=0;block<packed.size();++block)if(packed[block]==255) {
      const size_t index=exception_words.size();
      if(index>0xffffff)throw std::runtime_error("例外索引超出24bit");
      packed[block]=(uint32_t(index)<<8)|255;
      for(unsigned half=0;half<2;++half) {
        uint32_t word=0;
        for(unsigned k=0;k<4;++k) {
          const size_t i=block*8+half*4+k;
          const uint32_t value=uint32_t(rgb[3*i])|(uint32_t(rgb[3*i+1])<<8)|(uint32_t(rgb[3*i+2])<<16);
          word|=uint32_t(lookup[value])<<(8*k);
        }
        exception_words.push_back(word);
      }
    }
    info.blocks=packed.size();info.fast_blocks=good;info.table_capacity_bytes=packed.capacity()*sizeof(uint32_t);
    info.temporary_peak_bytes=rgb.capacity()+lookup.capacity()+values.capacity()*sizeof(uint32_t)+info.table_capacity_bytes+exception_words.capacity()*sizeof(uint32_t);
    h.compiled.swap(packed);h.exceptions.swap(exception_words);info.enabled=1;info.reason=0;
    try {
      // 四个输入ID按小端打包；对齐词gather加移位，不再需要末端额外词。
      h.direct_index.allocate(size_t{1}<<22);
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(4)
#endif
      for(long long group=0;group<(1LL<<22);++group) {
        uint32_t word=0;
        for(unsigned k=0;k<4;++k) {
          const uint32_t address=uint32_t(group)*4+k;
          const size_t i=((address&255u)<<16)|(address&0xff00u)|(address>>16);
          const uint32_t v=uint32_t(rgb[3*i])|(uint32_t(rgb[3*i+1])<<8)|(uint32_t(rgb[3*i+2])<<16);
          word|=uint32_t(lookup[v])<<(8*k);
        }
        h.direct_index.data()[size_t(group)]=word;
      }
      info.temporary_peak_bytes+=h.direct_index.bytes();
      // 单线程和分离输出保留线性表；多线程原地使用8×8×1颜色块。
      // 只置换本对象的精确ID，绝不读取照片、gold或历史输出。
      try {
        h.tilexy_index.allocate(size_t{1}<<22);
        const auto* linear=reinterpret_cast<const uint8_t*>(h.direct_index.data());
        auto* tilexy=reinterpret_cast<uint8_t*>(h.tilexy_index.data());
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(4)
#endif
        for(long long address=0;address<(1LL<<24);++address) {
          // 交换R的位3..5和G的位0..2；该置换自逆，最高改动位为10。
          const uint32_t c=uint32_t(address),swap=((c>>5)^c)&0x38u;
          tilexy[size_t(address)]=linear[c^swap^(swap<<5)];
        }
        info.temporary_peak_bytes+=h.tilexy_index.bytes();
      }catch(const std::bad_alloc&) {} // 第二表分配失败时保留已完成的线性精确路径。
    }catch(const std::bad_alloc&) {} // 新直表失败时保留完整23，不改变输出。

  }catch(const std::bad_alloc&) {std::vector<uint32_t>().swap(h.compiled);std::vector<uint32_t>().swap(h.exceptions);info.enabled=0;info.reason=3;}
  info.prepare_seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
}

}

extern "C" {
uint32_t jshc_cc_abi_version(void) {return 1;}
uint32_t jshc_cc_revision(void) {return 73;}
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
    prepare_palette(*h);
    *output=h.release();message(error,size,"");return 0;
  } catch (const std::exception& e) {message(error,size,e.what());return 1;}
}
void jshc_cc_destroy(void* handle) {delete static_cast<Handle*>(handle);}
size_t jshc_cc_model_bytes(const void* handle) {
  if(!handle)return 0;const auto& h=*static_cast<const Handle*>(handle);
  size_t bytes=sizeof(Handle)+h.models.capacity()*sizeof(jshc::SparseLut)+h.fractions.capacity()*sizeof(std::vector<uint32_t>)+h.views.capacity()*sizeof(jshc_channel::View)+h.original.capacity()*sizeof(void*);
  for(const auto& m:h.models)bytes+=m.runtime_bytes()-sizeof(jshc::SparseLut);
  for(const auto& f:h.fractions)bytes+=f.capacity()*sizeof(uint32_t);
  bytes+=h.cache.capacity()*sizeof(uint32_t)+(h.compiled.capacity()+h.exceptions.capacity())*sizeof(uint32_t)+h.direct_index.bytes()+h.tilexy_index.bytes();
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
int jshc_cc_get_palette_info(const void* handle,jshc_cc_palette_info* output,size_t bytes) {
  if(!handle || !output || bytes!=sizeof(jshc_cc_palette_info))return 1;
  *output=static_cast<const Handle*>(handle)->palette_info;return 0;
}
int jshc_cc_copy_palette(const void* handle,uint32_t* output,size_t entries,uint32_t* palette,size_t palette_entries) {
  if(!handle || !palette || palette_entries!=256)return 1;
  const auto& h=*static_cast<const Handle*>(handle);
  if(entries!=h.compiled.size() || (entries && !output))return 1;
  if(entries)std::memcpy(output,h.compiled.data(),entries*sizeof(uint32_t));
  std::memcpy(palette,h.output_palette.data(),256*sizeof(uint32_t));return 0;
}
int jshc_cc_get_exception_info(const void* handle,jshc_cc_exception_info* output,size_t bytes) {
  if(!handle || !output || bytes!=sizeof(jshc_cc_exception_info))return 1;
  const auto& h=*static_cast<const Handle*>(handle);
  *output={1,h.palette_info.enabled,h.exceptions.size(),h.exceptions.capacity()*sizeof(uint32_t)};return 0;
}
int jshc_cc_copy_exceptions(const void* handle,uint32_t* output,size_t entries) {
  if(!handle)return 1;
  const auto& values=static_cast<const Handle*>(handle)->exceptions;
  if(entries!=values.size() || (entries && !output))return 1;
  if(entries)std::memcpy(output,values.data(),entries*sizeof(uint32_t));return 0;
}
int jshc_cc_get_direct_info(const void* handle,jshc_cc_direct_info* output,size_t bytes) {
  if(!handle || !output || bytes!=sizeof(jshc_cc_direct_info))return 1;
  const auto& h=*static_cast<const Handle*>(handle);
  *output={1,uint32_t(!h.direct_index.empty()),9,0,h.direct_index.size(),h.direct_index.bytes(),0,0};return 0;
}
int jshc_cc_copy_direct(const void* handle,uint32_t* output,size_t entries) {
  if(!handle)return 1;const auto& h=*static_cast<const Handle*>(handle);
  if(entries!=h.direct_index.size() || (entries && !output))return 1;
  if(entries)std::memcpy(output,h.direct_index.data(),entries*sizeof(uint32_t));return 0;
}
int jshc_cc_get_paged_info(const void* handle,jshc_cc_paged_info* output,size_t bytes) {
  if(!handle || !output || bytes!=sizeof(jshc_cc_paged_info))return 1;
  const auto& h=*static_cast<const Handle*>(handle);
  *output={1,uint32_t(h.direct_index.advice()==0),0,0,uint64_t(reinterpret_cast<uintptr_t>(h.direct_index.data())),h.direct_index.bytes()};return 0;
}
JSHC_CC_API int jshc_cc_get_tilexy_info(const void* handle,jshc_cc_direct_info* output,size_t bytes) {
  if(!handle || !output || bytes!=sizeof(jshc_cc_direct_info))return 1;
  const auto& h=*static_cast<const Handle*>(handle);
  *output={1,uint32_t(!h.tilexy_index.empty()),17,0,h.tilexy_index.size(),h.tilexy_index.bytes(),0,0};return 0;
}
JSHC_CC_API int jshc_cc_copy_tilexy(const void* handle,uint32_t* output,size_t entries) {
  if(!handle)return 1;const auto& h=*static_cast<const Handle*>(handle);
  if(entries!=h.tilexy_index.size() || (entries && !output))return 1;
  if(entries)std::memcpy(output,h.tilexy_index.data(),entries*sizeof(uint32_t));return 0;
}
JSHC_CC_API int jshc_cc_get_tilexy_paged_info(const void* handle,jshc_cc_paged_info* output,size_t bytes) {
  if(!handle || !output || bytes!=sizeof(jshc_cc_paged_info))return 1;
  const auto& h=*static_cast<const Handle*>(handle);
  *output={1,uint32_t(h.tilexy_index.advice()==0),0,0,uint64_t(reinterpret_cast<uintptr_t>(h.tilexy_index.data())),h.tilexy_index.bytes()};return 0;
}
int jshc_cc_apply_to(void* handle,const uint8_t* source,uint8_t* destination,size_t bytes,int kernel,int threads,char* error,size_t size) {
  try {if(!handle)throw std::runtime_error("空研究句柄");apply_to(*static_cast<Handle*>(handle),source,destination,bytes,kernel,threads);message(error,size,"");return 0;}
  catch(const std::exception& e) {message(error,size,e.what());return 1;}
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
