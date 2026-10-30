"""101单版生产/有限合同生成，不修改100已执行源，不执行native。"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def finite_source(source):
    text=source.read_text(encoding='utf-8')
    text=text.replace('// 100固定B批准备器有限合同：独立四项uint64凸权重，不使用gold/照片。',
        '// 101固定B批准备器：父100逐值、独立u64、合法极值View和纯地址方盒。')
    text=text.replace('#include <stdexcept>','#include <stdexcept>\n#include <limits>')
    text=text.replace('avx2_compile_direct_scanline','avx2_compile_direct_early_index').replace('avx2_compile_direct(', 'avx2_compile_direct_scanline(')
    text=text.replace('uint8_t oracle(const jshc_channel::View& v,const std::vector<uint32_t>& ids,uint32_t code)',
        'uint8_t oracle(const jshc_channel::View& v,const jshc_channel::SuffixCacheView& cache,const std::vector<uint32_t>& ids,uint32_t code)')
    old='''  require(r>=112 && r<=128 && g-r>=-16 && g-r<=16 && b-r>=-16 && b-r<=16,"u64真值越过固定cache域");
  return uint8_t(ids[size_t(r-112)*33u*33u+size_t(g-r+16)*33u+size_t(b-r+16)]);'''
    new='''  require(r>=cache.r_min && r<=cache.r_max && g-r>=cache.dg_min && g-r<=cache.dg_max && b-r>=cache.db_min && b-r<=cache.db_max,"u64真值越过合法cache域");
  const int64_t index=int64_t(r-cache.r_min)*cache.width_g*cache.width_b+int64_t(g-r-cache.dg_min)*cache.width_b+b-r-cache.db_min;
  require(index>=0 && uint64_t(index)<ids.size(),"u64合法cache索引越界");
  return uint8_t(ids[size_t(index)]);'''
    assert old in text;text=text.replace(old,new)
    marker='''    for(const int m:{17,18,25,33})for(int layout=0;layout<3;++layout) {'''
    replacement='''    unsigned pure_address_cases=0,negative_alpha_views=0,positive_beta_views=0,zero_beta_views=0;
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
      const int layout=case_index<12?case_index%3:0;'''
    assert marker in text;text=text.replace(marker,replacement)
    old='''        nodes[(size_t(r)*size_t(m)+size_t(g))*size_t(m)+size_t(b)]=value|(value<<8)|(value<<16);'''
    new='''        uint32_t red=value,green=value,blue=value;
        if(case_index==12){green=value-96;blue=value-96;}
        if(case_index==14){green=value-56;blue=value-56;}
        if(case_index==15){red=255;green=blue=0;}
        if(case_index==16)blue=112u+uint32_t((7*r+3*g+5*b)%17);
        if(case_index==17)green=112u+uint32_t((7*r+3*g+5*b)%17);
        if(case_index==18){red=127;green=uint32_t((13*r+29*g+37*b+5*r*g)&255);blue=uint32_t((31*r+19*g+7*b+3*g*b)&255);}
        if(case_index==19)red=green=blue=0;
        nodes[(size_t(r)*size_t(m)+size_t(g))*size_t(m)+size_t(b)]=red|(green<<8)|(blue<<16);'''
    assert old in text;text=text.replace(old,new)
    old='''      std::vector<uint32_t> ids(17u*33u*33u),table(ids.size());'''
    new='''      int r_min=112,r_max=128,dg_min=-16,db_min=-16,wg=33,wb=33;
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
      std::vector<uint32_t> ids(entries),table(ids.size());'''
    assert old in text;text=text.replace(old,new)
    text=text.replace('''      const jshc_channel::SuffixCacheView cache={table.data(),112,128,-16,16,-16,16,33,33};''',
        '''      const jshc_channel::SuffixCacheView cache={table.data(),r_min,r_max,dg_min,dg_min+wg-1,db_min,db_min+wb-1,wg,wb};''')
    text=text.replace('oracle(view,ids,uint32_t(begin+i))','oracle(view,cache,ids,uint32_t(begin+i))')
    # 修改的是本新文件的固定口径；源100保持原字节。
    for old,new in [('views_count==12','views_count==20'),('full_batches==36','full_batches==60'),('fallback_batches==96','fallback_batches==160'),
            ('candidate_calls==792','candidate_calls==1320'),('old_calls==132','old_calls==220'),('canaries==924','canaries==1540'),
            ('readonly_checks==924','readonly_checks==1540'),('oracle_pixels==2363136','oracle_pixels==3938560'),
            ('old_pixels==2363136','old_pixels==3938560'),('candidate_pixels==14178816','candidate_pixels==23631360')]:
        assert old in text;text=text.replace(old,new)
    marker='''    std::printf("{\\"passed\\":true,'''
    assert marker in text
    text=text.replace(marker,'''    require(pure_address_cases==93312 && negative_alpha_views==6 && positive_beta_views==2 && zero_beta_views==2,"固定代数/合法极值计数不符");
    std::printf("{\\"pure_address_cases\\":93312,\\"legal_extreme_views\\":8,\\"negative_alpha_views\\":6,\\"positive_beta_views\\":2,\\"zero_beta_views\\":2,\\"passed\\":true,''')
    text=text.replace('old97_calls','old100_calls').replace('old97_pixels','old100_pixels')
    return text


def main():
    source=ROOT/'experiments/p16-scanline-prepare-runtime';target=ROOT/'experiments/p16-early-index-runtime'
    target.mkdir(exist_ok=False)
    runtime=(source/'channel_runtime.cpp').read_bytes()
    assert runtime.count(b'avx2_compile_direct_scanline(')==2 and runtime.count(b'return 100;')==1
    runtime=runtime.replace(b'avx2_compile_direct_scanline(',b'avx2_compile_direct_early_index(').replace(b'return 100;',b'return 101;')
    (target/'channel_runtime.cpp').write_bytes(runtime)
    for name in ('compile_shared_avx2.cpp','compile_scanline_avx2.cpp','small_palette.hpp','workload_hint.h'):
        (target/name).write_bytes((source/name).read_bytes())
    (target/'compile_index_avx2.cpp').write_bytes((ROOT/'experiments/p16-early-index-draft/compile_index_avx2.cpp').read_bytes())
    (target/'finite_contract.cpp').write_text(finite_source(source/'finite_contract.cpp'),encoding='utf-8',newline='\n')
    cmake=(source/'CMakeLists.txt').read_text(encoding='utf-8')
    cmake=cmake.replace('jshc_scanline_prepare','jshc_early_index').replace('p16_scanline_contract','p16_early_index_contract')
    cmake=cmake.replace('compile_shared_avx2.cpp compile_scanline_avx2.cpp','compile_shared_avx2.cpp compile_scanline_avx2.cpp compile_index_avx2.cpp')
    cmake=cmake.replace('# 100仅新增固定B批扫描线准备器；原97八对象和公开apply路径保持。','# 101只新增精确索引/早消费prepare；100九旧对象和公开apply保持。')
    (target/'CMakeLists.txt').write_text(cmake,encoding='utf-8',newline='\n')


if __name__=='__main__':main()
