/* 独立C99头文件的差分验证入口；不依赖C++运行库。 */
#define FC_C_IMPLEMENTATION
#include "flash_chroma_c.h"
#if defined(_WIN32)
#define FC_BRIDGE_API __declspec(dllexport)
#else
#define FC_BRIDGE_API __attribute__((visibility("default")))
#endif
FC_BRIDGE_API int fc_c_bridge_apply(const fc_bytes* blobs,const fc_bytes* sidecars,
    const uint8_t* source,size_t source_bytes,size_t source_stride,uint8_t* destination,
    size_t destination_bytes,size_t destination_stride,size_t width,size_t height) {
    fc_model models[4];
    const fc_model* pointers[4];
    fc_chain chain;
    size_t i;
    fc_status status;
    if (!blobs || !sidecars) return -1;
    for (i=0;i<4;++i) {
        status=fc_model_init(&models[i],blobs[i],sidecars[i]);
        if (status!=FC_OK) return (int)status;
        pointers[i]=&models[i];
    }
    status=fc_chain_init(&chain,pointers);
    if (status!=FC_OK) return (int)status;
    return (int)fc_apply_rgb8(&chain,source,source_bytes,source_stride,destination,
                             destination_bytes,destination_stride,width,height);
}
