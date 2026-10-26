"""唯一页别名导出及API/回收/格式前置执行前冻结；不授权图像或吞吐。"""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    output=ROOT/'experiments/page-alias-runtime-v1.json'
    if output.exists():raise FileExistsError('不能覆写执行前冻结协议')
    names=['scripts/export_page_alias.py','scripts/page_alias_runtime.py','scripts/page_alias_front.py','scripts/freeze_page_alias_runtime.py','scripts/run_page_alias_front.py','scripts/profile_page_alias.py','scripts/win_readonly_rom.py','scripts/study_memory_rom.py','scripts/bench_memory_rom.py','experiments/page-alias-runtime-design-v1.md','experiments/page-alias-census-v1.json']
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    original=ROOT/'artifacts/p16-memory-rom-v2/rom-0.bin';library=ROOT/'artifacts/p16-memory-clang-store-build-v1/jshc_memory_clang_store.dll';census=ROOT/'report/data/p16-page-alias-census-v1/census-raw.zip'
    if sha(original)!='146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5' or sha(library)!='442bc4243920280480807e4e291dff3aa2ffbdb87a0edd4407affad90578c723':raise AssertionError('原件ROM/DLL不同')
    inputs=[original,library,census,*[library.parent/name for name in ('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll')]]
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_sha256={str(path):sha(path) for path in inputs},original_rom=str(original),original_rom_sha256=sha(original),library=str(library),census_zip=str(census),census_support_sha256='bfc96db68384a70c40c7df596b8d6a1fb1411a189d8059620b44e58b02dc3025',logical_id_sha256='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0',format=dict(page_bytes=4096,pages=4096,unique_pages=3082,header_page_bytes=4096,header_bias=3040,page_id_bytes=16384,pool_offset=20480,expected_alias_backing=12644352,expected_aligned_backing=16781312,model_bytes=1056,owner_bytes=48,model_view_span=16781312,reserve_span=16785408,guard_va=4096),protocol='唯一固定导出后，原普通RO/同布局未去重RO/alias各一fresh；相同imports、原DLL、完整流式输入SHA与receipt校验。记录Python启动外部wall、全部前置及open/validation/prepare/touch/close阶段，PSAPI全计数、实际保护/regions/QueryWorkingSetEx；无像素完整域/百图/性能。之后唯一真实API/lifecycle/格式合同进程。',failure_protocol='open/file_size/section/reserve各一次；split及map预定0/1/2048/4096和native prepare调用前失败；unmap4096/coalesce/release/close_section/close_file各一次显式重试；map2048+unmap2047双失败保留异常owner后显式重试。所有已创建部分均真实OS资源。任何预料外失败保留原件STOP，不修源重采；未回收owner在子进程等待status/retry显式指令，不让进程退出掩盖回收。',format_contract='原容器、count1/256固定合法夹具，全部256palette与末ID；固定畸形字段/metadata首末ID/截断/多余/摘要/native count/缺失文件拒绝，关闭清零/不可重开/写共享拒绝；三种缺新API明确原RO fallback、不能授alias资格。',gate='实际文件+48B必要owner+1056B原Model相对16779328至少净省1MiB，真实API/所有资源/保护/全blob摘要及格式合同全过，否则STOP。此阶段不以WS/private变化替代backing净收益，不授任何100..50吞吐档。',scope='Windows独立loader，不改C99/AVX/旧DLL/数学；容量保留虚拟16MiB跨度；同进程ShareCount无PFN，unique backing不等实际唯一物理页；OS VAD/PTE与Python额外对象成本另列，零quota字段不表示无内核成本。')
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dict(plan=str(output),sha256=sha(output),source_files=len(names),input_files=len(inputs)))
if __name__=='__main__':main()
