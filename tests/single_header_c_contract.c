/* C99 单头合同：混合网格、分输出坐标、独立 u64 参考及拒绝不写。
 * 仅测试夹具使用静态大数组和 stdio；运行库不依赖它们。
 */
#define FC_C_IMPLEMENTATION
#include "flash_chroma_c.h"
#include <stdio.h>
#include <string.h>

#define MAX_MODEL (16u + 12u*33u + 3840u + 3u*33u*33u*33u)
#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "C99 单头合同失败，行号 %d\n", __LINE__); return 1; } } while (0)

static uint8_t blobs[4][MAX_MODEL+3];
static uint8_t sidecars[4][FC_C_SIDECAR_BYTES+3];
static fc_model models[4];
static fc_chain chain;
static uint8_t input[3u*65537u], output[3u*65537u], expected[3u*65537u];
static size_t blob_sizes[4];
static unsigned comparisons;

static void write32(uint8_t *p, uint32_t value)
{
    unsigned i;
    for (i=0; i<4; ++i) p[i]=(uint8_t)(value>>(8u*i));
}

static uint32_t read32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1]<<8) | ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24);
}

static uint32_t coordinate(uint32_t i, uint32_t m, unsigned axis)
{
    uint32_t q=i*255u/(m-1u);
    return axis==1 ? (q+i*i*255u/((m-1u)*(m-1u)))/2u : q;
}

static uint32_t float_bits(uint32_t value)
{
    uint32_t exponent=150u;
    if (!value) return 0;
    while (value<(1u<<23)) { value<<=1; --exponent; }
    return (exponent<<23) | (value&0x7fffffu);
}

static size_t make_model(uint8_t *p, uint8_t *side, uint32_t m, uint32_t seed)
{
    const size_t axis=16u+12u*m, size=axis+3840u+3u*m*m*m;
    unsigned a,c,x;
    size_t i;
    memset(p,0,size);
    p[0]='S'; p[1]='L'; p[2]='U'; p[3]='T';
    write32(p+4,1); write32(p+8,m);
    for (a=0; a<3; ++a) {
        for (i=0; i<m; ++i) write32(p+16u+4u*(a*m+i),float_bits(coordinate((uint32_t)i,m,a)));
        for (x=0; x<256; ++x) {
            uint32_t cell=0,lo,hi,f;
            while (cell<m-2u && coordinate(cell+1u,m,a)<=x) ++cell;
            lo=coordinate(cell,m,a); hi=coordinate(cell+1u,m,a);
            f=((x-lo)*65536u+(hi-lo)/2u)/(hi-lo);
            p[axis+a*256u+x]=(uint8_t)cell;
            write32(p+axis+768u+4u*(a*256u+x),f);
            for (c=0; c<3; ++c) {
                uint32_t change=(c+1u)*4096u+(a+1u)*257u;
                uint32_t cf=(x&1u) ? (f>change ? f-change : 0u) :
                    (f+change<65536u ? f+change : 65536u);
                write32(side+4u*((c*3u+a)*256u+x),cf);
            }
        }
    }
    for (i=axis+3840u; i<size; ++i) {
        seed=seed*1664525u+1013904223u;
        p[i]=(uint8_t)(seed>>24);
    }
    return size;
}

/* 参考实现使用独立轴排名和 u64 累加，不调用生产排序网络或单像素函数。 */
static void oracle_pixel(const fc_chain *pipeline, const uint8_t *src, uint8_t *dst)
{
    uint8_t colour[3];
    unsigned s,c,a,b;
    colour[0]=src[0]; colour[1]=src[1]; colour[2]=src[2];
    for (s=0; s<4; ++s) {
        const fc_model *m=pipeline->models[s];
        const size_t stride[3]={(size_t)m->m*m->m,m->m,1};
        size_t base=0;
        uint8_t next[3];
        for (a=0; a<3; ++a) base+=m->index[a*256u+colour[a]]*stride[a];
        for (c=0; c<3; ++c) {
            uint32_t f[3], weight[4];
            unsigned rank[3], order[3];
            size_t vertex[4];
            uint64_t sum=32768;
            const uint8_t *fractions=m->sidecar.data ? m->sidecar.data+c*3072u : m->fraction_le;
            for (a=0; a<3; ++a) f[a]=read32(fractions+4u*(a*256u+colour[a]));
            for (a=0; a<3; ++a) {
                rank[a]=0;
                for (b=0; b<3; ++b)
                    if (f[b]>f[a] || (f[b]==f[a] && b<a)) ++rank[a];
                order[rank[a]]=a;
            }
            vertex[0]=base;
            for (a=0; a<3; ++a) vertex[a+1u]=vertex[a]+stride[order[a]];
            weight[0]=65536u-f[order[0]];
            weight[1]=f[order[0]]-f[order[1]];
            weight[2]=f[order[1]]-f[order[2]];
            weight[3]=f[order[2]];
            for (a=0; a<4; ++a) sum+=(uint64_t)weight[a]*m->nodes[3u*vertex[a]+c];
            next[c]=(uint8_t)(sum/65536u);
        }
        colour[0]=next[0]; colour[1]=next[1]; colour[2]=next[2];
    }
    dst[0]=colour[0]; dst[1]=colour[1]; dst[2]=colour[2];
}

static int initialize(unsigned side_mask)
{
    const fc_model *views[4];
    unsigned s;
    for (s=0; s<4; ++s) {
        fc_bytes blob={blobs[s]+1,blob_sizes[s]};
        fc_bytes side={(side_mask&(1u<<s)) ? sidecars[s]+1 : NULL,
            (side_mask&(1u<<s)) ? FC_C_SIDECAR_BYTES : 0u};
        CHECK(fc_model_init(&models[s],blob,side)==FC_OK);
        views[s]=&models[s];
    }
    CHECK(fc_chain_init(&chain,views)==FC_OK);
    return 0;
}

int main(void)
{
    const uint32_t sizes[4]={17,18,25,33};
    unsigned s,mode;
    size_t i,n;
    uint32_t seed=1907;
    uint8_t block[3u*257u+32u], snapshot[sizeof(block)];
    fc_bytes absent={NULL,0};
    for (s=0; s<4; ++s) blob_sizes[s]=make_model(blobs[s]+1,sidecars[s]+1,sizes[s],s+99u);
    for (i=0; i<sizeof(input); ++i) { seed=seed*1664525u+1013904223u; input[i]=(uint8_t)(seed>>24); }
    for (mode=0; mode<3; ++mode) {
        CHECK(initialize(mode==0 ? 0u : mode==1 ? 1u : 15u)==0);
        for (i=0; i<65537u; ++i) oracle_pixel(&chain,input+3u*i,expected+3u*i);
        CHECK(fc_apply_rgb8(&chain,input,sizeof(input),sizeof(input),output,sizeof(output),sizeof(output),65537u,1)==FC_OK);
        CHECK(memcmp(output,expected,sizeof(output))==0); ++comparisons;
        memcpy(output,input,sizeof(output));
        CHECK(fc_apply_rgb8(&chain,output,sizeof(output),sizeof(output),output,sizeof(output),sizeof(output),65537u,1)==FC_OK);
        CHECK(memcmp(output,expected,sizeof(output))==0); ++comparisons;
        for (n=0; n<=257u; ++n) {
            memset(block,0xad,sizeof(block));
            memcpy(block+1,input,n*3u);
            CHECK(fc_apply_rgb8(&chain,block+1,sizeof(block)-2,n*3u,block+1,sizeof(block)-2,n*3u,n,1)==FC_OK);
            CHECK(memcmp(block+1,expected,n*3u)==0);
            CHECK(block[0]==0xad && block[1+n*3u]==0xad); ++comparisons;
        }
        memset(block,0xad,sizeof(block));
        CHECK(fc_apply_rgb8(&chain,input,sizeof(input),31,block+1,sizeof(block)-1,35,9,5)==FC_OK);
        for (i=0; i<5; ++i) {
            size_t x;
            for (x=0; x<9; ++x) {
                uint8_t ref[3];
                oracle_pixel(&chain,input+i*31u+x*3u,ref);
                CHECK(memcmp(block+1+i*35u+x*3u,ref,3)==0);
            }
            CHECK(block[1+i*35u+27u]==0xad);
        }
        ++comparisons;
    }
    CHECK(fc_apply_rgb8(&chain,NULL,0,0,NULL,0,0,0,SIZE_MAX)==FC_OK);
    CHECK(fc_apply_rgb8(&chain,NULL,0,0,NULL,0,0,SIZE_MAX,0)==FC_OK);
    CHECK(fc_apply_rgb8(NULL,NULL,0,0,NULL,0,0,0,0)==FC_NULL);
    memset(block,0xa7,sizeof(block)); memcpy(snapshot,block,sizeof(block));
    CHECK(fc_apply_rgb8(&chain,block,sizeof(block),33,block+1,sizeof(block)-1,33,11,1)==FC_OVERLAP);
    CHECK(fc_apply_rgb8(&chain,input,sizeof(input),32,block,sizeof(block),33,11,1)==FC_SIZE);
    CHECK(fc_apply_rgb8(&chain,input,32,33,block,sizeof(block),33,11,1)==FC_SIZE);
    CHECK(fc_apply_rgb8(&chain,input,sizeof(input),33,block,sizeof(block),33,SIZE_MAX/3u+1u,1)==FC_OVERFLOW);
    CHECK(fc_apply_rgb8(&chain,input,sizeof(input),SIZE_MAX,block,sizeof(block),33,11,2)==FC_OVERFLOW);
    CHECK(fc_apply_rgb8(&chain,input,sizeof(input),33,blobs[0]+1,blob_sizes[0],33,11,1)==FC_OVERLAP);
    CHECK(fc_apply_rgb8(&chain,input,sizeof(input),33,sidecars[0]+1,FC_C_SIDECAR_BYTES,33,11,1)==FC_OVERLAP);
    CHECK(memcmp(block,snapshot,sizeof(block))==0);
    ++comparisons;
    {
        fc_model probe,saved;
        fc_bytes blob={blobs[0]+1,blob_sizes[0]};
        fc_bytes side={sidecars[0]+1,FC_C_SIDECAR_BYTES};
        const uint32_t axis=16u+12u*sizes[0];
        uint8_t original;
        CHECK(fc_model_init(&probe,blob,side)==FC_OK); saved=probe;
        for (n=0; n<blob.size; ++n) {
            fc_bytes truncated={blob.data,n};
            CHECK(fc_model_init(&probe,truncated,side)!=FC_OK);
            CHECK(memcmp(&probe,&saved,sizeof(probe))==0);
        }
        ++blob.size;
        CHECK(fc_model_init(&probe,blob,side)==FC_SIZE); --blob.size;
        side.size=FC_C_SIDECAR_BYTES-1u;
        CHECK(fc_model_init(&probe,blob,side)==FC_SIZE); ++side.size;
        write32(sidecars[0]+1,65537u);
        CHECK(fc_model_init(&probe,blob,side)==FC_RANGE);
        write32(sidecars[0]+1,0);
        original=blobs[0][1u+axis]; blobs[0][1u+axis]=255u;
        CHECK(fc_model_init(&probe,blob,absent)==FC_RANGE); blobs[0][1u+axis]=original;
        write32(blobs[0]+1u+axis+768u,65537u);
        CHECK(fc_model_init(&probe,blob,absent)==FC_RANGE); write32(blobs[0]+1u+axis+768u,0);
        write32(blobs[0]+1u+16u,0x7fc00000u);
        CHECK(fc_model_init(&probe,blob,absent)==FC_FORMAT); write32(blobs[0]+1u+16u,0);
        CHECK(memcmp(&probe,&saved,sizeof(probe))==0); ++comparisons;
    }
    printf("C99 单头合同通过：%u 组检查，三种侧表配置各65537像素及0..257短尾。\n",comparisons);
    return 0;
}
