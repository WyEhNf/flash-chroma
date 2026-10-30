"""在M16S离线导出、构建和验证前冻结16+1bit布局及七角色协议。"""
import argparse
from pathlib import Path
from study_memory_rom import ROOT,sha,save,read

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('old-build','old-roms','ref80','data-root'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();old=read(ROOT/'experiments/compact-dictionary-v1.json')
    names=['experiments/split-dictionary-runtime/'+n for n in ('memory_rom.h','memory_rom.c','memory_parallel.cpp','channel_avx2_split.cpp')]
    names+=['scripts/'+n for n in ('generate_split_dictionary.py','export_split_dictionary.py','build_split_dictionary.py','verify_split_dictionary.py','freeze_split_dictionary.py','bench_split_dictionary.py','study_memory_rom.py','bench_memory_rom.py','bench_compact_dictionary.py')]
    names+=['experiments/compact-dictionary-split-design.md','experiments/compact-dictionary-runtime/channel_avx2_17.cpp']
    inputs=[a.old_build/'jshc_memory_rom.dll',a.old_roms/'rom-17.bin',a.old_roms/'rom-24.bin',Path(old['reference32']['path']),Path(old['input_rom_path']),Path(old['reference78']['path']),a.ref80]
    inputs+=[a.data_root/n for n in ('artifacts/cinema-current-anchor-accept-v1/candidate-base.slut','artifacts/cinema-current-anchor-accept-v1/channel-frac.bin','artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage2.slut','artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut','artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage4.slut','artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb')]
    path=ROOT/'experiments/split-dictionary-v1.json'
    if path.exists():raise FileExistsError(path)
    save(path,dict(purpose=__doc__,source_sha256={n:sha(ROOT/n) for n in names},input_sha256={str(n.resolve()):sha(n) for n in inputs},input_rom_path=old['input_rom_path'],input_rom_sha256=old['input_rom_sha256'],reference78=old['reference78'],reference32=old['reference32'],old_build=str(a.old_build.resolve()),old_roms=str(a.old_roms.resolve()),roles=['ref78','ref80','dict32','avx2_24','avx2_17','avx2_split','c99_split'],format=dict(magic='M16S',version=1,low_bytes=2097152,high_bytes=131072,pool_offset=2228224,block_bytes=16),protocol='先完整16MiB逻辑ID重建、C99/desktopScalar/AVX2单四线程完整256^3、有限与拒绝及图像/ROM/平面末端保护页。全过后七角色四新worker轮转/反序，每次预热1+5完整百图，原地/分离及1/4线程，最后独立每角色RSS。',gate='精度逐字节不变100%；同worker较快78/80耗时除候选耗时，全部四worker最劣按100/90/80/70/60/50档。80 A/A单对0.8..1.25且中位1/1.1..1.1，失败清空该情形资格。原同容量17bit及3B/32bit同时列出，不拼接跨场最好值。',scope='只改变精确派生运行时布局，不改模型/ISA/AVX2循环其余token。ROM借用+C99零堆；四线程需要桌面OMP适配器，不是纯C99吞吐声明。离线峰值与实际常驻及fresh-process RSS分列。'))
    print(path,sha(path))
if __name__=='__main__':main()
