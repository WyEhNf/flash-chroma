/* Freestanding AArch64 Linux verification harness, not a deployment runtime.
 * stdout is two consecutive raw RGB8 cubes (specialized, then generic).
 * The host hashes each stream against frozen independent native evidence.
 * Linux syscall numbers are read from asm-generic/unistd.h in the recorded WSL.
 * Inline assembly here only enters the Linux kernel; LUT arithmetic stays C99.
 */
#include "jshc_portable.h"

#if !defined(__aarch64__)
#error This harness requires AArch64 Linux user-mode execution.
#endif

extern const uint8_t model_blob_0[], model_blob_0_end[];
extern const uint8_t model_blob_1[], model_blob_1_end[];
extern const uint8_t model_blob_2[], model_blob_2_end[];
extern const uint8_t model_blob_3[], model_blob_3_end[];

void *memcpy(void *destination, const void *source, size_t count) {
    uint8_t *d=(uint8_t *)destination; const uint8_t *s=(const uint8_t *)source;
    size_t i; for (i=0;i<count;++i) d[i]=s[i]; return destination;
}
void *memset(void *destination, int value, size_t count) {
    uint8_t *d=(uint8_t *)destination;
    size_t i; for (i=0;i<count;++i) d[i]=(uint8_t)value; return destination;
}

static long linux_write(const uint8_t *data, size_t count) {
    register long x0 __asm__("x0")=1;
    register const uint8_t *x1 __asm__("x1")=data;
    register size_t x2 __asm__("x2")=count;
    register long x8 __asm__("x8")=64;
    __asm__ volatile("svc 0" : "+r"(x0) : "r"(x1),"r"(x2),"r"(x8) : "memory","cc");
    return x0;
}

static void finish(long status) {
    register long x0 __asm__("x0")=status;
    register long x8 __asm__("x8")=93;
    __asm__ volatile("svc 0" : : "r"(x0),"r"(x8) : "memory","cc");
    __builtin_unreachable();
}

static void write_all(const uint8_t *data, size_t count) {
    while (count) {
        long written=linux_write(data,count);
        if (written==-4) continue; /* EINTR */
        if (written<=0 || (size_t)written>count) finish(90);
        data+=(size_t)written; count-=(size_t)written;
    }
}

#define BLOCK_PIXELS 1024u
static jshc_p_model models[4];
static jshc_p_chain chains[2];
static uint8_t input[BLOCK_PIXELS*3u], output[BLOCK_PIXELS*3u];

void _start(void) {
    const uint8_t *blobs[4]={model_blob_0,model_blob_1,model_blob_2,model_blob_3};
    const uint8_t *ends[4]={model_blob_0_end,model_blob_1_end,model_blob_2_end,model_blob_3_end};
    const jshc_p_model *views[4];
    uint32_t base,i,variant;
    unsigned stage;
    for (stage=0;stage<4;++stage) {
        jshc_p_status status=jshc_p_model_prepare(&models[stage],blobs[stage],(size_t)((uintptr_t)ends[stage]-(uintptr_t)blobs[stage]));
        if (status!=JSHC_P_OK) finish(10+(long)status);
        views[stage]=&models[stage];
    }
    for (variant=0;variant<2;++variant) {
        jshc_p_status status=jshc_p_chain_prepare(&chains[variant],views,variant ? JSHC_P_FORCE_GENERIC : 0u);
        if (status!=JSHC_P_OK) finish(30+(long)status);
    }
    for (variant=0;variant<2;++variant) {
        for (base=0;base<UINT32_C(16777216);base+=BLOCK_PIXELS) {
            jshc_p_status status;
            for (i=0;i<BLOCK_PIXELS;++i) {
                uint32_t key=base+i;
                input[3u*i]=(uint8_t)(key>>16);
                input[3u*i+1u]=(uint8_t)(key>>8);
                input[3u*i+2u]=(uint8_t)key;
            }
            status=jshc_p_apply_rgb8(&chains[variant],input,sizeof(input),sizeof(input),
                output,sizeof(output),sizeof(output),BLOCK_PIXELS,1);
            if (status!=JSHC_P_OK) finish(50+(long)status);
            write_all(output,sizeof(output));
        }
    }
    finish(0);
}
