// final1：既有前中层精度算法与既有Direct运行内核的组合；不读取图像进行准备。
#ifndef ZMX_FINAL1_PIPELINE_HPP
#define ZMX_FINAL1_PIPELINE_HPP
#include "candidate.hpp"
#include <cstdio>

namespace fc_delivery {
inline fc_framework::FitOptions sampling_options() {
    fc_framework::FitOptions o; o.grid=fc_framework::Grid::FrameworkStep; o.prove_structure=false; return o;
}
template<class Lut>
bool sample(const std::vector<std::uint16_t>& raw,int size,Lut& output) {
    try { const auto s=fc_framework::prepare_stage(raw,unsigned(size),sampling_options());
        output.data.assign(s.nodes_data(),s.nodes_data()+s.node_bytes());output.size=int(s.m);return true;
    } catch(const std::exception& e){std::fprintf(stderr,"采样失败：%s\n",e.what());return false;}
}
template<class Lut>
class Pipeline {
    fc_framework::precision::Models stages_{};
    std::array<const Lut*,4> bindings_{};
    fc_framework::Chain chain_;
    fc_framework::FitReport fit_{};
    bool ready_=false;
    double fit_seconds_=0,search_seconds_=0,prepare_seconds_=0;
    std::string search_report_="{}";
public:
    bool prepare(const fc_framework::precision::Sources& raw,std::array<Lut,4>& models) {
        ready_=false; bindings_={};search_report_="{}";
        try {
            for(unsigned i=0;i<4;++i){
                stages_[i]=fc_framework::prepare_stage(raw[i],unsigned(models[i].size),sampling_options());
                if(models[i].data.size()!=stages_[i].node_bytes() || !std::equal(models[i].data.begin(),models[i].data.end(),stages_[i].nodes_data()))return false;
            }
            auto t=fc_framework::fit_detail::seconds();
            fc_framework::FitExperimentOptions fit_options;
            stages_[3]=fc_framework::fit_chain_last(raw,stages_,fit_,fit_options);
            fit_seconds_=fc_framework::fit_detail::seconds()-t;
            t=fc_framework::fit_detail::seconds();
            bool all33=true;for(const auto& s:stages_)all33&=s.m==33;
            if(all33){const auto gold=fc_framework::precision::truth(raw);
                stages_=candidate::run(raw,stages_,gold,"prefix_nodes",search_report_);}
            search_seconds_=fc_framework::fit_detail::seconds()-t;
            for(unsigned i=0;i<4;++i)models[i].data.assign(stages_[i].nodes_data(),stages_[i].nodes_data()+stages_[i].node_bytes());
            std::array<const fc_framework::Stage*,4> pointers{{&stages_[0],&stages_[1],&stages_[2],&stages_[3]}};
            fc_framework::Options o;o.backend=fc::Backend::Auto;o.structure=false;o.threads=1;
            o.representation=FLASH_CHROMA_ENABLE_DIRECT?fc::Representation::DirectRGB24:fc::Representation::Sparse;
            o.block_pixels=65536;o.max_workspace_bytes=64*fc::MiB;
            t=fc_framework::fit_detail::seconds();
            auto status=chain_.prepare(pointers,o);
            if(status!=fc::Status::Ok && o.representation==fc::Representation::DirectRGB24){o.representation=fc::Representation::Sparse;status=chain_.prepare(pointers,o);}
            prepare_seconds_=fc_framework::fit_detail::seconds()-t;
            if(status!=fc::Status::Ok)return false;
            for(unsigned i=0;i<4;++i)bindings_[i]=&models[i];ready_=true;return true;
        }catch(const std::exception& e){std::fprintf(stderr,"final1准备失败：%s\n",e.what());return false;}
    }
    template<class Image>
    bool apply(const Image& source,const Lut& l1,const Lut& l2,const Lut& l3,const Lut& l4,Image& output)const{
        if(!ready_||source.C!=3||source.H<=0||source.W<=0||bindings_!=std::array<const Lut*,4>{{&l1,&l2,&l3,&l4}}||
           output.H!=source.H||output.W!=source.W||output.C!=source.C||source.data.size()!=source.size()||output.data.size()!=source.size())return false;
        return chain_.apply(source.ptr(),output.ptr(),std::size_t(source.H)*source.W)==fc::Status::Ok;
    }
    const auto& stages()const noexcept{return stages_;}
    const auto& info()const noexcept{return chain_.info();}
    const auto& fit_report()const noexcept{return fit_;}
    const auto& search_report()const noexcept{return search_report_;}
    double fit_seconds()const noexcept{return fit_seconds_;}
    double search_seconds()const noexcept{return search_seconds_;}
    double prepare_seconds()const noexcept{return prepare_seconds_;}
};
}
#endif
