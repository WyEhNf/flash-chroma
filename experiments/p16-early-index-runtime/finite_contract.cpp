// 101固定B批准备器：父100逐值、独立u64、合法极值View和纯地址方盒。
#include "channel_views.hpp"
#include "suffix_cache.hpp"
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <stdexcept>
#include <limits>
#include <vector>

namespace jshc_channel {
void avx2_compile_direct_scanline(const View*,const SuffixCacheView&,const uint32_t*,uint8_t*,size_t,size_t) noexcept;
void avx2_compile_direct_early_index(const View*,const SuffixCacheView&,const uint32_t*,uint8_t*,size_t,size_t) noexcept;
}
namespace {
void require(bool ok,const char* message) {if(!ok)throw std::runtime_error(message);}
uint32_t scalar_channel(const jshc_channel::View& v,uint32_t code,int channel) {
  const unsigned input[3]={code&255u,(code>>8)&255u,code>>16};
  uint32_t fractions[3];size_t steps[3]={size_t(v.sr),size_t(v.sg),1},base=0;
  for(int a=0;a<3;++a) {
    const uint32_t axis=v.axes[channel][a][input[a]];
    base+=size_t(axis>>17)*steps[a];fractions[a]=axis&0x1ffffu;
  }
  // 排序只改变四项非负凸权重；并列的零系数不依赖角的选择。
  for(int i=0;i<2;++i)for(int j=i+1;j<3;++j)if(fractions[i]<fractions[j]) {
    std::swap(fractions[i],fractions[j]);std::swap(steps[i],steps[j]);
  }
  const uint32_t weights[4]={65536u-fractions[0],fractions[0]-fractions[1],fractions[1]-fractions[2],fractions[2]};
  const size_t corners[4]={base,base+steps[0],base+steps[0]+steps[1],base+size_t(v.sr+v.sg+1)};
  uint64_t sum=0;
  for(int i=0;i<4;++i)sum+=uint64_t(weights[i])*uint64_t((v.nodes[corners[i]]>>(8*channel))&255u);
  return uint32_t((sum+32768u)/65536u);
}
uint8_t oracle(const jshc_channel::View& v,const jshc_channel::SuffixCacheView& cache,const std::vector<uint32_t>& ids,uint32_t code) {
  const int r=int(scalar_channel(v,code,0)),g=int(scalar_channel(v,code,1)),b=int(scalar_channel(v,code,2));
  require(r>=cache.r_min && r<=cache.r_max && g-r>=cache.dg_min && g-r<=cache.dg_max && b-r>=cache.db_min && b-r<=cache.db_max,"u64真值越过合法cache域");
  const int64_t index=int64_t(r-cache.r_min)*cache.width_g*cache.width_b+int64_t(g-r-cache.dg_min)*cache.width_b+b-r-cache.db_min;
  require(index>=0 && uint64_t(index)<ids.size(),"u64合法cache索引越界");
  return uint8_t(ids[size_t(index)]);
}
void verify_buffer(const std::vector<uint8_t>& buffer,size_t offset,const std::vector<uint8_t>& expected) {
  require(std::all_of(buffer.begin(),buffer.begin()+static_cast<std::ptrdiff_t>(offset),[](uint8_t x){return x==173;}),"前哨兵改变");
  require(std::equal(expected.begin(),expected.end(),buffer.begin()+static_cast<std::ptrdiff_t>(offset)),"输出ID与独立u64不同");
  require(std::all_of(buffer.begin()+static_cast<std::ptrdiff_t>(offset+expected.size()),buffer.end(),[](uint8_t x){return x==173;}),"后哨兵改变");
}
}
int main() {
  try {
    uint64_t oracle_pixels=0,candidate_pixels=0,old_pixels=0;
    unsigned views_count=0,full_batches=0,fallback_batches=0,candidate_calls=0,old_calls=0,canaries=0,readonly_checks=0;
    unsigned zero_fractions=0,endpoint_fractions=0,unaligned_axes=0;
    const std::array<std::array<size_t,2>,8> fallbacks={{{0,0},{0,8},{8,8},{248,16},{256,256},{65528,16},{65536,8},{(size_t{1}<<24)-8,8}}};
    unsigned pure_address_cases=0,negative_alpha_views=0,positive_beta_views=0,zero_beta_views=0;
    // 证明方盒超集仅作整数代数，不创建表、不执行gather。
    for(const int wg:{1,2,33,511})for(const int wb:{1,2,33,511})
      for(const int r0:{0,112,255})for(const int dg0:{-255,0,255})for(const int db0:{-255,0,255})
        for(const int r:{0,1,127,128,254,255})for(const int g:{0,1,127,128,254,255})for(const int b:{0,1,127,128,254,255}) {
          const int64_t w=int64_t(wg)*wb,alpha=w-wb-1,beta=-int64_t(r0)*w-int64_t(dg0)*wb-db0;
          const int64_t product=int64_t(r)*alpha,p0=product+beta,product_g=int64_t(g)*wb,p1=p0+product_g,index=p1+b;
          const int64_t old_index=int64_t(r-r0)*w+int64_t(g-r-dg0)*wb+b-r-db0;
          for(const int64_t value:{w,alpha,beta,product,p0,product_g,p1,index,old_index})
            require(value>=std::numeric_limits<int32_t>::min() && value<=std::numeric_limits<int32_t>::max(),"纯地址中间量int32越界");
          const int32_t actual_p0=int32_t(r)*int32_t(alpha)+int32_t(beta);
          const int32_t actual_p1=actual_p0+int32_t(g)*int32_t(wb),actual_index=actual_p1+int32_t(b);
          require(index==old_index && actual_p0==p0 && actual_p1==p1 && actual_index==index,"纯地址展开不等价");
          ++pure_address_cases;
        }
    for(int case_index=0;case_index<20;++case_index) {
      const int ordinary_m[4]={17,18,25,33},extra_m[8]={17,18,25,33,17,25,33,18};
      const int m=case_index<12?ordinary_m[case_index/3]:extra_m[case_index-12];
      const int layout=case_index<12?case_index%3:0;
      std::vector<uint32_t> nodes(size_t(m)*size_t(m)*size_t(m));
      for(int r=0;r<m;++r)for(int g=0;g<m;++g)for(int b=0;b<m;++b) {
        const uint32_t value=112u+uint32_t((3*r+5*g+7*b+2*r*g+3*g*b)%17);
        uint32_t red=value,green=value,blue=value;
        if(case_index==12){green=value-96;blue=value-96;}
        if(case_index==14){green=value-56;blue=value-56;}
        if(case_index==15){red=255;green=blue=0;}
        if(case_index==16)blue=112u+uint32_t((7*r+3*g+5*b)%17);
        if(case_index==17)green=112u+uint32_t((7*r+3*g+5*b)%17);
        if(case_index==18){red=127;green=uint32_t((13*r+29*g+37*b+5*r*g)&255);blue=uint32_t((31*r+19*g+7*b+3*g*b)&255);}
        if(case_index==19)red=green=blue=0;
        nodes[(size_t(r)*size_t(m)+size_t(g))*size_t(m)+size_t(b)]=red|(green<<8)|(blue<<16);
      }
      std::array<std::array<std::vector<uint32_t>,3>,3> axes;
      std::array<std::array<uint32_t*,3>,3> pointers{};
      const uint32_t levels[8]={0,1,16384,32768,32768,49152,65535,65536};
      for(int c=0;c<3;++c)for(int a=0;a<3;++a) {
        axes[c][a].assign(264,0xcacacacau);
        const auto address=reinterpret_cast<uintptr_t>(axes[c][a].data());
        const size_t offset=((4u+32u-(address%32u))%32u)/4u;
        uint32_t* axis=axes[c][a].data()+offset;pointers[c][a]=axis;
        require(reinterpret_cast<uintptr_t>(axis)%32u==4u,"私有轴必须4字节对齐且非32字节对齐");++unaligned_axes;
        std::vector<int> boundaries(size_t(m),0);boundaries.back()=256;
        for(int i=1;i<m-1;++i)boundaries[size_t(i)]=i*256/(m-1)+(i+a)%3-1;
        // B=127也取内部fraction；固定不等距分界，不依赖任何gold输出。
        if(a==2)boundaries[size_t((m-1)/2)]-=4;
        int cell=0;uint32_t previous=0;
        for(int code=0;code<256;++code) {
          while(cell<m-2 && code>=boundaries[size_t(cell+1)])++cell;
          const int position=code-boundaries[size_t(cell)],length=boundaries[size_t(cell+1)]-boundaries[size_t(cell)];
          uint32_t fraction=levels[size_t(position*7/(length-1))];
          if(layout==2 && c==1)fraction=uint32_t((uint64_t(fraction)*fraction+32768u)/65536u);
          if(layout==2 && c==2)fraction=65536u-uint32_t((uint64_t(65536u-fraction)*(65536u-fraction)+32768u)/65536u);
          axis[code]=(uint32_t(cell)<<17)|fraction;
          const uint32_t q=uint32_t(cell)*65536u+fraction;
          require(code==0 || q>=previous,"有限模型轴坐标不单调");previous=q;
          zero_fractions+=fraction==0;endpoint_fractions+=fraction==65536;
        }
      }
      jshc_channel::View view{};view.nodes=nodes.data();view.sr=m*m;view.sg=m;view.shared=layout!=2;
      for(int c=0;c<3;++c)for(int a=0;a<3;++a)view.axes[c][a]=pointers[layout==0?0:c][a];
      int r_min=112,r_max=128,dg_min=-16,db_min=-16,wg=33,wb=33;
      if(case_index>=12){wg=wb=1;dg_min=db_min=0;}
      if(case_index==12)dg_min=db_min=-96;
      if(case_index==14)dg_min=db_min=-56;
      if(case_index==15){r_min=r_max=255;dg_min=db_min=-255;}
      if(case_index==16){wb=511;db_min=-255;}
      if(case_index==17){wg=511;dg_min=-255;}
      if(case_index==18){r_min=r_max=127;wg=wb=511;dg_min=db_min=-255;}
      if(case_index==19)r_min=r_max=0;
      const size_t entries=size_t(r_max-r_min+1)*size_t(wg)*size_t(wb);
      require(entries<=262144,"合法手工cacheView超过1MiB预算");
      const int64_t alpha=int64_t(wg)*wb-wb-1,beta=-int64_t(r_min)*wg*wb-int64_t(dg_min)*wb-db_min;
      negative_alpha_views+=alpha<0;positive_beta_views+=beta>0;zero_beta_views+=beta==0;
      std::vector<uint32_t> ids(entries),table(ids.size());
      for(size_t i=0;i<ids.size();++i)ids[i]=uint32_t((i*73u+(i/33u)*19u+11u)%251u);
      const auto original_axes=axes;const auto original_nodes=nodes,original_ids=ids,original_table=table;
      const jshc_channel::SuffixCacheView cache={table.data(),r_min,r_max,dg_min,dg_min+wg-1,db_min,db_min+wb-1,wg,wb};
      auto readonly=[&]() {require(axes==original_axes && nodes==original_nodes && ids==original_ids && table==original_table,"只读输入改变");++readonly_checks;};
      auto check=[&](size_t begin,size_t pixels,bool full) {
        std::vector<uint8_t> expected(pixels);
        for(size_t i=0;i<pixels;++i)expected[i]=oracle(view,cache,ids,uint32_t(begin+i));
        oracle_pixels+=pixels;
        std::vector<uint8_t> old(pixels+128,173);
        jshc_channel::avx2_compile_direct_scanline(&view,cache,ids.data(),old.data()+64,begin,pixels);++old_calls;old_pixels+=pixels;
        verify_buffer(old,64,expected);readonly();++canaries;
        for(const size_t extra:{size_t(0),size_t(1),size_t(3),size_t(7),size_t(15),size_t(31)}) {
          const size_t offset=64+extra;std::vector<uint8_t> output(pixels+offset+64,173);
          jshc_channel::avx2_compile_direct_early_index(&view,cache,ids.data(),output.data()+offset,begin,pixels);
          ++candidate_calls;candidate_pixels+=pixels;verify_buffer(output,offset,expected);readonly();++canaries;
        }
        if(full)++full_batches;else ++fallback_batches;
      };
      for(const size_t blue:{size_t(0),size_t(127),size_t(255)})check(blue*65536u,65536,true);
      for(const auto& pair:fallbacks)check(pair[0],pair[1],false);
      ++views_count;
    }
    require(views_count==20 && full_batches==60 && fallback_batches==160,"固定批计数不符");
    require(candidate_calls==1320 && old_calls==220 && canaries==1540 && readonly_checks==1540,"固定入口调用计数不符");
    require(oracle_pixels==3938560 && old_pixels==3938560 && candidate_pixels==23631360,"固定像素计数不符");
    require(pure_address_cases==93312 && negative_alpha_views==6 && positive_beta_views==2 && zero_beta_views==2,"固定代数/合法极值计数不符");
    std::printf("{\"pure_address_cases\":93312,\"legal_extreme_views\":8,\"negative_alpha_views\":6,\"positive_beta_views\":2,\"zero_beta_views\":2,\"passed\":true,\"views\":%u,\"full_batches\":%u,\"fallback_batches\":%u,\"candidate_calls\":%u,\"old100_calls\":%u,\"native_calls\":%u,\"oracle_pixels\":%llu,\"old100_pixels\":%llu,\"candidate_pixels\":%llu,\"canary_cases\":%u,\"readonly_checks\":%u,\"axis_mod32_four_cases\":%u,\"zero_fractions\":%u,\"endpoint_fractions\":%u,\"full_chain_calls\":0,\"photo_calls\":0,\"performance_calls\":0}\n",
      views_count,full_batches,fallback_batches,candidate_calls,old_calls,candidate_calls+old_calls,
      static_cast<unsigned long long>(oracle_pixels),static_cast<unsigned long long>(old_pixels),static_cast<unsigned long long>(candidate_pixels),canaries,readonly_checks,unaligned_axes,zero_fractions,endpoint_fractions);
    return 0;
  }catch(const std::exception& error) {std::fprintf(stderr,"%s\n",error.what());return 1;}
}
