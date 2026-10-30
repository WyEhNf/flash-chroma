"""在导出/构建/全域/性能前冻结M16P的独立3B和17bit候选协议。"""
import argparse
from pathlib import Path
from study_memory_rom import ROOT,sha,save

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--reference32',type=Path,required=True);p.add_argument('--reference78',type=Path,required=True);a=p.parse_args()
    names=['experiments/compact-dictionary-runtime/'+n for n in ('memory_rom.h','memory_rom.c','memory_parallel.cpp','channel_avx2_17.cpp','channel_avx2_24.cpp')]
    names+=['scripts/'+n for n in ('generate_compact_dictionary.py','freeze_compact_dictionary.py','export_compact_dictionary.py','build_compact_dictionary.py','verify_compact_dictionary.py','verify_compact_dictionary_contract.py','bench_compact_dictionary.py','study_memory_rom.py','bench_memory_rom.py','verify_memory_rom_contract.py')]
    names+=['experiments/skylake-andn-split-runtime/channel_avx2.cpp','experiments/memory-rom/memory_parallel.cpp']
    save(ROOT/'experiments/compact-dictionary-v1.json',dict(purpose='第七独立阶段：已验16B字典32bit偏移压为3B绝对偏移/17bit块ID，固定精确节点，不改模型。',source_sha256={n:sha(ROOT/n) for n in names},input_rom_path=str(a.rom.resolve()),input_rom_sha256=sha(a.rom),reference32=dict(path=str(a.reference32.resolve()),sha256=sha(a.reference32)),reference78=dict(path=str(a.reference78.resolve()),sha256=sha(a.reference78)),protocol='独立完整16MiB逻辑ID重建；原C99和桌面scalar/AVX2各两格式完整256^3；有限720形状/偏移和保护页/非对齐/拒绝；全部通过再四worker轮转反序×各角色预热1+5完整百图，单/四线程原地/分离；独立各角色RSS。',roles=['ref78','ref80','dict32','avx2_24','avx2_17','c99_24','c99_17'],gate='mean/p99/max与逐图误差不变，精度100%；以每worker同场最快78/80耗时除候选耗时，四worker最差按100/90/80/70/60/50分档；80尾部A/A每对0.8..1.25且四进程中位1/1.1..1.1，失败清空资格，不挑较好worker。',scope='M16P为研究ROM，SLUT输入仍原四个33^3；不宣称官方等价许可/成绩。常驻=实际ROM+sizeof(model)，C99无堆；offline exporter RSS和native fresh-process RSS分开，C994线程依赖桌面OpenMP适配器。'))
    print(sha(ROOT/'experiments/compact-dictionary-v1.json'))
if __name__=='__main__':main()
