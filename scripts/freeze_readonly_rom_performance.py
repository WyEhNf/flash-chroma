"""RO完整质量后、唯一八角色正式前冻结输入闭包；不运行性能。"""
import ast
from pathlib import Path
from study_memory_rom import ROOT,sha,read,save
def main():
    output=ROOT/'experiments/memory-rom-readonly-performance-v1.json'
    if output.exists():raise FileExistsError('不能覆写冻结正式计划')
    quality_plan=ROOT/'experiments/memory-rom-readonly-v1.json';q=read(quality_plan)
    if sha(quality_plan)!='95b289d4f0a40baa1974fd902a6ceb59f7986c5bc67216f8ae8714468d1cc855':raise AssertionError('已执行质量计划不同')
    if any(sha(ROOT/n)!=v for n,v in q['source_sha256'].items()):raise AssertionError('已验源改变')
    sources=set(q['source_sha256'])|{'experiments/memory-rom-readonly-v1.json','scripts/bench_readonly_rom.py','scripts/freeze_readonly_rom_performance.py','scripts/audit_readonly_rom_performance.py','scripts/bench_le16_block1024.py','experiments/skylake-andn-split-v1.json'}
    for name in sources:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    data=Path('F:/Hackathon/projects/16-lut-color');build=ROOT/'artifacts/p16-memory-build-v2';ref78=build/'jshc_memory_ref78.dll';ref80=Path('F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/baseline/libjshc_skylake_andn_normal.dll');inputs=dict(q['input_sha256'])
    for path in (ref78,ref80):inputs[str(path)]=sha(path)
    if inputs[str(ref78)]!='bac736cd9933c5a87a31909ba3652c204ee36ccf7915d1d2071f80637cd896ce' or inputs[str(ref80)]!='c9d8a28ecac46de47037572f1985bc2010c0c8a745df74450ca204e6f9721917':raise AssertionError('同源78/80身份不同')
    spec=read(ROOT/'experiments/skylake-andn-split-v1.json')
    for item in [spec['fixed_inputs']['base'],spec['fixed_inputs']['sidecar'],*spec['suffix_models']]:
        path=data/item['path'];inputs[str(path)]=sha(path)
        if inputs[str(path)]!=item['sha256']:raise AssertionError('原a399模型输入不同')
    for folder in (build,ref80.parent,Path(q['library']).parent):
        for name in ('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll'):
            path=folder/name;inputs[str(path)]=sha(path)
    quality=ROOT/'artifacts/p16-readonly-rom-quality-v1'
    for name in ('execution.json','commit-summary.json','original_cow/results.json','cow/results.json','readonly/results.json','quality/results.json'):path=quality/name;inputs[str(path)]=sha(path)
    if read(quality/'execution.json')['status']!='quality-passed-performance-not-run' or not read(quality/'commit-summary.json')['passed'] or not read(quality/'quality/results.json')['passed']:raise AssertionError('完整质量/提交门槛未通过')
    save(output,dict(purpose=__doc__,source_sha256={n:sha(ROOT/n) for n in sorted(sources)},input_sha256=inputs,quality_plan_sha256=sha(quality_plan),library=q['library'],rom=q['rom'],data_root=str(data),build=str(build),reference78=str(ref78),reference80=str(ref80),labels=['ref78','ref80','original_avx','original_c99','cow_avx','cow_c99','readonly_avx','readonly_c99'],protocol='唯一4镜像新worker、8角色全驻留、相同图片地址；0x55进程允许集但无逐OMP绑定/锁频。双接口1/4线程各1+5完整100图；640正式+128预热+80AA=848调用，8同import独立RSS。全部原轮次/端点/正确性/实际库保护保留，不补跑。',gates='每worker较快78/80耗时/候选耗时，全部worker最劣分别按100/90/80/70/60/50；AA单对[.8,1.25]且中位[1/1.1,1.1]，无效全档清空。精度轴独立100%，不能用慢COW分母授速度。',auxiliary_pairs='RO/原ACCESS_COPY和RO/新WinAPI-COW各AVX/C99，以control耗时/RO耗时，全部worker原数与最劣/median另列，并标同场AA；不改变主资格。',memory='所有ROM16778272+model1056=16779328B；新RO只承诺实测提交收益，不冒称capacity/物理WS下降。原COW微实验close句柄+1观察原因未知保留。',stop='任一输入或输出不符停止保留，不修后重采同阶段；有效模式低50拒绝对应资格，AA无效不能授档。',performance_status='冻结不表示已执行；root另授排他窗才一次运行。'))
    print(dict(plan=str(output),sha256=sha(output)))
if __name__=='__main__':main()
