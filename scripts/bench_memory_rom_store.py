"""冻结比较C99八像素组内重叠写与78/80：三容量、四进程、双接口和1/4线程。"""
from pathlib import Path
import sys
import bench_memory_rom as bench
from study_memory_rom import ROOT,sha,save,read

if __name__=='__main__':
    implementation=Path(bench.__file__);plan=ROOT/'experiments/memory-rom-store-v1.json'
    if any(sha(ROOT/n)!=v for n,v in read(plan)['source_sha256'].items()):raise ValueError('冻结源码变化')
    bench.labels=lambda:['ref78','ref80','c99_0','c99_4','c99_6']
    bench.__file__=__file__;bench.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]);save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(plan),wrapper_sha256=sha(__file__),benchmark_module_sha256=sha(implementation)))
