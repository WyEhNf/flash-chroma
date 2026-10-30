/* direct准备专用：证明首层到达域，精确编译后三层，再并行扫描首层。
 * 注入点位于 fc::detail 内、AVX2原语之后。关闭开关时只留下空域描述。
 */
struct PrepareDomain {
    int r_min=0, r_max=-1, dg_min=0, dg_max=-1, db_min=0, db_max=-1;
    int width_g=0, width_b=0;
    std::size_t entries=0;
    bool proven=false;
};

#if FLASH_CHROMA_ENABLE_PREPARE_CACHE
inline int prepare_min(int a,int b) noexcept { return a<b?a:b; }
inline int prepare_max(int a,int b) noexcept { return a>b?a:b; }
inline std::int64_t prepare_floor_q16(std::int64_t n) noexcept {
    return n>=0?n/65536:-((-n+65535)/65536);
}
inline std::uint32_t prepare_fraction(const fc_core::fc_model& m,unsigned channel,unsigned axis,unsigned code) noexcept {
    const auto* p=m.sidecar.data?m.sidecar.data+(channel*768u+axis*256u+code)*4u:
        m.fraction_le+(axis*256u+code)*4u;
    return read32(p);
}

/* 与旧域证书相同的逐cell界：同坐标时通道差在八角点差的凸包内；
 * 分输出坐标的每轴扰动以该cell四条平行边斜率的最小/最大值包围。
 * 对负下界取floor、正上界取ceil，覆盖每级half-up后的整数差。
 * 固定局部数组1920B，八角点96B；它们是有界栈，不属于arena账单。
 */
inline PrepareDomain prepare_domain(const fc_core::fc_model& first) noexcept {
    PrepareDomain d;
    int rmin=255,rmax=0,gmin=255,gmax=-255,bmin=255,bmax=-255;
    const std::size_t nodes=std::size_t(first.m)*first.m*first.m;
    for(std::size_t i=0;i<nodes;++i) {
        const int r=first.nodes[i*3],g=int(first.nodes[i*3+1])-r,b=int(first.nodes[i*3+2])-r;
        rmin=prepare_min(rmin,r);rmax=prepare_max(rmax,r);
        gmin=prepare_min(gmin,g);gmax=prepare_max(gmax,g);
        bmin=prepare_min(bmin,b);bmax=prepare_max(bmax,b);
    }
    d.r_min=rmin;d.r_max=rmax;
    d.dg_min=prepare_max(-255,gmin-2);d.dg_max=prepare_min(255,gmax+2);
    d.db_min=prepare_max(-255,bmin-2);d.db_max=prepare_min(255,bmax+2);
    d.width_g=d.dg_max-d.dg_min+1;d.width_b=d.db_max-d.db_min+1;
    d.entries=std::size_t(rmax-rmin+1)*std::size_t(d.width_g)*std::size_t(d.width_b);
    if(d.entries>2u*MiB/sizeof(std::uint32_t)) {d.entries=0;return d;}
    const unsigned cells=first.m-1;
    int low[2][3][32],high[2][3][32],count[3][32]{};
    for(unsigned c=0;c<2;++c)for(unsigned a=0;a<3;++a)for(unsigned i=0;i<cells;++i) {
        low[c][a][i]=65536;high[c][a][i]=-65536;
    }
    for(unsigned a=0;a<3;++a)for(unsigned x=0;x<256;++x) {
        const unsigned cell=first.index[a*256u+x];++count[a][cell];
        const int red=int(prepare_fraction(first,0,a,x));
        for(unsigned c=0;c<2;++c) {
            const int delta=int(prepare_fraction(first,c+1,a,x))-red;
            low[c][a][cell]=prepare_min(low[c][a][cell],delta);
            high[c][a][cell]=prepare_max(high[c][a][cell],delta);
        }
    }
    bool reachable=false;
    for(unsigned r=0;r<cells;++r)for(unsigned g=0;g<cells;++g)for(unsigned b=0;b<cells;++b) {
        if(!count[0][r]||!count[1][g]||!count[2][b])continue;
        reachable=true;
        const unsigned indices[3]={r,g,b};int corner[8][3];
        for(unsigned k=0;k<8;++k) {
            const auto at=((std::size_t(r+((k>>2)&1))*first.m+g+((k>>1)&1))*first.m+b+(k&1))*3;
            for(unsigned c=0;c<3;++c)corner[k][c]=first.nodes[at+c];
        }
        for(unsigned c=0;c<2;++c) {
            int nmin=255,nmax=-255;
            for(unsigned k=0;k<8;++k) {
                const int diff=corner[k][c+1]-corner[k][0];
                nmin=prepare_min(nmin,diff);nmax=prepare_max(nmax,diff);
            }
            std::int64_t lower=0,upper=0;
            for(unsigned a=0;a<3;++a) {
                const unsigned bit=1u<<(2-a);int smin=255,smax=-255;
                for(unsigned k=0;k<8;++k)if(!(k&bit)) {
                    const int slope=corner[k|bit][c+1]-corner[k][c+1];
                    smin=prepare_min(smin,slope);smax=prepare_max(smax,slope);
                }
                const int lo=low[c][a][indices[a]],hi=high[c][a][indices[a]];
                const std::int64_t products[4]={std::int64_t(smin)*lo,std::int64_t(smin)*hi,
                    std::int64_t(smax)*lo,std::int64_t(smax)*hi};
                auto pmin=products[0],pmax=products[0];
                for(unsigned k=1;k<4;++k) {if(products[k]<pmin)pmin=products[k];if(products[k]>pmax)pmax=products[k];}
                lower+=pmin;upper+=pmax;
            }
            const int lo=prepare_max(-255,nmin+int(prepare_floor_q16(lower)));
            const int hi=prepare_min(255,nmax-int(prepare_floor_q16(-upper)));
            if(lo<(c?d.db_min:d.dg_min)||hi>(c?d.db_max:d.dg_max)) {d.entries=0;return d;}
        }
    }
    d.proven=reachable;
    if(!reachable)d.entries=0;
    return d;
}

constexpr std::size_t prepare_chunk_pixels=4096;
constexpr std::size_t prepare_chunk_bytes=prepare_chunk_pixels*3;
inline unsigned prepare_cache_workers(const PrepareDomain& d,const RuntimeConfig& config) noexcept {
    const auto blocks=d.entries/prepare_chunk_pixels+(d.entries%prepare_chunk_pixels!=0);
    return blocks<config.threads?static_cast<unsigned>(blocks):config.threads;
}
inline std::size_t prepare_cache_scratch(const PrepareDomain& d,const RuntimeConfig& config) noexcept {
    if(!d.proven)return 0;
    const bool rgb=config.representation==Representation::DirectRGB24;
    const bool narrow=config.representation==Representation::DirectU8;
    const auto cache_bytes=aligned(d.entries*4);
    const auto used_stride=aligned((narrow?256u:65536u)/8u);
    return cache_bytes+(rgb?0:cache_bytes+(narrow?1024u:131072u)*8u+std::size_t(config.threads)*used_stride)+
        std::size_t(prepare_cache_workers(d,config))*prepare_chunk_bytes;
}

/* 一次只处理有界RGB块；失效域槽存UINT32_MAX，不参与palette资格。
 * 末块按8像素补零，cache自身按64B预留，因此向量末写仍在arena内。
 */
FC_AVX2 inline void prepare_suffix_block(const PackedView* views,const PrepareDomain& d,
    std::size_t begin,std::size_t n,std::uint8_t* colours,std::uint32_t* cache) noexcept {
    const std::size_t rounded=(n+7u)&~std::size_t{7};
    const std::size_t plane=std::size_t(d.width_g)*d.width_b;
    for(std::size_t i=0;i<rounded;++i) {
        const auto index=begin+i;
        const int r=d.r_min+int(index/plane);
        const int g=r+d.dg_min+int((index/std::size_t(d.width_b))%std::size_t(d.width_g));
        const int b=r+d.db_min+int(index%std::size_t(d.width_b));
        const bool valid=i<n&&g>=0&&g<=255&&b>=0&&b<=255;
        auto* p=colours+i*3;
        p[0]=valid?std::uint8_t(r):0;p[1]=valid?std::uint8_t(g):0;p[2]=valid?std::uint8_t(b):0;
        cache[index]=valid?0:0xffffffffu;
    }
    for(std::size_t i=0;i<rounded;i+=8) {
        Rgb value;load8(colours+i*3,value);
        for(unsigned s=1;s<4;++s)transform(views[s],value);
        const auto packed=_mm256_or_si256(value.r,_mm256_or_si256(_mm256_slli_epi32(value.g,8),_mm256_slli_epi32(value.b,16)));
        const auto invalid=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(cache+begin+i));
        _mm256_storeu_si256(reinterpret_cast<__m256i*>(cache+begin+i),_mm256_or_si256(packed,invalid));
    }
}

/* R连续加载、G/B广播；分输出侧表分别计算自己的分数与顶点排序。 */
template<bool Shared>
FC_AVX2 inline void prepare_first8(const PackedView& v,unsigned red,
    const std::uint32_t* green,const std::uint32_t* blue,Rgb& rgb) noexcept {
    const auto ar=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(v.axes[0][0]+red));
    const auto ag=_mm256_set1_epi32(static_cast<int>(green[0])),ab=_mm256_set1_epi32(static_cast<int>(blue[0]));
    const auto base=_mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ar,17),_mm256_set1_epi32(v.sr)),
        _mm256_add_epi32(_mm256_mullo_epi32(_mm256_srli_epi32(ag,17),_mm256_set1_epi32(v.sg)),_mm256_srli_epi32(ab,17)));
    const auto mask=_mm256_set1_epi32(0x1ffff),x=_mm256_and_si256(ar,mask),y=_mm256_and_si256(ag,mask),z=_mm256_and_si256(ab,mask);
    const auto n0=gather(v.nodes,base),n3=gather(v.nodes,_mm256_add_epi32(base,_mm256_set1_epi32(v.sr+v.sg+1)));
    if constexpr(Shared) {
        __m256i high,middle,low,first,last;geometry(v,x,y,z,high,middle,low,first,last);
        const auto n1=gather(v.nodes,_mm256_add_epi32(base,first));
        const auto n2=gather(v.nodes,_mm256_add_epi32(base,_mm256_sub_epi32(_mm256_set1_epi32(v.sr+v.sg+1),last)));
        rgb.r=interpolate<0>(n0,n1,n2,n3,high,middle,low);
        rgb.g=interpolate<1>(n0,n1,n2,n3,high,middle,low);
        rgb.b=interpolate<2>(n0,n1,n2,n3,high,middle,low);
    } else {
        rgb.r=channel<0>(v,base,n0,n3,x,y,z);
        rgb.g=channel<1>(v,base,n0,n3,
            _mm256_and_si256(_mm256_loadu_si256(reinterpret_cast<const __m256i*>(v.axes[1][0]+red)),mask),
            _mm256_and_si256(_mm256_set1_epi32(static_cast<int>(green[1])),mask),
            _mm256_and_si256(_mm256_set1_epi32(static_cast<int>(blue[1])),mask));
        rgb.b=channel<2>(v,base,n0,n3,
            _mm256_and_si256(_mm256_loadu_si256(reinterpret_cast<const __m256i*>(v.axes[2][0]+red)),mask),
            _mm256_and_si256(_mm256_set1_epi32(static_cast<int>(green[2])),mask),
            _mm256_and_si256(_mm256_set1_epi32(static_cast<int>(blue[2])),mask));
    }
}

template<unsigned Format,bool Shared>
FC_AVX2 inline void prepare_direct_blue(const PackedView& first,const PrepareDomain& d,
    const std::uint32_t* table,std::uint8_t* destination,unsigned blue_code,std::uint8_t* used) noexcept {
    std::uint32_t blues[Shared?1:3];
    for(unsigned c=0;c<(Shared?1u:3u);++c)blues[c]=first.axes[c][2][blue_code];
    const auto bytes8=_mm_setr_epi8(0,4,8,12,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1);
    const auto words8=_mm_setr_epi8(0,1,4,5,8,9,12,13,-1,-1,-1,-1,-1,-1,-1,-1);
    for(unsigned green_code=0;green_code<256;++green_code) {
        std::uint32_t greens[Shared?1:3];
        for(unsigned c=0;c<(Shared?1u:3u);++c)greens[c]=first.axes[c][1][green_code];
        for(unsigned red_code=0;red_code<256;red_code+=8) {
            Rgb rgb;prepare_first8<Shared>(first,red_code,greens,blues,rgb);
            const auto dg=_mm256_sub_epi32(rgb.g,rgb.r),db=_mm256_sub_epi32(rgb.b,rgb.r);
            const auto index=_mm256_add_epi32(
                _mm256_mullo_epi32(_mm256_sub_epi32(rgb.r,_mm256_set1_epi32(d.r_min)),_mm256_set1_epi32(d.width_g*d.width_b)),
                _mm256_add_epi32(_mm256_mullo_epi32(_mm256_sub_epi32(dg,_mm256_set1_epi32(d.dg_min)),_mm256_set1_epi32(d.width_b)),
                    _mm256_sub_epi32(db,_mm256_set1_epi32(d.db_min))));
            const auto value=gather(table,index);
            auto* out=destination+(std::size_t(green_code)*256+red_code)*Format;
            if constexpr(Format==3) {
                const auto mask=_mm256_set1_epi32(255);
                rgb.r=_mm256_and_si256(value,mask);rgb.g=_mm256_and_si256(_mm256_srli_epi32(value,8),mask);rgb.b=_mm256_srli_epi32(value,16);
                store8(out,rgb);
            } else {
                /* worker私有位图只记录实际完整RGB8到达的ID；缓存超集不能冒充可达palette。 */
                alignas(32) std::uint32_t reached[8];
                _mm256_store_si256(reinterpret_cast<__m256i*>(reached),value);
                for(unsigned i=0;i<8;++i)used[reached[i]>>3]|=std::uint8_t(1u<<(reached[i]&7));
                const auto lo=_mm256_castsi256_si128(value),hi=_mm256_extracti128_si256(value,1);
                if constexpr(Format==1) {
                    _mm_storel_epi64(reinterpret_cast<__m128i*>(out),_mm_unpacklo_epi32(_mm_shuffle_epi8(lo,bytes8),_mm_shuffle_epi8(hi,bytes8)));
                } else {
                    _mm_storeu_si128(reinterpret_cast<__m128i*>(out),_mm_unpacklo_epi64(_mm_shuffle_epi8(lo,words8),_mm_shuffle_epi8(hi,words8)));
                }
            }
        }
    }
}

inline bool prepare_cached_direct(const PackedView* views,const PrepareDomain& d,
    const RuntimeConfig& config,std::uint8_t* destination,std::uint8_t* temporary,
    std::uint32_t* palette,std::uint32_t* palette_count) noexcept {
    if(!d.proven)return false;
    const bool rgb=config.representation==Representation::DirectRGB24;
    const bool narrow=config.representation==Representation::DirectU8;
    const std::size_t cache_bytes=aligned(d.entries*4),slots=narrow?1024:131072,limit=narrow?256:65536;
    auto* cache=reinterpret_cast<std::uint32_t*>(temporary);
    auto* ids=rgb?nullptr:reinterpret_cast<std::uint32_t*>(temporary+cache_bytes);
    auto* keys=rgb?nullptr:reinterpret_cast<std::uint32_t*>(temporary+2*cache_bytes);
    auto* values=rgb?nullptr:keys+slots;
    const auto used_stride=aligned(limit/8u);
    auto* used=rgb?nullptr:reinterpret_cast<std::uint8_t*>(values+slots);
    auto* scratch=rgb?temporary+cache_bytes:used+std::size_t(config.threads)*used_stride;
    const std::size_t blocks=d.entries/prepare_chunk_pixels+(d.entries%prepare_chunk_pixels!=0);
#if FLASH_CHROMA_ENABLE_OPENMP
    const int workers=omp_in_parallel()?1:static_cast<int>(prepare_cache_workers(d,config));
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
    for(long long task=0;task<static_cast<long long>(blocks);++task) {
        const std::size_t begin=std::size_t(task)*prepare_chunk_pixels;
        const std::size_t n=d.entries-begin<prepare_chunk_pixels?d.entries-begin:prepare_chunk_pixels;
        std::size_t worker=0;
#if FLASH_CHROMA_ENABLE_OPENMP
        worker=static_cast<std::size_t>(omp_get_thread_num());
#endif
        prepare_suffix_block(views,d,begin,n,scratch+worker*prepare_chunk_bytes,cache);
    }
    if(!rgb) {
        for(std::size_t i=0;i<slots;++i)keys[i]=0xffffffffu;
        for(std::size_t i=0;i<limit;++i)palette[i]=0;
        std::uint32_t count=0;
        for(std::size_t i=0;i<d.entries;++i) {
            const auto colour=cache[i];
            if(colour==0xffffffffu) {ids[i]=0;continue;}
            std::size_t slot=(std::uint32_t(colour*2654435761u))>>(narrow?22:15);
            while(keys[slot]!=0xffffffffu&&keys[slot]!=colour)slot=(slot+1)&(slots-1);
            if(keys[slot]==0xffffffffu) {
                /* 超集palette过大不等于实际全RGB8过大，必须走通用资格回退。 */
                if(count==limit)return false;
                keys[slot]=colour;values[slot]=count;palette[count++]=colour;
            }
            ids[i]=values[slot];
        }
        if(!count)return false;
        *palette_count=count;
    } else *palette_count=0;
    if(!rgb)for(std::size_t i=0;i<std::size_t(config.threads)*used_stride;++i)used[i]=0;
#if FLASH_CHROMA_ENABLE_OPENMP
    const int direct_workers=omp_in_parallel()?1:static_cast<int>(config.threads);
#pragma omp parallel for schedule(static) num_threads(direct_workers)
#endif
    for(int blue=0;blue<256;++blue) {
        const auto* lookup=rgb?cache:ids;
        const auto offset=std::size_t(blue)*65536u*(rgb?3u:(narrow?1u:2u));
        std::size_t worker=0;
#if FLASH_CHROMA_ENABLE_OPENMP
        worker=static_cast<std::size_t>(omp_get_thread_num());
#endif
        auto* reached=rgb?nullptr:used+worker*used_stride;
        if(rgb) {
            if(views[0].shared)prepare_direct_blue<3,true>(views[0],d,lookup,destination+offset,unsigned(blue),nullptr);
            else prepare_direct_blue<3,false>(views[0],d,lookup,destination+offset,unsigned(blue),nullptr);
        } else if(narrow) {
            if(views[0].shared)prepare_direct_blue<1,true>(views[0],d,lookup,destination+offset,unsigned(blue),reached);
            else prepare_direct_blue<1,false>(views[0],d,lookup,destination+offset,unsigned(blue),reached);
        } else {
            if(views[0].shared)prepare_direct_blue<2,true>(views[0],d,lookup,destination+offset,unsigned(blue),reached);
            else prepare_direct_blue<2,false>(views[0],d,lookup,destination+offset,unsigned(blue),reached);
        }
    }
    if(!rgb) {
        /* 合并worker位图，只报告完整RGB8实际可达颜色数。
         * 私有palette仍保留超集ID及未用槽；热核只按固定容量访问，不把该计数当ID上界。
         * 这样无需为了只读诊断再读写整张16/32MiB direct表。
         */
        for(unsigned worker=1;worker<config.threads;++worker)
            for(std::size_t i=0;i<used_stride;++i)used[i]|=used[std::size_t(worker)*used_stride+i];
        const auto old_count=*palette_count;
        std::uint32_t actual=0;
        for(std::uint32_t i=0;i<old_count;++i)if(used[i>>3]&(1u<<(i&7)))++actual;
        *palette_count=actual;
    }
    if(rgb)for(unsigned i=0;i<4;++i)destination[colours*3+i]=0;
    return true;
}
#endif
