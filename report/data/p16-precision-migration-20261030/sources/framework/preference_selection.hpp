/* 本机LUT-only偏好选择；完整域质量与合成时间来自本次运行，不使用照片或历史目录。 */
#ifndef FLASH_CHROMA_FRAMEWORK_PREFERENCE_SELECTION_HPP
#define FLASH_CHROMA_FRAMEWORK_PREFERENCE_SELECTION_HPP
#include "precision_pipeline.hpp"
#include <cstdio>
#include <iomanip>
#include <locale>
#include <memory>
#include <optional>
#include <sstream>
#include <string>

namespace fc_framework {
struct PreferenceOptions {
    fc::Preference weights{};
    std::vector<std::array<unsigned,4>> sizes{{17,17,17,17},{33,33,33,33}};
    std::vector<fc::Representation> representations{fc::Representation::Sparse,fc::Representation::DirectRGB24};
    FitOptions fit{};
    std::string fit_method="sample";
    precision::Options history{};
    fc::Backend backend=fc::Backend::Auto;
    std::size_t max_runtime_bytes=(std::numeric_limits<std::size_t>::max)();
    std::size_t max_workspace_bytes=64*fc::MiB;
    std::optional<double> max_domain_mean,max_pixel_error,max_ms_per_megapixel;
    bool allow_unstable=false;
    unsigned calibration_repetitions=5;
    double aa_limit=.05;
    bool structure=false;
    std::size_t block_pixels=65536;
};
struct SelectionResult {
    bool selected=false;
    fc::SelectionStatus status=fc::SelectionStatus::NoFeasible;
    std::array<Stage,4> stages{};
    Options options{};
    Info expected_info{};
    std::size_t expected_runtime_bytes=0;
    std::size_t candidate_index=(std::numeric_limits<std::size_t>::max)();
    std::string report_json;
};
namespace preference_detail {
constexpr std::size_t calibration_pixels=1024u*768u,domain_chunk_pixels=65536;
constexpr std::uint32_t calibration_seed=0x006d2b79u,calibration_multiplier=0x009e3779u;
inline volatile std::uint64_t consumed_output=0;
inline bool nonnegative(double x){return std::isfinite(x)&&x>=0;}
inline bool uses_time(const PreferenceOptions& p){return p.weights.speed>0||p.max_ms_per_megapixel.has_value();}
inline std::string validate(const PreferenceOptions& p){
    const auto& w=p.weights;
    if(!nonnegative(w.accuracy)||!nonnegative(w.speed)||!nonnegative(w.compactness)||
       w.accuracy>1||w.speed>1||w.compactness>1||!(w.accuracy+w.speed+w.compactness>0))
        return "ABC权重须分别在[0,1]内且总和大于零";
    if(p.sizes.empty()||p.representations.empty())return "候选尺寸和表示不能为空";
    if(p.sizes.size()>64||p.representations.size()>4)return "候选计划超过64个尺寸组合或4种表示";
    for(std::size_t i=0;i<p.sizes.size();++i){
        for(unsigned m:p.sizes[i])if(m<17||m>33)return "各级m须在17..33内";
        for(std::size_t j=0;j<i;++j)if(p.sizes[j]==p.sizes[i])return "候选尺寸重复";
    }
    for(std::size_t i=0;i<p.representations.size();++i){
        const auto r=p.representations[i];
        if(r!=fc::Representation::Sparse&&r!=fc::Representation::DirectU8&&
           r!=fc::Representation::DirectU16&&r!=fc::Representation::DirectRGB24)return "候选表示非法";
        for(std::size_t j=0;j<i;++j)if(p.representations[j]==r)return "候选表示重复";
    }
    if(p.fit.grid!=Grid::FrameworkStep&&p.fit.grid!=Grid::UniformRounded)return "网格策略非法";
    if(p.fit_method!="sample"&&p.fit_method!="independent_ls"&&p.fit_method!="chain_ls"&&p.fit_method!="history")return "拟合策略非法";
    if(p.backend!=fc::Backend::Auto&&p.backend!=fc::Backend::Scalar&&p.backend!=fc::Backend::Avx2)return "后端非法";
    if(!p.block_pixels||p.block_pixels>(std::numeric_limits<std::size_t>::max)()/3)return "像素块大小非法";
    if(p.calibration_repetitions<3||p.calibration_repetitions>31||p.calibration_repetitions%2==0)
        return "校准次数须为3..31内奇数";
    if(!nonnegative(p.aa_limit)||p.aa_limit>=1)return "A/A阈值须在[0,1)内";
    for(const auto* v:{&p.max_domain_mean,&p.max_pixel_error,&p.max_ms_per_megapixel})
        if(v->has_value()&&!nonnegative(**v))return "质量和时间预算须为有限非负数";
    return {};
}
inline fc::Request make_request(const PreferenceOptions& p,const char* context){
    fc::Request r;r.context=context;r.preference=p.weights;r.max_threads=1;
    r.use_time=uses_time(p);r.require_stable_time=!p.allow_unstable;
    r.max_runtime_bytes=p.max_runtime_bytes;r.max_workspace_bytes=p.max_workspace_bytes;
    r.has_time_limit=p.max_ms_per_megapixel.has_value();
    if(r.has_time_limit)r.max_batch_ms=*p.max_ms_per_megapixel*(double(calibration_pixels)/1e6);
    return r;
}
inline fc::SelectionStatus choose(const std::vector<fc::Candidate>& input,const PreferenceOptions& p,
                                  const char* context,fc::SelectionView* output){
    if(!validate(p).empty())return fc::SelectionStatus::InvalidRequest;
    auto candidates=input;
    // 此wrapper中worst_image_mean存完整域最大误差上界，不是实测照片mean。
    for(auto& c:candidates)if((p.max_domain_mean&&c.mean_error>*p.max_domain_mean)||
                              (p.max_pixel_error&&c.worst_image_mean>*p.max_pixel_error))c.accuracy_verified=false;
    return fc::select(candidates.data(),candidates.size(),make_request(p,context),output);
}
inline Options execution_options(const fc::Candidate& c,const PreferenceOptions& p){
    Options o;o.backend=c.config.backend;o.representation=c.config.representation;o.structure=p.structure;
    o.threads=1;o.block_pixels=c.config.block_pixels;o.max_workspace_bytes=c.config.max_workspace_bytes;return o;
}
struct ResourceAccounting{std::size_t wrapper_nodes_bytes=0,shared_ownership_estimate_bytes=0,runtime_bytes=0;};
inline void add_bytes(std::size_t& total,std::size_t bytes){
    if(bytes>(std::numeric_limits<std::size_t>::max)()-total)throw std::overflow_error("资源记账溢出");
    total+=bytes;
}
inline ResourceAccounting account_resources(const Info& info,std::size_t wrapper_nodes){
    ResourceAccounting r;r.wrapper_nodes_bytes=wrapper_nodes;
    // Stage本体已在Info.object_bytes；这里只加四个shared_ptr及每个控制块2指针估算。
    r.shared_ownership_estimate_bytes=4*(sizeof(std::shared_ptr<Stage>)+2*sizeof(void*));
    for(auto n:{info.model_bytes,info.arena_bytes,info.object_bytes,wrapper_nodes,r.shared_ownership_estimate_bytes})
        add_bytes(r.runtime_bytes,n);
    return r;
}
inline double median(std::vector<double> values){
    if(values.empty())return std::numeric_limits<double>::quiet_NaN();
    std::sort(values.begin(),values.end());const auto n=values.size();
    return n%2?values[n/2]:(values[n/2-1]/2+values[n/2]/2);
}
struct TimeControl{double median_a_ms=0,median_b_ms=0,relative_drift=0;bool passed=false;};
inline TimeControl control(const std::vector<double>& a,const std::vector<double>& b,double limit){
    TimeControl r;if(a.empty()||a.size()!=b.size()||!nonnegative(limit)||limit>=1)return r;
    for(const auto* v:{&a,&b})for(double x:*v)if(!std::isfinite(x)||!(x>0))return r;
    r.median_a_ms=median(a);r.median_b_ms=median(b);
    r.relative_drift=std::abs(r.median_a_ms-r.median_b_ms)/(std::min)(r.median_a_ms,r.median_b_ms);
    r.passed=r.relative_drift<=limit;return r;
}
inline std::uint64_t hash_bytes(const std::uint8_t* p,std::size_t n,std::uint64_t h=14695981039346656037ull){
    for(std::size_t i=0;i<n;++i){h^=p[i];h*=1099511628211ull;}return h;
}
inline std::uint64_t hash_raw(const std::vector<std::uint16_t>& raw){
    std::uint64_t h=14695981039346656037ull;
    for(auto v:raw){h^=v&255;h*=1099511628211ull;h^=v>>8;h*=1099511628211ull;}return h;
}
inline std::string hex(std::uint64_t value){
    std::ostringstream s;s<<std::hex<<std::setfill('0')<<std::setw(16)<<value;return s.str();
}
inline std::string quoted(const std::string& text){
    std::ostringstream s;s<<'"';
    for(unsigned char c:text)switch(c){
        case '"':s<<"\\\"";break;case '\\':s<<"\\\\";break;
        case '\n':s<<"\\n";break;case '\r':s<<"\\r";break;case '\t':s<<"\\t";break;
        default:if(c<32)s<<"\\u00"<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(c)<<std::dec;else s<<char(c);
    }
    s<<'"';return s.str();
}
inline void number(std::ostream& s,double v){if(std::isfinite(v))s<<std::setprecision(17)<<v;else s<<"null";}
inline void numbers(std::ostream& s,const std::vector<double>& v){
    s<<'[';for(std::size_t i=0;i<v.size();++i){if(i)s<<',';number(s,v[i]);}s<<']';
}
inline void optional_number(std::ostream& s,const std::optional<double>& v){if(v)number(s,*v);else s<<"null";}
inline const char* representation_name(fc::Representation r){
    switch(r){case fc::Representation::Sparse:return "sparse";case fc::Representation::DirectU8:return "direct_u8";
        case fc::Representation::DirectU16:return "direct_u16";case fc::Representation::DirectRGB24:return "direct_rgb24";}
    return "invalid";
}
inline void require(fc::Status status,const char* action){
    if(status!=fc::Status::Ok)throw std::runtime_error(std::string(action)+":"+fc::status_string(status));
}
inline void progress(const std::string& text){
    std::fprintf(stderr,"[偏好选择] %s\n",text.c_str());std::fflush(stderr);
}
inline std::array<const Stage*,4> pointers(const std::array<Stage,4>& stages){
    return {{&stages[0],&stages[1],&stages[2],&stages[3]}};
}
inline void fill_domain(std::vector<std::uint8_t>& input,std::size_t begin,std::size_t n){
    input.resize(n*3);for(std::size_t i=0;i<n;++i){const auto c=begin+i;
        input[i*3]=std::uint8_t(c);input[i*3+1]=std::uint8_t(c>>8);input[i*3+2]=std::uint8_t(c>>16);}
}
inline std::uint32_t synthetic_code(std::size_t i){
    return (std::uint32_t(i)*calibration_multiplier+calibration_seed)&0xffffffu;
}
inline std::vector<std::uint8_t> synthetic_input(){
    std::vector<std::uint8_t> v(calibration_pixels*3);for(std::size_t i=0;i<calibration_pixels;++i){
        const auto c=synthetic_code(i);v[i*3]=std::uint8_t(c);v[i*3+1]=std::uint8_t(c>>8);v[i*3+2]=std::uint8_t(c>>16);}return v;
}
inline std::vector<std::uint8_t> synthetic_expected(const std::vector<std::uint8_t>& reference){
    std::vector<std::uint8_t> v(calibration_pixels*3);
    for(std::size_t i=0;i<calibration_pixels;++i)
        std::memcpy(v.data()+i*3,reference.data()+std::size_t(synthetic_code(i))*3,3);
    return v;
}
struct Calibration{
    std::vector<double> warmup,pre_a,pre_b,samples,post_a,post_b;
    TimeControl pre{},post{};std::uint64_t output_hash=0;bool verified=false,stable=false;
    double batch_ms=std::numeric_limits<double>::quiet_NaN();
};
inline double timed_apply(const Chain& chain,const std::vector<std::uint8_t>& input,
                          const std::vector<std::uint8_t>& expected,std::uint64_t& hash){
    std::vector<std::uint8_t> output;const auto start=std::chrono::steady_clock::now();
    output.resize(input.size());const auto status=chain.apply(input.data(),output.data(),calibration_pixels);
    const auto stop=std::chrono::steady_clock::now();require(status,"合成校准映射失败");
    if(output!=expected)throw std::runtime_error("合成输出与同模型Scalar完整域不同");
    hash=hash_bytes(output.data(),output.size());consumed_output=hash;
    const double ms=std::chrono::duration<double,std::milli>(stop-start).count();
    if(!std::isfinite(ms)||!(ms>0))throw std::runtime_error("合成校准时间无效");
    return ms;
}
inline void calibrate(const Chain& chain,const std::vector<std::uint8_t>& input,
                      const std::vector<std::uint8_t>& expected,const PreferenceOptions& p,Calibration& c){
    c={};for(unsigned i=0;i<2;++i)c.warmup.push_back(timed_apply(chain,input,expected,c.output_hash));
    auto aa=[&](std::vector<double>& a,std::vector<double>& b){
        for(unsigned i=0;i<p.calibration_repetitions;++i){
            if(i%2){b.push_back(timed_apply(chain,input,expected,c.output_hash));a.push_back(timed_apply(chain,input,expected,c.output_hash));}
            else {a.push_back(timed_apply(chain,input,expected,c.output_hash));b.push_back(timed_apply(chain,input,expected,c.output_hash));}
        }
    };
    aa(c.pre_a,c.pre_b);c.pre=control(c.pre_a,c.pre_b,p.aa_limit);
    for(unsigned i=0;i<p.calibration_repetitions;++i)c.samples.push_back(timed_apply(chain,input,expected,c.output_hash));
    aa(c.post_a,c.post_b);c.post=control(c.post_a,c.post_b,p.aa_limit);
    c.batch_ms=median(c.samples);c.verified=true;c.stable=c.pre.passed&&c.post.passed;
}
struct Model{
    std::array<unsigned,4> sizes{};std::array<Stage,4> stages{};std::array<FitReport,4> fits{};
    std::array<std::string,4> hashes{};std::string id,error,history_report="null";
    double prepare_ms=0,domain_mean=std::numeric_limits<double>::quiet_NaN();
    double domain_rms=std::numeric_limits<double>::quiet_NaN(),domain_max=std::numeric_limits<double>::quiet_NaN();
    std::uint64_t scalar_hash=0;bool accuracy_verified=false;
};
struct CachedStage{unsigned m=0;Stage stage;FitReport fit;};
struct Record{
    std::size_t model_index=0;fc::Representation requested_representation=fc::Representation::Sparse;
    std::string id,error,exclusion;fc::Candidate candidate{};Info info{};ResourceAccounting resources{};
    Calibration calibration{};double prepare_ms=0,contract_ms=0;std::size_t verified_pixels=0;std::uint64_t output_hash=0;
};
inline std::vector<std::uint8_t> scalar_domain(const Model& m,const std::vector<std::uint8_t>& truth,
                                             double& mean,double& rms,double& maximum){
    Chain chain;Options o;o.backend=fc::Backend::Scalar;o.representation=fc::Representation::Sparse;o.structure=false;
    require(chain.prepare(pointers(m.stages),o),"Scalar稀疏准备失败");
    std::vector<std::uint8_t> output(dense_values),input;double sum=0;std::uint64_t sse=0;unsigned max_squared=0;
    for(std::size_t begin=0;begin<dense_nodes;begin+=domain_chunk_pixels){
        const auto n=(std::min)(domain_chunk_pixels,dense_nodes-begin);fill_domain(input,begin,n);
        require(chain.apply(input.data(),output.data()+begin*3,n),"Scalar完整域映射失败");
        for(std::size_t i=begin;i<begin+n;++i){unsigned squared=0;for(unsigned c=0;c<3;++c){
            const int d=int(output[i*3+c])-int(truth[i*3+c]);squared+=unsigned(d*d);}
            sum+=std::sqrt(double(squared));sse+=squared;max_squared=(std::max)(max_squared,squared);}
    }
    mean=sum/dense_nodes;rms=std::sqrt(double(sse)/dense_nodes);maximum=std::sqrt(double(max_squared));return output;
}
inline void verify_domain(const Chain& chain,const std::vector<std::uint8_t>& expected,Record& r){
    std::vector<std::uint8_t> input,output(domain_chunk_pixels*3);std::uint64_t hash=14695981039346656037ull;
    for(std::size_t begin=0;begin<dense_nodes;begin+=domain_chunk_pixels){
        const auto n=(std::min)(domain_chunk_pixels,dense_nodes-begin);fill_domain(input,begin,n);
        // 先逐字节投毒，避免未写输出因复用缓冲而假通过。
        for(std::size_t i=0;i<n*3;++i)output[i]=std::uint8_t(expected[begin*3+i]^255u);
        require(chain.apply(input.data(),output.data(),n),"候选完整域映射失败");
        if(std::memcmp(output.data(),expected.data()+begin*3,n*3))throw std::runtime_error("候选与Scalar稀疏完整RGB域不同");
        hash=hash_bytes(output.data(),n*3,hash);r.verified_pixels+=n;
    }
    r.output_hash=hash;consumed_output=hash;
}
inline void info_json(std::ostream& s,const Info& v){
    s<<"{\"structured\":"<<(v.structured?"true":"false")<<",\"backend\":"<<unsigned(v.backend)
     <<",\"representation\":"<<unsigned(v.representation)<<",\"threads\":"<<v.threads
     <<",\"model_bytes\":"<<v.model_bytes<<",\"sidecar_bytes\":"<<v.sidecar_bytes
     <<",\"arena_bytes\":"<<v.arena_bytes<<",\"object_bytes\":"<<v.object_bytes
     <<",\"proof_nodes\":"<<v.proof_nodes<<",\"palette_entries\":"<<v.palette_entries<<'}';
}
inline void control_json(std::ostream& s,const TimeControl& c){
    s<<"{\"median_a_ms\":";number(s,c.median_a_ms);s<<",\"median_b_ms\":";number(s,c.median_b_ms);
    s<<",\"relative_drift\":";number(s,c.relative_drift);s<<",\"passed\":"<<(c.passed?"true":"false")<<'}';
}
inline std::string report(const PreferenceOptions& p,const SelectionResult& result,const std::string& error,
                          const std::array<std::string,4>& raw_hashes,const std::string& context,
                          const std::vector<Model>& models,const std::vector<Record>& records,
                          const fc::SelectionView& view,double offline_ms){
    std::ostringstream s;s.imbue(std::locale::classic());s<<std::setprecision(17);
    s<<"{\"schema\":\"flash-chroma-lut-preferences-v1\",\"selected\":"<<(result.selected?"true":"false")
     <<",\"status\":"<<quoted(fc::selection_status_string(result.status))<<",\"error\":"<<quoted(error)
     <<",\"context\":"<<quoted(context)<<",\"source_lut_u16le_fnv1a64\":[";
    for(unsigned i=0;i<4;++i){if(i)s<<',';s<<quoted(raw_hashes[i]);}
    s<<"],\"fingerprint_scope\":\"FNV-1a64为本次绑定指纹而非密码学SHA；调用者另绑定构建与报告文件\"";
#ifdef __VERSION__
    s<<",\"compiler\":"<<quoted(__VERSION__);
#else
    s<<",\"compiler\":\"未提供__VERSION__\"";
#endif
    s<<",\"compiled_capabilities\":"<<fc::compiled_capabilities()<<",\"available_backends\":"<<fc::available_backends()
     <<",\"pointer_bytes\":"<<sizeof(void*)<<",\"algorithm_threads\":1,\"weights\":[";
    number(s,p.weights.accuracy);s<<',';number(s,p.weights.speed);s<<',';number(s,p.weights.compactness);
    s<<"],\"grid\":"<<quoted(p.fit.grid==Grid::FrameworkStep?"framework":"uniform")<<",\"fit\":"<<quoted(p.fit_method)
     <<",\"requested_backend\":"<<unsigned(p.backend)<<",\"structure\":"<<(p.structure?"true":"false")
     <<",\"block_pixels\":"<<p.block_pixels<<",\"max_runtime_bytes\":"<<p.max_runtime_bytes
     <<",\"max_workspace_bytes\":"<<p.max_workspace_bytes<<",\"max_domain_mean\":";optional_number(s,p.max_domain_mean);
    s<<",\"max_pixel_error\":";optional_number(s,p.max_pixel_error);
    s<<",\"max_ms_per_megapixel\":";optional_number(s,p.max_ms_per_megapixel);
    s<<",\"quality_scope\":\"完整256^3输入相对本次原始四LUT逐级uint16/16再uint8；mean是逐像素RGB欧氏距离\""
     <<",\"worst_image_mean_semantics\":\"core字段存完整RGB域最大像素误差，作为任意图mean保守上界；不是实测照片mean\""
     <<",\"resource_scope\":\"最终Info.model+arena+object+原main四份节点副本+shared管理估算；sidecar不重复计。非allocator/RSS/峰值，不含原始LUT、图片输出和全部候选/拟合/校准暂态\""
     <<",\"shared_ownership_formula\":\"4*(sizeof(shared_ptr<Stage>)+2*sizeof(void*))；Stage本体已在Info.object内\""
     <<",\"time_requested\":"<<(uses_time(p)?"true":"false")<<",\"allow_unstable\":"<<(p.allow_unstable?"true":"false")
     <<",\"calibration\":{\"pixels\":"<<calibration_pixels<<",\"width\":1024,\"height\":768,\"seed\":"<<calibration_seed
     <<",\"multiplier\":"<<calibration_multiplier
     <<",\"algorithm\":\"code=(i*multiplier+seed)&0xffffff，RGB为低/中/高字节；无图片输入\""
     <<",\"scope\":\"每次fresh vector.resize零初始化+apply；释放、逐字节比较、FNV消费在计时外；不代表照片速度或官方分数\""
     <<",\"warmup\":2,\"repetitions\":"<<p.calibration_repetitions<<",\"aa_limit\":";number(s,p.aa_limit);
    s<<",\"order\":\"模型/表示按请求固定顺序；每候选预A/A交替AB/BA、正式重复、后A/A交替AB/BA；无跨候选随机化\"}"
     <<",\"offline_total_ms\":";number(s,offline_ms);
    s<<",\"requested_sizes\":[";
    for(std::size_t i=0;i<p.sizes.size();++i){if(i)s<<',';s<<'[';for(unsigned j=0;j<4;++j){if(j)s<<',';s<<p.sizes[i][j];}s<<']';}
    s<<"],\"requested_representations\":[";
    for(std::size_t i=0;i<p.representations.size();++i){if(i)s<<',';s<<quoted(representation_name(p.representations[i]));}
    s<<"],\"models\":[";
    for(std::size_t i=0;i<models.size();++i){
        if(i)s<<',';
        const auto& m=models[i];s<<"{\"id\":"<<quoted(m.id)<<",\"sizes\":[";
        for(unsigned j=0;j<4;++j){if(j)s<<',';s<<m.sizes[j];}s<<"],\"model_fnv1a64\":[";
        for(unsigned j=0;j<4;++j){if(j)s<<',';s<<quoted(m.hashes[j]);}s<<"],\"error\":"<<quoted(m.error)<<",\"prepare_ms\":";number(s,m.prepare_ms);
        s<<",\"accuracy_verified\":"<<(m.accuracy_verified?"true":"false")<<",\"domain_mean\":";number(s,m.domain_mean);
        s<<",\"domain_rms\":";number(s,m.domain_rms);s<<",\"domain_max\":";number(s,m.domain_max);
        s<<",\"scalar_output_fnv1a64\":"<<quoted(hex(m.scalar_hash))<<",\"history\":"<<m.history_report<<",\"fit_stages\":[";
        for(unsigned j=0;j<4;++j){if(j)s<<',';const auto& f=m.fits[j];
            s<<"{\"candidate_used\":"<<(f.candidate_used?"true":"false")<<",\"changed_nodes\":"<<f.changed_nodes
             <<",\"source_separable_skipped\":"<<(f.source_separable_skipped?"true":"false")<<'}';}
        s<<"]}";
    }
    s<<"],\"candidates\":[";
    for(std::size_t i=0;i<records.size();++i){
        if(i)s<<',';
        const auto& r=records[i];const auto& c=r.candidate;
        s<<"{\"id\":"<<quoted(r.id)<<",\"model_index\":"<<r.model_index
         <<",\"requested_representation\":"<<quoted(representation_name(r.requested_representation))
         <<",\"error\":"<<quoted(r.error)<<",\"exclusion\":"<<quoted(r.exclusion)<<",\"actual\":";info_json(s,r.info);
        s<<",\"runtime_bytes\":"<<r.resources.runtime_bytes<<",\"wrapper_nodes_bytes\":"<<r.resources.wrapper_nodes_bytes
         <<",\"shared_ownership_estimate_bytes\":"<<r.resources.shared_ownership_estimate_bytes
         <<",\"correctness_verified\":"<<(c.correctness_verified?"true":"false")
         <<",\"accuracy_verified\":"<<(c.accuracy_verified?"true":"false")<<",\"resources_verified\":"<<(c.resources_verified?"true":"false")
         <<",\"full_domain_verified_pixels\":"<<r.verified_pixels<<",\"output_fnv1a64\":"<<quoted(hex(r.output_hash))
         <<",\"prepare_ms\":";number(s,r.prepare_ms);s<<",\"contract_ms\":";number(s,r.contract_ms);
        s<<",\"time_verified\":"<<(c.time_verified?"true":"false")<<",\"time_stable\":"<<(c.time_stable?"true":"false")
         <<",\"batch_ms\":";number(s,c.batch_ms);s<<",\"ms_per_megapixel\":";number(s,c.batch_ms*1e6/calibration_pixels);
        s<<",\"warmup_ms\":";numbers(s,r.calibration.warmup);s<<",\"pre_a_ms\":";numbers(s,r.calibration.pre_a);
        s<<",\"pre_b_ms\":";numbers(s,r.calibration.pre_b);s<<",\"samples_ms\":";numbers(s,r.calibration.samples);
        s<<",\"post_a_ms\":";numbers(s,r.calibration.post_a);s<<",\"post_b_ms\":";numbers(s,r.calibration.post_b);
        s<<",\"pre_control\":";control_json(s,r.calibration.pre);s<<",\"post_control\":";control_json(s,r.calibration.post);
        s<<",\"synthetic_output_fnv1a64\":"<<quoted(hex(r.calibration.output_hash))<<'}';
    }
    s<<"],\"selection\":{\"candidate_index\":";if(result.selected)s<<result.candidate_index;else s<<"null";
    s<<",\"eligible\":"<<view.eligible<<",\"frontier_size\":"<<view.frontier_size<<",\"score\":";number(s,view.score);
    s<<",\"provisional\":"<<(view.provisional?"true":"false")<<",\"expected_runtime_bytes\":"<<result.expected_runtime_bytes
     <<",\"expected_info\":";info_json(s,result.expected_info);s<<"}}";return s.str();
}
} // namespace preference_detail

inline SelectionResult select_preferences(const std::array<std::vector<std::uint16_t>,4>& raw,const PreferenceOptions& p={}){
    using namespace preference_detail;
    SelectionResult result;fc::SelectionView view;std::vector<Model> models;std::vector<Record> records;
    std::array<std::string,4> raw_hashes{};std::string context,error;
    const auto started=std::chrono::steady_clock::now();
    auto finish=[&](){result.report_json=report(p,result,error,raw_hashes,context,models,records,view,
        std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-started).count());};
    error=validate(p);
    if(!error.empty()){result.status=fc::SelectionStatus::InvalidRequest;finish();return result;}
    for(const auto& t:raw)if(t.size()!=dense_values){error="输入须为本次四张完整uint16 LUT";
        result.status=fc::SelectionStatus::InvalidRequest;finish();return result;}
    try{
        progress("绑定本次四张LUT并生成独立完整RGB域参考，尚未读取图片");
        for(unsigned i=0;i<4;++i)raw_hashes[i]=hex(hash_raw(raw[i]));
        context="local-lut-v1";for(const auto& h:raw_hashes)context+='-'+h;
        context+='-'+std::to_string(fc::available_backends());
        // 原参考只查本次原始四表；不使用稀疏预测、图片或旧输出。
        std::vector<std::uint8_t> truth(dense_values);
        for(std::size_t code=0;code<dense_nodes;++code){
            const auto t=fit_chain_detail::target(raw,{{unsigned(code&255),unsigned((code>>8)&255),unsigned(code>>16)}});
            for(unsigned c=0;c<3;++c)truth[code*3+c]=std::uint8_t(t[c]);
        }
        const auto synthetic=uses_time(p)?synthetic_input():std::vector<std::uint8_t>{};
        models.reserve(p.sizes.size());records.reserve(p.sizes.size()*p.representations.size());
        std::array<std::vector<CachedStage>,4> stage_cache;
        for(const auto& sizes:p.sizes){
            models.emplace_back();auto& m=models.back();m.sizes=sizes;m.id="m";
            for(unsigned i=0;i<4;++i){if(i)m.id+='-';m.id+=std::to_string(sizes[i]);}
            progress(m.id+"：构建固定节点/拟合并核对完整RGB域质量");
            const auto model_start=std::chrono::steady_clock::now();std::vector<std::uint8_t> scalar,expected;
            try{
                for(unsigned i=0;i<4;++i){
                    auto& cache=stage_cache[i];
                    auto found=std::find_if(cache.begin(),cache.end(),[&](const CachedStage& c){return c.m==sizes[i];});
                    if(found==cache.end()){
                        CachedStage entry;entry.m=sizes[i];entry.stage=prepare_stage(raw[i],sizes[i],p.fit);
                        if(p.fit_method=="independent_ls")entry.stage=fit_full(raw[i],entry.stage,entry.fit);
                        cache.push_back(std::move(entry));found=cache.end()-1;
                    }
                    m.stages[i]=found->stage;m.fits[i]=found->fit;
                }
                if(p.fit_method=="chain_ls")m.stages[3]=fit_chain_last(raw,m.stages,m.fits[3]);
                if(p.fit_method=="history"){precision::Report report;auto options=p.history;
                    if(!options.capacities.empty())throw std::invalid_argument("偏好候选的容量由sizes控制，history内部不得另换容量");
                    m.stages=precision::migrate(raw,m.stages,report,options);m.history_report=precision::json(report);}
                for(unsigned i=0;i<4;++i){const auto& stage=m.stages[i];auto hash=hash_bytes(stage.blob.data(),stage.blob.size());
                    hash=hash_bytes(stage.fractions.data(),stage.fractions.size(),hash);const std::uint8_t kind=static_cast<std::uint8_t>(stage.interpolation);hash=hash_bytes(&kind,1,hash);m.hashes[i]=hex(hash);}
                scalar=scalar_domain(m,truth,m.domain_mean,m.domain_rms,m.domain_max);
                m.scalar_hash=hash_bytes(scalar.data(),scalar.size());m.accuracy_verified=true;
                if(uses_time(p))expected=synthetic_expected(scalar);
            }catch(const std::exception& e){m.error=e.what();}
            m.prepare_ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-model_start).count();
            for(const auto rep:p.representations){
                records.emplace_back();auto& r=records.back();r.model_index=models.size()-1;r.requested_representation=rep;
                r.id=m.id+'-'+representation_name(rep);auto& c=r.candidate;
                progress(r.id+"：准备实际表示、全域逐字节合同和预算检查");
                c.config.backend=fc::Backend::Scalar;c.config.representation=rep;c.config.threads=1;
                c.config.block_pixels=p.block_pixels;c.config.max_workspace_bytes=p.max_workspace_bytes;
                if(!m.error.empty()){r.error=m.error;continue;}
                c.mean_error=m.domain_mean;c.worst_image_mean=m.domain_max;c.accuracy_verified=true;
                if((p.max_domain_mean&&m.domain_mean>*p.max_domain_mean)||(p.max_pixel_error&&m.domain_max>*p.max_pixel_error)){
                    r.exclusion="完整RGB域质量预算不满足";continue;
                }
                try{
                    // 一次只保留一个Chain；Scalar参考Chain已释放，其完整域期望字节流继续复用。
                    Chain chain;Options o;o.backend=p.backend;o.representation=rep;o.structure=p.structure;
                    o.threads=1;o.block_pixels=p.block_pixels;o.max_workspace_bytes=p.max_workspace_bytes;
                    auto at=std::chrono::steady_clock::now();require(chain.prepare(pointers(m.stages),o),"候选准备失败");
                    r.prepare_ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-at).count();r.info=chain.info();
                    c.config.backend=r.info.backend;c.config.representation=r.info.representation;c.config.threads=r.info.threads;
                    std::size_t nodes=0;for(const auto& stage:m.stages)add_bytes(nodes,stage.node_bytes());
                    r.resources=account_resources(r.info,nodes);c.runtime_bytes=r.resources.runtime_bytes;c.workspace_bytes=r.info.arena_bytes;
                    c.resources_verified=true;
                    if(c.runtime_bytes>p.max_runtime_bytes||c.workspace_bytes>p.max_workspace_bytes){
                        r.exclusion="最终计划自有payload或工作区预算不满足";continue;
                    }
                    at=std::chrono::steady_clock::now();verify_domain(chain,scalar,r);
                    r.contract_ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-at).count();c.correctness_verified=true;
                    if(uses_time(p)){
                        progress(r.id+"：合成输入前后A/A与单线程校准");
                        calibrate(chain,synthetic,expected,p,r.calibration);c.batch_ms=r.calibration.batch_ms;
                        c.time_verified=r.calibration.verified;c.time_stable=r.calibration.stable;
                        if(!c.time_stable&&!p.allow_unstable)r.exclusion="前后A/A漂移未通过，拒绝速度资格";
                        if(p.max_ms_per_megapixel&&c.batch_ms*1e6/calibration_pixels>*p.max_ms_per_megapixel)
                            r.exclusion="合成校准ms/MP超过预算";
                    }
                }catch(const std::exception& e){r.error=e.what();c.correctness_verified=false;c.time_verified=false;c.time_stable=false;}
            }
        }
        std::vector<fc::Candidate> candidates;candidates.reserve(records.size());
        for(auto& r:records){
            r.candidate.id=r.id.c_str();r.candidate.context=context.c_str();r.candidate.model_id=models[r.model_index].id.c_str();
            r.candidate.evidence="本次LUT完整域与合成校准";candidates.push_back(r.candidate);
        }
        result.status=choose(candidates,p,context.c_str(),&view);
        if(result.status==fc::SelectionStatus::Ok){
            const auto& chosen=records[view.index];result.selected=true;result.candidate_index=view.index;
            result.options=execution_options(chosen.candidate,p);result.expected_info=chosen.info;
            result.expected_runtime_bytes=chosen.resources.runtime_bytes;
            // 返回已拟合模型，不重新拟合；其余候选模型和参考/校准缓冲在本函数结束时销毁。
            result.stages=models[chosen.model_index].stages;
        }else error=fc::selection_status_string(result.status);
    }catch(const std::exception& e){error=e.what();result.status=fc::SelectionStatus::NoFeasible;result.selected=false;}
    finish();return result;
}
} // namespace fc_framework
#endif
