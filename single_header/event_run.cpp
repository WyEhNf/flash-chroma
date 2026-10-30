/* 独立比赛接入示例：只依赖标准库与交付hpp，读写连续RGB8，不做拟合或官方判分。 */
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"

#include <array>
#include <cerrno>
#include <charconv>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

struct Options {
    std::array<fs::path, 4> models{}, sidecars{};
    fs::path input, output, report;
    std::size_t width=1024, height=768, count=1;
    fc::RuntimeConfig config;
    bool help=false;
};

double milliseconds(Clock::time_point begin, Clock::time_point end=Clock::now()) {
    return std::chrono::duration<double, std::milli>(end-begin).count();
}

std::string quote(const std::string& value) {
    static constexpr char hex[]="0123456789abcdef";
    std::string result="\"";
    for(unsigned char c:value) {
        if(c=='"'||c=='\\') { result+='\\'; result+=static_cast<char>(c); }
        else if(c<32) { result+="\\u00"; result+=hex[c>>4]; result+=hex[c&15]; }
        else result+=static_cast<char>(c);
    }
    return result+'"';
}

std::size_t integer(const std::string& value,const std::string& flag) {
    std::uint64_t number=0;
    const auto parsed=std::from_chars(value.data(),value.data()+value.size(),number);
    if(parsed.ec!=std::errc{}||parsed.ptr!=value.data()+value.size()||
       number>std::numeric_limits<std::size_t>::max())
        throw std::invalid_argument(flag+"需要范围内的非负十进制整数");
    return static_cast<std::size_t>(number);
}

std::size_t product(std::size_t a,std::size_t b,const char* label) {
    if(b&&a>std::numeric_limits<std::size_t>::max()/b)
        throw std::overflow_error(std::string(label)+"尺寸乘积溢出");
    return a*b;
}

void require(fc::Status status,const char* label) {
    if(status!=fc::Status::Ok)
        throw std::runtime_error(std::string(label)+"失败（"+std::to_string(static_cast<unsigned>(status))+"）："+fc::status_string(status));
}

Options parse(int argc,char** argv) {
    Options o; std::set<std::string> seen;
    for(int at=1;at<argc;++at) {
        const std::string flag=argv[at];
        if(flag=="--help"||flag=="-h") { o.help=true; continue; }
        if(!seen.insert(flag).second)throw std::invalid_argument("参数重复："+flag);
        const auto next=[&]() -> std::string {
            if(++at>=argc)throw std::invalid_argument("参数缺少值："+flag);
            return argv[at];
        };
        if(flag=="--models"||flag=="--sidecars") {
            auto& values=flag=="--models"?o.models:o.sidecars;
            for(auto& path:values) {const auto value=next();if(value!="-")path=fs::path(value);}
        } else if(flag=="--input")o.input=next();
        else if(flag=="--output")o.output=next();
        else if(flag=="--report")o.report=next();
        else if(flag=="--width")o.width=integer(next(),flag);
        else if(flag=="--height")o.height=integer(next(),flag);
        else if(flag=="--count")o.count=integer(next(),flag);
        else if(flag=="--threads") {
            const auto n=integer(next(),flag);if(n<1||n>256)throw std::invalid_argument("线程数必须为1..256");
            o.config.threads=static_cast<unsigned>(n);
        } else if(flag=="--block-pixels")o.config.block_pixels=integer(next(),flag);
        else if(flag=="--workspace-bytes")o.config.max_workspace_bytes=integer(next(),flag);
        else if(flag=="--backend") {
            const auto value=next();
            if(value=="auto")o.config.backend=fc::Backend::Auto;
            else if(value=="scalar")o.config.backend=fc::Backend::Scalar;
            else if(value=="avx2")o.config.backend=fc::Backend::Avx2;
            else if(value=="avx512")o.config.backend=fc::Backend::Avx512;
            else throw std::invalid_argument("后端应为auto/scalar/avx2/avx512");
        } else if(flag=="--representation") {
            const auto value=next();
            if(value=="sparse")o.config.representation=fc::Representation::Sparse;
            else if(value=="direct_u8")o.config.representation=fc::Representation::DirectU8;
            else if(value=="direct_u16")o.config.representation=fc::Representation::DirectU16;
            else if(value=="direct_rgb24")o.config.representation=fc::Representation::DirectRGB24;
            else throw std::invalid_argument("表示应为sparse/direct_u8/direct_u16/direct_rgb24");
        } else if(flag=="--target") {
            const auto value=next();
            if(value=="desktop")o.config.target=fc::Target::Desktop;
            else if(value=="mobile")o.config.target=fc::Target::Mobile;
            else if(value=="embedded")o.config.target=fc::Target::Embedded;
            else if(value=="portable")o.config.target=fc::Target::Portable;
            else throw std::invalid_argument("目标应为desktop/mobile/embedded/portable");
        } else throw std::invalid_argument("未知参数："+flag);
    }
    if(o.help)return o;
    for(const auto& path:o.models)if(path.empty())throw std::invalid_argument("必须提供四个--models SLUT文件");
    if(o.input.empty()||o.output.empty())throw std::invalid_argument("必须提供--input和--output");
    if(!o.width||!o.height||!o.count||!o.config.block_pixels)
        throw std::invalid_argument("width/height/count/block-pixels必须大于0");
    return o;
}

void usage() {
    std::cout<<"独立单头RGB8四级执行示例（不做拟合、精度验收或官方判分）\n"
        "用法：flash_chroma_run --models stage1.slut stage2.slut stage3.slut stage4.slut\n"
        "  --input input.rgb --output output.rgb [--report run.json]\n"
        "  [--sidecars stage1.sidecar - - -] [--width 1024 --height 768 --count 1]\n"
        "  [--backend auto|scalar|avx2|avx512] [--threads 1] [--block-pixels 65536]\n"
        "  [--representation sparse|direct_u8|direct_u16|direct_rgb24]\n"
        "  [--workspace-bytes 字节预算] [--target desktop|mobile|embedded|portable]\n"
        "输入为按帧连续的行主序RGB8，无文件头或padding。sidecar必须给四槽，'-'为空。\n"
        "输出和报告均排他创建，拒绝覆盖；失败保留已经写出的片段。\n";
}

std::vector<std::uint8_t> read_model(const fs::path& path,bool sidecar) {
    if(!fs::is_regular_file(path))throw std::invalid_argument("模型不是普通文件："+path.u8string());
    const auto bytes=fs::file_size(path);
    constexpr std::uintmax_t max_slut=16+12*33+768+3072+33*33*33*3;
    if((sidecar&&bytes!=9216)||(!sidecar&&(!bytes||bytes>max_slut)))
        throw std::invalid_argument("模型或sidecar长度不符合交付格式："+path.u8string());
    std::vector<std::uint8_t> value(static_cast<std::size_t>(bytes));
    std::ifstream stream(path,std::ios::binary);
    if(!stream.read(reinterpret_cast<char*>(value.data()),static_cast<std::streamsize>(value.size())))
        throw std::runtime_error("读取模型失败："+path.u8string());
    return value;
}

/* C11标准的x模式提供排他创建，避免exists检查后的同名文件被覆盖。 */
class NewFile {
    std::FILE* file_=nullptr;
public:
    std::size_t bytes=0;
    NewFile()=default;
    NewFile(const NewFile&)=delete;
    NewFile& operator=(const NewFile&)=delete;
    ~NewFile(){if(file_)std::fclose(file_);}
    bool opened() const {return file_!=nullptr;}
    void open(const fs::path& path) {
        const auto parent=path.parent_path();if(!parent.empty())fs::create_directories(parent);
        file_=std::fopen(path.string().c_str(),"wbx");
        if(!file_)throw std::runtime_error("无法排他创建文件（现有文件不会覆盖）："+path.u8string()+"；"+std::strerror(errno));
    }
    void write(const void* data,std::size_t size) {
        const auto done=std::fwrite(data,1,size,file_);bytes+=done;
        if(done!=size)throw std::runtime_error("写入失败，已写出的片段保留");
    }
    void flush(){if(file_&&std::fflush(file_)!=0)throw std::runtime_error("输出刷新失败，已写出的片段保留");}
};

struct Measurement {
    std::size_t written=0,expected_bytes=0;
    double prepare_ms=0,apply_ms=0,io_ms=0,wall_ms=0;
    fc::Requirements resources{};
    fc::Backend backend=fc::Backend::Scalar;
    std::uint32_t palette=0;
    bool cache=false;
};

std::string report(const Options& o,const Measurement& m,const NewFile& output,bool completed,const std::string& error) {
    std::ostringstream json;json<<std::fixed<<std::setprecision(6);
    json<<"{\n  \"completed\": "<<(completed?"true":"false")
        <<",\n  \"error\": "<<(error.empty()?"null":quote(error))
        <<",\n  \"width\": "<<o.width<<",\n  \"height\": "<<o.height
        <<",\n  \"frames_requested\": "<<o.count<<",\n  \"frames_written\": "<<m.written
        <<",\n  \"input\": "<<quote(fs::absolute(o.input).u8string())
        <<",\n  \"output\": "<<quote(fs::absolute(o.output).u8string())
        <<",\n  \"input_bytes_expected\": "<<m.expected_bytes<<",\n  \"output_bytes_written\": "<<output.bytes
        <<",\n  \"models\": [";
    for(std::size_t i=0;i<4;++i)json<<(i?", ":"")<<quote(fs::absolute(o.models[i]).u8string());
    json<<"],\n  \"sidecars\": [";
    for(std::size_t i=0;i<4;++i)json<<(i?", ":"")<<(o.sidecars[i].empty()?"null":quote(fs::absolute(o.sidecars[i]).u8string()));
    json<<"],\n  \"config\": {\"target\": "<<static_cast<unsigned>(o.config.target)
        <<", \"backend_requested\": "<<static_cast<unsigned>(o.config.backend)
        <<", \"backend_selected\": "<<static_cast<unsigned>(m.backend)
        <<", \"representation\": "<<static_cast<unsigned>(o.config.representation)
        <<", \"threads_requested\": "<<o.config.threads<<", \"block_pixels\": "<<o.config.block_pixels
        <<", \"max_workspace_bytes\": "<<o.config.max_workspace_bytes<<"},\n"
        <<"  \"resources\": {\"model_bytes\": "<<m.resources.model_bytes
        <<", \"persistent_bytes\": "<<m.resources.persistent_bytes<<", \"temporary_bytes\": "<<m.resources.temporary_bytes
        <<", \"arena_bytes\": "<<m.resources.arena_bytes<<", \"object_bytes\": "<<m.resources.object_bytes
        <<", \"palette_entries\": "<<m.palette<<", \"prepared_with_suffix_cache\": "<<(m.cache?"true":"false")<<"},\n"
        <<"  \"timings_ms\": {\"prepare\": "<<m.prepare_ms<<", \"apply_only_sum\": "<<m.apply_ms
        <<", \"raw_io_sum\": "<<m.io_ms<<", \"whole_wall\": "<<m.wall_ms<<"},\n"
        <<"  \"available_capabilities\": "<<fc::available_backends()<<",\n"
        <<"  \"scope\": "<<quote("按帧流式执行；prepare只计Runtime::prepare，apply_only_sum仅累计映射调用；raw_io_sum含raw读写与末尾刷新；whole_wall从参数解析后到输出刷新，含检查、模型读取、分配、准备及raw读写，不含本JSON写出。")<<",\n"
        <<"  \"quality_verified\": false,\n  \"official_score_available\": false,\n"
        <<"  \"note\": "<<quote("本入口不读取密集源LUT、不拟合、不计算色差；图像为RGB8，保持四级模型与每级Q16 half-up。模型/arena容量不含图像、分配器和OS/OpenMP线程栈，不等于进程RSS上界。")<<"\n}\n";
    return json.str();
}

int run(const Options& o) {
    const auto began=Clock::now();Measurement m;NewFile output,record;bool report_touched=false;
    try {
        const auto row_bytes=product(o.width,3,"行"),frame_bytes=product(row_bytes,o.height,"帧");
        m.expected_bytes=product(frame_bytes,o.count,"批次");
        if(frame_bytes>static_cast<std::uintmax_t>(std::numeric_limits<std::streamsize>::max())||
           m.expected_bytes>static_cast<std::uintmax_t>(std::numeric_limits<std::streamoff>::max()))
            throw std::overflow_error("输入大小超过标准文件流的寻址范围");
        if(!fs::is_regular_file(o.input)||fs::file_size(o.input)!=m.expected_bytes)
            throw std::invalid_argument("输入必须是长度恰好等于width*height*3*count的连续RGB8普通文件");
        if(fs::exists(o.output)||(!o.report.empty()&&fs::exists(o.report)))
            throw std::invalid_argument("输出或报告已经存在，拒绝覆盖");
        if(!o.report.empty()&&fs::absolute(o.output).lexically_normal()==fs::absolute(o.report).lexically_normal())
            throw std::invalid_argument("raw输出与JSON报告不能使用同一路径");
        std::array<std::vector<std::uint8_t>,4> models,sidecars;fc::ModelBundle bundle;
        for(std::size_t i=0;i<4;++i) {
            models[i]=read_model(o.models[i],false);bundle.models[i]={models[i].data(),models[i].size()};
            if(!o.sidecars[i].empty()) {sidecars[i]=read_model(o.sidecars[i],true);bundle.sidecars[i]={sidecars[i].data(),sidecars[i].size()};}
        }
        require(fc::Runtime::requirements(bundle,o.config,&m.resources),"工作区查询");
        std::unique_ptr<std::uint8_t[]> arena(m.resources.arena_bytes?new std::uint8_t[m.resources.arena_bytes]:nullptr);
        std::unique_ptr<std::uint8_t[]> source(new std::uint8_t[frame_bytes]),destination(new std::uint8_t[frame_bytes]);
        fc::Runtime runtime;auto started=Clock::now();
        require(fc::Runtime::prepare(bundle,o.config,{arena.get(),m.resources.arena_bytes},&runtime),"模型准备");
        m.prepare_ms=milliseconds(started);m.backend=runtime.selected_backend();m.palette=runtime.palette_entries();m.cache=runtime.prepared_with_suffix_cache();
        std::ifstream input(o.input,std::ios::binary);if(!input)throw std::runtime_error("无法打开raw输入");
        output.open(o.output);if(!o.report.empty())record.open(o.report);
        for(std::size_t frame=0;frame<o.count;++frame) {
            started=Clock::now();input.read(reinterpret_cast<char*>(source.get()),static_cast<std::streamsize>(frame_bytes));m.io_ms+=milliseconds(started);
            if(!input)throw std::runtime_error("输入读取不足，完整帧输出片段保留");
            started=Clock::now();
            const auto status=runtime.apply(source.get(),frame_bytes,row_bytes,destination.get(),frame_bytes,row_bytes,o.width,o.height);
            m.apply_ms+=milliseconds(started);require(status,"图像映射");
            started=Clock::now();output.write(destination.get(),frame_bytes);m.io_ms+=milliseconds(started);++m.written;
        }
        started=Clock::now();output.flush();m.io_ms+=milliseconds(started);m.wall_ms=milliseconds(began);
        const auto value=report(o,m,output,true,"");
        if(record.opened()) {report_touched=true;record.write(value.data(),value.size());record.flush();}
        std::cout<<value;return 0;
    } catch(const std::exception& error) {
        m.wall_ms=milliseconds(began);
        try {output.flush();}catch(...){}
        if(record.opened()&&!report_touched) {
            try {const auto value=report(o,m,output,false,error.what());record.write(value.data(),value.size());record.flush();}catch(...){}
        }
        std::cerr<<"执行失败："<<error.what()<<"\n";return 1;
    }
}
}

int main(int argc,char** argv) {
    try {const auto options=parse(argc,argv);if(options.help){usage();return 0;}return run(options);}
    catch(const std::exception& error){std::cerr<<"参数错误："<<error.what()<<"\n使用--help查看完整参数。\n";return 2;}
}
