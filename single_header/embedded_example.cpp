// 本文件与flash_chroma_framework.hpp即可由C++17工具链编译；无需项目.c/.h或Python。
// 使用设备对应的C++工具链；裸机/freestanding目标自动识别，无需开启SIMD构建参数。
// 仅在一个.cpp首次include前定义IMPLEMENTATION；可选EMBEDDED宏须在各翻译单元一致。
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma_framework.hpp"

static_assert(fc::is_embedded(), "应使用嵌入式构建配置");
static_assert(FLASH_CHROMA_ENABLE_AVX2 == 0 && FLASH_CHROMA_ENABLE_DIRECT == 0 &&
              FLASH_CHROMA_ENABLE_OPENMP == 0 && FLASH_CHROMA_ENABLE_PREPARE_CACHE == 0,
              "嵌入式构建不应包含桌面加速依赖");

namespace flash_chroma_embedded_example {

// 四个models指向预先压缩的SLUT字节数组，可放只读ROM；它们须比runtime活得更久。
// 可在PC上用同一hpp的桌面模式生成模型，再以const字节数组编入.cpp。
fc::Status prepare(const fc::ModelBundle& models, fc::Runtime& runtime) noexcept {
    fc::RuntimeConfig config;
    config.backend = fc::Backend::Scalar;
    config.representation = fc::Representation::Sparse;
    config.threads = 1;
    config.max_workspace_bytes = 0;
    fc::Requirements resources;
    const auto status = fc::Runtime::requirements(models, config, &resources);
    if (status != fc::Status::Ok) return status;
    if (resources.arena_bytes != 0) return fc::Status::Budget;
    return fc::Runtime::prepare(models, config, {nullptr, 0}, &runtime);
}

// 输入/输出由调用者持有，支持行步长；执行四级RGB8/Q16映射，不分配堆或执行文件I/O。
fc::Status apply(const fc::Runtime& runtime,
                 const std::uint8_t* input, std::size_t input_bytes, std::size_t input_stride,
                 std::uint8_t* output, std::size_t output_bytes, std::size_t output_stride,
                 std::size_t width, std::size_t height) noexcept {
    return runtime.apply(input, input_bytes, input_stride,
                         output, output_bytes, output_stride, width, height);
}

} // namespace flash_chroma_embedded_example
