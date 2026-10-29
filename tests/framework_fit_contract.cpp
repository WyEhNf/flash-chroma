// 可选拟合的格式兼容、收敛与门控报告契约；不进行性能测量。
#define main framework_benchmark_embedded_main
#include "../framework/benchmark.cpp"
#undef main

void require_fit(bool condition,const char* message){if(!condition)throw std::runtime_error(message);}
int main(){try{
    const std::string old="old,33,33,33,33,uniform,0,2,0,65536,134217728";
    require_fit(parse_spec(old).fit=="sample","11项旧格式默认值改变");
    for(const auto* mode:{"sample","independent_ls","chain_ls"})
        require_fit(parse_spec(old+','+mode).fit==mode,"第12项拟合解析失败");
    for(const auto* suffix:{",unknown",",sample,extra"}){
        bool rejected=false;try{(void)parse_spec(old+suffix);}catch(const std::runtime_error&){rejected=true;}
        require_fit(rejected,"非法拟合模式或额外字段未拒绝");
    }
    // 人工构造已知解的对称正定15邻居矩阵，核对预条件CG实际残差。
    fc_framework::fit_detail::Coordinates coords = []{
        fc_framework::Stage stage;stage.m=17;
        // 只构造坐标所需的合法模型；采样源是图像无关的全零LUT。
        const std::vector<std::uint16_t> raw(fc_framework::dense_values);
        fc_framework::FitOptions options;options.prove_structure=false;
        stage=fc_framework::prepare_stage(raw,17,options);
        return fc_framework::fit_detail::Coordinates(stage);
    }();
    fc_framework::fit_detail::Normal matrix(coords);
    std::vector<std::array<double,3>> initial(matrix.count);
    std::vector<double> truth(matrix.count),reg(matrix.count),rhs;
    fc_framework::FitExperimentOptions options;
    for(std::size_t i=0;i!=matrix.count;++i){matrix.h[i][0]=4;truth[i]=double(i%251);reg[i]=options.regularization*5;
        if(i+1<matrix.count)matrix.h[i][1]=.25;}
    matrix.multiply(truth,rhs,reg);
    for(std::size_t i=0;i!=matrix.count;++i)matrix.rhs[i][0]=rhs[i];
    fc_framework::FitChannelReport convergence;
    const auto solved=fc_framework::fit_detail::solve_channel(matrix,0,initial,options,convergence);
    require_fit(convergence.converged,"人工SPD求解未收敛");
    for(std::size_t i=0;i!=matrix.count;++i)require_fit(std::abs(solved[i]-truth[i])<1e-4,"人工SPD已知解不符");
    Candidate c;c.spec.fit="independent_ls";c.model=std::make_shared<PreparedModels>();
    c.model->reports[0].source_separable_skipped=true;
    std::ostringstream report;fit_reports(report,c);
    require_fit(report.str().find("\"baseline\":null")!=std::string::npos,"未测全域不得报告为零误差");
    require_fit(report.str().find("\"full_domain_guard_passed\":null")!=std::string::npos,"跳过不能冒充通过门控");
    std::cout<<"拟合格式兼容、已知解CG、报告门控契约通过。\n";return 0;
}catch(const std::exception& e){std::cerr<<"拟合契约失败："<<e.what()<<'\n';return 1;}}
