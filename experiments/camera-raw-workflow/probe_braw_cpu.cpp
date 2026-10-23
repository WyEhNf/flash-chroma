// 只读核对官方BRAW API版本、CPU配置和素材身份；不提交任何帧解码任务。
#include "BlackmagicRawAPI.h"
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
static void ok(HRESULT code) { if (FAILED(code)) throw std::runtime_error(std::to_string(code)); }
int main(int argc, char** argv) {
    try {
        if (argc != 2) return 2;
        auto factory = CreateBlackmagicRawFactoryInstance();
        if (!factory) throw std::runtime_error("官方factory不可用");
        IBlackmagicRaw* codec = nullptr; ok(factory->CreateCodec(&codec));
        IBlackmagicRawConfiguration* config = nullptr;
        IBlackmagicRawConfigurationEx* extra = nullptr;
        ok(codec->QueryInterface(IID_IBlackmagicRawConfiguration, reinterpret_cast<void**>(&config)));
        ok(codec->QueryInterface(IID_IBlackmagicRawConfigurationEx, reinterpret_cast<void**>(&extra)));
        ok(config->SetCPUThreads(4)); ok(config->SetPipeline(blackmagicRawPipelineCPU, nullptr, nullptr));
        ok(extra->SetInstructionSet(blackmagicRawInstructionSetAVX2));
        uint32_t threads = 0; BlackmagicRawPipeline pipeline{}; BlackmagicRawInstructionSet instruction{};
        BRawStr version = nullptr, camera = nullptr;
        ok(config->GetCPUThreads(&threads)); ok(config->GetPipeline(&pipeline, nullptr, nullptr));
        ok(extra->GetInstructionSet(&instruction)); ok(config->GetVersion(&version));
        IBlackmagicRawClip* clip = nullptr; ok(codec->OpenClip(argv[1], &clip)); ok(clip->GetCameraType(&camera));
        std::cout << "{\"sdk_version\":" << std::quoted(version) << ",\"camera\":" << std::quoted(camera)
                  << ",\"threads\":" << threads << ",\"cpu_pipeline_confirmed\":" << (pipeline == blackmagicRawPipelineCPU ? "true" : "false")
                  << ",\"avx2_confirmed\":" << (instruction == blackmagicRawInstructionSetAVX2 ? "true" : "false") << "}\n";
        clip->Release(); extra->Release(); config->Release(); codec->Release(); factory->Release();
        return threads == 4 && pipeline == blackmagicRawPipelineCPU && instruction == blackmagicRawInstructionSetAVX2 ? 0 : 1;
    } catch (const std::exception& exc) { std::cerr << exc.what() << '\n'; return 1; }
}
