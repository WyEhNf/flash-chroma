/* 精确 direct 热核：从成熟 adaptive-linear 路径迁移的标量 ILP 查表与 AVX2 打包。
 * 本片段由生成器嵌入 fc::detail；调用者先检查 AVX2，输入/输出只能同址或分离。
 * U8/U16 表不要求 guard；RGB24 沿用原有的四字节尾部容量契约。
 * 基础路径不依赖 BMI；可选强目标函数由每块一次的 CPU 能力检测保护。
 * 不申请堆，不使用可变全局状态，也不改变任何模型或四级整数结果。
 */

template<bool Wide>
inline std::uint32_t direct_palette_id(const std::uint8_t* table,std::uint32_t code) noexcept {
    if constexpr(Wide)return reinterpret_cast<const std::uint16_t*>(table)[code];
    else return table[code];
}

template<bool Wide>
inline std::uint32_t direct_palette_value(const std::uint8_t* table,
    const std::uint32_t* palette,std::uint32_t code) noexcept {
    return palette[direct_palette_id<Wide>(table,code)];
}

/* 仅宽循环使用；第四字节只用于机器读取，随后掩掉，不参与颜色地址。 */
inline std::uint32_t direct_code_wide(const std::uint8_t* p) noexcept {
    std::uint32_t value;std::memcpy(&value,p,4);return value&0xffffffu;
}

/* 精确读取八个像素的24B，不依赖下一个像素或图像 padding。 */
template<bool Wide>
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_read_exact(
    const std::uint8_t* table,const std::uint32_t* palette,const std::uint8_t* p) noexcept {
    std::uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
    return _mm256_setr_epi32(
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t(a&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t((a>>24)&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t(((a>>48)|(b<<16))&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t((b>>8)&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t((b>>32)&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t(((b>>56)|(c<<8))&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t((c>>16)&0xffffffu))),
        static_cast<int>(direct_palette_value<Wide>(table,palette,std::uint32_t(c>>40))));
}

/* 八路ID读取按两组提前发出；其后再读取小调色板，保留成熟内核的ILP组织。 */
template<bool Wide>
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_read_wide(
    const std::uint8_t* table,const std::uint32_t* palette,const std::uint8_t* p) noexcept {
    const auto i0=direct_palette_id<Wide>(table,direct_code_wide(p));
    const auto i1=direct_palette_id<Wide>(table,direct_code_wide(p+3));
    const auto i2=direct_palette_id<Wide>(table,direct_code_wide(p+6));
    const auto i3=direct_palette_id<Wide>(table,direct_code_wide(p+9));
    __asm__ volatile("" : : "r"(i0),"r"(i1),"r"(i2),"r"(i3) : "memory");
    const __m128i lo=_mm_setr_epi32(static_cast<int>(palette[i0]),static_cast<int>(palette[i1]),
        static_cast<int>(palette[i2]),static_cast<int>(palette[i3]));
    const auto i4=direct_palette_id<Wide>(table,direct_code_wide(p+12));
    const auto i5=direct_palette_id<Wide>(table,direct_code_wide(p+15));
    const auto i6=direct_palette_id<Wide>(table,direct_code_wide(p+18));
    const auto i7=direct_palette_id<Wide>(table,direct_code_wide(p+21));
    __asm__ volatile("" : : "r"(i4),"r"(i5),"r"(i6),"r"(i7) : "memory");
    const __m128i hi=_mm_setr_epi32(static_cast<int>(palette[i4]),static_cast<int>(palette[i5]),
        static_cast<int>(palette[i6]),static_cast<int>(palette[i7]));
    return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
}

/* 保持强目标只进入独立 BMI 主模板，不内联到仅支持 AVX2 的分派函数。 */
#if defined(__x86_64__)
#define FC_DIRECT_BMI __attribute__((target("avx2,bmi")))

FC_DIRECT_BMI inline __attribute__((always_inline)) std::uint64_t direct_pair48_input(
    const std::uint8_t* p) noexcept {
    typedef std::uint64_t unaligned_alias_u64 __attribute__((aligned(1),may_alias));
    const std::uint64_t high_mask=0xffff000000000000ULL;
    std::uint64_t packed;
    /* AT&T顺序为内存、取反掩码、目标，结果精确保留低48位的两个RGB像素。 */
    __asm__("andn %1, %q2, %q0" : "=r"(packed)
        : "m"(*reinterpret_cast<const unaligned_alias_u64*>(p)),"r"(high_mask) : "cc");
    return packed;
}

template<bool Wide>
FC_DIRECT_BMI inline __attribute__((always_inline)) __m256i direct_read_pair48(
    const std::uint8_t* table,const std::uint32_t* palette,const std::uint8_t* p) noexcept {
    const auto q0=direct_pair48_input(p);
    const auto i0=direct_palette_id<Wide>(table,std::uint32_t(q0&0xffffffu));
    const auto i1=direct_palette_id<Wide>(table,std::uint32_t(q0>>24));
    const auto q1=direct_pair48_input(p+6);
    const auto i2=direct_palette_id<Wide>(table,std::uint32_t(q1&0xffffffu));
    const auto i3=direct_palette_id<Wide>(table,std::uint32_t(q1>>24));
    __asm__ volatile("" : : "r"(i0),"r"(i1),"r"(i2),"r"(i3) : "memory");
    const auto lo=_mm_setr_epi32(static_cast<int>(palette[i0]),static_cast<int>(palette[i1]),
        static_cast<int>(palette[i2]),static_cast<int>(palette[i3]));
    const auto q2=direct_pair48_input(p+12);
    const auto i4=direct_palette_id<Wide>(table,std::uint32_t(q2&0xffffffu));
    const auto i5=direct_palette_id<Wide>(table,std::uint32_t(q2>>24));
    const auto q3=direct_pair48_input(p+18);
    const auto i6=direct_palette_id<Wide>(table,std::uint32_t(q3&0xffffffu));
    const auto i7=direct_palette_id<Wide>(table,std::uint32_t(q3>>24));
    __asm__ volatile("" : : "r"(i4),"r"(i5),"r"(i6),"r"(i7) : "memory");
    const auto hi=_mm_setr_epi32(static_cast<int>(palette[i4]),static_cast<int>(palette[i5]),
        static_cast<int>(palette[i6]),static_cast<int>(palette[i7]));
    return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
}
#endif

FC_AVX2 inline __attribute__((always_inline)) void direct_output8(
    std::uint8_t* p,__m256i value) noexcept {
    const auto bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(
        0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,
        0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
    const auto lo=_mm256_castsi256_si128(bytes),hi=_mm256_extracti128_si256(bytes,1);
    _mm_storeu_si128(reinterpret_cast<__m128i*>(p),_mm_or_si128(lo,_mm_slli_si128(hi,12)));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(p+16),_mm_srli_si128(hi,4));
}

template<int Phase>
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_pack(__m256i value) noexcept {
    const auto bytes=_mm256_shuffle_epi8(value,_mm256_setr_epi8(
        0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1,
        0,1,2,4,5,6,8,9,10,12,13,14,-1,-1,-1,-1));
    if constexpr(Phase==0)return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(0,1,2,4,5,6,3,7));
    else if constexpr(Phase==1)return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(2,4,5,6,3,7,0,1));
    else if constexpr(Phase==2)return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(5,6,3,7,0,1,2,4));
    else return _mm256_permutevar8x32_epi32(bytes,_mm256_setr_epi32(3,7,0,1,2,4,5,6));
}

FC_AVX2 inline __attribute__((always_inline)) void direct_output32_stream(
    std::uint8_t* p,__m256i v0,__m256i v1,__m256i v2,__m256i v3) noexcept {
    const auto s0=_mm256_blend_epi32(v0,v1,0xc0);
    const auto s1=_mm256_permute2x128_si256(v1,v2,0x30);
    const auto s2=_mm256_blend_epi32(v3,v2,0x03);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(p),s0);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(p+32),s1);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(p+64),s2);
}

FC_AVX2 inline __attribute__((always_inline)) void direct_output32(
    std::uint8_t* p,__m256i v0,__m256i v1,__m256i v2,__m256i v3) noexcept {
    const auto a=_mm256_castsi256_si128(v0),b=_mm256_extracti128_si256(v0,1);
    const auto c=_mm256_castsi256_si128(v1),d=_mm256_extracti128_si256(v1,1);
    const auto e=_mm256_castsi256_si128(v2),f=_mm256_extracti128_si256(v2,1);
    const auto g=_mm256_castsi256_si128(v3),h=_mm256_extracti128_si256(v3,1);
    const auto s0=_mm256_inserti128_si256(_mm256_castsi128_si256(a),_mm_unpacklo_epi64(b,c),1);
    const auto s1=_mm256_inserti128_si256(_mm256_castsi128_si256(_mm_alignr_epi8(d,c,8)),e,1);
    const auto s2=_mm256_inserti128_si256(_mm256_castsi128_si256(_mm_unpacklo_epi64(f,g)),_mm_alignr_epi8(h,g,8),1);
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(p),s0);
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(p+32),s1);
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(p+64),s2);
}

template<bool Wide>
inline void direct_palette_scalar(const std::uint8_t* table,const std::uint32_t* palette,
    const std::uint8_t* src,std::uint8_t* dst) noexcept {
    store_rgb(dst,direct_palette_value<Wide>(table,palette,rgb32(src)));
}

template<bool Wide>
FC_AVX2 inline void direct_palette_run(const std::uint8_t* table,const std::uint32_t* palette,
    const std::uint8_t* source,std::uint8_t* destination,std::size_t remaining) noexcept {
    const std::size_t initial=remaining>341?1024:remaining*3;
    for(std::size_t offset=0;offset<initial;offset+=64)
        _mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_NTA);
    /* 3与64互质；最多63个像素后到达缓存行边界，且不写入范围外。 */
    for(;remaining&&(reinterpret_cast<std::uintptr_t>(destination)&63);source+=3,destination+=3,--remaining)
        direct_palette_scalar<Wide>(table,palette,source,destination);
    bool streamed=false;
    for(;remaining>=72;source+=192,destination+=192,remaining-=64) {
        /* 最大提示地址为source+1215；remaining>=406保证它仍在当前输入块内。 */
        if(remaining>=406) {
            const auto* future=source+1024;
            _mm_prefetch(reinterpret_cast<const char*>(future),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+64),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+128),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+191),_MM_HINT_NTA);
        }
        /* 宽读末端多出的1B位于剩余块内；先读取64像素，再写精确192B。 */
        const auto r0=direct_pack<0>(direct_read_wide<Wide>(table,palette,source));
        const auto r1=direct_pack<1>(direct_read_wide<Wide>(table,palette,source+24));
        const auto r2=direct_pack<2>(direct_read_wide<Wide>(table,palette,source+48));
        const auto r3=direct_pack<3>(direct_read_wide<Wide>(table,palette,source+72));
        const auto r4=direct_pack<0>(direct_read_wide<Wide>(table,palette,source+96));
        const auto r5=direct_pack<1>(direct_read_wide<Wide>(table,palette,source+120));
        const auto r6=direct_pack<2>(direct_read_wide<Wide>(table,palette,source+144));
        const auto r7=direct_pack<3>(direct_read_wide<Wide>(table,palette,source+168));
        direct_output32_stream(destination,r0,r1,r2,r3);
        direct_output32_stream(destination+96,r4,r5,r6,r7);
        streamed=true;
    }
    /* 在普通尾部、调用方读取和OpenMP barrier前发布NT写入。 */
    if(streamed)_mm_sfence();
    for(;remaining>=40;source+=96,destination+=96,remaining-=32) {
        const auto r0=direct_pack<0>(direct_read_wide<Wide>(table,palette,source));
        const auto r1=direct_pack<0>(direct_read_wide<Wide>(table,palette,source+24));
        const auto r2=direct_pack<0>(direct_read_wide<Wide>(table,palette,source+48));
        const auto r3=direct_pack<0>(direct_read_wide<Wide>(table,palette,source+72));
        direct_output32(destination,r0,r1,r2,r3);
    }
    for(;remaining>=8;source+=24,destination+=24,remaining-=8)
        direct_output8(destination,direct_read_exact<Wide>(table,palette,source));
    for(;remaining;source+=3,destination+=3,--remaining)
        direct_palette_scalar<Wide>(table,palette,source,destination);
}

/* 与基础模板保持同一写入、预取和短尾协议；只替换宽循环的双像素读取。 */
#if defined(__x86_64__)
template<bool Wide>
FC_DIRECT_BMI inline void direct_palette_run_bmi(const std::uint8_t* table,const std::uint32_t* palette,
    const std::uint8_t* source,std::uint8_t* destination,std::size_t remaining) noexcept {
    const std::size_t initial=remaining>341?1024:remaining*3;
    for(std::size_t offset=0;offset<initial;offset+=64)
        _mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_NTA);
    for(;remaining&&(reinterpret_cast<std::uintptr_t>(destination)&63);source+=3,destination+=3,--remaining)
        direct_palette_scalar<Wide>(table,palette,source,destination);
    bool streamed=false;
    for(;remaining>=72;source+=192,destination+=192,remaining-=64) {
        if(remaining>=406) {
            const auto* future=source+1024;
            _mm_prefetch(reinterpret_cast<const char*>(future),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+64),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+128),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+191),_MM_HINT_NTA);
        }
        /* 最后一次8B读取起于source+186，末端194B仍在72像素的216B内。 */
        const auto r0=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source));
        const auto r1=direct_pack<1>(direct_read_pair48<Wide>(table,palette,source+24));
        const auto r2=direct_pack<2>(direct_read_pair48<Wide>(table,palette,source+48));
        const auto r3=direct_pack<3>(direct_read_pair48<Wide>(table,palette,source+72));
        const auto r4=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source+96));
        const auto r5=direct_pack<1>(direct_read_pair48<Wide>(table,palette,source+120));
        const auto r6=direct_pack<2>(direct_read_pair48<Wide>(table,palette,source+144));
        const auto r7=direct_pack<3>(direct_read_pair48<Wide>(table,palette,source+168));
        direct_output32_stream(destination,r0,r1,r2,r3);
        direct_output32_stream(destination+96,r4,r5,r6,r7);
        streamed=true;
    }
    if(streamed)_mm_sfence();
    for(;remaining>=40;source+=96,destination+=96,remaining-=32) {
        /* 最后一次8B读取起于source+90，末端98B仍在40像素的120B内。 */
        const auto r0=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source));
        const auto r1=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source+24));
        const auto r2=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source+48));
        const auto r3=direct_pack<0>(direct_read_pair48<Wide>(table,palette,source+72));
        direct_output32(destination,r0,r1,r2,r3);
    }
    for(;remaining>=8;source+=24,destination+=24,remaining-=8)
        direct_output8(destination,direct_read_exact<Wide>(table,palette,source));
    for(;remaining;source+=3,destination+=3,--remaining)
        direct_palette_scalar<Wide>(table,palette,source,destination);
}
#endif

/* 保留旧gather作为可复测基线，表尾guard与精确24B图像读写契约不变。 */
FC_AVX2 inline void direct_rgb24_gather_run(const std::uint8_t* table,const std::uint8_t* src,
    std::uint8_t* dst,std::size_t pixels) noexcept {
    const auto mask=_mm256_set1_epi32(255);
    std::size_t i=0;
    for(;pixels-i>=8;i+=8) {
        Rgb rgb;load8(src+3*i,rgb);
        const auto code=_mm256_or_si256(rgb.r,_mm256_or_si256(_mm256_slli_epi32(rgb.g,8),_mm256_slli_epi32(rgb.b,16)));
        const auto offset=_mm256_add_epi32(code,_mm256_slli_epi32(code,1));
        const auto value=_mm256_i32gather_epi32(reinterpret_cast<const int*>(table),offset,1);
        rgb.r=_mm256_and_si256(value,mask);rgb.g=_mm256_and_si256(_mm256_srli_epi32(value,8),mask);
        rgb.b=_mm256_and_si256(_mm256_srli_epi32(value,16),mask);store8(dst+3*i,rgb);
    }
    for(;i<pixels;++i)store_rgb(dst+3*i,rgb32(table+std::size_t(rgb32(src+3*i))*3));
}

/* RGB24节点只有3B；读取第4B由既有表尾guard保证，打包时明确丢弃。 */
inline std::uint32_t direct_rgb24_value(const std::uint8_t* table,std::uint32_t code) noexcept {
    std::uint32_t value;std::memcpy(&value,table+std::size_t(code)*3,4);return value;
}

/* 输入只读精确24B，用于最后的8像素及保护页边界。 */
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_rgb24_read_exact(
    const std::uint8_t* table,const std::uint8_t* p) noexcept {
    std::uint64_t a,b,c;std::memcpy(&a,p,8);std::memcpy(&b,p+8,8);std::memcpy(&c,p+16,8);
    return _mm256_setr_epi32(
        static_cast<int>(direct_rgb24_value(table,std::uint32_t(a&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t((a>>24)&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t(((a>>48)|(b<<16))&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t((b>>8)&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t((b>>32)&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t(((b>>56)|(c<<8))&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t((c>>16)&0xffffffu))),
        static_cast<int>(direct_rgb24_value(table,std::uint32_t(c>>40))));
}

/* 八个独立节点读取分组发出，减少单条gather内部的串行等待。 */
FC_AVX2 inline __attribute__((always_inline)) __m256i direct_rgb24_read_wide(
    const std::uint8_t* table,const std::uint8_t* p) noexcept {
    const auto v0=direct_rgb24_value(table,direct_code_wide(p));
    const auto v1=direct_rgb24_value(table,direct_code_wide(p+3));
    const auto v2=direct_rgb24_value(table,direct_code_wide(p+6));
    const auto v3=direct_rgb24_value(table,direct_code_wide(p+9));
    __asm__ volatile("" : : "r"(v0),"r"(v1),"r"(v2),"r"(v3) : "memory");
    const auto lo=_mm_setr_epi32(static_cast<int>(v0),static_cast<int>(v1),static_cast<int>(v2),static_cast<int>(v3));
    const auto v4=direct_rgb24_value(table,direct_code_wide(p+12));
    const auto v5=direct_rgb24_value(table,direct_code_wide(p+15));
    const auto v6=direct_rgb24_value(table,direct_code_wide(p+18));
    const auto v7=direct_rgb24_value(table,direct_code_wide(p+21));
    __asm__ volatile("" : : "r"(v4),"r"(v5),"r"(v6),"r"(v7) : "memory");
    const auto hi=_mm_setr_epi32(static_cast<int>(v4),static_cast<int>(v5),static_cast<int>(v6),static_cast<int>(v7));
    return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
}

template<bool Stream>
FC_AVX2 inline void direct_rgb24_block_run(const std::uint8_t* table,const std::uint8_t* source,
    std::uint8_t* destination,std::size_t remaining) noexcept {
    const std::size_t initial=remaining>341?1024:remaining*3;
    for(std::size_t offset=0;offset<initial;offset+=64)
        _mm_prefetch(reinterpret_cast<const char*>(source+offset),_MM_HINT_NTA);
    for(;remaining&&(reinterpret_cast<std::uintptr_t>(destination)&63);source+=3,destination+=3,--remaining)
        store_rgb(destination,rgb32(table+std::size_t(rgb32(source))*3));
    bool streamed=false;
    for(;remaining>=72;source+=192,destination+=192,remaining-=64) {
        if(remaining>=406) {
            const auto* future=source+1024;
            _mm_prefetch(reinterpret_cast<const char*>(future),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+64),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+128),_MM_HINT_NTA);
            _mm_prefetch(reinterpret_cast<const char*>(future+191),_MM_HINT_NTA);
        }
        /* 最后一个宽输入读取末端为193B，始终在至少216B的剩余输入内。 */
        const auto r0=direct_pack<0>(direct_rgb24_read_wide(table,source));
        const auto r1=direct_pack<1>(direct_rgb24_read_wide(table,source+24));
        const auto r2=direct_pack<2>(direct_rgb24_read_wide(table,source+48));
        const auto r3=direct_pack<3>(direct_rgb24_read_wide(table,source+72));
        const auto r4=direct_pack<0>(direct_rgb24_read_wide(table,source+96));
        const auto r5=direct_pack<1>(direct_rgb24_read_wide(table,source+120));
        const auto r6=direct_pack<2>(direct_rgb24_read_wide(table,source+144));
        const auto r7=direct_pack<3>(direct_rgb24_read_wide(table,source+168));
        if constexpr(Stream) {
            direct_output32_stream(destination,r0,r1,r2,r3);
            direct_output32_stream(destination+96,r4,r5,r6,r7);
            streamed=true;
        } else {
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination),_mm256_blend_epi32(r0,r1,0xc0));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+32),_mm256_permute2x128_si256(r1,r2,0x30));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+64),_mm256_blend_epi32(r3,r2,0x03));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+96),_mm256_blend_epi32(r4,r5,0xc0));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+128),_mm256_permute2x128_si256(r5,r6,0x30));
            _mm256_store_si256(reinterpret_cast<__m256i*>(destination+160),_mm256_blend_epi32(r7,r6,0x03));
        }
    }
    if(streamed)_mm_sfence();
    for(;remaining>=40;source+=96,destination+=96,remaining-=32) {
        const auto r0=direct_pack<0>(direct_rgb24_read_wide(table,source));
        const auto r1=direct_pack<0>(direct_rgb24_read_wide(table,source+24));
        const auto r2=direct_pack<0>(direct_rgb24_read_wide(table,source+48));
        const auto r3=direct_pack<0>(direct_rgb24_read_wide(table,source+72));
        direct_output32(destination,r0,r1,r2,r3);
    }
    for(;remaining>=8;source+=24,destination+=24,remaining-=8)
        direct_output8(destination,direct_rgb24_read_exact(table,source));
    for(;remaining;source+=3,destination+=3,--remaining)
        store_rgb(destination,rgb32(table+std::size_t(rgb32(source))*3));
}

/* 回归复测可显式重放旧核；两个版本共享模型/表格式与资源需求。 */
FC_AVX2 inline void direct_rgb24_run(const std::uint8_t* table,const std::uint8_t* src,
    std::uint8_t* dst,std::size_t pixels) noexcept {
#if defined(FLASH_CHROMA_RGB24_LEGACY) && FLASH_CHROMA_RGB24_LEGACY
    direct_rgb24_gather_run(table,src,dst,pixels);
#elif defined(FLASH_CHROMA_RGB24_STREAMING) && FLASH_CHROMA_RGB24_STREAMING
    direct_rgb24_block_run<true>(table,src,dst,pixels);
#else
    direct_rgb24_block_run<false>(table,src,dst,pixels);
#endif
}

FC_AVX2 inline void direct8(const std::uint8_t* table,const std::uint32_t* palette,Representation rep,
    const std::uint8_t* src,std::uint8_t* dst,std::size_t pixels) noexcept {
    if(rep==Representation::DirectRGB24) {direct_rgb24_run(table,src,dst,pixels);return;}
    /* GCC/Clang已初始化的CPU能力位：每块检查一次，不在八像素循环里做CPUID。 */
#if defined(__x86_64__)
    if(__builtin_cpu_supports("bmi")) {
        if(rep==Representation::DirectU8)direct_palette_run_bmi<false>(table,palette,src,dst,pixels);
        else direct_palette_run_bmi<true>(table,palette,src,dst,pixels);
        return;
    }
#endif
    if(rep==Representation::DirectU8)direct_palette_run<false>(table,palette,src,dst,pixels);
    else direct_palette_run<true>(table,palette,src,dst,pixels);
}

#undef FC_DIRECT_BMI
