"""固定P4/LE16单版全部质量执行前冻结；不授权性能或跨平台运行。"""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    output=ROOT/'experiments/page-id16-runtime-v1.json'
    if output.exists():raise FileExistsError('不能覆写质量前冻结协议')
    names=['experiments/page-id16-runtime-design-v1.md',*['experiments/page-id16-runtime/'+name for name in ('page_id16.h','page_id16_internal.h','page_id16.c','page_parallel.cpp','page_avx2.cpp')],*['scripts/'+name for name in ('export_page_id16.py','page_id16_common.py','build_page_id16.py','verify_page_id16.py','freeze_page_id16_runtime.py','run_page_id16_quality.py','win_readonly_rom.py','study_memory_rom.py','bench_memory_rom.py')],'experiments/le16-block1024-runtime/channel_avx2_le16.cpp']
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    rom=ROOT/'artifacts/p16-memory-rom-v2/rom-0.bin';alias=ROOT/'artifacts/p16-page-alias-runtime-v1/export/alias.bin';census=ROOT/'report/data/p16-page-alias-census-v1/census-raw.zip';photos=Path('F:/Hackathon/projects/16-lut-color/artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb');dep=ROOT/'artifacts/p16-memory-clang-store-build-v1';tools=dict(clang='C:/Program Files/LLVM/bin/clang.exe',gcc='E:/mingw64/bin/gcc.exe',gpp='E:/mingw64/bin/g++.exe')
    expected={rom:'146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5',alias:'30b3a9092f511944ccf89af2f0da86f59abdc3700bcae42d0e089dab7515db6e',photos:'e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd',dep/'jshc_memory_clang_store.dll':'442bc4243920280480807e4e291dff3aa2ffbdb87a0edd4407affad90578c723'}
    for path,value in expected.items():
        if sha(path)!=value:raise AssertionError('固定原件身份不同：'+str(path))
    paths=[*expected,census,*[dep/name for name in ('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll')],*[Path(value) for value in tools.values()]]
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_sha256={str(path):sha(path) for path in paths},original_rom=str(rom),alias=str(alias),census_zip=str(census),photos=str(photos),photos_sha256=expected[photos],dependency_dir=str(dep),tools=tools,format=dict(version=1,page_shift=12,pages=4096,source_unique_pages=3082,palette_slots=256,source_palette_count=230,prefix=1056,map_bytes=8192,pool_offset=9248,pool_bytes=12623872,guard_bytes=4,projected_file_bytes=12633124,projected_x64_model_bytes=40,projected_wasm32_model_bytes=20,projected_x64_capacity=12633164),protocol='唯一消费原分类导出，不重census/改页宽/扫参数；Clang严格C99 generic核与GCC固定旧LE16 IO框架AVX2/OMP串行构建一次。独立uint64原M16D oracle，9模式完整域与逐100图精确比对，另有限/guard/拒绝/生命周期。OMP≤4/OpenBLAS1，不计吞吐。',quality=dict(full_modes=9,finite_modes=10,finite_lengths=[0,1,7,8,9,31,32,40,64,72,73,405,406,1023,1024,1025,4095,4096,4097,65535,65536,65537],io_offsets=[0,1,3,7],rom_offsets=list(range(8)),rom_guard_fixtures=['actual','count1','count256','max4096'],invalid_map_ids=[4096,65535],expected_full_sha256='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22',expected_photos_sha256='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'),gate='实际文件+实际sizeof新Model相对16779328至少省1MiB，且全部格式/完整域/逐图/u64/guard/拒绝过；首次失败原样STOP，不自行修后重采。全部通过仅ready，性能/WASM/对象交叉编译另授。',scope='借用新5word ABI，不混旧1056B Model；C99 LE字节，无heap；x86 AVX2同数学但非BE证据。无AVX512，不把Windows alias成功/unknown或旧WASM当此新点成绩。')
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dict(plan=str(output),sha256=sha(output),source_files=len(names),input_files=len(paths)))
if __name__=='__main__':main()
