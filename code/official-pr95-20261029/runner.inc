// 扩展验证独立于官方首次调用计时，保留所有重复样本。
std::vector<uint8_t> read_bytes(const std::string& p) {
    std::ifstream f(p,std::ios::binary|std::ios::ate);
    if(!f)throw std::runtime_error("读取文件失败");
    const auto n=f.tellg();f.seekg(0);std::vector<uint8_t> v(static_cast<size_t>(n));
    if(!f.read(reinterpret_cast<char*>(v.data()),n))throw std::runtime_error("读取不完整");return v;
}
int extended(const std::string& data) {
    std::setvbuf(stdout,nullptr,_IONBF,0);
    std::array<fc_model,4> cm{};const fc_model* ptrs[4];fc_chain cc{};
    for(int i=0;i<4;++i) {
        bridge_models[i]=read_bytes(bridge_dir()+"/stage-"+std::to_string(i+1)+".slut");
        bridge_bundle.models[i]={bridge_models[i].data(),bridge_models[i].size()};
        if(fc_model_init(&cm[i],{bridge_models[i].data(),bridge_models[i].size()},{nullptr,0})!=FC_OK)return 2;
        ptrs[i]=&cm[i];
    }
    if(fc_chain_init(&cc,ptrs)!=FC_OK)return 3;
    std::array<Image,4> images, refs;
    for(int i=0;i<4;++i) {
        if(!image_load_bin(data+"/image/"+std::to_string(i+1)+".bin",images[i]))return 4;
        refs[i]=images[i];refs[i].data=read_bytes(bridge_dir()+"/reference-"+std::to_string(i+1)+".bin");
        if(refs[i].data.size()!=images[i].data.size())return 5;
    }
    const size_t total=size_t(256)*256*256;
    std::vector<uint8_t> inputs(total*3),expected(total*3),actual(total*3);
    for(size_t i=0;i<total;++i){inputs[i*3]=uint8_t(i>>16);inputs[i*3+1]=uint8_t(i>>8);inputs[i*3+2]=uint8_t(i);}
    if(fc_apply_rgb8(&cc,inputs.data(),inputs.size(),total*3,expected.data(),expected.size(),total*3,total,1)!=FC_OK)return 6;
    std::printf("FULL_DOMAIN_C99 pixels=%zu\n",total);
    struct Entry {int backend,rep;std::unique_ptr<fc::Runtime> run;std::unique_ptr<uint8_t[]> arena;};
    std::vector<Entry> entries;
    for(int rep=0;rep<4;++rep)for(int backend=1;backend<=2;++backend) {
        fc::RuntimeConfig cfg;cfg.backend=static_cast<fc::Backend>(backend);cfg.representation=static_cast<fc::Representation>(rep);cfg.threads=1;
        fc::Requirements q;auto s=fc::Runtime::requirements(bridge_bundle,cfg,&q);
        if(s!=fc::Status::Ok){std::printf("FAIL_REQUIRE backend=%d rep=%d status=%u\n",backend,rep,unsigned(s));return 7;}
        Entry e;e.backend=backend;e.rep=rep;e.run.reset(new fc::Runtime);
        const double start=now_sec();e.arena.reset(q.arena_bytes ? new uint8_t[q.arena_bytes] : nullptr);
        s=fc::Runtime::prepare(bridge_bundle,cfg,{e.arena.get(),q.arena_bytes},e.run.get());
        const double prep=(now_sec()-start)*1000;
        if(s==fc::Status::Capacity && (rep==1||rep==2)){std::printf("NOT_APPLICABLE backend=%d rep=%d status=10 prepare_ms=%.6f\n",backend,rep,prep);continue;}
        if(s!=fc::Status::Ok){std::printf("FAIL_PREPARE backend=%d rep=%d status=%u\n",backend,rep,unsigned(s));return 8;}
        if(e.run->apply(inputs.data(),inputs.size(),total*3,actual.data(),actual.size(),total*3,total,1)!=fc::Status::Ok)return 9;
        if(actual!=expected){std::printf("FAIL_DOMAIN backend=%d rep=%d\n",backend,rep);return 10;}
        std::printf("CONFIG backend=%d rep=%d prepare_ms=%.6f model=%zu arena=%zu persistent=%zu temporary=%zu palette=%u cache=%d full_domain_equal=1\n",backend,rep,prep,q.model_bytes,q.arena_bytes,q.persistent_bytes,q.temporary_bytes,unsigned(e.run->palette_entries()),int(e.run->prepared_with_suffix_cache()));
        entries.push_back(std::move(e));
    }
    // 正确性、误差和输出落盘均在重复计时之外。
    std::array<Image,4> outputs;
    for(int i=0;i<4;++i)outputs[i]=images[i];
    for(auto& e:entries)for(int i=0;i<4;++i) {
        auto& in=images[i];auto& out=outputs[i];
        if(e.run->apply(in.ptr(),in.data.size(),size_t(in.W)*3,out.ptr(),out.data.size(),size_t(out.W)*3,in.W,in.H)!=fc::Status::Ok)return 11;
        size_t mismatch=0;for(size_t j=0;j<in.data.size()/3;++j) {
            const size_t ix=(size_t(in.data[3*j])<<16)|(size_t(in.data[3*j+1])<<8)|in.data[3*j+2];
            for(int c=0;c<3;++c)mismatch+=out.data[3*j+c]!=expected[3*ix+c];
        }
        if(mismatch)return 12;
        std::vector<double> errors;errors.reserve(size_t(in.W)*in.H);double sum=0;
        for(size_t j=0;j<out.data.size();j+=3){double sq=0;for(int c=0;c<3;++c){int d=int(out.data[j+c])-int(refs[i].data[j+c]);sq+=d*d;}double d=std::sqrt(sq);errors.push_back(d);sum+=d;}
        std::sort(errors.begin(),errors.end());
        const double official=color_dalta_calc(refs[i],out);
        if(std::abs(official-sum/errors.size())>1e-10)return 13;
        std::printf("QUALITY backend=%d rep=%d image=%d mean=%.12f p99=%.12f max=%.12f mismatch=0\n",e.backend,e.rep,i+1,official,errors[size_t(std::ceil(.99*errors.size()))-1],errors.back());
        if(e.backend==1&&e.rep==0)bridge_save(out.data,"candidate-"+std::to_string(i+1)+".bin");
    }
    // 一次预热与 9 个交错周期；每轮包含全部四图，排除分配、读盘与验证。
    for(int cycle=-1;cycle<9;++cycle)for(size_t j=0;j<entries.size();++j) {
        auto& e=entries[cycle%2==0 ? entries.size()-1-j : j];double all=0;
        for(int i=0;i<4;++i){auto& in=images[i];auto& out=outputs[i];const double t=now_sec();auto s=e.run->apply(in.ptr(),in.data.size(),size_t(in.W)*3,out.ptr(),out.data.size(),size_t(out.W)*3,in.W,in.H);double ms=(now_sec()-t)*1000;if(s!=fc::Status::Ok)return 14;all+=ms;if(cycle>=0)std::printf("TIME cycle=%d backend=%d rep=%d image=%d ms=%.9f\n",cycle,e.backend,e.rep,i+1,ms);}
        if(cycle>=0)std::printf("BATCH cycle=%d backend=%d rep=%d ms=%.9f\n",cycle,e.backend,e.rep,all);
    }
    std::puts("COMPLETED=1");return 0;
}
int main(int argc,char**argv) {
    try {if(argc==3&&std::string(argv[2])=="--extended")return extended(argv[1]);return official_main(argc,argv);}
    catch(const std::exception& e){std::fprintf(stderr,"测试异常：%s\n",e.what());return 99;}
}
