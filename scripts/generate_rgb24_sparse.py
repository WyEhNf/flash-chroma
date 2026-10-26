"""从已冻结compact源生成独立RGB24研究快照；不改上一阶段所测文件。"""
from pathlib import Path
from study_memory_rom import ROOT,sha

def replace(source,before,after,count=1):
    if source.count(before)!=count:raise AssertionError('源快照替换计数变化：'+before)
    return source.replace(before,after)

def main():
    directory=ROOT/'experiments/rgb24-sparse-runtime';directory.mkdir(exist_ok=False)
    runtime=ROOT/'experiments/compact-sparse-runtime/channel_runtime.cpp'
    if sha(runtime)!='16032485c4bb1a4baa09b4a3d872cce9f5c8713540813d296b10cdc4f9c44dab':raise AssertionError('compact父快照变化')
    source=runtime.read_text(encoding='utf-8')
    source=replace(source,'// 通用冻结稀疏句柄：保留packed节点和必要轴表，逐级校验后释放canonical表示。','// 独立RGB24冻结句柄：owned uint32存储的字节表示每节点三字节，末尾另有guardword。')
    source=replace(source,'void scalar(','''// 字节访问可查看任意对象表示；此标量路径不作不对齐uint32解引用，并显式解释LE RGB。
uint32_t packed_node(const uint32_t* words,size_t index) {
  const auto* p=reinterpret_cast<const unsigned char*>(words)+3*index;
  return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16);
}
void scalar(''')
    for index in ('base','base+a','base+a+b','base+v.sr+v.sg+1'):
        source=replace(source,'v.nodes['+index+']','packed_node(v.nodes,'+index+')')
    source=replace(source,'uint32_t jshc_cc_revision(void) {return 1001;}','uint32_t jshc_cc_revision(void) {return 1002;}')
    source=replace(source,'''table.nodes.resize(m.nodes.size()/3);
      for(size_t i=0;i<table.nodes.size();++i)table.nodes[i]=uint32_t(m.nodes[3*i])|(uint32_t(m.nodes[3*i+1])<<8)|(uint32_t(m.nodes[3*i+2])<<16);''','''// vector整体提供uint32对齐及对象生命周期；通过unsigned-char规则写入其对象表示。
      // 最末RGB节点的4B gather只多读一字节；额外guardword始终owned且已零初始化。
      table.nodes.resize((m.nodes.size()+3)/4+1);
      std::memcpy(table.nodes.data(),m.nodes.data(),m.nodes.size());''')
    (directory/'channel_runtime.cpp').write_text(source,encoding='utf-8',newline='\n')
    source=(ROOT/'experiments/channel-runtime/channel_avx2.cpp').read_text(encoding='utf-8')
    source=replace(source,'template<int C>\ninline __m256i interpolate(','''// AVX2 builtin定义为按字节地址Load32(base+index*scale)，不等同普通不对齐int解引用。
// owned uint32数组保证base对齐；scale1读取3*i处的RGB及一个owned邻接/guard字节。
inline __m256i gather_node(const uint32_t* data,const __m256i& index) {
  const __m256i offset=_mm256_add_epi32(index,_mm256_slli_epi32(index,1));
  return _mm256_and_si256(_mm256_i32gather_epi32(reinterpret_cast<const int*>(data),offset,1),_mm256_set1_epi32(0xffffff));
}
template<int C>
inline __m256i interpolate(''')
    source=replace(source,'gather(v.nodes,','gather_node(v.nodes,',6)
    source+='''
// 只在独立边界测试库暴露，正式像素库不增加公开调用。
#if defined(JSHC_RGB24_PROBE)
extern "C" __declspec(dllexport) void jshc_rgb24_probe8(const uint32_t* data,const int32_t* indexes,uint32_t* output) {
  const __m256i index=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(indexes));
  const __m256i value=jshc_channel::gather_node(data,index);
  _mm256_storeu_si256(reinterpret_cast<__m256i*>(output),value);
}
#endif
'''
    (directory/'channel_avx2.cpp').write_text(source,encoding='utf-8',newline='\n')
    source=(ROOT/'scripts/bench_compact_sparse.py').read_text(encoding='utf-8').replace('通用稀疏句柄','RGB24稀疏句柄').replace('冻结稀疏句柄','RGB24冻结句柄')
    source=replace(source,'experiments/compact-sparse-v1.json','experiments/rgb24-sparse-v1.json')
    (ROOT/'scripts/bench_rgb24_sparse.py').write_text(source,encoding='utf-8',newline='\n')
    source=(ROOT/'scripts/verify_compact_sparse.py').read_text(encoding='utf-8')
    source=replace(source,'experiments/compact-sparse-v1.json','experiments/rgb24-sparse-v1.json')
    source=replace(source,'d.revision!=1001','d.revision!=1002')
    (ROOT/'scripts/verify_rgb24_sparse.py').write_text(source,encoding='utf-8',newline='\n')
    print(directory)
if __name__=='__main__':main()
