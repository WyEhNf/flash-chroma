/* 完整LUT联合质量加权的box-QP、Lp IRLS与尾部再加权。 */
#ifndef FLASH_CHROMA_FRAMEWORK_PRECISION_FIT_HPP
#define FLASH_CHROMA_FRAMEWORK_PRECISION_FIT_HPP
#include "precision_search.hpp"
namespace fc_framework { namespace precision {
enum class Weight { Uniform, Lp6, Tail };
struct BoxReport {unsigned sweeps=0;double kkt=0;bool converged=false;std::size_t changed=0;};
// 每一行保留3×3×3邻居，因此三线性和分输出坐标无需降格成四面体。
inline Stage box_fit(const Stage& initial,const std::vector<Point>& points,Weight weighting,BoxReport& report,
                     unsigned max_sweeps=320,double tolerance=1e-7){
    if(points.empty()||!max_sweeps||!(tolerance>0))throw std::invalid_argument("box拟合参数非法");
    const auto model=detail::view(initial);const unsigned m=model.m;const auto n=initial.node_bytes()/3;
    Histogram h;for(const auto& p:points)h.add(p.error,p.mass);const unsigned threshold=h.quality().p99_squared;
    Stage result=initial;auto* output=result.blob.data()+(result.nodes_data()-result.blob.data());
    std::array<std::ptrdiff_t,27> delta{};
    for(int r=-1;r<=1;++r)for(int g=-1;g<=1;++g)for(int b=-1;b<=1;++b)
        delta[(r+1)*9+(g+1)*3+b+1]=r*int(m*m)+g*int(m)+b;
    report={};bool all=true;
    for(unsigned c=0;c<3;++c){
        std::vector<std::array<double,27>> matrix(n);std::vector<double> rhs(n),x(n),reg(n);
        for(const auto& p:points){const auto geometry_=geometry(model,initial.interpolation,p.rgb,c);
            double mass=p.mass;
            if(weighting==Weight::Lp6)mass*=std::pow(1.0+p.error/(1.0+threshold),2);
            if(weighting==Weight::Tail&&p.error>=threshold)mass*=32;
            const double scale=1.0/double(std::uint64_t{1}<<geometry_.shift);
            for(unsigned i=0;i<geometry_.count;++i){if(!geometry_.weight[i])continue;const auto a=geometry_.node[i];const double wi=geometry_.weight[i]*scale;
                rhs[a]+=mass*wi*component(p.target,c);
                for(unsigned j=0;j<geometry_.count;++j){const auto b=geometry_.node[j];
                    const int dr=int(b/(m*m))-int(a/(m*m)),dg=int(b/m%m)-int(a/m%m),db=int(b%m)-int(a%m);
                    matrix[a][(dr+1)*9+(dg+1)*3+db+1]+=mass*wi*(geometry_.weight[j]*scale);}}
        }
        for(std::size_t i=0;i<n;++i){x[i]=initial.nodes_data()[3*i+c];reg[i]=1e-5*(matrix[i][13]+1);rhs[i]+=reg[i]*x[i];matrix[i][13]+=reg[i];}
        double residual=INFINITY;unsigned sweeps=0;
        for(;sweeps<max_sweeps;++sweeps){
            for(std::size_t i=0;i<n;++i){double off=0;for(unsigned k=0;k<27;++k)if(k!=13&&matrix[i][k])off+=matrix[i][k]*x[std::size_t(std::ptrdiff_t(i)+delta[k])];
                x[i]=(std::max)(0.0,(std::min)(255.0,(rhs[i]-off)/matrix[i][13]));}
            residual=0;
            for(std::size_t i=0;i<n;++i){double gradient=-rhs[i];for(unsigned k=0;k<27;++k)if(matrix[i][k])gradient+=matrix[i][k]*x[std::size_t(std::ptrdiff_t(i)+delta[k])];
                const double projected=x[i]-(std::max)(0.0,(std::min)(255.0,x[i]-gradient/matrix[i][13]));residual=(std::max)(residual,std::abs(projected));}
            if(residual<=tolerance){++sweeps;break;}
        }
        report.sweeps=(std::max)(report.sweeps,sweeps);report.kkt=(std::max)(report.kkt,residual);all=all&&residual<=tolerance;
        for(std::size_t i=0;i<n;++i)output[3*i+c]=std::uint8_t(fit_detail::integer(x[i]));
    }
    report.converged=all;
    for(std::size_t i=0;i<n;++i)for(unsigned c=0;c<3;++c)report.changed+=output[3*i+c]!=initial.nodes_data()[3*i+c];
    if(report.changed)clear_proof(result);return result;
}
inline Stage fit_source_box(const std::vector<std::uint16_t>& raw,const Stage& stage,Weight weight,BoxReport& report){
    if(raw.size()!=dense_values)throw std::invalid_argument("独立box拟合需要完整LUT");
    const auto view=detail::view(stage);std::vector<Point> points(dense_nodes);
    for(std::uint32_t i=0;i<dense_nodes;++i){const auto target=source_color(raw,i);points[i]={i,target,1,distance(detail::map(view,stage.interpolation,i),target)};}
    return box_fit(stage,points,weight,report);
}
} }
#endif
