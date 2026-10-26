"""只读tag普查前冻结唯一16B源与脚本；不运行统计或生成新ROM。"""
from study_memory_rom import ROOT,sha,save

def main():
    path=ROOT/'experiments/tagged-block16-census-v1.json'
    if path.exists():raise FileExistsError(path)
    source=ROOT/'artifacts/p16-memory-rom-v2/rom-4.bin'
    save(path,dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in ('scripts/profile_tagged_block16.py','scripts/freeze_tagged_block16_census.py','scripts/study_memory_rom.py','scripts/bench_memory_rom.py')},input_rom_path=str(source),input_rom_sha256='904f768b4729e1a71c8b03ddaa953b4ad183baee65498b6741068cbbc218ab22',block_bytes=16,parameters='只读一次，无块尺寸/tag布局/阈值/格式参数扫描。依据模型本身RGB恒定性，检查palette互异再使用unique≤230界。',outputs='全1048576 map引用加权覆盖、unique覆盖、16777216色逻辑SHA、原/投影容量与增加、离线峰值；不生成新ROM、不读取gold/照片、不计时mapper。',decision='先完整报告，一次普查后由root判断是否值得实现唯一M16T版本；非零覆盖不是速度通过，未实现容量不作为双底线候选。',scope='当前只冻结普查；native/性能另等授权，保留旧负例，不改默认。'))
    print(path,sha(path))
if __name__=='__main__':main()
