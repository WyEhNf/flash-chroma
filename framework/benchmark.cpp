// 同一单线程框架口径的受控比较：准备先于图像读取，质量与计时分列。
#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "precision_pipeline.hpp"
#include "framework_io.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <sstream>

namespace {
using Clock = std::chrono::steady_clock;
namespace fs = std::filesystem;
volatile std::uint64_t consumed = 0;
double ms(Clock::time_point start) { return std::chrono::duration<double, std::milli>(Clock::now()-start).count(); }

std::string quote(const std::string& value) {
    std::ostringstream s; s << '"';
    for (unsigned char c : value) {
        if (c == '"' || c == '\\') s << '\\' << char(c);
        else if (c < 32) s << "\\u" << std::hex << std::setw(4) << std::setfill('0') << unsigned(c) << std::dec;
        else s << char(c);
    }
    s << '"'; return s.str();
}
std::string hash(const std::vector<std::uint8_t>& bytes) {
    std::uint64_t result = UINT64_C(14695981039346656037);
    for (auto b : bytes) { result ^= b; result *= UINT64_C(1099511628211); }
    consumed ^= result;
    std::ostringstream s; s << std::hex << std::setw(16) << std::setfill('0') << result; return s.str();
}
void save(const fs::path& path, const std::string& data) {
    fc_framework_io::write_rgb_file_new(path.string(), std::vector<std::uint8_t>(data.begin(),data.end()));
}
std::uint64_t number(const std::string& text) {
    if (text.empty() || text.find_first_not_of("0123456789") != std::string::npos) throw std::runtime_error("需要非负整数");
    std::size_t end=0; auto value=std::stoull(text,&end); if(end!=text.size())throw std::runtime_error("整数未完整解析"); return value;
}
double median(std::vector<double> values) {
    if(values.empty())return 0;
    std::sort(values.begin(),values.end());const auto n=values.size();return n%2?values[n/2]:(values[n/2-1]+values[n/2])/2;
}

struct Spec {
    std::string id, grid, fit="sample";
    std::array<unsigned,4> m{};
    bool structure=false;
    fc::Backend backend=fc::Backend::Avx2;
    fc::Representation representation=fc::Representation::Sparse;
    std::size_t block=65536,budget=128*fc::MiB;
};
Spec parse_spec(std::string value) {
    std::replace(value.begin(),value.end(),',',' ');std::istringstream s(value);Spec result;unsigned structure,backend,representation;
    if(!(s>>result.id>>result.m[0]>>result.m[1]>>result.m[2]>>result.m[3]>>result.grid>>structure>>backend>>representation>>result.block>>result.budget))
        throw std::runtime_error("candidate需要id,m1,m2,m3,m4,grid,structure,backend,representation,block,budget");
    if(s>>result.fit){std::string extra;if(s>>extra)throw std::runtime_error("candidate有多余字段");}
    if(result.id.empty()||result.id.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")!=std::string::npos)
        throw std::runtime_error("candidate ID必须为安全ASCII标识符");
    for(auto m:result.m)if(m<17||m>33)throw std::runtime_error("m必须在17..33");
    if((result.grid!="framework"&&result.grid!="uniform")||structure>1||(backend!=0&&backend!=1&&backend!=2)||representation>3||!result.block||
       (result.fit!="sample"&&result.fit!="independent_ls"&&result.fit!="chain_ls"&&result.fit!="history"))
        throw std::runtime_error("candidate配置非法");
    result.structure=structure;result.backend=static_cast<fc::Backend>(backend);result.representation=static_cast<fc::Representation>(representation);return result;
}
struct Image {
    std::vector<std::uint8_t> pixels,reference;
    std::string name,input_hash,reference_hash;
};
struct Metric { double mean=0,rms=0,max=0;std::string output_hash; };
struct PreparedModels {
    std::shared_ptr<std::array<fc_framework::Stage,4>> stages=std::make_shared<std::array<fc_framework::Stage,4>>();
    std::array<fc_framework::FitReport,4> reports{};
    std::array<int,4> reused={-1,-1,-1,-1};
    double model_ms=0;
    std::string history="null";
};
struct Candidate {
    Spec spec;
    std::shared_ptr<PreparedModels> model;
    std::shared_ptr<std::array<fc_framework::Stage,4>> stages;
    std::unique_ptr<fc_framework::Chain> chain;
    bool ready=false;
    std::string error;
    unsigned status=0;
    double model_ms=0,prepare_ms=0;
    std::vector<Metric> metrics;
    std::vector<std::vector<double>> samples;
};
std::vector<std::uint8_t> reference(const std::array<std::vector<std::uint16_t>,4>& raw,
                                    const std::vector<std::uint8_t>& input) {
    auto output=input;
    for(const auto& table:raw)for(std::size_t i=0;i<output.size();i+=3) {
        // 与原框架lut_sparse_ref(...,256)的轴序、通道交换和/16截断一致。
        const std::size_t index=((std::size_t(output[i+2])*256+output[i+1])*256+output[i])*3;
        const std::uint8_t r=static_cast<std::uint8_t>(table[index+2]/16);
        const std::uint8_t g=static_cast<std::uint8_t>(table[index+1]/16);
        const std::uint8_t b=static_cast<std::uint8_t>(table[index]/16);
        output[i]=r;output[i+1]=g;output[i+2]=b;
    }
    return output;
}
Metric error_metric(const std::vector<std::uint8_t>& result,const std::vector<std::uint8_t>& expected) {
    if(result.size()!=expected.size()||result.empty()||result.size()%3)throw std::runtime_error("误差计算形状不符");
    Metric m;double square=0;
    for(std::size_t i=0;i<result.size();i+=3){const double r=int(result[i])-int(expected[i]),g=int(result[i+1])-int(expected[i+1]),b=int(result[i+2])-int(expected[i+2]);
        const double sq=r*r+g*g+b*b,d=std::sqrt(sq);m.mean+=d;square+=sq;m.max=(std::max)(m.max,d);}
    const auto count=result.size()/3;m.mean/=count;m.rms=std::sqrt(square/count);m.output_hash=hash(result);return m;
}
struct Applied { std::vector<std::uint8_t> pixels; double elapsed_ms=0; };
Applied apply(Candidate& candidate,const Image& input) {
    const auto t=Clock::now();
    // 新建输出容器、resize/零初始化均在框架同一计时区间内。
    Applied result;
    result.pixels.resize(input.pixels.size());
    const auto status=candidate.chain->apply(input.pixels.data(),result.pixels.data(),input.pixels.size()/3);
    const double elapsed=ms(t);
    if(status!=fc::Status::Ok)throw std::runtime_error("实际apply失败，状态"+std::to_string(static_cast<unsigned>(status)));
    result.elapsed_ms=elapsed;return result;
}
std::vector<double> batch(Candidate& candidate,const std::vector<Image>& images,bool compare) {
    std::vector<double> times;times.reserve(images.size());
    for(std::size_t i=0;i<images.size();++i){auto result=apply(candidate,images[i]);times.push_back(result.elapsed_ms);
        const auto actual=hash(result.pixels);if(compare&&actual!=candidate.metrics.at(i).output_hash)throw std::runtime_error("重复运行输出身份改变："+candidate.spec.id);}
    return times;
}
double total(const std::vector<double>& x){double s=0;for(auto t:x)s+=t;return s;}
void array(std::ostream& s,const std::vector<double>& values){s<<'[';for(std::size_t i=0;i<values.size();++i){if(i)s<<',';s<<values[i];}s<<']';}
void fit_error(std::ostream& s,const fc_framework::FitError& e){
    s<<"{\"sse\":"<<e.sse<<",\"mean\":"<<e.mean<<",\"rms\":"<<std::sqrt(double(e.sse)/fc_framework::dense_nodes)
     <<",\"max\":"<<std::sqrt(double(e.max_squared))<<",\"linear_sse\":"<<e.linear_sse<<'}';
}
void fit_reports(std::ostream& s,const Candidate& c){
    s<<'[';
    if(c.model&&c.spec.fit!="sample")for(unsigned i=c.spec.fit=="chain_ls"?3:0;i!=4;++i){
        if(i!=(c.spec.fit=="chain_ls"?3u:0u))s<<',';
        const auto& r=c.model->reports[i];
        s<<"{\"stage\":"<<i+1<<",\"reused_from_stage\":";if(c.model->reused[i]<0)s<<"null";else s<<c.model->reused[i]+1;
        s<<",\"scope\":"<<quote(c.spec.fit=="chain_ls"?"original_chain_full_rgb_last_stage":"original_stage_full_rgb")
         <<",\"samples\":"<<r.samples<<",\"candidate_used\":"<<(r.candidate_used?"true":"false")
         <<",\"source_separable_skipped\":"<<(r.source_separable_skipped?"true":"false")
         <<",\"full_domain_guard_passed\":";if(!r.samples)s<<"null";else s<<(r.candidate_used?"true":"false");
        s<<",\"changed_nodes\":"<<r.changed_nodes<<",\"integer_sweeps\":"<<r.integer_sweeps
         <<",\"matrix_bytes\":"<<r.matrix_bytes<<",\"temporary_payload_estimate_bytes\":"<<r.temporary_bytes
         <<",\"assembly_ms\":"<<r.assembly_seconds*1000<<",\"solve_ms\":"<<r.solve_seconds*1000
         <<",\"evaluation_ms\":"<<r.evaluation_seconds*1000<<",\"linear_sse_before\":"<<r.linear_sse_before
         <<",\"linear_sse_after\":"<<r.linear_sse_after<<",\"baseline\":";
        if(r.samples)fit_error(s,r.baseline);else s<<"null";s<<",\"candidate\":";
        if(r.samples)fit_error(s,r.candidate);else s<<"null";
        s<<",\"channels\":[";for(unsigned ch=0;ch!=3;++ch){if(ch)s<<',';s<<"{\"iterations\":"<<r.channels[ch].iterations
           <<",\"relative_residual\":"<<r.channels[ch].relative_residual<<",\"converged\":"<<(r.channels[ch].converged?"true":"false")<<'}';}s<<"]}";
    }
    s<<']';
}

int run(int argc,char** argv) {
    if(argc==4&&std::string(argv[1])=="--cache-one"){
        const auto t=Clock::now();std::vector<std::uint16_t> raw;fc_framework_io::read_3dl(argv[2],raw);
        const auto parse_ms=ms(t);fc_framework_io::write_u16_cache_new(argv[3],raw);
        std::cout<<"{\"values\":"<<raw.size()<<",\"parse_ms\":"<<parse_ms<<",\"total_ms\":"<<ms(t)<<",\"format\":\"u16le-file-order\"}\n";return 0;
    }
    if(argc==2&&std::string(argv[1])=="--help"){
        std::cout<<"单线程框架比较：--lut-cache P1 P2 P3 P4 --image-list LIST --output NEWDIR --candidate id,m1,m2,m3,m4,uniform|framework,structure,backend,representation,block,budget[,sample|independent_ls|chain_ls] [重复candidate] --reps 7 --aa-reps 7 --warmup 2 --aa-limit 0.05 --seed 20261029 --width 1024 --height 768 [--threshold T] [--write-outputs]\n";return 0;
    }
    std::array<std::string,4> paths{};std::string list,output,aa_id;std::vector<Spec> specs;
    unsigned reps=7,aa_reps=7,warmup=2,width=1024,height=768;std::uint64_t seed=20261029;
    double aa_limit=.05,threshold=0;bool has_threshold=false,dump=false;
    auto need=[&](int& i)->std::string{if(++i>=argc)throw std::runtime_error("选项缺少参数");return argv[i];};
    for(int i=1;i<argc;++i){std::string key=argv[i];
        if(key=="--lut-cache"){for(auto& p:paths)p=need(i);}
        else if(key=="--image-list")list=need(i);else if(key=="--output")output=need(i);
        else if(key=="--candidate")specs.push_back(parse_spec(need(i)));else if(key=="--aa-config")aa_id=need(i);
        else if(key=="--reps")reps=static_cast<unsigned>(number(need(i)));else if(key=="--aa-reps")aa_reps=static_cast<unsigned>(number(need(i)));
        else if(key=="--warmup")warmup=static_cast<unsigned>(number(need(i)));else if(key=="--seed")seed=number(need(i));
        else if(key=="--width")width=static_cast<unsigned>(number(need(i)));else if(key=="--height")height=static_cast<unsigned>(number(need(i)));
        else if(key=="--aa-limit")aa_limit=std::stod(need(i));else if(key=="--threshold"){threshold=std::stod(need(i));has_threshold=true;}
        else if(key=="--write-outputs")dump=true;else throw std::runtime_error("未知选项："+key);
    }
    if(output.empty()||list.empty()||paths[0].empty()||specs.empty()||!width||!height||reps<3||aa_reps<3||reps>1000||aa_reps>1000||warmup>100||!std::isfinite(aa_limit)||aa_limit<0||aa_limit>=1||(has_threshold&&(!std::isfinite(threshold)||threshold<0)))
        throw std::runtime_error("缺少必要输入或比较参数非法");
    const std::size_t pixels=std::size_t(width)*height;if(pixels/width!=height||pixels>(std::numeric_limits<std::size_t>::max)()/3)throw std::runtime_error("图像尺寸溢出");
    std::map<std::string,bool> ids;for(const auto& spec:specs)if(!ids.emplace(spec.id,true).second)throw std::runtime_error("candidate ID重复");
    const fs::path directory(output);if(fs::exists(directory))throw std::runtime_error("输出目录已存在，拒绝覆盖");fs::create_directories(directory);
    const auto run_start=Clock::now();
    try {
        std::array<std::vector<std::uint16_t>,4> raw;const auto load_start=Clock::now();
        for(unsigned i=0;i<4;++i)fc_framework_io::read_u16_cache(paths[i],raw[i]);
        const auto load_ms=ms(load_start);
        // 所有模型和运行时先完成准备；此阶段尚未打开图片列表。
        std::map<std::string,std::shared_ptr<PreparedModels>> models;
        std::vector<std::unique_ptr<Candidate>> candidates;
        for(const auto& spec:specs){auto c=std::make_unique<Candidate>();c->spec=spec;
            try {std::string key=spec.grid+'-'+spec.fit;for(auto m:spec.m)key+='-'+std::to_string(m);
                if(!models.count(key)){auto model=std::make_shared<PreparedModels>();const auto t=Clock::now();
                    fc_framework::FitOptions fit;fit.grid=spec.grid=="framework"?fc_framework::Grid::FrameworkStep:fc_framework::Grid::UniformRounded;fit.prove_structure=true;
                    for(unsigned i=0;i<4;++i)(*model->stages)[i]=fc_framework::prepare_stage(raw[i],spec.m[i],fit);
                    if(spec.fit=="independent_ls"){
                        const auto sampled=*model->stages;
                        for(unsigned i=0;i<4;++i){
                            for(unsigned j=0;j<i;++j)if(raw[i]==raw[j]&&sampled[i].blob==sampled[j].blob){model->reused[i]=int(j);break;}
                            if(model->reused[i]>=0){(*model->stages)[i]=(*model->stages)[model->reused[i]];model->reports[i]=model->reports[model->reused[i]];}
                            else (*model->stages)[i]=fc_framework::fit_full(raw[i],sampled[i],model->reports[i]);
                        }
                    }else if(spec.fit=="chain_ls")(*model->stages)[3]=fc_framework::fit_chain_last(raw,*model->stages,model->reports[3]);
                    else if(spec.fit=="history"){fc_framework::precision::Report report;*model->stages=fc_framework::precision::migrate(raw,*model->stages,report);model->history=fc_framework::precision::json(report);}
                    model->model_ms=ms(t);models.emplace(key,model);}
                c->model=models.at(key);c->stages=c->model->stages;c->model_ms=c->model->model_ms;c->chain=std::make_unique<fc_framework::Chain>();
                fc_framework::Options options;options.backend=spec.backend;options.representation=spec.representation;options.structure=spec.structure;options.threads=1;options.block_pixels=spec.block;options.max_workspace_bytes=spec.budget;
                std::array<const fc_framework::Stage*,4> views;for(unsigned i=0;i<4;++i)views[i]=&(*c->stages)[i];
                const auto t=Clock::now();const auto status=c->chain->prepare(views,options);c->prepare_ms=ms(t);c->status=static_cast<unsigned>(status);
                c->ready=status==fc::Status::Ok;if(!c->ready)c->error=fc::status_string(status);
            }catch(const std::exception& e){c->error=e.what();c->status=999;}
            candidates.push_back(std::move(c));
        }
        std::ifstream image_list(list);if(!image_list)throw std::runtime_error("不能打开图片列表");std::vector<Image> images;std::string name;
        while(std::getline(image_list,name)){if(!name.empty()&&name.back()=='\r')name.pop_back();if(name.empty()||name[0]=='#')continue;
            fs::path path(name);if(path.is_relative())path=fs::path(list).parent_path()/path;Image image;image.name=path.string();image.pixels=fc_framework_io::read_rgb_file(image.name,pixels*3);image.input_hash=hash(image.pixels);images.push_back(std::move(image));}
        if(images.empty())throw std::runtime_error("图片列表为空");
        const auto ref_start=Clock::now();
        if(dump)fs::create_directories(directory/"outputs"/"reference");
        for(std::size_t i=0;i<images.size();++i){images[i].reference=reference(raw,images[i].pixels);images[i].reference_hash=hash(images[i].reference);
            if(dump)fc_framework_io::write_rgb_file_new((directory/"outputs"/"reference"/("image-"+std::to_string(i+1)+".bin")).string(),images[i].reference);}
        const auto reference_ms=ms(ref_start);
        for(auto& c:candidates)if(c->ready){if(dump)fs::create_directories(directory/"outputs"/c->spec.id);
            for(std::size_t i=0;i<images.size();++i){auto result=apply(*c,images[i]);c->metrics.push_back(error_metric(result.pixels,images[i].reference));
                if(dump)fc_framework_io::write_rgb_file_new((directory/"outputs"/c->spec.id/("image-"+std::to_string(i+1)+".bin")).string(),result.pixels);}}
        Candidate* baseline=nullptr;for(auto& c:candidates)if(c->ready&&(aa_id.empty()||c->spec.id==aa_id)){baseline=c.get();break;}
        if(!baseline)throw std::runtime_error("没有可运行A/A候选");
        for(unsigned i=0;i<warmup;++i)batch(*baseline,images,true);
        std::vector<double> aa_a,aa_b;std::vector<std::vector<double>> aa_a_images,aa_b_images;
        for(unsigned i=0;i<aa_reps;++i){if(i%2){auto b=batch(*baseline,images,true);auto a=batch(*baseline,images,true);aa_b.push_back(total(b));aa_a.push_back(total(a));aa_a_images.push_back(a);aa_b_images.push_back(b);}
            else{auto a=batch(*baseline,images,true);auto b=batch(*baseline,images,true);aa_a.push_back(total(a));aa_b.push_back(total(b));aa_a_images.push_back(a);aa_b_images.push_back(b);}}
        const double aa_mid_a=median(aa_a),aa_mid_b=median(aa_b),drift=aa_mid_a>0?std::abs(aa_mid_b/aa_mid_a-1):1;
        const bool stable=drift<=aa_limit;
        std::vector<std::vector<std::string>> orders;
        if(stable){std::vector<std::size_t> order;for(std::size_t i=0;i<candidates.size();++i)if(candidates[i]->ready){order.push_back(i);for(unsigned j=0;j<warmup;++j)batch(*candidates[i],images,true);}
            std::mt19937_64 rng(seed);for(unsigned r=0;r<reps;++r){std::shuffle(order.begin(),order.end(),rng);std::vector<std::string> record;
                for(auto i:order){record.push_back(candidates[i]->spec.id);candidates[i]->samples.push_back(batch(*candidates[i],images,true));}orders.push_back(std::move(record));}}
        std::ostringstream report;report<<std::setprecision(17);
        report<<"{\"schema\":\"framework_benchmark_v1\",\"completed\":true,\"time_stable\":"<<(stable?"true":"false")<<",\"threads\":1,\"cpu_only\":true,\"fit_uses_images\":false,\"width\":"<<width<<",\"height\":"<<height<<",\"image_count\":"<<images.size()<<",\"source_cache_load_ms\":"<<load_ms<<",\"reference_ms\":"<<reference_ms<<",\"whole_wall_ms\":"<<ms(run_start)<<",\"seed\":"<<seed<<",\"repetitions\":"<<reps<<",\"warmup\":"<<warmup<<",\"threshold\":";
        if(has_threshold)report<<threshold;else report<<"null";
        report<<",\"timing_scope\":\"fresh output vector resize plus single-thread Chain::apply; excludes input decode, LUT preprocessing, reference, hash and output write\",\"aa\":{\"candidate\":"<<quote(baseline->spec.id)<<",\"passed\":"<<(stable?"true":"false")<<",\"relative_median_drift\":"<<drift<<",\"limit\":"<<aa_limit<<",\"a_batch_ms\":";array(report,aa_a);report<<",\"b_batch_ms\":";array(report,aa_b);report<<",\"per_image_a_ms\":[";
        for(std::size_t i=0;i<aa_a_images.size();++i){if(i)report<<',';array(report,aa_a_images[i]);}report<<"],\"per_image_b_ms\":[";for(std::size_t i=0;i<aa_b_images.size();++i){if(i)report<<',';array(report,aa_b_images[i]);}report<<"]},\"images\":[";
        for(std::size_t i=0;i<images.size();++i){if(i)report<<',';report<<"{\"index\":"<<i+1<<",\"input_fnv1a64\":"<<quote(images[i].input_hash)<<",\"reference_fnv1a64\":"<<quote(images[i].reference_hash)<<"}";}report<<"],\"candidates\":[";
        for(std::size_t ci=0;ci<candidates.size();++ci){const auto& c=*candidates[ci];if(ci)report<<',';report<<"{\"id\":"<<quote(c.spec.id)<<",\"ready\":"<<(c.ready?"true":"false")<<",\"status\":"<<c.status<<",\"error\":"<<quote(c.error)<<",\"m\":[";
            for(unsigned i=0;i<4;++i){if(i)report<<',';report<<c.spec.m[i];}report<<"],\"grid\":"<<quote(c.spec.grid)<<",\"fit\":"<<quote(c.spec.fit)<<",\"requested_structure\":"<<(c.spec.structure?"true":"false")<<",\"requested_backend\":"<<static_cast<unsigned>(c.spec.backend)<<",\"requested_representation\":"<<static_cast<unsigned>(c.spec.representation)<<",\"block_pixels\":"<<c.spec.block<<",\"workspace_budget\":"<<c.spec.budget<<",\"model_prepare_ms\":"<<c.model_ms<<",\"runtime_prepare_ms\":"<<c.prepare_ms;
            report<<",\"fit_parameters\":{\"cg_max_iterations\":160,\"relative_tolerance\":1e-8,\"regularization\":1e-5,\"integer_sweeps\":8,\"guard_full_domain\":true},\"fit_reports\":";fit_reports(report,c);
            report<<",\"history\":"<<(c.model?c.model->history:"null");
            if(c.ready){const auto info=c.chain->info();report<<",\"actual\":{\"structured\":"<<(info.structured?"true":"false")<<",\"backend\":"<<static_cast<unsigned>(info.backend)<<",\"representation\":"<<static_cast<unsigned>(info.representation)<<",\"threads\":"<<info.threads<<",\"model_bytes\":"<<info.model_bytes<<",\"sidecar_bytes\":"<<info.sidecar_bytes<<",\"arena_bytes\":"<<info.arena_bytes<<",\"object_bytes\":"<<info.object_bytes<<",\"palette_entries\":"<<info.palette_entries<<"},\"stage_proofs\":[";
                for(unsigned i=0;i<4;++i){if(i)report<<',';const auto& stage=(*c.stages)[i];report<<"{\"separable\":"<<(stage.separable_proven?"true":"false")<<",\"nodes_checked\":"<<stage.proof_nodes<<"}";}report<<"],\"quality\":[";bool quality=true;double worst=0;
                for(std::size_t i=0;i<c.metrics.size();++i){if(i)report<<',';const auto& m=c.metrics[i];quality=quality&&(!has_threshold||m.mean<threshold);worst=(std::max)(worst,m.mean);report<<"{\"image\":"<<i+1<<",\"mean\":"<<m.mean<<",\"rms\":"<<m.rms<<",\"max\":"<<m.max<<",\"output_fnv1a64\":"<<quote(m.output_hash)<<"}";}report<<"],\"worst_image_mean\":"<<worst<<",\"all_image_mean_pass\":"<<(has_threshold?(quality?"true":"false"):"null")<<",\"samples_ms\":[";
                std::vector<double> totals;for(std::size_t i=0;i<c.samples.size();++i){if(i)report<<',';array(report,c.samples[i]);totals.push_back(total(c.samples[i]));}report<<"],\"batch_median_ms\":";if(totals.empty())report<<"null";else report<<median(totals);
            }report<<'}';}
        report<<"],\"randomized_orders\":[";for(std::size_t i=0;i<orders.size();++i){if(i)report<<',';report<<'[';for(std::size_t j=0;j<orders[i].size();++j){if(j)report<<',';report<<quote(orders[i][j]);}report<<']';}report<<"],\"output_consumed\":true,\"official_score_available\":false}\n";
        save(directory/"results.json",report.str());std::cout<<"{\"completed\":true,\"time_stable\":"<<(stable?"true":"false")<<",\"candidate_count\":"<<candidates.size()<<",\"images\":"<<images.size()<<"}\n";return stable?0:3;
    }catch(const std::exception& e){save(directory/"failure.json","{\"completed\":false,\"error\":"+quote(e.what())+"}\n");throw;}
}
}
int main(int argc,char** argv){try{return run(argc,argv);}catch(const std::exception& e){std::cerr<<"错误："<<e.what()<<'\n';return 1;}}
