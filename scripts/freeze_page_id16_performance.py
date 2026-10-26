"""P4质量独立审计后冻结六角色656调用+6RSS；仍待root正式grant。"""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    output=ROOT/'experiments/page-id16-performance-v1.json'
    if output.exists():raise FileExistsError('不能覆写性能冻结协议')
    quality_plan=read(ROOT/'experiments/page-id16-runtime-v1.json');quality=ROOT/'artifacts/p16-page-id16-runtime-v1';audit=read(quality/'quality-audit.json')
    if not audit['audit_passed'] or audit['actual_capacity']!=12633164 or any(sha(ROOT/name)!=value for name,value in quality_plan['source_sha256'].items()):raise AssertionError('质量原件/独立审计未完成')
    names=[*quality_plan['source_sha256'],'experiments/skylake-andn-split-v1.json','experiments/page-id16-performance-design-v1.md',*['scripts/'+name for name in ('audit_page_id16_quality.py','bench_page_id16.py','audit_page_id16_performance.py','freeze_page_id16_performance.py','run_page_id16_performance.py')]]
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    libraries=dict(ref78=str(ROOT/'artifacts/p16-memory-build-v2/jshc_memory_ref78.dll'),ref80='F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll',linear=str(ROOT/'artifacts/p16-memory-clang-store-build-v1/jshc_memory_clang_store.dll'),p4=str(quality/'build/jshc_page_id16.dll'))
    libraries={key:str(Path(value)) for key,value in libraries.items()}
    expected={'ref78':'bac736cd9933c5a87a31909ba3652c204ee36ccf7915d1d2071f80637cd896ce','ref80':'c9d8a28ecac46de47037572f1985bc2010c0c8a745df74450ca204e6f9721917','linear':'442bc4243920280480807e4e291dff3aa2ffbdb87a0edd4407affad90578c723','p4':'a4b442de7e2e9c579349736a5285f928fc9b379e357ab2db12b6b968061f0b92'}
    if any(sha(libraries[key])!=value for key,value in expected.items()):raise AssertionError('冻结角色DLL不同')
    data=Path('F:/Hackathon/projects/16-lut-color');models=[data/'artifacts/cinema-current-anchor-accept-v1/candidate-base.slut',data/'artifacts/cinema-current-anchor-accept-v1/channel-frac.bin',*[data/('artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage'+str(stage)+'.slut') for stage in (2,3,4)]]
    paths=[*[Path(value) for value in libraries.values()],quality/'rom/page-id16.bin',quality/'quality/results.json',quality/'quality-audit.json',quality/'run.json',ROOT/'experiments/page-id16-runtime-v1.json',*models]
    inputs={**quality_plan['input_sha256'],**{str(path):sha(path) for path in paths}}
    roles=['ref78','ref80','linear_avx','linear_c99','p4_avx','p4_c99'];capacities={role:28046644 if role.startswith('ref') else 16779328 if role.startswith('linear') else 12633164 for role in roles}
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_sha256=inputs,libraries=libraries,roles=roles,capacities=capacities,original_rom=quality_plan['original_rom'],page_rom=str(quality/'rom/page-id16.bin'),data_root=str(data),photos=quality_plan['photos'],expected_output_sha256=quality_plan['quality']['expected_photos_sha256'],process_allowed_mask=85,workers=4,repeats=5,calls=656,rss_processes=6,protocol='同场六角色全驻留/同source及target；四fresh镜像顺序，每四模式各ref80 warm1+before2，六角色warm1+measure5，after2；整数ns/每调用全235MB SHA及CPU。4*4*(5+6*6)=656，另6fresh RSS无图片。',aa_gate='每worker after两次平均/before两次平均须在[0.8,1.25]；任何worker失效则该模式全角色档位清空，不补跑/不缩轮。',tier_gate='主分母每worker min(median78,median80)，四worker最劣；精确Decimal100/90/80/70/60/50，全部四模式均有效才有global，任何有效低50保留反例。',scope='保持b41c503e唯一源码/ROM/DLL，不额外编译/参数扫描；不授WASM/交叉对象或赛事许可。冻结后仍需root明确正式排他grant。')
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dict(plan=str(output),sha256=sha(output),sources=len(names),inputs=len(inputs),calls=656,rss_processes=6))
if __name__=='__main__':main()
