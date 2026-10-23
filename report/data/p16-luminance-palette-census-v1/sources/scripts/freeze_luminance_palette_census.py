"""仅静态写入固定输入亮度16bank/7bit普查计划，不读取ROM、不导入数值库。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    path=ROOT/'experiments/luminance-palette-census-v1.json'
    if path.exists():raise FileExistsError('不覆盖静态计划')
    names=['scripts/profile_luminance_palette_banks.py','scripts/freeze_luminance_palette_census.py','scripts/study_memory_rom.py','scripts/bench_memory_rom.py','experiments/luminance-palette-design-v1.md']
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_rom_path=str(ROOT/'artifacts/p16-memory-rom-v2/rom-4.bin'),input_rom_sha256='904f768b4729e1a71c8b03ddaa953b4ad183baee65498b6741068cbbc218ab22',logical_sha256='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0',output_path='artifacts/p16-luminance-palette-census-v1',key='bank=(R+2*G+B)>>6',bank_count=16,local_id_bits=7,gate='全16777216输入各bank独立最终RGB色数都<=128；任一>128则失败停止，不修改key/分区/位宽、删除输入或引入例外路径。',execution='待root明确grant后唯一普查，分262144输入chunk，一线程预计2–5秒/工作集<100MiB；完整bank×globalID频数及域SHA，独立输入卷积核域覆盖。输出目录只允许预登记的一个，不构建native/新ROM，不读照片/gold。',projected_format=dict(magic='L7BK',header_bytes=32,bank_count_bytes=32,local_palette_bytes=8192,bitstream_bytes=14680064,zero_guard_bytes=4,rom_bytes=14688324,windows_x64_borrowed_model_expected_bytes=32,resident_expected_bytes=14688356,actual_abi_verified=False,scope='只定布局投影，未实现。四个pointer/size_t字段借用ROM，避免漏算palette/count/guard及原global palette重复；native须实测ABI。'),decision='失败即封存负例停止；若全部<=128仍只证明7bit存在，另由root决定是否冻结唯一native/质量/同场性能，不从旧有损7bit搬速度。',scope='固定a399与原精确ROM，独立无损机制；旧字典/tag失败不变，默认不改。查重见冻结设计，不声称历史/业界首创。')
    with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(path,sha(path))
if __name__=='__main__':main()
