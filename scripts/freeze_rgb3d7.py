"""在唯一C7BK导出/编译/质量前冻结全部执行源、同场控制与六档协议。"""
from pathlib import Path
from study_memory_rom import ROOT,sha,read,save
def main():
    path=ROOT/'experiments/rgb3d-palette7-native-v1.json'
    if path.exists():raise FileExistsError('不覆盖冻结计划')
    common=read(ROOT/'experiments/tagged-block16-native-v1.json');oldcompiler=read(ROOT/'experiments/memory-rom-clang-store-v1.json');linear=ROOT/'artifacts/p16-memory-clang-store-build-v1/jshc_memory_clang_store.dll';linear_rom=ROOT/'artifacts/p16-memory-rom-v2/rom-0.bin';census=ROOT/'report/data/p16-rgb3d-palette-census-v1/census-raw.zip';clang='C:/Program Files/LLVM/bin/clang.exe'
    if sha(census)!='63366451b76ffcf2d4039b7358b038758f530282f93561793a8076cd11fab0e7':raise AssertionError('既有完整频数ZIP不同')
    files=[*sorted((ROOT/'experiments/rgb3d-palette7-runtime').glob('*.*')),*[ROOT/'scripts'/n for n in ('rgb3d7_support.py','generate_rgb3d7.py','rgb3d7_bench_prefix.py','rgb3d7_bench_suffix.py','bench_rgb3d7.py','export_rgb3d7.py','build_rgb3d7.py','verify_rgb3d7.py','freeze_rgb3d7.py','bench_le16_block1024.py','bench_memory_rom.py','study_memory_rom.py')],ROOT/'experiments/rgb3d-palette7-design-v1.md',ROOT/'experiments/rgb3d-palette7-proposed-v1.json'];inputs={}
    for name,value in common['input_sha256'].items():
        if name.endswith('photos.rgb') or name.endswith('.slut') or name.endswith('channel-frac.bin') or name.endswith('jshc_memory_ref78.dll') or name.endswith('libjshc_skylake_andn_normal.dll'):
            if sha(name)!=value:raise AssertionError('共同输入身份不同')
            inputs[name]=value
    for source in (linear,linear_rom,census,Path(clang),Path('E:/mingw64/bin/gcc.exe'),Path('E:/mingw64/bin/g++.exe')):inputs[str(source)]=sha(source)
    if inputs[str(Path(clang))]!=oldcompiler['input_sha256'][str(Path(clang).resolve())]:raise AssertionError('原预定Clang工具已变化')
    oldbuild=ROOT/'artifacts/p16-memory-clang-store-build-v1/build.json'
    if sha(linear)!=read(oldbuild)['libraries']['jshc_memory_clang_store.dll']:raise AssertionError('旧Clang控制库不是原构建')
    inputs[str(oldbuild)]=sha(oldbuild)
    photos=next(n for n in inputs if n.endswith('photos.rgb'))
    save(path,dict(purpose=__doc__,source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},input_sha256=inputs,source_rom=str(ROOT/'artifacts/p16-memory-rom-v2/rom-4.bin'),source_rom_sha256='904f768b4729e1a71c8b03ddaa953b4ad183baee65498b6741068cbbc218ab22',census_zip=str(census),census_zip_sha256=inputs[str(census)],frequency_support_sha256='6d51134d1abbb8e6bfde3e9d16d4ad65566a085d3f2ecf5afef680511232403a',clang=clang,reference78=common['reference78'],linear_reference=dict(library=str(linear),library_sha256=sha(linear),rom=str(linear_rom),rom_sha256=sha(linear_rom),model_bytes=1056,resident_bytes=16779328,scope='旧Clang同DLL kernel1原ANDN AVX/0原Clang C99 store，实际模块路径核验；仅配对，不作分母。'),photos=photos,photos_sha256=inputs[photos],key='bank=(R>>5)|((G>>5)<<3)|((B>>5)<<6)',local_id_bits=7,bank_count=512,local_order='原globalID升序、只读已有正频数项，无照片/排序扫描',rom_expected_bytes=14943268,model_expected_bytes=32,resident_expected_bytes=14943300,baseline_capacity=28046644,roles=['ref78','ref80','linear8_avx','linear8_clang_c99','rgb3d7_avx','rgb3d7_c99'],quality='独立解码实际序列化全部RGB，8完整域/8百图；有限/零长/非对齐/拒绝/IO和ROM只读双保护；512bank×128合法槽及count1、八种7bit起点、最后guard/末palette。核心C99 Clang generic x64对象检查；AVX2沿旧输入/输出仅改lookup。',performance='质量后另等root排他grant。六角色四worker0x55，双接口1/4线程预热1+5完整百图，656 native+6RSS；较快78/80为唯一分母，全部最劣100/90/80/70/60/50，AA单对.8..1.25且中位1/1.1..1.1失败清空，不补跑。',stop='质量失败先停止性能；有效任何模式低50拒绝整体，不扫描key/bit/编译器/loop；原6bit/其它旧失败不修改。',scope='固定a399独立无损内存分支，不重census、不读gold/照片选型；照片仅质量和以后正式性能。当前容量仍投影，待真实ABI/ROM确认；无正式性能/新WASM/实板或官方许可结论。'))
    print(path,sha(path))
if __name__=='__main__':main()
