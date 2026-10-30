"""冻结copy4五角色双阶段1040调用/5RSS及每进程真实模块观察，等待正式grant。"""
import ast
from pathlib import Path
from study_memory_rom import ROOT,sha,read,save

def main():
    output=ROOT/'experiments/page-id16-copy4-performance-v1.json'
    if output.exists():raise FileExistsError('copy4正式协议不能覆盖')
    quality_plan=ROOT/'experiments/page-id16-copy4-runtime-v1.json'
    original=read(quality_plan)
    quality=ROOT/'artifacts/p16-page-id16-copy4-v1'
    audit=read(quality/'quality-audit.json')
    if not audit['audit_passed'] or audit['actual_capacity']!=12633164 or sha(quality_plan)!='9f6b8f226e8ea0bfc1609dae694e8f5b699666d05ba57e1829ed72d2af7919be' or any(sha(ROOT/name)!=value for name,value in original['source_sha256'].items()):raise AssertionError('唯一copy4质量/源不同')
    names=list(dict.fromkeys([*original['source_sha256'],'experiments/skylake-andn-split-v1.json','experiments/page-id16-copy4-performance-design-v1.md',*['scripts/'+name for name in ('bench_page_id16.py','bench_page_id16_v2.py','observe_page_id16_modules.py','audit_page_id16_copy4_quality.py','bench_page_id16_copy4.py','audit_page_id16_copy4_performance.py','freeze_page_id16_copy4_performance.py','run_page_id16_copy4_performance.py')]]))
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    libraries=dict(ref78=ROOT/'artifacts/p16-memory-build-v2/jshc_memory_ref78.dll',ref80=Path('F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll'),linear=ROOT/'artifacts/p16-memory-clang-store-build-v1/jshc_memory_clang_store.dll',p4=ROOT/'artifacts/p16-page-id16-runtime-v1/build/jshc_page_id16.dll',copy4=quality/'build/jshc_page_id16_copy4.dll')
    libraries={name:str(path) for name,path in libraries.items()}
    expected={'ref78':'bac736cd9933c5a87a31909ba3652c204ee36ccf7915d1d2071f80637cd896ce','ref80':'c9d8a28ecac46de47037572f1985bc2010c0c8a745df74450ca204e6f9721917','linear':'442bc4243920280480807e4e291dff3aa2ffbdb87a0edd4407affad90578c723','p4':'a4b442de7e2e9c579349736a5285f928fc9b379e357ab2db12b6b968061f0b92','copy4':'0a61d36b6844ff54fce4f49ecd783cb3f1265e6c7a676f0fb85631bda7752090'}
    if any(sha(libraries[name])!=value for name,value in expected.items()):raise AssertionError('五个实际角色库不同')
    dependency_names=('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll')
    dependencies=[Path(path).parent/name for path in libraries.values() for name in dependency_names]
    if any(not path.is_file() for path in dependencies):raise FileNotFoundError('五目录实际四依赖缺失')
    data=Path('F:/Hackathon/projects/16-lut-color')
    models=[data/'artifacts/cinema-current-anchor-accept-v1/candidate-base.slut',data/'artifacts/cinema-current-anchor-accept-v1/channel-frac.bin',*[data/('artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage'+str(stage)+'.slut') for stage in (2,3,4)]]
    built=read(quality/'build/build.json')
    paths=[quality_plan,quality/'quality/results.json',quality/'quality-audit.json',quality/'run.json',quality/'build/build.json',quality/'build/machine-code-gate.json',*[quality/'build'/name for name in built['outputs']],*[Path(path) for path in libraries.values()],*dependencies,*models]
    inputs={str(Path(name)):value for name,value in original['input_sha256'].items()}
    inputs.update({str(path):sha(path) for path in paths})
    roles=['ref78','ref80','linear_c99','p4_c99','p4_copy4']
    capacities={role:28046644 if role.startswith('ref') else 16779328 if role=='linear_c99' else 12633164 for role in roles}
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_sha256=inputs,libraries=libraries,roles=roles,capacities=capacities,original_rom=original['original_rom'],page_rom=original['page_rom'],photos=original['photos'],data_root=str(data),expected_output_sha256=original['quality']['expected_photos_sha256'],process_allowed_mask=85,workers=4,phases=2,repeats_per_phase=5,calls_per_cell=65,calls_per_worker=260,calls=1040,measured_calls=800,rss_processes=5,protocol='每cell ref80 warm1+before2，两phase五角色各warm1+timed5，phase2完整role镜像，after2；四fresh0x55/同source及target/全模型驻留，逐调用全235MB SHA/整数ns/CPU/地址。每worker及每RSS各自准备前/后/close后真实模块路径/SHA/数量观察在计时外。',aa_gate='每worker/cell ref80外围after均值/before均值及全部五角色phase2五次median/phase1五次median，闭区间[.8,1.25]全过；任一失效整cell五角色清档，任一worker失效整个模式清档，不补跑。',tier_gate='同worker/同phase较快78/80耗时除以候选同phase中位数，四worker×两phase取最劣，Decimal100/90/80/70/60/50独立判；全部四模式有效才给global，任何有效低50保留反例。旧P4/linear配对仅辅助，不合并十样本救线。',scope='仅新copy4 C99的kernel0，原ROM/40BABI/core/AVX对象和库保持质量原件；不新编译/调ISA/输入选择/WASM，实际模块必须是冻结输入且每种一份，否则身份STOP。等待root正式独占grant，首次源/native/输出错误保留STOP。')
    save(output,value)
    print(dict(plan=str(output),sha256=sha(output),sources=len(names),inputs=len(inputs),calls=1040,rss_processes=5),flush=True)

if __name__=='__main__':main()
