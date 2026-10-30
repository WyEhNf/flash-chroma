"""在编译和性能前冻结独立RGB24源、参考输入与验收协议。"""
from study_memory_rom import ROOT,sha,read,save

def main():
    previous=read(ROOT/'experiments/compact-sparse-v1.json')
    names=list(previous['source_sha256'])
    for n in ('experiments/compact-sparse-runtime/channel_runtime.cpp','scripts/build_compact_sparse.py','scripts/bench_compact_sparse.py'):names.remove(n)
    names+=['experiments/rgb24-sparse-runtime/channel_runtime.cpp','experiments/rgb24-sparse-runtime/channel_avx2.cpp','scripts/generate_rgb24_sparse.py','scripts/build_rgb24_sparse.py','scripts/bench_rgb24_sparse.py','scripts/verify_rgb24_sparse.py','scripts/verify_rgb24_probe.py','scripts/check_compact_three_stage.py','scripts/freeze_rgb24_sparse.py']
    save(ROOT/'experiments/rgb24-sparse-v1.json',dict(purpose='第六独立阶段：通用节点RGB32→精确RGB24，owned uint32存储+guardword，AVX2单gather字节偏移。',source_sha256={n:sha(ROOT/n) for n in names},inputs=previous['inputs'],parent_compact_plan_sha256=sha(ROOT/'experiments/compact-sparse-v1.json'),cases=previous['cases'],protocol='先256保护页节点probe、原有限1584与后补192三级u64合同、a399六配置完整域和一般四级完整域；全部通过后同场compact/specialized/78/80四worker各5完整百图，1/4线程及独立1/32句柄RSS。',gate=previous['gate'],metrics=previous['metrics'],references=['https://www.intel.com/content/www/us/en/docs/cpp-compiler/developer-guide-reference/2021-8/intrinsics-for-gather-operations.html','https://clang.llvm.org/doxygen/avx2intrin_8h_source.html#l04981'],boundaries='单gather依赖x86 AVX2 intrinsic字节地址Load32契约，不用普通不对齐int解引用；标量显式LE三字节读取。没有C99/整库big-endian认证，未量化节点或修改模型。'))
    print(sha(ROOT/'experiments/rgb24-sparse-v1.json'))
if __name__=='__main__':main()
