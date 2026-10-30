"""在唯一4bank的native导出/构建前冻结实现、ABI增加16B与完整七角色协议。"""
import argparse
from pathlib import Path
from study_memory_rom import ROOT,sha,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--old-build',type=Path,required=True);p.add_argument('--old-roms',type=Path,required=True);a=p.parse_args();parent=read(ROOT/'experiments/split-dictionary-v1.json');profile=ROOT/'artifacts/p16-banked-dictionary-profile-v1/results.json';result=read(profile)
    if not result['selected'] or result['selected']['banks']!=4:raise AssertionError('不得改变容量选择规则')
    path=ROOT/'experiments/banked-dictionary-native-v1.json'
    if path.exists():raise FileExistsError(path)
    names=['experiments/banked-dictionary-runtime/'+n for n in ('memory_rom.h','memory_rom.c','memory_parallel.cpp','channel_avx2_bank.cpp')]
    names+=['scripts/'+n for n in ('profile_banked_dictionary.py','generate_banked_dictionary.py','banked_dictionary_support.py','export_banked_dictionary.py','build_banked_dictionary.py','verify_banked_dictionary.py','bench_banked_dictionary.py','freeze_banked_dictionary.py','study_memory_rom.py','bench_memory_rom.py','bench_compact_dictionary.py')]
    names+=['experiments/banked-dictionary-profile-v1.json','experiments/split-dictionary-runtime/memory_rom.h','experiments/split-dictionary-runtime/memory_rom.c','experiments/split-dictionary-runtime/memory_parallel.cpp','experiments/split-dictionary-runtime/channel_avx2_split.cpp','scripts/build_split_dictionary.py','scripts/verify_split_dictionary.py']
    save(path,dict(purpose=__doc__,source_sha256={n:sha(ROOT/n) for n in names},input_sha256=parent['input_sha256'],input_rom_path=parent['input_rom_path'],input_rom_sha256=parent['input_rom_sha256'],reference78=parent['reference78'],old_build=str(a.old_build.resolve()),old_roms=str(a.old_roms.resolve()),profile_result_path=str(profile),profile_result_sha256=sha(profile),selected_banks=4,profile_resident_bytes=4248640,native_model_bytes=1072,native_extra_model_bytes=16,native_resident_bytes=4248656,format='M16B v1，4bank；2MiB LE16局部ID、16B LE32 bases元数据、连续bank pool；完整256项合法palette。model独立bases[4]比profile旧假设多16B，不改写profile原数据。',protocol='仅实现选定4bank，不扫描其它bank数。先完整16MiB逻辑ID重建、C99/desktopScalar/AVX2单四线程完整256^3、有限/拒绝/非对齐/256合法palette/图像及ROM末端保护页，再七角色四新worker轮转反序，双接口单四线程各预热1+5完整百图及每角色独立RSS。',roles=['ref78','ref80','dict32','avx2_24','avx2_17','avx2_bank','c99_bank'],gate='精度逐字节不变100%；每worker较快78/80耗时除候选，全部四worker最劣按100/90/80/70/60/50。A/A单对0.8..1.25且中位1/1.1..1.1；失败清空正式档位，不挑worker/不跨场拼最好。相同照片批次一次API处理100张连接数据，输入恢复不计时。',scope='a399模型不变，仅精确派生ROM表示；C99零堆核心，四线程需要桌面OMP适配器。新ABI必须用1072B对象，不复用旧1056B适配器。sha预检已流式，RSS含Python/导入/库/预检，不虚构整文件分配。'))
    print(path,sha(path))
if __name__=='__main__':main()
