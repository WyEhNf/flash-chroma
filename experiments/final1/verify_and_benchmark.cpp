// final1验收：完整域与冻结历史模型一致；保留原TimeCost、参考映射和Delta边界。
#define main final1_original_main
#include "final1/main.cpp"
#undef main
#include <filesystem>
#include <iostream>
#include <iomanip>
#include <numeric>
namespace v {
namespace fs=std::filesystem;namespace p=fc_framework::precision;
using Bytes=std::vector<std::uint8_t>;
void require(bool x,const char* s){if(!x)throw std::runtime_error(s);}
Bytes read(const fs::path& pth){std::ifstream f(pth,std::ios::binary);require(bool(f),"打开失败");return Bytes(std::istreambuf_iterator<char>(f),{});}
void save(const fs::path& pth,const Bytes& b){std::ofstream f(pth,std::ios::binary);f.write(reinterpret_cast<const char*>(b.data()),b.size());require(bool(f),"写入失败");}
std::uint64_t hash(const Bytes& b){std::uint64_t h=14695981039346656037ull;for(auto x:b)h=(h^x)*1099511628211ull;return h;}
p::Models load_models(const fs::path& dir){p::Models m;for(unsigned i=0;i<4;++i){m[i].m=33;m[i].blob=read(dir/(std::to_string(i)+".slut"));m[i].fractions=read(dir/(std::to_string(i)+".fractions"));}return m;}
Image load_image(const fs::path& folder,unsigned i){Image image;require(image_load_bin((folder/(std::to_string(i)+".bin")).string(),image),"图片读取失败");return image;}
double elapsed(double t){return now_sec()-t;}
p::Histogram compare(const Image&a,const Image&b){require(a.size()==b.size(),"图像大小不同");p::Histogram h;for(std::size_t i=0;i<a.size();i+=3){unsigned e=0;for(unsigned c=0;c<3;++c){int d=int(a.data[i+c])-b.data[i+c];e+=d*d;}h.add(e,1);}return h;}
int run(int argc,char**argv){
 require(argc==5,"参数：data目录 冻结前中层结果目录 候选模型库 新结果目录");
 fs::path data=argv[1],expected=argv[2],bank=argv[3],out=argv[4];require(!fs::exists(out),"拒绝覆盖结果");fs::create_directories(out);
 std::array<std::vector<std::uint16_t>,4> raw;std::array<Lut3D,4> ref,models;
 double t=now_sec();for(unsigned i=0;i<4;++i)require(lut_read_3dl((data/"LUT"/("Test"+std::to_string(i+1)+".3DL")).string(),raw[i]),"LUT读取失败");double read_s=elapsed(t);
 t=now_sec();for(unsigned i=0;i<4;++i){require(lut_sparse_ref(raw[i],256,ref[i]),"参考准备失败");require(lut_sparse(raw[i],33,models[i]),"采样失败");}double sample_reference_s=elapsed(t);
 std::cout<<"开始从原始LUT重新生成final1模型\n"<<std::flush;
 t=now_sec();require(fc_delivery_pipeline.prepare(raw,models),"final1准备失败");double prep_s=elapsed(t);
 auto frozen=load_models(expected);const auto& actual=fc_delivery_pipeline.stages();
 fs::create_directories(out/"model");
 for(unsigned i=0;i<4;++i){require(actual[i].blob==frozen[i].blob&&actual[i].fractions==frozen[i].fractions,"模型不等于历史prefix_nodes");save(out/"model"/(std::to_string(i)+".slut"),actual[i].blob);save(out/"model"/(std::to_string(i)+".fractions"),actual[i].fractions);}
 for(auto& r:raw)std::vector<std::uint16_t>().swap(r);
 std::ofstream searches(out/"search.json");searches<<fc_delivery_pipeline.search_report();searches.close();
 std::ifstream old(expected/"domain.rgb",std::ios::binary);require(bool(old),"缺少历史全域输出");
 p::Histogram domain;Image input;input.H=1;input.W=65536;input.C=3;input.data.resize(input.size());Bytes old_bytes(input.size());
 for(unsigned begin=0;begin<(1u<<24);begin+=65536){for(unsigned j=0;j<65536;++j)for(unsigned c=0;c<3;++c)input.data[3*j+c]=std::uint8_t((begin+j)>>(8*c));
  Image pred,gold;require(apply_3d_lut(input,models[0],models[1],models[2],models[3],pred),"完整域apply失败");require(apply_3d_lut_ref(input,ref[0],ref[1],ref[2],ref[3],gold),"完整域参考失败");
  old.read(reinterpret_cast<char*>(old_bytes.data()),old_bytes.size());require(bool(old)&&old_bytes==pred.data,"全域输出不同于已独立验证的历史输出");
  for(std::size_t i=0;i<input.size();i+=3){unsigned d=0;for(unsigned c=0;c<3;++c){int e=int(pred.data[i+c])-gold.data[i+c];d+=e*e;}domain.add(d,1);}}
 std::cout<<"完整16777216色逐字节验证通过，开始104图与正式边界测速\n"<<std::flush;
 std::ofstream correctness(out/"correctness.json");correctness<<std::setprecision(17)<<"{\"model_equal_to_frozen_prefix_nodes\":true,\"all_rgb24_output_equal\":true,\"domain\":"<<p::quality_json(domain.quality())<<",\"backend\":"<<unsigned(fc_delivery_pipeline.info().backend)<<",\"model_bytes\":"<<fc_delivery_pipeline.info().model_bytes<<",\"arena_bytes\":"<<fc_delivery_pipeline.info().arena_bytes<<",\"read_seconds\":"<<read_s<<",\"reference_and_sample_seconds\":"<<sample_reference_s<<",\"prepare_seconds\":"<<prep_s<<",\"fit_seconds\":"<<fc_delivery_pipeline.fit_seconds()<<",\"search_seconds\":"<<fc_delivery_pipeline.search_seconds()<<",\"direct_prepare_seconds\":"<<fc_delivery_pipeline.prepare_seconds()<<",\"images\":[";
 bool first=true;for(unsigned d=0;d<2;++d)for(unsigned i=1;i<=(d?100:4);++i){Image img=load_image(data/(d?"photos100":"official4"),i),pred,gold;require(apply_3d_lut(img,models[0],models[1],models[2],models[3],pred),"图片apply失败");require(apply_3d_lut_ref(img,ref[0],ref[1],ref[2],ref[3],gold),"图片参考失败");if(!first)correctness<<',';first=false;correctness<<"{\"dataset\":\""<<(d?"photos100":"official4")<<"\",\"image\":"<<i<<",\"quality\":"<<p::quality_json(compare(pred,gold).quality())<<",\"output_fnv64\":"<<hash(pred.data)<<'}';}
 correctness<<"]}\n";correctness.close();
 std::ofstream timing(out/"timing.json");timing<<std::setprecision(17)<<"{\"scope\":\"final1实际apply；fresh输出复制与映射在TimeCost内；读图在计时之前，原参考和两次Delta在之后；不额外调用apply预热；正确性验收先于五轮计时\",\"rounds\":[";
 for(unsigned round=0;round<5;++round){if(round)timing<<',';timing<<"{\"round\":"<<round<<",\"per_image_ms\":[";double total=0;
  for(unsigned i=1;i<=100;++i){Image img=load_image(data/"photos100",i);double at=now_sec();Image output;require(apply_3d_lut(img,models[0],models[1],models[2],models[3],output),"计时apply失败");double ms=elapsed(at)*1000;total+=ms;Image gold;require(apply_3d_lut_ref(img,ref[0],ref[1],ref[2],ref[3],gold),"计时参考失败");volatile double d1=color_dalta_calc(img,gold),d2=color_dalta_calc(gold,output);(void)d1;(void)d2;if(i>1)timing<<',';timing<<ms;}
  timing<<"],\"mean_ms\":"<<total/100<<'}';timing.flush();std::cout<<"final1百图第"<<round+1<<"轮："<<total/100<<"ms/图\n"<<std::flush;}
 timing<<"]}\n";timing.close();
 require(fc::available_backends()&2u,"对照要求AVX2");
 std::vector<std::string> names={"chain33","prefix_nodes","geometry_output","history"};std::vector<Bytes> tables;
 for(const auto& name:names){auto m=load_models(bank/name);p::Evaluator eval(m);Bytes table((1u<<24)*3+4);for(unsigned c=0;c<(1u<<24);++c){auto value=eval.map(c);for(unsigned k=0;k<3;++k)table[3ull*c+k]=std::uint8_t(value>>(8*k));}tables.push_back(std::move(table));}
 Bytes shared(tables[0].size());std::ofstream control(out/"fixed-address-control.json");control<<std::setprecision(17)<<"{\"scope\":\"相同Direct表地址、相同pair32核；fresh输出复制在内；原参考与Delta保持在每图之后；仅为隔离模型和地址影响的对照，不替代实际apply计时\",\"samples\":[";first=true;
 auto batch=[&](unsigned n,const char* phase,unsigned round){std::copy(tables[n].begin(),tables[n].end(),shared.begin());double total=0;
  for(unsigned i=1;i<=100;++i){Image img=load_image(data/"photos100",i);double at=now_sec();Image result;result=img;for(std::size_t offset=0;offset<img.size()/3;offset+=65536)fc::detail::direct_rgb24_candidate_run<1,0,true,32,true>(shared.data(),img.ptr()+3*offset,result.ptr()+3*offset,(std::min)(std::size_t{65536},img.size()/3-offset));total+=elapsed(at)*1000;
   Image gold;require(apply_3d_lut_ref(img,ref[0],ref[1],ref[2],ref[3],gold),"对照参考失败");volatile double d1=color_dalta_calc(img,gold),d2=color_dalta_calc(gold,result);(void)d1;(void)d2;}
  if(!first)control<<',';first=false;control<<"{\"variant\":\""<<names[n]<<"\",\"phase\":\""<<phase<<"\",\"round\":"<<round<<",\"mean_ms\":"<<total/100<<'}';control.flush();};
 for(unsigned r=0;r<2;++r){batch(0,"aa_pre_a",r);batch(0,"aa_pre_b",r);}
 for(unsigned r=0;r<3;++r)for(unsigned c=1;c<4;++c){batch(0,"a1",r);batch(c,"b1",r);batch(c,"b2",r);batch(0,"a2",r);}
 for(unsigned r=0;r<2;++r){batch(0,"aa_post_a",r);batch(0,"aa_post_b",r);}
 control<<"]}\n";control.close();std::cout<<"固定地址ABBA和A/A对照完成\n"<<std::flush;return 0;
}
}
int main(int argc,char**argv){try{return v::run(argc,argv);}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
