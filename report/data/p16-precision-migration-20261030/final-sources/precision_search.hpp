/* 完整LUT域的联合支撑、真实整数后缀重放与固定锚点门控；不接受照片频数。 */
#ifndef FLASH_CHROMA_FRAMEWORK_PRECISION_SEARCH_HPP
#define FLASH_CHROMA_FRAMEWORK_PRECISION_SEARCH_HPP
#include "precision_geometry.hpp"
#include <functional>

namespace fc_framework { namespace precision {
constexpr unsigned max_error_squared=3*255*255;
struct Roots {
    std::vector<double> value;
    std::vector<std::uint64_t> lower,upper;
    Roots():value(max_error_squared+1),lower(value.size()),upper(value.size()){
        for(unsigned d=0;d<value.size();++d){value[d]=std::sqrt(double(d));
            // 逐二进制数位开方；d*2^48需66位，余数及根始终装入64位。
            std::uint64_t q=0,remainder=0;
            for(int bit=32;bit>=0;--bit){remainder=(remainder<<2)|(bit>=24?((d>>(2*(bit-24)))&3u):0u);
                q<<=1;const auto trial=(q<<1)|1u;if(remainder>=trial){remainder-=trial;++q;}}
            lower[d]=q;upper[d]=q+(remainder!=0);}
    }
};
inline const Roots& roots(){static const Roots r;return r;}
struct Quality {std::uint64_t pixels=0,sse=0;double mean=0,rms=0,p99=0,max=0,cvar=0;unsigned p99_squared=0,p99_upper_squared=0,p99_weight=0,max_squared=0;};
struct Histogram {
    std::vector<std::uint64_t> count;
    std::uint64_t total=0,sse=0;
    unsigned largest=0;
    Histogram():count(max_error_squared+1){}
    void add(unsigned d,std::uint64_t n){count.at(d)+=n;total+=n;sse+=std::uint64_t(d)*n;largest=(std::max)(largest,d);}
    void remove(unsigned d,std::uint64_t n){if(d>=count.size()||count[d]<n)throw std::runtime_error("误差直方图增量下溢");count[d]-=n;total-=n;sse-=std::uint64_t(d)*n;while(largest&&count[largest]==0)--largest;}
    Quality quality()const{
        Quality q;q.pixels=total;q.sse=sse;if(!total)return q;
        long double sum=0,tail=0;std::uint64_t accumulated=0,remaining=(total+99)/100;
        const std::uint64_t rank=99*(total-1)/100;q.p99_weight=unsigned(99*(total-1)%100);bool low=false,high=false;
        for(unsigned d=0;d<=largest;++d){sum+=static_cast<long double>(count[d])*roots().value[d];accumulated+=count[d];
            if(!low&&accumulated>rank){q.p99_squared=d;low=true;}
            if(!high&&accumulated>rank+(q.p99_weight!=0)){q.p99_upper_squared=d;high=true;}}
        for(unsigned d=largest;;--d){const auto n=(std::min)(remaining,count[d]);tail+=static_cast<long double>(n)*roots().value[d];remaining-=n;if(!remaining||!d)break;}
        q.mean=double(sum/total);q.rms=std::sqrt(double(sse)/total);q.p99=(roots().value[q.p99_squared]*(100-q.p99_weight)+roots().value[q.p99_upper_squared]*q.p99_weight)/100;q.max_squared=largest;q.max=roots().value[largest];q.cvar=double(tail/((total+99)/100));return q;
    }
};
// 用相同误差桶抵消后再作Q24上下界比较，避免依赖浮点mean最后一位。
inline bool certified_mean_leq(const Histogram& a,const Histogram& b){
    if(a.total!=b.total)return false;
    std::int64_t upper=0;
    for(unsigned d=0;d<=(std::max)(a.largest,b.largest);++d){const auto delta=std::int64_t(a.count[d])-std::int64_t(b.count[d]);
        upper+=delta*std::int64_t(delta>=0?roots().upper[d]:roots().lower[d]);}
    return upper<=0;
}
enum class Objective { Mean, Maximum, P99, CVaR, Lp };
struct Guard {bool mean=true,sse=true,maximum=true,p99=true,cvar=true,pointwise=false;};
inline bool certified_tail_leq(const Histogram& a,const Histogram& b){
    if(a.total!=b.total)return false;std::uint64_t left=(a.total+99)/100,right=left;std::int64_t upper=0;
    for(int d=int((std::max)(a.largest,b.largest));d>=0&&(left||right);--d){const auto na=(std::min)(left,a.count[d]),nb=(std::min)(right,b.count[d]);left-=na;right-=nb;
        const auto delta=std::int64_t(na)-std::int64_t(nb);upper+=delta*std::int64_t(delta>=0?roots().upper[d]:roots().lower[d]);}
    return upper<=0;
}
inline bool accepts(const Histogram& candidate,const Histogram& anchor,const Guard& guard){
    if(candidate.total!=anchor.total||!candidate.total)return false;
    if(guard.mean&&!certified_mean_leq(candidate,anchor))return false;
    if(guard.sse&&candidate.sse>anchor.sse)return false;
    if(guard.maximum&&candidate.largest>anchor.largest)return false;
    if(guard.p99||guard.cvar){const auto c=candidate.quality(),a=anchor.quality();
        if(guard.p99){if(c.p99_squared>a.p99_squared||c.p99_upper_squared>a.p99_upper_squared){
            Histogram ch,ah;ch.add(c.p99_squared,100-c.p99_weight);ch.add(c.p99_upper_squared,c.p99_weight);
            ah.add(a.p99_squared,100-a.p99_weight);ah.add(a.p99_upper_squared,a.p99_weight);if(!certified_mean_leq(ch,ah))return false;}}
        if(guard.cvar&&!certified_tail_leq(candidate,anchor))return false;}
    return true;
}
inline long double lp(const Histogram& h){long double value=0;for(unsigned i=0;i<=h.largest;++i)value+=static_cast<long double>(h.count[i])*i*i*i;return value;}
inline bool better(const Histogram& a,const Histogram& b,Objective objective){
    const auto x=a.quality(),y=b.quality();
    if(objective==Objective::Maximum&&x.max_squared!=y.max_squared)return x.max_squared<y.max_squared;
    if(objective==Objective::P99&&x.p99!=y.p99)return x.p99<y.p99;
    if(objective==Objective::CVaR&&std::abs(x.cvar-y.cvar)>1e-12)return x.cvar<y.cvar;
    if(objective==Objective::Lp){const auto l=lp(a),r=lp(b);if(l!=r)return l<r;}
    if(x.mean<y.mean-1e-12)return certified_mean_leq(a,b);
    return std::abs(x.mean-y.mean)<=1e-12&&a.sse<b.sse;
}
inline unsigned distance(std::uint32_t a,std::uint32_t b){unsigned d=0;for(unsigned c=0;c<3;++c){const int e=int(component(a,c))-int(component(b,c));d+=unsigned(e*e);}return d;}
inline std::vector<std::uint32_t> truth(const Sources& raw){
    for(const auto& s:raw)if(s.size()!=dense_values)throw std::invalid_argument("精度准备需要四张完整LUT");
    std::vector<std::uint32_t> result(dense_nodes);
    for(std::uint32_t i=0;i<dense_nodes;++i){auto v=i;for(const auto& s:raw)v=source_color(s,v);result[i]=v;}return result;
}
inline Histogram evaluate(const Models& models,const std::vector<std::uint32_t>& gold){
    if(gold.size()!=dense_nodes)throw std::invalid_argument("完整域参考长度不符");
    const Evaluator evaluator(models);Histogram h;
    for(std::uint32_t i=0;i<dense_nodes;++i)h.add(distance(evaluator.map(i),gold[i]),1);return h;
}
struct Point {std::uint32_t rgb,target,mass,error,local_error=0;};
struct Support {
    std::vector<Point> points;
    std::vector<std::uint32_t> suffix;
    Histogram histogram;
    unsigned stage=0;
    const std::vector<std::uint16_t>* local_source=nullptr;double local_weight=0;
    Support(const Models& models,const std::vector<std::uint32_t>& gold,unsigned stage_index,
            const std::vector<std::uint16_t>* source=nullptr,double weight=0):stage(stage_index),local_source(source),local_weight(weight){
        if(stage>=4||gold.size()!=dense_nodes)throw std::invalid_argument("联合支撑阶段或参考非法");
        if(!std::isfinite(weight)||weight<0||(weight&&(!source||source->size()!=dense_values)))throw std::invalid_argument("本级加后缀双目标参数非法");
        Evaluator e(models);std::vector<std::uint64_t> pairs(dense_nodes);
        for(std::uint32_t i=0;i<dense_nodes;++i)pairs[i]=std::uint64_t(e.map(i,0,stage))|(std::uint64_t(gold[i])<<24);
        std::sort(pairs.begin(),pairs.end());
        for(std::size_t i=0;i<pairs.size();){std::size_t j=i+1;while(j<pairs.size()&&pairs[j]==pairs[i])++j;
            points.push_back({std::uint32_t(pairs[i]&0xffffffu),std::uint32_t(pairs[i]>>24),std::uint32_t(j-i),0});i=j;}
        std::vector<std::uint64_t>().swap(pairs);
        if(stage!=3){suffix.resize(dense_nodes);for(std::uint32_t i=0;i<dense_nodes;++i)suffix[i]=e.map(i,stage+1);}
        const auto view=detail::view(models[stage]);
        for(auto& p:points){auto output=detail::map(view,models[stage].interpolation,p.rgb);if(local_weight)p.local_error=distance(output,source_color(*local_source,p.rgb));if(!suffix.empty())output=suffix[output];
            p.error=distance(output,p.target);histogram.add(p.error,p.mass);}
        if(histogram.total!=dense_nodes)throw std::runtime_error("联合支撑丢失完整域质量");
    }
    unsigned error(const Stage& model,const Point& point)const{
        const auto m=detail::view(model);auto output=detail::map(m,model.interpolation,point.rgb);
        if(!suffix.empty())output=suffix[output];return distance(output,point.target);
    }
};
struct SearchReport {std::uint64_t support_rows=0,proposals=0,accepted=0;Quality before{},after{};};
// 同一候选先计算全部受影响支撑，再事务式更新直方图；拒绝时逐项恢复。
inline bool trial(Stage& model,Support& support,const std::vector<std::uint32_t>& affected,
                  const Histogram& anchor,const std::vector<unsigned>& caps,const Guard& guard,
                  Objective objective,std::vector<unsigned>& errors){
    errors.clear();errors.reserve(affected.size());const auto view=detail::view(model);std::vector<unsigned> local_errors;long double joint_delta=0;
    for(auto i:affected){const auto& p=support.points[i];auto output=detail::map(view,model.interpolation,p.rgb);
        if(support.local_weight){const auto d=distance(output,source_color(*support.local_source,p.rgb));local_errors.push_back(d);joint_delta+=p.mass*support.local_weight*(roots().value[d]-roots().value[p.local_error]);}
        if(!support.suffix.empty())output=support.suffix[output];
        const unsigned d=distance(output,p.target);if(guard.pointwise&&d>caps[i])return false;errors.push_back(d);joint_delta+=p.mass*(roots().value[d]-roots().value[p.error]);}
    if(support.local_weight&&joint_delta>0)return false;
    Histogram before=support.histogram;
    for(std::size_t k=0;k<affected.size();++k){const auto& p=support.points[affected[k]];support.histogram.remove(p.error,p.mass);support.histogram.add(errors[k],p.mass);}
    const bool take=accepts(support.histogram,anchor,guard)&&better(support.histogram,before,objective);
    if(take){for(std::size_t k=0;k<affected.size();++k){support.points[affected[k]].error=errors[k];if(support.local_weight)support.points[affected[k]].local_error=local_errors[k];}}
    else support.histogram=std::move(before);
    return take;
}
inline SearchReport optimize_nodes(Models& models,const std::vector<std::uint32_t>& gold,unsigned stage,
                                  const Histogram& anchor,const Guard& guard,Objective objective,unsigned budget=128,unsigned sweeps=1,
                                  const std::vector<std::uint16_t>* source=nullptr,double local_weight=0){
    Support support(models,gold,stage,source,local_weight);SearchReport report;report.support_rows=support.points.size();report.before=support.histogram.quality();
    auto& model=models[stage];auto view=detail::view(model);const auto nodes=model.node_bytes()/3;
    std::vector<long double> score(nodes);std::vector<unsigned> caps;caps.reserve(support.points.size());
    for(const auto& p:support.points){caps.push_back(p.error);for(unsigned c=0;c<3;++c){const auto g=geometry(view,model.interpolation,p.rgb,c);
        for(unsigned k=0;k<g.count;++k)if(g.weight[k])score[g.node[k]]+=static_cast<long double>(p.mass)*p.error*double(g.weight[k])/double(std::uint64_t{1}<<g.shift);}}
    std::vector<std::size_t> order(nodes);std::iota(order.begin(),order.end(),0);
    std::stable_sort(order.begin(),order.end(),[&](auto a,auto b){return score[a]>score[b];});
    order.resize((std::min)(std::size_t(budget),nodes));while(!order.empty()&&score[order.back()]==0)order.pop_back();
    std::vector<int> selected(nodes,-1);for(std::size_t i=0;i<order.size();++i)selected[order[i]]=int(i);
    std::vector<std::vector<std::uint32_t>> links(order.size());
    for(std::uint32_t i=0;i<support.points.size();++i){std::array<std::size_t,24> seen{};unsigned n=0;
        for(unsigned c=0;c<3;++c){const auto g=geometry(view,model.interpolation,support.points[i].rgb,c);for(unsigned k=0;k<g.count;++k)if(g.weight[k]&&selected[g.node[k]]>=0){
            if(std::find(seen.begin(),seen.begin()+n,g.node[k])==seen.begin()+n){seen[n++]=g.node[k];links[selected[g.node[k]]].push_back(i);}}}}
    std::vector<unsigned> errors;auto* bytes=model.blob.data()+(model.nodes_data()-model.blob.data());
    for(unsigned sweep=0;sweep<sweeps;++sweep)for(std::size_t k=0;k<order.size();++k){const auto node=order[k];
        for(int step:{1,2,4})for(int r=-1;r<=1;++r)for(int g=-1;g<=1;++g)for(int b=-1;b<=1;++b){if(!r&&!g&&!b)continue;
            const int delta[3]={r*step,g*step,b*step};std::array<std::uint8_t,3> old;bool valid=true;
            for(unsigned c=0;c<3;++c){old[c]=bytes[node*3+c];const int value=int(old[c])+delta[c];if(value<0||value>255)valid=false;}
            if(!valid)continue;for(unsigned c=0;c<3;++c)bytes[node*3+c]=std::uint8_t(int(old[c])+delta[c]);++report.proposals;
            if(trial(model,support,links[k],anchor,caps,guard,objective,errors)){++report.accepted;clear_proof(model);}
            else for(unsigned c=0;c<3;++c)bytes[node*3+c]=old[c];
        }
    }
    report.after=support.histogram.quality();return report;
}
inline SearchReport calibrate_coordinates(Models& models,const std::vector<std::uint32_t>& gold,unsigned stage,
                                         const Histogram& anchor,const Guard& guard,Objective objective,unsigned budget=64,bool per_output=true,
                                         const std::vector<std::uint16_t>* source=nullptr,double local_weight=0){
    auto& model=models[stage];if(!per_output&&!model.fractions.empty())throw std::invalid_argument("共享坐标校准须在分输出坐标之前");if(per_output)initialize_sidecar(model);
    Support support(models,gold,stage,source,local_weight);SearchReport report;report.support_rows=support.points.size();report.before=support.histogram.quality();
    const unsigned channels=per_output?3:1;const auto view=detail::view(model);
    std::vector<long double> score(channels*768);std::vector<unsigned> caps;caps.reserve(support.points.size());
    for(const auto& p:support.points){caps.push_back(p.error);for(unsigned c=0;c<channels;++c)for(unsigned a=0;a<3;++a)score[c*768+a*256+component(p.rgb,a)]+=static_cast<long double>(p.error)*p.mass;}
    std::vector<unsigned> order(score.size());std::iota(order.begin(),order.end(),0);
    std::stable_sort(order.begin(),order.end(),[&](unsigned a,unsigned b){return score[a]>score[b];});order.resize((std::min)(order.size(),std::size_t(budget)));
    std::vector<unsigned> errors;std::vector<std::uint32_t> affected;
    for(auto coordinate:order){if(score[coordinate]==0)continue;const unsigned c=coordinate/768,a=coordinate/256%3,v=coordinate%256;
        affected.clear();for(std::uint32_t i=0;i<support.points.size();++i)if(component(support.points[i].rgb,a)==v)affected.push_back(i);
        const unsigned cell=view.index[a*256+v];
        auto* f=per_output?model.fractions.data()+c*3072:model.blob.data()+16+12*model.m+768;
        const auto read=[&](unsigned x){return fc_core::fc_detail_read32(f+(a*256+x)*4);};
        const unsigned low=v&&view.index[a*256+v-1]==cell?read(v-1):0;
        const unsigned high=v<255&&view.index[a*256+v+1]==cell?read(v+1):65536;
        for(int magnitude:{4096,1024,256,64,16,4,1})for(int sign:{-1,1}){
            const auto old=read(v);const int proposed=int(old)+sign*magnitude;if(proposed<int(low)||proposed>int(high))continue;
            auto& bytes=per_output?model.fractions:model.blob;const std::size_t offset=per_output?c*3072+(a*256+v)*4:16+12*model.m+768+(a*256+v)*4;
            detail::put32(bytes,offset,unsigned(proposed));++report.proposals;
            if(trial(model,support,affected,anchor,caps,guard,objective,errors)){++report.accepted;clear_proof(model);}
            else detail::put32(bytes,offset,old);
        }
    }
    report.after=support.histogram.quality();return report;
}
struct BoxVariable {std::size_t node;unsigned channel;int radius;};
// 穷举冻结整数箱；预算不足直接拒绝，不把局部搜索冒称箱内最优。
inline SearchReport exact_integer_box(Models& models,const std::vector<std::uint32_t>& gold,unsigned stage,
                                     const std::vector<BoxVariable>& variables,const Histogram& anchor,const Guard& guard,
                                     Objective objective,std::uint64_t max_assignments=100000){
    if(stage>=4||variables.empty())throw std::invalid_argument("整数箱必须非空且指定合法级");
    auto& model=models[stage];auto* bytes=model.blob.data()+(model.nodes_data()-model.blob.data());
    std::vector<int> low,high;std::vector<std::size_t> offsets;std::uint64_t assignments=1;
    for(const auto& v:variables){if(v.node>=model.node_bytes()/3||v.channel>=3||v.radius<0||v.radius>255)throw std::invalid_argument("整数箱变量越界");
        const auto offset=v.node*3+v.channel;if(std::find(offsets.begin(),offsets.end(),offset)!=offsets.end())throw std::invalid_argument("整数箱变量重复");offsets.push_back(offset);
        low.push_back((std::max)(0,int(bytes[offset])-v.radius));high.push_back((std::min)(255,int(bytes[offset])+v.radius));
        const auto width=std::uint64_t(high.back()-low.back()+1);if(assignments>max_assignments/width)throw std::invalid_argument("整数箱超过完整穷举预算");assignments*=width;}
    Support support(models,gold,stage);SearchReport report;report.before=support.histogram.quality();report.support_rows=support.points.size();
    const auto view=detail::view(model);std::vector<std::uint32_t> affected;std::vector<unsigned> caps,errors;
    for(std::uint32_t i=0;i<support.points.size();++i){const auto& p=support.points[i];caps.push_back(p.error);bool touches=false;
        for(const auto& v:variables){const auto g=geometry(view,model.interpolation,p.rgb,v.channel);for(unsigned k=0;k<g.count;++k)touches=touches||(g.node[k]==v.node&&g.weight[k]);}if(touches)affected.push_back(i);}
    std::vector<std::uint8_t> best;for(auto i:offsets)best.push_back(bytes[i]);
    for(std::uint64_t key=0;key<assignments;++key){auto code=key;for(std::size_t i=0;i<offsets.size();++i){const auto width=high[i]-low[i]+1;bytes[offsets[i]]=std::uint8_t(low[i]+code%width);code/=width;}
        ++report.proposals;if(trial(model,support,affected,anchor,caps,guard,objective,errors)){++report.accepted;for(std::size_t i=0;i<offsets.size();++i)best[i]=bytes[offsets[i]];}}
    for(std::size_t i=0;i<offsets.size();++i)bytes[offsets[i]]=best[i];if(report.accepted)clear_proof(model);
    report.after=support.histogram.quality();return report;
}
} } // namespace fc_framework::precision
#endif
