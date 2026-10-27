// 宿主验证适配层：分配器与FFI只在此处，部署用头文件不依赖本文件。
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
#include <cstdint>
#include <new>
#include <vector>

#if defined(_WIN32)
#define FC_BRIDGE_API __declspec(dllexport)
#else
#define FC_BRIDGE_API __attribute__((visibility("default")))
#endif

struct fc_bridge_config {
    uint32_t target, backend, representation, threads;
    uint64_t block_pixels, max_workspace_bytes;
};
struct fc_bridge_bytes { const uint8_t* data; size_t size; };
struct fc_bridge_info {
    uint64_t persistent_bytes, temporary_bytes, arena_bytes, model_bytes;
    uint64_t alignment, object_bytes;
    uint32_t selected_backend, palette_entries;
};
struct fc_bridge_handle {
    fc::Runtime runtime;
    std::vector<uint8_t> arena;
};
static fc::RuntimeConfig config_from(const fc_bridge_config& source) {
    fc::RuntimeConfig value;
    value.target = static_cast<fc::Target>(source.target);
    value.backend = static_cast<fc::Backend>(source.backend);
    value.representation = static_cast<fc::Representation>(source.representation);
    value.threads = source.threads;
    value.block_pixels = static_cast<size_t>(source.block_pixels);
    value.max_workspace_bytes = static_cast<size_t>(source.max_workspace_bytes);
    return value;
}
static fc::ModelBundle bundle_from(const fc_bridge_bytes* models, const fc_bridge_bytes* sidecars) {
    fc::ModelBundle result{};
    for (size_t i=0;i<4;++i) {
        result.models[i]={models[i].data,models[i].size};
        result.sidecars[i]={sidecars[i].data,sidecars[i].size};
    }
    return result;
}
static void info_from(fc_bridge_info* output, const fc::Requirements& req,
                      uint32_t backend, uint32_t palette) {
    if (!output) return;
    *output = {req.persistent_bytes,req.temporary_bytes,req.arena_bytes,req.model_bytes,
               req.alignment,req.object_bytes,backend,palette};
}
extern "C" {
FC_BRIDGE_API uint32_t fc_bridge_capabilities() { return fc::available_backends(); }
FC_BRIDGE_API int fc_bridge_query(const fc_bridge_bytes* models,const fc_bridge_bytes* sidecars,
                                 const fc_bridge_config* config,fc_bridge_info* output) {
    if (!models || !sidecars || !config || !output) return -1;
    if(config->block_pixels>SIZE_MAX || config->max_workspace_bytes>SIZE_MAX)return 5;
    fc::Requirements req{};
    const auto status=fc::Runtime::requirements(bundle_from(models,sidecars),config_from(*config),&req);
    info_from(output,req,0,0);
    return static_cast<int>(status);
}
FC_BRIDGE_API int fc_bridge_create(const fc_bridge_bytes* models,const fc_bridge_bytes* sidecars,
                                  const fc_bridge_config* config,void** output,fc_bridge_info* info) {
    if (!models || !sidecars || !config || !output) return -1;
    if(config->block_pixels>SIZE_MAX || config->max_workspace_bytes>SIZE_MAX)return 5;
    *output=nullptr;
    fc::Requirements req{};
    const auto bundle=bundle_from(models,sidecars);
    const auto selected=config_from(*config);
    auto status=fc::Runtime::requirements(bundle,selected,&req);
    if (static_cast<int>(status)!=0) return static_cast<int>(status);
    auto* handle=new(std::nothrow) fc_bridge_handle;
    if (!handle) return -2;
    try { handle->arena.resize(req.arena_bytes); }
    catch (const std::bad_alloc&) { delete handle; return -2; }
    status=fc::Runtime::prepare(bundle,selected,
        fc::Workspace{handle->arena.data(),handle->arena.size()},&handle->runtime);
    if (static_cast<int>(status)!=0) { delete handle; return static_cast<int>(status); }
    info_from(info,handle->runtime.resources(),static_cast<uint32_t>(handle->runtime.selected_backend()),
              static_cast<uint32_t>(handle->runtime.palette_entries()));
    *output=handle;
    return 0;
}
FC_BRIDGE_API int fc_bridge_apply(void* handle,const uint8_t* source,size_t source_bytes,
    size_t source_stride,uint8_t* destination,size_t destination_bytes,size_t destination_stride,
    size_t width,size_t height) {
    if (!handle) return -1;
    return static_cast<int>(static_cast<fc_bridge_handle*>(handle)->runtime.apply(source,source_bytes,
        source_stride,destination,destination_bytes,destination_stride,width,height));
}
FC_BRIDGE_API void fc_bridge_destroy(void* handle) { delete static_cast<fc_bridge_handle*>(handle); }
}
