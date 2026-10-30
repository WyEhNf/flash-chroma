"""唯一1024块LE16的导出/构建/质量/五角色性能前冻结。"""
from study_memory_rom import ROOT,sha,read,save as save_raw

def save(path,data):
    data['process_control']=dict(allowed_cpus=[0,2,4,6],mask='0x55',omp_proc_bind='false',omp_places=None,records='所有测量及RSS进程读回process/system原/实际mask；560次native调用前后caller CPU记录在wall计时外，保留预热/主要/AA全部调用。非逐OMP线程绑定，未锁频。',scope='在首次冻结前确定的新控制环境；只同场各角色比较，不拿旧unbound绝对时间归因或恢复旧反例。')
    return save_raw(path,data)

def main():
    path=ROOT/'experiments/le16-block1024-v1.json'
    if path.exists():raise FileExistsError(path)
    old=read(ROOT/'experiments/color-dictionary-v1.json');input_rom=ROOT/'artifacts/p16-memory-rom-v2/rom-10.bin';old_dll=ROOT/'artifacts/p16-memory-build-v2/jshc_memory_rom.dll';inputs=dict(old['input_sha256']);inputs[str(input_rom)]=sha(input_rom);files=[*sorted((ROOT/'experiments/le16-block1024-runtime').glob('*.*')),*[ROOT/'scripts'/name for name in ('generate_le16_block1024.py','export_le16_block1024.py','build_le16_block1024.py','verify_le16_block1024.py','bench_le16_block1024.py','freeze_le16_block1024.py','study_memory_rom.py','bench_memory_rom.py')]]
    if sha(input_rom)!='b36d97216acb7a200cdd95abf66e4c101d0db43d6eed5680487067ef51df58c3' or sha(old_dll)!='88bddba254d4ad7755778c2c24a6a5660af1d463704db90c556b7889e28d57f6':raise AssertionError('旧1024身份不同')
    save(path,dict(purpose=__doc__,source_sha256={x.relative_to(ROOT).as_posix():sha(x) for x in files},input_sha256=inputs,input_rom_path=str(input_rom),input_rom_sha256=sha(input_rom),reference1024=dict(path=str(old_dll),sha256=sha(old_dll)),reference78=old['reference78'],old_avx2_source_path=str(ROOT/'artifacts/p16-memory-build-v2/memory_avx2_10.cpp'),old_avx2_source_sha256=sha(ROOT/'artifacts/p16-memory-build-v2/memory_avx2_10.cpp'),format='唯一M10L v1：1024B块、16384项LE16 ID、原10482块pool顺序及256槽palette不变；最多65536块，ID65535合法。C99原逐像素算法，AVX原1024源码仅改lookup及namespace。',expected_rom_bytes=10767392,expected_model_bytes=1056,expected_resident_bytes=10768448,expected_saved_bytes=32768,baseline_capacity=28046644,roles=['ref78','ref80','old1024','avx2_le16','c99_le16'],quality='完整16MiB逻辑ID重建；纯C99/桌面scalar/AVX1/4各原地/分离共8配置完整256^3；有限/拒绝/非对齐/图片guard/真实和强制最后map及pool ROM guard；65536块ID65535+256合法palette正向夹具。',protocol='质量先行且正式性能另等root。五角色四新worker，双接口1/4线程预热1+5完整百图，输入恢复不计时，首尾SHA；每角色独立RSS，含Python/NumPy/库。全部源与旧控制不变，无参数扫描或补跑。',gate='精度逐字节100%；每worker min(78,80)耗时/候选，全worker最劣100/90/80/70/60/50。AA逐对0.8..1.25且中位1/1.1..1.1，失效清空对应所有档。旧1024若出现有效低50反例，历史通过保持但联合全情形推荐降级。',hypothesis='只省32KiB首级map，可能改善缓存也可能被shift/add抵消；不预称L1命中或更快。不得用原1024慢基线替代快速分母。',scope='固定a399模型，无gold/照片选型，无AVX512/native/其它新变体/affinity/WASM；默认与原件不变。'))
    print(path,sha(path))
if __name__=='__main__':main()
