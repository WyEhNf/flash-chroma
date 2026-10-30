"""准备82静态失败/83完整验收的共同归档入口；本文件不复制构建或执行候选。"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'report/data/skylake-andn-normal-v1/archive.py').read_text(encoding='utf-8')
source=source.replace('归档80','归档83').replace('andn_normal','input256_ordered').replace('andn-normal','input256-ordered')
source=source.replace('normal_inplace_','input256_ordered_inplace_')
source=source.replace("('prepare_input256_ordered_checks.py',)","('prepare_input256_deferred_glue.py','repair_input256_deferred_bench.py','prepare_input256_deferred_perf.py','prepare_input256_ordered_glue.py','prepare_input256_ordered_perf.py','prepare_r8_packed_profile.py','prepare_input256_ordered_archive.py')")
needle="    paths = archive_build()"
extra='''    paths = archive_build()
    # 82只有静态失败，不存在完整域或性能样本；归档其原件，不能择优替代83。
    failed = read(ROOT/'artifacts/skylake-input256-deferred-static-v1/results.json')
    independent = read(ROOT/'artifacts/skylake-input256-deferred-static-v1/independent_results.json')
    assert not failed['accepted'] and not independent['accepted']
    for name in ('skylake-input256-deferred-static-v1','skylake-input256-deferred-preflight-v1','skylake-r8-packed-profile-v1'):
        paths.extend(copy_folder(name))
    old_source=ROOT/'artifacts/skylake-input256-deferred-linux-build-v1'
    old_target=HERE/'skylake-input256-deferred-linux-build-v1';old_target.mkdir()
    old_chosen=['build.json','build-log.json','compile_commands.json','libraries-Release.json','measured-source.zip',*sorted(p.name for p in old_source.glob('libjshc*.so'))]
    for name in old_chosen:shutil.copy2(old_source/name,old_target/name)
    with zipfile.ZipFile(old_target/'build-intermediates.zip','w',zipfile.ZIP_DEFLATED) as stream:
        for path in sorted(old_source.rglob('*')):
            if path.is_file() and path.name not in old_chosen:stream.write(path,path.relative_to(old_source).as_posix())
    paths.extend(p for p in old_target.rglob('*') if p.is_file())'''
assert source.count(needle)==1;source=source.replace(needle,extra)
source=source.replace("    full = read(HERE/'skylake-input256-ordered-linux-full-v1/results.json')", "    full = read(HERE/'skylake-input256-ordered-linux-full-v1/results.json')")
target=ROOT/'report/data/skylake-input256-ordered-v1';target.mkdir(exist_ok=False)
with (target/'archive.py').open('x',encoding='utf-8',newline='') as stream:stream.write(source)
print('共同归档入口已准备，尚未执行复制或原生。')
