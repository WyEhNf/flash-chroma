"""静态六角色1920调用/6RSS协议冻结器；完整review后另grant才可运行。"""
import ast
from pathlib import Path
from study_memory_rom import ROOT, read, save, sha


def main():
    output = ROOT / 'experiments/page-id16-native-pages-performance-v1.json'
    if output.exists():
        raise FileExistsError('唯一formal协议不能覆盖')
    quality_plan = ROOT / 'experiments/page-id16-native-pages-full-v1.json'
    if sha(quality_plan) != 'c345f5bbc3118bff60854bba07e7b96ff5a782209a96466641655c75e7b10dc1':
        raise AssertionError('唯一完整质量协议不同')
    old = read(quality_plan)
    for name, value in old['source_sha256'].items():
        if sha(ROOT / name) != value:
            raise AssertionError('旧冻结源改变')
    for name, value in old['input_sha256'].items():
        if sha(name) != value:
            raise AssertionError('旧冻结输入改变')
    quality = ROOT / 'artifacts/p16-page-native-pages-full-v1'
    audit = quality / 'independent-audit.json'
    if sha(audit) != '9d0da2e2debc6073b8de2771f16bd52b57d550a3a27b4f06f88f277e625314e4' or not read(audit)['passed']:
        raise AssertionError('唯一完整质量独立审计不同')
    names = list(old['source_sha256'])
    names += ['experiments/page-id16-native-pages-performance-design-v1.md',
              'experiments/skylake-andn-split-v1.json', *['scripts/' + name for name in (
              'bench_page_id16.py', 'bench_page_id16_v2.py', 'observe_page_id16_modules.py',
              'bench_page_id16_native_pages.py', 'audit_page_id16_native_pages_performance.py',
              'freeze_page_id16_native_pages_performance.py', 'run_page_id16_native_pages_performance.py')]]
    names = list(dict.fromkeys(names))
    for name in names:
        if name.endswith('.py'):
            ast.parse((ROOT / name).read_text(encoding='utf-8'), filename=name)
    libraries = dict(ref78=ROOT / 'artifacts/p16-memory-build-v2/jshc_memory_ref78.dll',
        ref80=Path('F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll'),
        linear=ROOT / 'artifacts/p16-memory-clang-store-build-v1/jshc_memory_clang_store.dll',
        copy4=ROOT / 'artifacts/p16-page-id16-copy4-v1/build/jshc_page_id16_copy4.dll',
        p4=ROOT / 'artifacts/p16-page-id16-runtime-v1/build/jshc_page_id16.dll',
        pages=ROOT / 'artifacts/p16-page-native-pages-observer-v2/build/jshc_page_native_pages.dll')
    expected = dict(ref78='bac736cd9933c5a87a31909ba3652c204ee36ccf7915d1d2071f80637cd896ce',
        ref80='c9d8a28ecac46de47037572f1985bc2010c0c8a745df74450ca204e6f9721917',
        linear='442bc4243920280480807e4e291dff3aa2ffbdb87a0edd4407affad90578c723',
        copy4='0a61d36b6844ff54fce4f49ecd783cb3f1265e6c7a676f0fb85631bda7752090',
        p4='a4b442de7e2e9c579349736a5285f928fc9b379e357ab2db12b6b968061f0b92',
        pages='b326a9f3cc6dfa933964b65bf345bf15887d56c62904ad569554b42cf2e93ced')
    if any(sha(libraries[name]) != value for name, value in expected.items()):
        raise AssertionError('六固定库不同')
    dependency_names = ('libgcc_s_seh-1.dll', 'libgomp-1.dll', 'libstdc++-6.dll', 'libwinpthread-1.dll')
    paths = [quality_plan, quality / 'quality/results.json', audit]
    paths += [*libraries.values(), *[path.parent / name for path in libraries.values() for name in dependency_names]]
    data = Path('F:/Hackathon/projects/16-lut-color')
    paths += [data / 'artifacts/cinema-current-anchor-accept-v1/candidate-base.slut',
              data / 'artifacts/cinema-current-anchor-accept-v1/channel-frac.bin',
              *[data / f'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage{stage}.slut' for stage in (2, 3, 4)]]
    inputs = dict(old['input_sha256'])
    inputs.update({str(path): sha(path) for path in paths})
    roles = ['ref78', 'ref80', 'linear_c99', 'copy4_c99', 'p4_avx', 'pages_c99']
    save(output, dict(purpose=__doc__, source_sha256={name: sha(ROOT / name) for name in names},
        input_sha256=inputs, libraries={name: str(path) for name, path in libraries.items()},
        roles=roles, pair_controls=roles[:-1], data_root=str(data),
        original_rom=old['original_rom'], page_rom=old['page_rom'], photos=old['photos'],
        capacities={role: 28046644 if role.startswith('ref') else 16779328 if role == 'linear_c99' else 12665940 if role == 'pages_c99' else 12633164 for role in roles},
        expected_input_sha256='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd',
        expected_output_sha256='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528',
        expected_versions=dict(python='3.12.14', numpy='1.26.4'),
        required_environment=dict(OMP_NUM_THREADS='4', OMP_DYNAMIC='FALSE', OMP_THREAD_LIMIT='4',
            OMP_WAIT_POLICY='PASSIVE', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
            NUMEXPR_NUM_THREADS='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8'),
        workers=4, process_allowed_mask=85, allowed_cpus=[0, 2, 4, 6], pair_cells=80, warm_per_role_per_cell=2,
        timed_groups=4, repeats_per_group=5, calls_per_cell=24, calls_per_worker=480,
        calls=1920, timed_calls=1600, own_aa_controls=240, output_sha_checks=480,
        input_sha_checks=88, rss_processes=6, metrics=dict(inplace=['apply_ns', 'copy_apply_ns'], outplace=['apply_ns']),
        aa_closed_interval=['.85', '1.15'],
        protocol='五个A/B各四位置ABBA/BAAB每组5 timed，镜像warm各2；两角色双组自身AA，各pair/mode/metric独立。主78/80两个pair共同有效后取全部组/worker最劣，两原地metric同过才全局。',
        scope='只独立新协议，不恢复copy4旧失败。尚需root正式CPUgrant，不新编译/导出/调参/WASM；组末480输出SHA、88输入起止/cell末SHA、全master保护、三时点实际四依赖。'))
    print(dict(plan=str(output), sha256=sha(output), sources=len(names), inputs=len(inputs), calls=1920, rss=6), flush=True)


if __name__ == '__main__':
    main()
