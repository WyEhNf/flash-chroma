"""仅三角色确认原78/80与线性ANDN ROM；沿用首阶段四进程、双接口、A/A协议。"""
from pathlib import Path
import sys
import bench_memory_rom as bench
from study_memory_rom import ROOT,sha,save,read

if __name__=='__main__':
    implementation=Path(bench.__file__)
    plan=ROOT/'experiments/memory-rom-andn-v1.json'
    if any(sha(ROOT/n)!=v for n,v in read(plan)['source_sha256'].items()):raise ValueError('冻结源码变化')
    bench.labels=lambda:['ref78','ref80','avx2_0']
    # 主脚本产生的子进程必须重新进入本入口，保持三角色协议。
    bench.__file__=__file__
    bench.main()
    output=Path(sys.argv[sys.argv.index('--output')+1])
    save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(plan),wrapper_sha256=sha(__file__),benchmark_module_sha256=sha(implementation)))
