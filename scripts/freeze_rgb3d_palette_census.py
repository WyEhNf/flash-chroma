"""仅静态冻结RGB高3位512bank/6bit唯一普查，不读取ROM或导入数值库。"""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    path=ROOT/'experiments/rgb3d-palette-census-v1.json'
    if path.exists():raise FileExistsError('不得覆盖静态冻结')
    names=('scripts/profile_rgb3d_palette_banks.py','scripts/freeze_rgb3d_palette_census.py','scripts/study_memory_rom.py','scripts/bench_memory_rom.py','experiments/rgb3d-palette-design-v1.md')
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_rom_path=str(ROOT/'artifacts/p16-memory-rom-v2/rom-4.bin'),input_rom_sha256='904f768b4729e1a71c8b03ddaa953b4ad183baee65498b6741068cbbc218ab22',logical_sha256='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0',output_path='artifacts/p16-rgb3d-palette-census-v1',key='bank=(R>>5)|((G>>5)<<3)|((B>>5)<<6)',equivalent_same_key='((code>>5)&7)|((code>>10)&56)|((code>>15)&448),code=R|(G<<8)|(B<<16)',bank_count=512,bank_domain_colors=32768,local_id_bits=6,gate='唯一完整16M普查，每bank最终RGB集合<=64才可行；任一>64则停止，不改key/bit/bank数、局部细分、例外或删除输入。',execution='先仅静态设计；root明确grant后先freeze，再唯一执行profile。262144输入分块，1线程预计2–5秒/<100MiB；8002有限索引/越界合同，全域两种同一key公式逐项等价，每bank恰32768，全ID SHA及512×230联合频数。',projected_format=dict(magic='C6BK',header_bytes=32,bank_count_bytes=1024,bitstream_bytes=12582912,zero_guard_bytes=4,local_palette_bytes=131072,layout='header/counts/6bit bitstream/4zero guard/palette；最后palette词结束于ROM末端。',rom_bytes=12715044,windows_x64_borrowed_model_expected_bytes=32,resident_expected_bytes=12715076,actual_abi_verified=False,scope='不可变借用4字段model，无global palette副本；只布局投影，未导出/编译/验证guard。'),decision='失败封存负例即止；通过只证明表示存在，native/完整质量/同场100..50精度及速度矩阵另立冻结和授权，不搬旧有损7bit速度。',scope='独立于失败luma16/7bit，旧原件/门槛/默认不变；不读照片/gold，无native/速度或官方许可声明。')
    with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(path,sha(path))
if __name__=='__main__':main()
