// 本地调用官方BRAW 3.3 API；头文件和运行库由操作者提供，不随项目发布。
#include "BlackmagicRawAPI.h"
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

static void check(HRESULT value, const char* operation) {
    if (FAILED(value)) throw std::runtime_error(std::string(operation) + ":" + std::to_string(value));
}
static void string_attribute(IBlackmagicRawClipProcessingAttributes* attributes,
                             BlackmagicRawClipProcessingAttribute key, const char* text) {
    VARIANT value{};
    value.vt = blackmagicRawVariantTypeString;
    value.bstrVal = strdup(text);
    auto result = attributes->SetClipAttribute(key, &value);
    VariantClear(&value);
    check(result, text);
}
static void attribute(IBlackmagicRawClipProcessingAttributes* attributes,
                      BlackmagicRawClipProcessingAttribute key, const char* name) {
    VARIANT value{};
    check(attributes->GetClipAttribute(key, &value), name);
    std::cout << "\"" << name << "\":";
    if (value.vt == blackmagicRawVariantTypeString) std::cout << std::quoted(value.bstrVal);
    else if (value.vt == blackmagicRawVariantTypeU16) std::cout << value.uiVal;
    else std::cout << "null";
    VariantClear(&value);
}
class Callback final : public IBlackmagicRawCallback {
public:
    IBlackmagicRawClipProcessingAttributes* attributes = nullptr;
    std::filesystem::path output;
    uint64_t index = 0;
    std::atomic<int> failed{0};
    uint64_t completed = 0;
    double write_seconds = 0;
    HRESULT QueryInterface(REFIID, LPVOID*) override { return E_NOINTERFACE; }
    ULONG AddRef() override { return 1; }
    ULONG Release() override { return 1; }
    void ReadComplete(IBlackmagicRawJob* job, HRESULT result, IBlackmagicRawFrame* frame) override {
        try {
            check(result, "ReadComplete");
            check(frame->SetResolutionScale(blackmagicRawResolutionScaleFull), "full_resolution");
            check(frame->SetResourceFormat(blackmagicRawResourceFormatRGBF32), "RGBF32");
            IBlackmagicRawJob* process = nullptr;
            check(frame->CreateJobDecodeAndProcessFrame(attributes, nullptr, &process), "decode_process");
            check(process->Submit(), "submit_process");
        } catch (const std::exception& exc) { std::cerr << exc.what() << '\n'; failed = 1; }
        job->Release();
    }
    void ProcessComplete(IBlackmagicRawJob* job, HRESULT result, IBlackmagicRawProcessedImage* image) override {
        try {
            check(result, "ProcessComplete");
            uint32_t width = 0, height = 0, bytes = 0;
            void* pointer = nullptr;
            BlackmagicRawResourceFormat format{};
            BlackmagicRawResourceType type{};
            check(image->GetWidth(&width), "width"); check(image->GetHeight(&height), "height");
            check(image->GetResource(&pointer), "resource");
            check(image->GetResourceFormat(&format), "format");
            check(image->GetResourceType(&type), "type");
            check(image->GetResourceSizeBytes(&bytes), "bytes");
            if (format != blackmagicRawResourceFormatRGBF32 || type != blackmagicRawResourceTypeBufferCPU
                || !pointer || uint64_t(bytes) != uint64_t(width) * height * 12)
                throw std::runtime_error("官方返回资源不符合RGBF32紧密CPU合同");
            const auto start = std::chrono::steady_clock::now();
            char name[48]; std::snprintf(name, sizeof(name), "frame-%06llu.rgbf32", static_cast<unsigned long long>(index));
            auto path = output / name;
            if (std::filesystem::exists(path)) throw std::runtime_error("保留已有帧");
            FILE* stream = std::fopen(path.c_str(), "wb");
            if (!stream) throw std::runtime_error("输出帧打开失败");
            const auto written = std::fwrite(pointer, 1, bytes, stream);
            const auto closed = std::fclose(stream);
            if (written != bytes || closed) throw std::runtime_error("输出帧写入失败");
            write_seconds += std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
            ++completed;
        } catch (const std::exception& exc) { std::cerr << exc.what() << '\n'; failed = 1; }
        job->Release();
    }
    void DecodeComplete(IBlackmagicRawJob*, HRESULT) override {}
    void TrimProgress(IBlackmagicRawJob*, float) override {}
    void TrimComplete(IBlackmagicRawJob*, HRESULT) override {}
    void SidecarMetadataParseWarning(IBlackmagicRawClip*, BRawStr, uint32_t, BRawStr) override { failed = 1; }
    void SidecarMetadataParseError(IBlackmagicRawClip*, BRawStr, uint32_t, BRawStr) override { failed = 1; }
    void PreparePipelineComplete(void*, HRESULT result) override { if (FAILED(result)) failed = 1; }
};
int main(int argc, char** argv) {
    try {
        if (argc != 4) throw std::runtime_error("参数：输入BRAW 输出新目录 帧数；0仅检查，-1全部帧");
        auto factory = CreateBlackmagicRawFactoryInstance();
        if (!factory) throw std::runtime_error("官方factory创建失败");
        IBlackmagicRaw* codec = nullptr; check(factory->CreateCodec(&codec), "codec");
        IBlackmagicRawConfiguration* config = nullptr;
        check(codec->QueryInterface(IID_IBlackmagicRawConfiguration, reinterpret_cast<void**>(&config)), "configuration");
        check(config->SetPipeline(blackmagicRawPipelineCPU, nullptr, nullptr), "cpu_pipeline");
        check(config->SetCPUThreads(4), "four_threads");
        IBlackmagicRawConfigurationEx* extra = nullptr;
        check(codec->QueryInterface(IID_IBlackmagicRawConfigurationEx, reinterpret_cast<void**>(&extra)), "configuration_ex");
        check(extra->SetInstructionSet(blackmagicRawInstructionSetAVX2), "AVX2");
        IBlackmagicRawClip* clip = nullptr; check(codec->OpenClip(argv[1], &clip), "open_clip");
        uint32_t width = 0, height = 0; uint64_t frames = 0; float fps = 0;
        check(clip->GetWidth(&width), "width"); check(clip->GetHeight(&height), "height");
        check(clip->GetFrameCount(&frames), "count"); check(clip->GetFrameRate(&fps), "fps");
        IBlackmagicRawClipProcessingAttributes* attributes = nullptr;
        check(clip->CloneClipProcessingAttributes(&attributes), "attributes");
        const long long requested = std::stoll(argv[3]);
        if (requested != 0) {
            VARIANT gen{}; gen.vt = blackmagicRawVariantTypeU16; gen.uiVal = 5;
            check(attributes->SetClipAttribute(blackmagicRawClipProcessingAttributeColorScienceGen, &gen), "generation5");
            string_attribute(attributes, blackmagicRawClipProcessingAttributeGamut, "Blackmagic Design");
            string_attribute(attributes, blackmagicRawClipProcessingAttributeGamma, "Blackmagic Design Film");
            string_attribute(attributes, blackmagicRawClipProcessingAttributePost3DLUTMode, "Disabled");
        }
        std::cout << "{\"width\":" << width << ",\"height\":" << height << ",\"frames\":" << frames << ",\"fps\":" << fps << ",";
        attribute(attributes, blackmagicRawClipProcessingAttributeColorScienceGen, "color_science_gen"); std::cout << ',';
        attribute(attributes, blackmagicRawClipProcessingAttributeGamma, "gamma"); std::cout << ',';
        attribute(attributes, blackmagicRawClipProcessingAttributeGamut, "gamut"); std::cout << ',';
        attribute(attributes, blackmagicRawClipProcessingAttributePost3DLUTMode, "post_lut");
        Callback callback; callback.attributes = attributes; callback.output = argv[2];
        check(codec->SetCallback(&callback), "callback");
        if (requested != 0 && !std::filesystem::create_directories(callback.output))
            throw std::runtime_error("输出目录必须为新目录");
        const uint64_t count = requested < 0 ? frames : std::min(frames, uint64_t(requested));
        const auto start = std::chrono::steady_clock::now();
        for (uint64_t index = 0; index < count; ++index) {
            callback.index = index;
            IBlackmagicRawJob* job = nullptr;
            check(clip->CreateJobReadFrame(index, &job), "read_job"); check(job->Submit(), "submit_read");
            check(codec->FlushJobs(), "flush");
            if (callback.failed || callback.completed != index + 1) throw std::runtime_error("帧流水线失败或未完整写入");
        }
        const double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
        std::cout << ",\"decoded_frames\":" << callback.completed << ",\"decode_and_write_seconds\":" << std::setprecision(12)
                  << seconds << ",\"write_seconds\":" << callback.write_seconds << "}\n";
        check(codec->SetCallback(nullptr), "clear_callback");
        attributes->Release(); clip->Release(); extra->Release(); config->Release(); codec->Release(); factory->Release();
        return 0;
    } catch (const std::exception& exc) { std::cerr << exc.what() << '\n'; return 1; }
}
