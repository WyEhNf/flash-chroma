"""在唯一4KiB页普查前冻结源、原M16D与固定容量门，不运行映射。"""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    output=ROOT/'experiments/page-alias-census-v1.json'
    if output.exists():raise FileExistsError('不能覆写冻结协议')
    names=['scripts/profile_page_alias.py','scripts/freeze_page_alias_census.py','experiments/page-alias-census-design-v1.md']
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    rom=ROOT/'artifacts/p16-memory-rom-v2/rom-0.bin';identity=sha(rom)
    if identity!='146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5':raise AssertionError('原linear ROM不同')
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},rom=str(rom),rom_sha256=identity,logical_id_sha256='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0',page_bytes=4096,pages=4096,original_header_bytes=1056,header_page_bytes=4096,metadata_bytes=16384,model_bytes=1056,owner_state_expected_bytes=48,gate='基线16779328-(4096+16384+4096*uniquePages+实际原型owner状态48+原model1056)>=1048576；否则STOP。部署若增加必需常驻字段必须再扣账，不以原型投影代替实际容量。',protocol='唯一完整4096页exact-byte census；全ID流及独立pool重放SHA、独立Counter、16384有限索引公式+2非法code；不读照片/gold、不扫页尺寸、不生成新ROM/MapViewOfFile3/性能。',scope='虚拟跨度/逻辑blob_bytes不减少；unique backing不等物理RAM，后续QueryWorkingSetEx无PFN、PTE/VAD成本须另测/列未知。',references=['https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile3','https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc2'])
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dict(plan=str(output),sha256=sha(output)))
if __name__=='__main__':main()
