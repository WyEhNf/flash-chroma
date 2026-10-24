"""质量独立审计后冻结P4六角色双阶段1232调用+6RSS，正式执行仍待明确grant。"""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    output=ROOT/'experiments/page-id16-performance-v2.json'
    if output.exists():raise FileExistsError('不能覆写性能冻结协议')
    quality_plan=read(ROOT/'experiments/page-id16-runtime-v1.json')
    quality=ROOT/'artifacts/p16-page-id16-runtime-v1'
    audit=read(quality/'quality-audit.json')
    if not audit['audit_passed'] or audit['actual_capacity']!=12633164 or any(sha(ROOT/name)!=value for name,value in quality_plan['source_sha256'].items()):raise AssertionError('质量原件/独立审计未通过')
    old_drafts=['experiments/page-id16-performance-design-v1.md',*['scripts/'+name for name in ('bench_page_id16.py','audit_page_id16_performance.py','freeze_page_id16_performance.py','run_page_id16_performance.py')]]
    new_names=['experiments/page-id16-performance-design-v2.md',*['scripts/'+name for name in ('bench_page_id16_v2.py','audit_page_id16_performance_v2.py','freeze_page_id16_performance_v2.py','run_page_id16_performance_v2.py')]]
    names=list(dict.fromkeys([*quality_plan['source_sha256'],'experiments/skylake-andn-split-v1.json','scripts/audit_page_id16_quality.py',*old_drafts,*new_names]))
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    libraries=dict(ref78=str(ROOT/'artifacts/p16-memory-build-v2/jshc_memory_ref78.dll'),ref80='F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll',linear=str(ROOT/'artifacts/p16-memory-clang-store-build-v1/jshc_memory_clang_store.dll'),p4=str(quality/'build/jshc_page_id16.dll'))
    libraries={key:str(Path(value)) for key,value in libraries.items()}
    expected={'ref78':'bac736cd9933c5a87a31909ba3652c204ee36ccf7915d1d2071f80637cd896ce','ref80':'c9d8a28ecac46de47037572f1985bc2010c0c8a745df74450ca204e6f9721917','linear':'442bc4243920280480807e4e291dff3aa2ffbdb87a0edd4407affad90578c723','p4':'a4b442de7e2e9c579349736a5285f928fc9b379e357ab2db12b6b968061f0b92'}
    if any(sha(libraries[key])!=value for key,value in expected.items()):raise AssertionError('冻结角色DLL身份不同')
    dependency_names=('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll')
    dependencies=[Path(value).parent/name for value in libraries.values() for name in dependency_names]
    if any(not path.is_file() for path in dependencies):raise FileNotFoundError('实际DLL目录缺少必须冻结的四依赖')
    data=Path('F:/Hackathon/projects/16-lut-color')
    models=[data/'artifacts/cinema-current-anchor-accept-v1/candidate-base.slut',data/'artifacts/cinema-current-anchor-accept-v1/channel-frac.bin',*[data/('artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage'+str(stage)+'.slut') for stage in (2,3,4)]]
    paths=[*[Path(value) for value in libraries.values()],*dependencies,quality/'rom/page-id16.bin',quality/'quality/results.json',quality/'quality-audit.json',quality/'run.json',ROOT/'experiments/page-id16-runtime-v1.json',*models]
    inputs={str(Path(name)):value for name,value in quality_plan['input_sha256'].items()}
    inputs.update({str(path):sha(path) for path in paths})
    roles=['ref78','ref80','linear_avx','linear_c99','p4_avx','p4_c99']
    capacities={role:28046644 if role.startswith('ref') else 16779328 if role.startswith('linear') else 12633164 for role in roles}
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_sha256=inputs,libraries=libraries,roles=roles,capacities=capacities,original_rom=str(Path(quality_plan['original_rom'])),page_rom=str(quality/'rom/page-id16.bin'),data_root=str(data),photos=str(Path(quality_plan['photos'])),expected_output_sha256=quality_plan['quality']['expected_photos_sha256'],process_allowed_mask=85,workers=4,phases=2,repeats_per_phase=5,calls_per_cell=77,calls_per_worker=308,calls=1232,measured_calls=960,rss_processes=6,protocol='每cell ref80 warm1+before2；phase1六角色各warm1+timed5；phase2全role镜像各warm1+timed5；ref80 after2。四fresh镜像模式顺序，全模型同址/全驻留；整数ns和1232次完整235MB输出SHA/CPU/地址全部保留。',aa_gate='每worker/cell ref80外围after两次均值/before两次均值，以及六角色各自phase2五次median/phase1五次median，全部在闭区间[0.8,1.25]才有效。任一控制失效则该cell六角色全清档；任一worker失效则该模式六角色全不授档。',tier_gate='每worker每phase min(median78,median80)/candidate同phase median；每模式取全部四worker×两phase八比值最劣。独立Decimal100/90/80/70/60/50，不合并10样本救线；四模式全有效才可global，有效低50保留反例。',v1_scope='41/cell与656总调用v1静态草稿未执行；原文件保持，v2只import其身份/模型准备/允许集辅助，不调用v1 main。',scope='保持b41c503e唯一源码/ROM/DLL，无额外编译/参数扫描；精度与速度六档独立，不预授WASM或赛事许可。冻结后等待root正式排他grant，首身份/返回/输出失败STOP且不补跑。')
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(dict(plan=str(output),sha256=sha(output),sources=len(names),inputs=len(inputs),calls=1232,rss_processes=6))

if __name__=='__main__':main()
