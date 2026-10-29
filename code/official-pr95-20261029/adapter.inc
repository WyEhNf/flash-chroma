// 模型只由 LUT 生成；不读取图片，不启用多线程。
std::array<std::vector<uint8_t>, 4> bridge_models;
fc::ModelBundle bridge_bundle;
fc::Runtime bridge_runtime;
std::unique_ptr<uint8_t[]> bridge_arena;
int bridge_stage = 0, bridge_ref_counter = 0, bridge_image_counter = 0;
int bridge_m() { const char* p=std::getenv("FC_M"); return p ? std::atoi(p) : 17; }
std::string bridge_dir() { const char* p=std::getenv("FC_OUT"); if(!p) throw std::runtime_error("未指定输出目录"); return p; }
void bridge_save(const std::vector<uint8_t>& data,const std::string& name) {
    std::ofstream f(bridge_dir()+"/"+name,std::ios::binary);
    if(!f.write(reinterpret_cast<const char*>(data.data()),data.size())) throw std::runtime_error("保存失败");
}
void bridge_u32(std::vector<uint8_t>& v,uint32_t x) { for(int i=0;i<4;++i)v.push_back(uint8_t(x>>(8*i))); }
void bridge_f32(std::vector<uint8_t>& v,float x) { uint32_t u;std::memcpy(&u,&x,4);bridge_u32(v,u); }
bool bridge_sparse(const std::vector<uint16_t>& raw,int m,Lut3D& out) {
    if(m!=17 && m!=33) return false;
    const double start=now_sec();
    std::vector<int> axis(m);
    for(int i=0;i<m;++i)axis[i]=i*(256/(m-1));
    axis.back()=255;
    out.size=m; out.data.resize(size_t(m)*m*m*3);
    for(int r=0;r<m;++r)for(int g=0;g<m;++g)for(int b=0;b<m;++b) {
        const size_t src=((size_t(axis[b])*256+axis[g])*256+axis[r])*3;
        const size_t dst=((size_t(r)*m+g)*m+b)*3;
        for(int c=0;c<3;++c)out.data[dst+c]=uint8_t(raw[src+2-c]/16);
    }
    auto& blob=bridge_models.at(bridge_stage);
    blob={'S','L','U','T'};bridge_u32(blob,1);bridge_u32(blob,m);bridge_u32(blob,0);
    for(int a=0;a<3;++a)for(int x:axis)bridge_f32(blob,float(x));
    std::vector<uint32_t> frac;
    for(int a=0;a<3;++a)for(int x=0;x<256;++x) {
        int j=0;while(j<m-2 && x>=axis[j+1])++j;
        blob.push_back(uint8_t(j));
        const uint32_t den=axis[j+1]-axis[j];
        frac.push_back((uint32_t(x-axis[j])*65536u+den/2)/den);
    }
    for(auto q:frac)bridge_u32(blob,q);
    blob.insert(blob.end(),out.data.begin(),out.data.end());
    bridge_bundle.models[bridge_stage]={blob.data(),blob.size()};
    bridge_save(blob,"stage-"+std::to_string(bridge_stage+1)+".slut");
    std::printf("BRIDGE_SAMPLE stage=%d m=%d ms=%.6f bytes=%zu\n",bridge_stage+1,m,(now_sec()-start)*1000,blob.size());
    if(++bridge_stage==4) {
        fc::RuntimeConfig cfg;cfg.backend=fc::Backend::Scalar;cfg.threads=1;
        fc::Requirements req;
        auto s=fc::Runtime::requirements(bridge_bundle,cfg,&req);
        if(s!=fc::Status::Ok)throw std::runtime_error("容量查询失败");
        bridge_arena.reset(req.arena_bytes ? new uint8_t[req.arena_bytes] : nullptr);
        s=fc::Runtime::prepare(bridge_bundle,cfg,{bridge_arena.get(),req.arena_bytes},&bridge_runtime);
        if(s!=fc::Status::Ok)throw std::runtime_error("模型准备失败");
    }
    return true;
}
bool bridge_apply(const Image& img,Image& out) {
    out.H=img.H;out.W=img.W;out.C=3;out.data.resize(img.data.size());
    const auto s=bridge_runtime.apply(img.ptr(),img.data.size(),size_t(img.W)*3,out.ptr(),out.data.size(),size_t(img.W)*3,img.W,img.H);
    return s==fc::Status::Ok;
}
