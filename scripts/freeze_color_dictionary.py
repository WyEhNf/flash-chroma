"""在任何M16C导出、编译、质量及性能执行前冻结唯一版本与判据。"""
from study_memory_rom import ROOT,read,save,sha

def main():
    out=ROOT/'experiments/color-dictionary-v1.json'
    if out.exists():raise FileExistsError(out)
    old=read(ROOT/'experiments/banked-dictionary-native-v1.json')
    files=[*sorted((ROOT/'experiments/color-dictionary-runtime').glob('*.*')),*[ROOT/'scripts'/x for x in ('generate_color_dictionary.py','color_dictionary_support.py','export_color_dictionary.py','build_color_dictionary.py','verify_color_dictionary.py','bench_color_dictionary.py','freeze_color_dictionary.py','study_memory_rom.py','bench_memory_rom.py','bench_compact_dictionary.py')]]
    save(out,dict(purpose=__doc__,source_sha256={str(x.relative_to(ROOT)).replace('\\','/'):sha(x) for x in files},input_sha256=old['input_sha256'],input_rom_path=old['input_rom_path'],input_rom_sha256=old['input_rom_sha256'],reference78=old['reference78'],old_build=old['old_build'],old_roms=old['old_roms'],format='唯一M16C v1：32B头、3MiB LE24绝对pool偏移、原107707块各64B LE RGB32，块内16像素。Model三个指针/长度加两个uint32，Windows x64预期32B；无palette字段或230色限制。只从冻结M16D无损导出，无参数扫描。',expected_rom_bytes=10039008,expected_model_bytes=32,expected_resident_bytes=10039040,baseline_expected_capacity=28046644,roles=['ref78','ref80','avx2_24','avx2_color','c99_color'],quality='导出前冻结；离线全部16MiB逻辑ID与序列化RGB32独立重建。native纯C99/desktopScalar/AVX2单四线程完整256^3 SHA一致；有限/零长/原地/拒绝/非对齐/图像末端及ROM末端保护页，强制最后map指最后64B块，完整RGB24高值颜色合法。',protocol='不改变默认或旧DLL/ROM。质量先于性能；正式计时等root授权。五角色四新worker轮转/反序，单四线程、原地/分离各预热1+5完整100照片，旧3B同场只作比较，不恢复旧稳健50资格。每角色独立新进程RSS，file_digest流式SHA；同导入群峰值包括Python/库，不称纯模型RAM。',gate='逐字节100%精度，继承a399 mean/p99/max及逐图全部不变。速度按每worker min(78,80)耗时/候选，全部四worker最劣100/90/80/70/60/50。A/A逐对0.8..1.25且四worker中位1/1.1..1.1；任一失败清空相应正式档位。不择worker、不追加过线重跑、不拼跨场。',scope='C99零堆、不依赖AVX/OMP；四线程为桌面OMP适配器。AVX2仅既有输出循环及新RGB32读取，不启用AVX512/native。RGB32增大pool以消除palette串行读取，容量与速度取舍分别报告，精度100%不暗示速度通过。'))
    print(out,sha(out))
if __name__=='__main__':main()
