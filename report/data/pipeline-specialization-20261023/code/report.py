"""只从本次已完成的验证与配对计时生成报告，并核对冻结身份。"""
from pathlib import Path
import json,hashlib,statistics,sys,platform
OUT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((OUT/name).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read('plan.json');lock=read('run-lock.json');verification=read('verification.json')
workers=[read(f'worker-{i}.json') for i in [0,1]]
assert verification['complete'] and all(w['complete'] for w in workers)
for path,h in lock['files'].items():assert sha(OUT/path)==h,path
assert len(verification['cases'])==6 and all(len(w['cases'])==6 for w in workers)
assert all(w['plan_sha256']==verification['plan_sha256']==sha(OUT/'plan.json') for w in workers)
assert all(w['input_sha256']==verification['input_sha256'] and w['inputs_unchanged'] for w in workers)
control_ok=all(w['control']['valid'] for w in workers)
summary=[]
for case in plan['cases']:
    ident=(case['recipe'],case['m'])
    v=next(x for x in verification['cases'] if (x['recipe'],x['m'])==ident)
    assert v['full_cube_mismatches']==0 and v['baseline_cube_sha256']==v['candidate_cube_sha256']
    records=[next(x for x in w['cases'] if (x['recipe'],x['m'])==ident) for w in workers]
    pairs=[p for r in records for p in r['pairs']];assert len(pairs)==6
    for pair in pairs:
        a,b=pair['values']['baseline'],pair['values']['candidate']
        assert abs(pair['ratio']-b['seconds']/a['seconds'])<1e-12
        assert a['output_sha256']==b['output_sha256']==v['photos_output_sha256']
    ratios=[p['ratio'] for p in pairs];ratio=statistics.median(ratios)
    worker_ratios=[statistics.median(p['ratio'] for p in r['pairs']) for r in records]
    intermediate_ratios=[p['intermediate_ratio'] for p in pairs]
    intermediate_worker=[statistics.median(p['intermediate_ratio'] for p in r['pairs']) for r in records]
    for p in pairs:
        assert p['values']['intermediate']['output_sha256']==v['photos_output_sha256']
        assert abs(p['intermediate_ratio']-p['values']['candidate']['seconds']/p['values']['intermediate']['seconds'])<1e-12
    intermediate_ok=all(r<=.95 for r in intermediate_worker) and max(intermediate_ratios)<=1.02
    passes=intermediate_ok and control_ok and all(r<=plan['gate']['candidate_each_worker_median_ratio_max'] for r in worker_ratios) and max(ratios)<=plan['gate']['candidate_each_pair_ratio_max']
    summary.append(dict(recipe=ident[0],m=ident[1],kinds=v['kinds'],baseline_ms=statistics.median(p['values']['baseline']['ms_per_image'] for p in pairs),
        candidate_ms=statistics.median(p['values']['candidate']['ms_per_image'] for p in pairs),paired_median_ratio=ratio,speedup=1/ratio,
        time_reduction_percent=100*(1-ratio),worker_median_ratios=worker_ratios,min_pair_ratio=min(ratios),max_pair_ratio=max(ratios),gate_pass=passes,
        runtime_array_bytes=v['runtime_array_bytes'],node_bytes=v['serialized_node_bytes'],intermediate_ms=statistics.median(p['values']['intermediate']['ms_per_image'] for p in pairs),candidate_vs_intermediate_ratio=statistics.median(intermediate_ratios),intermediate_worker_ratios=intermediate_worker))
accepted=all(r['gate_pass'] for r in summary)
env=verification['environment'];root=Path(plan['input_root'])
prior=json.loads((root/'artifacts/lut-applicability-chain/20261021/data/chains.json').read_text(encoding='utf8'))
lines=['# 四级固定插值组合专门化实验（2026-10-23）','',
'Agent：Codex；Operator：本会话用户。阶段：承接 PR #56 的固定四级组合运行时优化。本地结果待审核，未提交或推送 GitHub。',
'','## 1. 本阶段目标与结果','',
'固定三条数值链、17³/33³两档和全部24个阶段模型引用，只改变运行时调用组织。基线保留PR #56的动态mixed函数，中间对照为上一轮的四级展开和kind常量化；本轮候选额外将12个阶段数组切片移到像素循环外，不为每个像素重新建立数组视图。m仍是运行时参数，节点、索引、Q16分数、插值运算顺序、逐级RGB8舍入和输出分配语义不变。没有重新拟合或搜索恢复组合。',
'',
f"完整色域验证6/6通过：每个设置遍历全部16,777,216输入颜色，专门化与动态基线逐字节一致；另有98,304个独立参考探针、12种有限长度和完整100图输出校验。两个进程的A/A控制{'通过' if control_ok else '未通过'}；六个设置的预定性能门槛{'全部通过' if accepted else '未全部通过'}。",
'',
'|链/尺寸|恢复组合，0=四面体/1=三线性|基线 ms/图|专门化 ms/图|配对中位耗时下降|配对吞吐倍数|门槛|',
'|---|---|---:|---:|---:|---:|---|']
for r in summary:lines.append(f"|{r['recipe']}/{r['m']}³|{r['kinds']}|{r['baseline_ms']:.3f}|{r['candidate_ms']:.3f}|{r['time_reduction_percent']:.2f}%|{r['speedup']:.3f}×|{'通过' if r['gate_pass'] else '未通过'}|")
lines+=['','本阶段为第二个独立实验；第一轮结果保存在相邻20261023目录，未改写或重新择优。', '', '|链/尺寸|中间对照 ms/图|外提相对中间对照耗时下降|', '|---|---:|---:|']
for r in summary:lines.append(f"|{r['recipe']}/{r['m']}³|{r['intermediate_ms']:.3f}|{100*(1-r['candidate_vs_intermediate_ratio']):.2f}%|")
lines+=['','时间列是六轮绝对时间的中位数，百分比和倍数则由六个同轮候选/基线配对比的中位数计算；两种统计量不能混用。ms/图为100张图批次的均摊，不是单张请求延迟。所有比较均是今天同机重新测量，不与旧报告时间或其他人的C++/AMD成绩计算速度比。',
'','## 2. 误差与正确性','',
'|链/尺寸|沿用PR56的平均RGB欧氏误差|最差图片P99|最大色差|本次完整色域相对动态基线的字节差|',
'|---|---:|---:|---:|---:|']
for r in summary:
    old=next(x for x in prior if x['recipe']==r['recipe'] and x['m']==r['m'])['modes']['matched']
    lines.append(f"|{r['recipe']}/{r['m']}³|{old['mean']:.6f}|{old['worst_image_p99']:.6f}|{old['max']:.6f}|0|")
lines+=['',
'上表误差数字明确复用PR56逐图证据：本轮百图输出SHA与其完全相同，完整色域也证明固定模型的映射没有变化，因此没有把后端加速描述为拟合精度改善。完整色域零差是候选与同一稀疏模型动态基线之间零差，不是相对原完整LUT零误差。指标不是CIEDE2000。',
'',
'三条链的LUT顺序、模型路径/文件SHA、筛选依据和参数全部保存在plan.json。原照片参与过旧筛选，不是盲测；链为四张创意LUT的数值串联，色彩域兼容性未经认证。独立参考在探针上使用整数Q16四面体及独立NumPy三线性；没有声称完整色域都与独立整数参考重新比较。',
'','## 3. 性能协议与控制','',
'测试目的为固定模型运行时性能，先完成正确性再启动两个串行新进程。Numba固定4线程，两个进程反转设置顺序；每个设置各3轮，动态基线、中间对照、外提候选三方循环轮换顺序，共6轮同场配对。预载100张1024×768 RGB8图片，每配置完整预热后计时；计入输出分配与四级映射，排除读图、模型加载、JIT、误差统计和SHA。每次计时结束后核对完整输出SHA，批次间哈希读取是协议的一部分。',
'',
'A/A采用链1/33³的同一个动态内核，每进程2对；只是检查本轮环境波动，不代表每一组或其他时间段都无噪声。预先冻结：控制中位比在[0.95,1.05]且每对在[0.90,1.10]；候选相对动态基线和中间对照，每个进程的配对中位比均≤0.95，所有单对≤1.02，六组全通过才支持该范围的统一采用建议。失败不修改门槛、不重新计时择优。门槛是本次工程筛查条件，不是统计显著性证明。',
'',
'|控制进程|A/A配对比|中位比|判定|','|---|---|---:|---|']
for w in workers:lines.append(f"|{w['worker']}|{[round(x['ratio'],6) for x in w['control']['pairs']]}|{w['control']['median_ratio']:.6f}|{'通过' if w['control']['valid'] else '未通过'}|")
lines+=['','|链/尺寸|进程0中位比|进程1中位比|最小单对比|最大单对比|','|---|---:|---:|---:|---:|']
for r in summary:lines.append(f"|{r['recipe']}/{r['m']}³|{r['worker_median_ratios'][0]:.6f}|{r['worker_median_ratios'][1]:.6f}|{r['min_pair_ratio']:.6f}|{r['max_pair_ratio']:.6f}|")
lines+=['','## 4. 环境、容量与适用范围','',
f"- 实际机器：{env['platform']}，{env['cpu_name']}，{env['machine']}；Python {env['python']}。",
f"- 依赖：`{json.dumps(env['packages'],ensure_ascii=False)}`；Numba LLVM CPU，线程层 {verification['threading_layer']}，4线程；未启用fastmath，采用本机默认JIT指令选择，未宣称特定C++ ISA实现已验证。",
f"- BLAS/MKL/OMP环境1；CPU亲和性保持系统允许集合 `{verification['affinity']}`，未绑定专用核心、锁频、控温或独占桌面环境。",
'- 数值源码固定PR42提交59586f7bd6dd248cf0b68bcbdff8e41cf95ac572，逐文件SHA与前次冻结快照核验一致。工作分支codex/pipeline-specialization-20261023从pipeline提交3d4d6d9建立。',
'- 两端共享同一批运行时数组，节点载荷和Q16表没有新增；研究入口沿用float64节点/分数数组，并非原生SLUT紧凑字节布局。没有增加完整RGB查找表或16MiB ID缓存。',
'- 专门化增加编译代码种类，代码页/RSS和实际生产启动成本尚未全面核算。verification.json保留首次调用的编译/缓存加载耗时，不纳入稳态提速；不能据此宣称短任务端到端同样加速。',
'- 本轮只验证六份固定模型组合、4线程Numba后端；没有新C++/AVX2/GPU/实板性能、不同线程扩展性、其他LUT模型正确性或官方达标结论。保留同场中间对照，以区分仅展开/常量化与视图外提的差异；没有将变化进一步归因于缓存、锁或具体机器指令，尚无底层计数证据。',
'','## 5. 已开发文件与复现','',
'|文件|作用|','|---|---|',
'|code/kernels.py|保持原动态mixed函数；四种固定kind组合的专门化函数|',
'|code/study.py|输入/源码哈希保护，完整色域与探针验证，同机配对计时和A/A控制|',
'|code/run.py|运行前冻结代码，串行执行验证及两个独立计时进程；拒绝重复启动|',
'|code/report.py|独立复算配对比例、输出SHA和门槛，生成报告与summary.json|',
'|plan.json、run-lock.json|测量前固定的方法、门槛、输入、代码身份|',
'|verification.json|6个设置的完整色域输出SHA、有限输入/独立探针和百图校验|',
'|worker-0.json、worker-1.json|实际环境、每轮时间、顺序、全部输出SHA及控制结果|',
'|verify.log、worker-0.log、worker-1.log|原始运行进度、失败信息（若有）|',
'',
'复现需Python及上列依赖，原冻结模型/照片、PR42隔离源码快照，以及PR56原始plan/chains JSON。plan.json的input_root明确指向本机冻结输入，不自动改用最新分支文件。先在新的输出目录复制代码及计划，核对输入根路径和哈希，再运行；现有结果与run-lock拒绝覆盖。',
'',
'```powershell',"$env:PYTHONIOENCODING='utf-8'",'D:\\anaconda\\python.exe <新的实验目录>/code/run.py','D:\\anaconda\\python.exe <新的实验目录>/code/report.py','```',
'','## 6. 下一步','',
('本次候选在预定范围内通过门槛。建议先作为研究后端选项保留，再把固定四级恢复组合移植到目标C++实现，以相同模型、独立参考和同轮基线验证收益。' if accepted else '本次未满足预定的全部门槛，保留原动态基线和全部结果，不将候选升级为默认。先根据控制是否有效及具体失败设置判断是测量问题还是候选收益不足；下一轮另立计划，不重跑本轮择优。'),
'',
'模型组合的16种插值枚举属于另一个精度选型实验，本轮没有混入；未知模型、完整生产容量/启动成本和目标原生后端验证仍未完成。阶段成果先供用户审核，不自动提交PR。']
(OUT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
(OUT/'summary.json').write_text(json.dumps(dict(control_valid=control_ok,all_cases_pass=accepted,rows=summary),ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'audit.json').write_text(json.dumps(dict(status='通过',purpose='冻结文件身份、输出SHA和配对统计独立复算；不是新增计时',environment=dict(python=sys.version,platform=platform.platform()),files={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='audit.json'}),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(control_valid=control_ok,all_cases_pass=accepted,rows=summary),ensure_ascii=False,indent=2))
