/* 赛事偏好合同：使用合成候选、人工计时序列与小型节点模型。
 * 不读取图片，不构造完整稠密LUT，也不执行性能测量。
 */
#define FLASH_CHROMA_IMPLEMENTATION
#include "preference_selection.hpp"
#include <cstdio>
#include <cstdlib>
#include <limits>

namespace {
namespace pd = fc_framework::preference_detail;
using Preferences = fc_framework::PreferenceOptions;
constexpr const char* context = "仅供合同的固定LUT身份";
std::size_t checks = 0;

void require(bool condition, const char* message) {
    ++checks;
    if (!condition) { std::fprintf(stderr, "赛事偏好合同失败：%s\n", message); std::exit(1); }
}
void near(double actual, double expected, const char* message) {
    require(std::isfinite(actual) && std::abs(actual - expected) < 1e-12, message);
}
fc::Candidate candidate(const char* id, double error, double time, std::size_t ram) {
    fc::Candidate result;
    result.id = id; result.context = context; result.model_id = id; result.evidence = "合成指标，不授实测资格";
    result.config.target = fc::Target::Desktop; result.config.backend = fc::Backend::Scalar;
    result.config.threads = 1; result.config.block_pixels = 19;
    result.mean_error = error; result.worst_image_mean = error + 4;
    result.batch_ms = time; result.runtime_bytes = ram; result.workspace_bytes = ram / 10;
    result.correctness_verified = result.accuracy_verified = result.resources_verified = true;
    result.time_verified = result.time_stable = true;
    return result;
}
std::vector<fc::Candidate> points() {
    return {candidate("accuracy", 1, 9, 900), candidate("speed", 9, 1, 900), candidate("compact", 9, 9, 100)};
}
std::size_t selected(const std::vector<fc::Candidate>& candidates, const Preferences& preferences) {
    fc::SelectionView result;
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::Ok,
            "合法合成候选必须能选出计划");
    return result.index;
}

void continuous_preference_contract() {
    const auto candidates = points(); Preferences preferences;
    require(pd::validate(preferences).empty(), "缺省偏好必须合法");
    preferences.weights = {1, 0, 0}; require(selected(candidates, preferences) == 0, "A偏好必须改变选中的模型");
    preferences.weights = {0, 1, 0}; require(selected(candidates, preferences) == 1, "B偏好必须选速度候选");
    preferences.weights = {0, 0, 1}; require(selected(candidates, preferences) == 2, "C偏好必须选低RAM候选");
    // 使用接近分界的任意实数，避免把三个预设档伪装成连续接口。
    preferences.weights = {.500001, .499999, 0}; require(selected(candidates, preferences) == 0, "分界左侧权重失效");
    preferences.weights = {.499999, .500001, 0}; require(selected(candidates, preferences) == 1, "分界右侧权重失效");
    preferences.weights = {.1, .1, .8}; require(selected(candidates, preferences) == 2, "三维共同参与评分");
    preferences.weights = {.1, .2, .3}; fc::SelectionView first;
    require(pd::choose(candidates, preferences, context, &first) == fc::SelectionStatus::Ok, "归一化首次选择失败");
    preferences.weights = {.2, .4, .6}; fc::SelectionView second;
    require(pd::choose(candidates, preferences, context, &second) == fc::SelectionStatus::Ok && first.index == second.index,
            "权重同比缩放不得改变赢家");
    near(first.score, second.score, "权重归一化不得重复或遗漏");
}

void hard_budget_contract() {
    const auto candidates = points(); Preferences preferences; preferences.weights = {1, 0, 0};
    preferences.max_runtime_bytes = 100;
    require(selected(candidates, preferences) == 2, "RAM硬上限必须优先于A偏好");
    preferences.max_runtime_bytes = 99; fc::SelectionView result;
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::NoFeasible &&
            result.index == (std::numeric_limits<std::size_t>::max)(), "无RAM可行解不得回退到超预算候选");
    preferences.max_runtime_bytes = 1000; preferences.max_workspace_bytes = 10;
    require(selected(candidates, preferences) == 2, "workspace硬上限必须与总RAM分别约束");
    preferences.max_workspace_bytes = 9;
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::NoFeasible,
            "无工作区可行解必须明确失败");
    preferences.max_workspace_bytes = 1000; preferences.max_domain_mean = 1;
    preferences.max_pixel_error = 5;
    require(selected(candidates, preferences) == 0, "全域mean/max预算边界应包含等号");
    preferences.max_domain_mean = std::nextafter(1.0, 0.0);
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::NoFeasible,
            "全域mean超限一浮点步亦不能接受");
    preferences.max_domain_mean = 1; preferences.max_pixel_error = std::nextafter(5.0, 0.0);
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::NoFeasible,
            "逐色max超限不可被平均值掩盖");
    preferences.max_domain_mean.reset(); preferences.max_pixel_error.reset();
    preferences.max_ms_per_megapixel = 2;
    require(selected(candidates, preferences) == 1, "每百万像素预算必须正确换算至校准像素数");
    const auto request = pd::make_request(preferences, context);
    near(request.max_batch_ms, 2.0 * 786432 / 1000000, "ms/MP预算被错误缩放");
    preferences.max_ms_per_megapixel = 0;
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::NoFeasible,
            "零时间预算不能静默撤销");
    preferences = Preferences{};
    require(pd::choose({}, preferences, context, &result) == fc::SelectionStatus::NoFeasible,
            "空候选目录不得产生虚构计划");
}

void invalid_request_contract() {
    const auto candidates = points(); const double nan = std::numeric_limits<double>::quiet_NaN();
    const double inf = std::numeric_limits<double>::infinity();
    for (const auto& weights : std::vector<fc::Preference>{{0,0,0}, {nan,0,1}, {0,inf,1}, {0,1,nan},
                                                        {-0.1,1,0}, {0,0,1.000001}}) {
        Preferences preferences; preferences.weights = weights; fc::SelectionView result;
        require(!pd::validate(preferences).empty(), "NaN/Inf/负数/超范围/全零权重必须拒绝");
        require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::InvalidRequest,
                "选择入口必须自行验证权重，不能依赖CLI");
    }
    for (double value : {nan, inf, -1.0}) for (unsigned field = 0; field < 3; ++field) {
        Preferences preferences;
        if (field == 0) preferences.max_domain_mean = value;
        else if (field == 1) preferences.max_pixel_error = value;
        else preferences.max_ms_per_megapixel = value;
        require(!pd::validate(preferences).empty(), "非法质量/时间预算必须拒绝");
    }
    for (unsigned value : {0u, 2u, 4u, 32u, 33u}) {
        Preferences preferences; preferences.calibration_repetitions = value;
        require(!pd::validate(preferences).empty(), "非法或偶数校准次数必须拒绝");
    }
    Preferences preferences; preferences.sizes = {{{17,17,16,17}}};
    require(!pd::validate(preferences).empty(), "混合m中的单级越界不能漏过");
    preferences = Preferences{}; preferences.block_pixels = 0;
    require(!pd::validate(preferences).empty(), "零工作块必须拒绝");
}

bool rejected_control(const std::vector<double>& a, const std::vector<double>& b, double limit) {
    try { return !pd::control(a, b, limit).passed; }
    catch (const std::exception&) { return true; }
}
void timing_qualification_contract() {
    const auto good = pd::control({9,1,4,5,3}, {5,4,6,3,7}, .3);
    near(good.median_a_ms, 4, "第一组中位数错误"); near(good.median_b_ms, 5, "第二组中位数错误");
    near(good.relative_drift, .25, "A/A漂移应除较小中位数"); require(good.passed, "允许范围内漂移应通过");
    require(!pd::control({9,1,4,5,3}, {5,4,6,3,7}, .2).passed, "超限漂移不能授稳定资格");
    require(rejected_control({}, {}, .05), "空计时不能通过");
    require(rejected_control({1}, {1,1}, .05), "次数不一致不能通过");
    require(rejected_control({1,0,1}, {1,1,1}, .05), "零计时不能通过");
    require(rejected_control({1,-1,1}, {1,1,1}, .05), "负计时不能通过");
    require(rejected_control({1,std::numeric_limits<double>::quiet_NaN(),1}, {1,1,1}, .05), "NaN计时不能通过");
    require(rejected_control({1,1,1}, {1,std::numeric_limits<double>::infinity(),1}, .05), "Inf计时不能通过");
    for (double limit : {-1.0, 1.0, std::numeric_limits<double>::quiet_NaN()})
        require(rejected_control({1,1,1}, {1,1,1}, limit), "非法漂移上限不能通过");
    auto candidates = points(); for (auto& item : candidates) item.time_stable = false;
    Preferences preferences; preferences.weights = {0,1,0}; fc::SelectionView result;
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::NoFeasible,
            "默认不得在全部时序漂移失败时仍选择稳定方案");
    preferences.allow_unstable = true;
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::Ok && result.provisional,
            "显式允许漂移仍须保留临时资格标记");
    for (auto& item : candidates) { item.time_verified = false; item.batch_ms = std::numeric_limits<double>::quiet_NaN(); }
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::NoFeasible,
            "允许漂移不等于允许缺少时间证据");
    preferences.weights = {1,0,0}; preferences.allow_unstable = false;
    require(pd::choose(candidates, preferences, context, &result) == fc::SelectionStatus::Ok && result.provisional,
            "纯精度选择可不计时，但不能伪造性能资格");
}

void resource_accounting_contract() {
    fc_framework::Info info;
    info.model_bytes = 101; info.arena_bytes = 211; info.object_bytes = 401; info.sidecar_bytes = 37;
    const auto accounted = pd::account_resources(info, 503);
    const auto owner_estimate = 4 * (sizeof(std::shared_ptr<fc_framework::Stage>) + 2 * sizeof(void*));
    require(accounted.wrapper_nodes_bytes == 503 && accounted.shared_ownership_estimate_bytes == owner_estimate,
            "原框架节点副本及共享控制块估算必须单独记账");
    require(accounted.runtime_bytes == 101 + 211 + 401 + 503 + owner_estimate,
            "C轴总RAM必须包含模型、arena、对象、框架副本和控制块");
    info.sidecar_bytes = 83;
    require(pd::account_resources(info, 503).runtime_bytes == accounted.runtime_bytes,
            "sidecar已是对象内子集，不得重复加总");
    info.model_bytes = (std::numeric_limits<std::size_t>::max)();
    bool overflow = false;
    try { (void)pd::account_resources(info, 503); } catch (const std::overflow_error&) { overflow = true; }
    require(overflow, "资源总和溢出不得绕回低RAM并通过预算");
}

fc_framework::Stage constant_stage(unsigned m, const std::array<std::uint8_t,3>& color) {
    fc_framework::Stage stage; stage.m = m;
    const std::size_t indices = 16 + 12 * m, fractions = indices + 768, nodes = fractions + 3072;
    stage.blob.resize(nodes + std::size_t(m) * m * m * 3);
    auto& bytes = stage.blob;
    bytes[0]='S'; bytes[1]='L'; bytes[2]='U'; bytes[3]='T';
    fc_framework::detail::put32(bytes,4,1); fc_framework::detail::put32(bytes,8,m);
    for (unsigned axis=0; axis<3; ++axis) {
        std::vector<unsigned> knots(m);
        for (unsigned i=0; i<m; ++i) {
            knots[i] = (i*255+(m-1)/2)/(m-1); const float knot = static_cast<float>(knots[i]);
            std::uint32_t bits; std::memcpy(&bits,&knot,4); fc_framework::detail::put32(bytes,16+(axis*m+i)*4,bits);
        }
        for (unsigned code=0; code<256; ++code) {
            unsigned cell=0; while(cell+2<m && knots[cell+1]<=code) ++cell;
            const unsigned width=knots[cell+1]-knots[cell];
            bytes[indices+axis*256+code]=static_cast<std::uint8_t>(cell);
            fc_framework::detail::put32(bytes,fractions+(axis*256+code)*4,((code-knots[cell])*65536+width/2)/width);
        }
    }
    for (std::size_t i=nodes; i<bytes.size(); ++i) bytes[i]=color[(i-nodes)%3];
    return stage;
}

void selected_plan_execution_contract() {
    auto candidates = points(); Preferences preferences; preferences.structure = false;
    const std::array<std::array<std::uint8_t,3>,3> colors{{{{3,71,149}},{{251,17,80}},{{47,128,6}}}};
    std::array<fc_framework::Stage,3> models{{constant_stage(17,colors[0]),constant_stage(19,colors[1]),constant_stage(21,colors[2])}};
    const std::array<fc::Preference,3> weights{{{1,0,0},{0,1,0},{0,0,1}}};
    std::vector<std::uint8_t> input(257*3), output(input.size());
    for (std::size_t i=0; i<input.size(); ++i) input[i]=static_cast<std::uint8_t>(i*73+19);
    for (unsigned wanted=0; wanted<3; ++wanted) {
        preferences.weights = weights[wanted]; const auto index=selected(candidates,preferences);
        const auto options=pd::execution_options(candidates[index],preferences);
        require(options.backend==candidates[index].config.backend && options.representation==candidates[index].config.representation &&
                options.threads==1 && options.block_pixels==candidates[index].config.block_pixels && !options.structure,
                "选中执行参数不得丢失或回退到缺省配置");
        fc_framework::Chain chain; const auto* stage=&models[index];
        require(chain.prepare({{stage,stage,stage,stage}},options)==fc::Status::Ok, "选中小型Stage计划无法准备");
        require(chain.info().backend==candidates[index].config.backend && chain.info().representation==candidates[index].config.representation,
                "实际准备后端/表示必须与选择结果一致");
        require(chain.apply(input.data(),output.data(),257)==fc::Status::Ok, "选中计划不能执行");
        for (std::size_t i=0; i<output.size(); ++i)
            require(output[i]==colors[wanted][i%3], "最终像素不是选中模型的独立解析结果");
    }
}
}

int main() {
    continuous_preference_contract(); hard_budget_contract(); invalid_request_contract();
    timing_qualification_contract(); resource_accounting_contract(); selected_plan_execution_contract();
    std::printf("赛事偏好轻量合同通过：%zu项；合成指标/Q16小型执行，不读取图片、不授性能资格。\n", checks);
    return 0;
}
