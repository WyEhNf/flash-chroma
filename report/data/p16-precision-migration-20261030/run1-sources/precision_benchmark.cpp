// 冻结配置后的完整域与百图回归；原图不参与模型生成。输出独立目录禁止覆盖。
#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "precision_pipeline.hpp"
#include "framework_io.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
namespace fs=std::filesystem;
using namespace fc_framework;
void save(const fs::path& p,const std::string& s){std::ofstream f(p,std::ios::binary);f<<s<<'\n';if(!f)throw std::runtime_error("写回执失败");}
void binary(const fs::path& p,const std::vector<std::uint8_t>& bytes){std::ofstream f(p,std::ios::binary);f.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());if(!f)throw std::runtime_error("写模型失败");}
std::array<const Stage*,4> ptrs(const precision::Models& m){return {{&m[0],&m[1],&m[2],&m[3]}};}
int main(int argc,char** argv){try{
    if(argc!=8)throw std::invalid_argument("参数：四份u16缓存 图片目录 新输出目录 full|bounded");
    const fs::path output=argv[6];if(fs::exists(output))throw std::invalid_argument("输出目录已存在");fs::create_directories(output);
    precision::Sources raw;precision::Models sampled;
    FitOptions fit;fit.grid=Grid::FrameworkStep;
    for(unsigned i=0;i<4;++i){fc_framework_io::read_u16_cache(argv[i+1],raw[i]);sampled[i]=prepare_stage(raw[i],33,fit);}
    precision::Options options;
    const std::string profile=argv[7];if(profile!="full"&&profile!="bounded")throw std::invalid_argument("未知预算");
    if(profile=="full")options.capacities={{{25,33,33,33}},{{33,25,33,33}},{{33,33,25,33}},{{33,33,33,25}}};
    precision::Report report;
    options.progress=[&](const std::string& name){save(output/"progress.json",precision::json(report));std::cout<<name<<std::endl;};
    const auto start=fit_detail::seconds();const auto models=precision::migrate(raw,sampled,report,options);
    save(output/"fit.json",precision::json(report));std::ostringstream meta;meta<<std::setprecision(17)<<"{\"profile\":"<<std::quoted(profile)<<",\"prepare_seconds\":"<<fit_detail::seconds()-start<<",\"stages\":[";
    for(unsigned i=0;i<4;++i){const auto& s=models[i];binary(output/(std::to_string(i)+".slut"),s.blob);binary(output/(std::to_string(i)+".fractions"),s.fractions);
        if(i)meta<<',';meta<<"{\"m\":"<<s.m<<",\"interpolation\":"<<unsigned(s.interpolation)<<",\"model_bytes\":"<<s.model_bytes()<<'}';}meta<<"]}";save(output/"model.json",meta.str());
    Options run;run.structure=false;run.backend=fc::Backend::Scalar;run.representation=fc::Representation::Sparse;
    Chain sparse,direct;if(sparse.prepare(ptrs(models),run)!=fc::Status::Ok)throw std::runtime_error("Sparse准备失败");run.backend=fc::Backend::Auto;run.representation=fc::Representation::DirectRGB24;
    if(direct.prepare(ptrs(models),run)!=fc::Status::Ok)throw std::runtime_error("RGB24准备失败");
    const auto gold=precision::truth(raw);precision::Histogram domain;std::vector<std::uint8_t> input(65536*3),a(input.size()),b(input.size());
    std::ofstream mapped(output/"domain.rgb",std::ios::binary);
    for(std::uint32_t begin=0;begin<dense_nodes;begin+=65536){for(unsigned j=0;j<65536;++j)for(unsigned c=0;c<3;++c)input[3*j+c]=std::uint8_t((begin+j)>>(8*c));
        if(sparse.apply(input.data(),a.data(),65536)!=fc::Status::Ok||direct.apply(input.data(),b.data(),65536)!=fc::Status::Ok||a!=b)throw std::runtime_error("全域Sparse/RGB24不一致");
        for(unsigned j=0;j<65536;++j)domain.add(precision::distance(detail::code(a.data()+3*j),gold[begin+j]),1);
        mapped.write(reinterpret_cast<const char*>(a.data()),a.size());}
    mapped.close();if(!mapped)throw std::runtime_error("全域输出写失败");
    save(output/"domain.json",precision::quality_json(domain.quality()));
    if(domain.quality().sse!=report.result.sse||std::abs(domain.quality().mean-report.result.mean)>1e-12)throw std::runtime_error("搜索与实际运行器质量不同");
    std::cout<<"完整域实际执行核一致，开始冻结模型百图回归"<<std::endl;
    std::ostringstream photos;photos<<std::setprecision(17)<<"{\"images\":[";double total=0,worst=0;
    for(unsigned image=1;image<=100;++image){const auto path=fs::path(argv[5])/(std::to_string(image)+".bin");const auto pixels=fc_framework_io::read_rgb_file(path.string(),1024*768*3);
        std::vector<std::uint8_t> rendered(pixels.size());const auto time=fit_detail::seconds();if(direct.apply(pixels.data(),rendered.data(),pixels.size()/3)!=fc::Status::Ok)throw std::runtime_error("照片映射失败");const double elapsed=fit_detail::seconds()-time;
        precision::Histogram h;for(std::size_t i=0;i<pixels.size();i+=3)h.add(precision::distance(detail::code(rendered.data()+i),gold[detail::code(pixels.data()+i)]),1);
        const auto q=h.quality();total+=q.mean;worst=(std::max)(worst,q.mean);if(image!=1)photos<<',';photos<<"{\"image\":"<<image<<",\"quality\":"<<precision::quality_json(q)<<",\"kernel_seconds_observation\":"<<elapsed<<'}';}
    photos<<"],\"mean\":"<<total/100<<",\"worst_image_mean\":"<<worst<<",\"backend\":"<<unsigned(direct.info().backend)<<",\"model_bytes\":"<<direct.info().model_bytes<<",\"arena_bytes\":"<<direct.info().arena_bytes<<'}';save(output/"photos.json",photos.str());
    std::cout<<"完成：mean="<<total/100<<" worst="<<worst<<std::endl;return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<std::endl;return 2;}}
