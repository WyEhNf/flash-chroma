"""独立复算照片输出和误差，保存中文报告及机器可读汇总。"""
from pathlib import Path
import hashlib
import json
import re
import sys
import numpy as np

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO.parents[1]
OUT=REPO/'artifacts/official-pr95-20261029'
REPORT=REPO/'report/official-pr95-20261029'
REPORT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((OUT/'input-manifest.json').read_text(encoding='utf-8'))
run=json.loads((OUT/'run-receipt.json').read_text(encoding='utf-8'))
assert run['completed'] and all(x['returncode']==0 for x in run['runs'])
pinned=json.loads((OUT/'run-pinned-receipt.json').read_text(encoding='utf-8'))
assert pinned['completed'] and all(x['returncode']==0 and x['actual_child_affinity']==[0] for x in pinned['runs'])

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def independent_tetra(pixels, folder):
    result=pixels.astype(np.int64)
    for stage in range(1,5):
        blob=(folder/f'stage-{stage}.slut').read_bytes()
        m=int.from_bytes(blob[8:12],'little')
        axes=np.frombuffer(blob,dtype='<f4',count=3*m,offset=16).reshape(3,m).astype(np.int64)
        assert np.all(axes[:,0]==0) and np.all(axes[:,-1]==255)
        index=[];fraction=[]
        for a in range(3):
            # 重新从节点轴推导区间与权重，不使用二进制预计算表。
            j=np.minimum(np.searchsorted(axes[a],result[:,a],side='right')-1,m-2)
            den=axes[a,j+1]-axes[a,j]
            q=((result[:,a]-axes[a,j])*65536+den//2)//den
            index.append(j);fraction.append(q)
        idx=np.stack(index,axis=1);frac=np.stack(fraction,axis=1)
        order=np.argsort(-frac,axis=1,kind='stable')
        f=np.take_along_axis(frac,order,axis=1)
        strides=np.array([m*m,m,1],dtype=np.int64)
        base=idx@strides
        offsets=strides[order]
        positions=np.stack([base,base+offsets[:,0],base+offsets[:,0]+offsets[:,1],base+m*m+m+1],axis=1)
        weights=np.stack([65536-f[:,0],f[:,0]-f[:,1],f[:,1]-f[:,2],f[:,2]],axis=1)
        assert np.all(weights.sum(axis=1)==65536) and weights.min()>=0
        nodes=np.frombuffer(blob,dtype=np.uint8,offset=16+12*m+3840).reshape(-1,3).astype(np.int64)
        result=((nodes[positions]*weights[:,:,None]).sum(axis=1)+32768)//65536
    return result.astype(np.uint8)

summary={'source_commit':manifest['source_commit'],'environment':run,'sets':{},'source_integrity':True,
         'primary_performance_environment':pinned,
         'independent_check':{'python':sys.version,'numpy':np.__version__,'scope':'全部4张官方照片；独立从轴节点推导Q16四面体权重'},
         'notes':['四级均为整步采样；17轴为0,16,...,240,255；33轴为0,8,...,248,255。',
                  'Test2/Test3/Test4文件相同；仅两种不同LUT。','官方首次apply包含输出vector分配；扩展热计时不含分配、读盘或准备。']}
for info in manifest['files']:
    assert sha(ROOT/info['path'])==info['sha256'], '官方输入被改动'

backend={1:'Scalar',2:'AVX2'};rep={0:'Sparse',1:'DirectU8',2:'DirectU16',3:'DirectRGB24'}
for m in (17,33):
    folder=OUT/f'm{m}'
    logs=(folder/'extended-pinned.log').read_text(encoding='utf-8')
    assert 'COMPLETED=1' in logs
    configs=[]
    for line in logs.splitlines():
        if line.startswith('CONFIG '):
            x=dict(re.findall(r'(\w+)=([\d.]+)',line));b=int(x['backend']);r=int(x['rep'])
            samples=[float(z) for z in re.findall(rf'^BATCH cycle=\d+ backend={b} rep={r} ms=([\d.]+)$',logs,re.M)]
            assert len(samples)==9 and int(x['full_domain_equal'])==1
            x={k:(float(v) if k=='prepare_ms' else int(v)) for k,v in x.items()}
            x.update(name=f'{rep[r]} {backend[b]}',batch_samples_ms=samples,
                     batch_median_ms=float(np.median(samples)),batch_min_ms=min(samples),batch_max_ms=max(samples),
                     per_image_average_ms=float(np.median(samples))/4)
            configs.append(x)
    hist=np.zeros(195076,dtype=np.int64);photos=[]
    for i in range(1,5):
        source=np.fromfile(ROOT/f'test/data/image/{i}.bin',dtype=np.uint8).reshape(-1,3)
        actual=np.fromfile(folder/f'candidate-{i}.bin',dtype=np.uint8).reshape(-1,3)
        expected=independent_tetra(source,folder)
        assert np.array_equal(actual,expected), f'独立参考失配 m={m} image={i}'
        reference=np.fromfile(folder/f'reference-{i}.bin',dtype=np.uint8).reshape(-1,3)
        delta=actual.astype(np.int32)-reference.astype(np.int32)
        sq=(delta*delta).sum(axis=1)
        one=np.bincount(sq,minlength=len(hist));hist+=one
        errors=np.sqrt(sq);n=len(sq)
        entry={'image':i,'pixels':n,'mean':float(errors.mean()),'p99':float(np.sqrt(np.searchsorted(one.cumsum(),int(np.ceil(.99*n))))),
               'max':float(errors.max()),'independent_numpy_equal':True,'output_sha256':sha(folder/f'candidate-{i}.bin'),
               'reference_sha256':sha(folder/f'reference-{i}.bin')}
        logged=re.search(rf'QUALITY backend=1 rep=0 image={i} mean=([\d.]+)',logs)
        assert abs(float(logged.group(1))-entry['mean'])<1e-9
        photos.append(entry)
    n=int(hist.sum())
    allstats={'pixels':n,'mean':float(np.dot(hist,np.sqrt(np.arange(len(hist))))/n),
              'p99':float(np.sqrt(np.searchsorted(hist.cumsum(),int(np.ceil(.99*n))))),
              'max':float(np.sqrt(np.flatnonzero(hist)[-1]))}
    official=[{'image':int(i),'seconds':float(t),'mean':float(d)} for i,t,d in re.findall(r'/image/(\d+)\.bin TimeCost: ([\d.]+), Delta: [\d.]+ ([\d.]+)',(folder/'official.log').read_text())]
    assert len(official)==4
    summary['sets'][str(m)]={'quality':allstats,'photos':photos,'configs':configs,'official_first_calls':official,
                            'models':[{'stage':i,'bytes':(folder/f'stage-{i}.slut').stat().st_size,'sha256':sha(folder/f'stage-{i}.slut')} for i in range(1,5)],
                            'not_applicable':[line for line in logs.splitlines() if line.startswith('NOT_APPLICABLE')]}

improvement=1-summary['sets']['33']['quality']['mean']/summary['sets']['17']['quality']['mean']
summary['mean_error_reduction_33_vs_17']=improvement
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')

lines=['# 官方测试框架接入 PR #95 的本机验证','',
'Agent：Codex /root；Operator：本会话用户；Task：按官方 test 包试跑 PR #95；Status：本机试跑与扩展核对完成，未做官方评分认证。','',
'## 测试对象与结论','',
f"使用 PR #95 的精确头文件提交 `{manifest['source_commit']}`，无内核改动。为官方的两个占位函数补充接入，分别从本次 LUT 生成全 17³、全 33³ 模型。稀疏化只使用 LUT；沿用官方整步轴采样、输入轴顺序、输出通道反转、除 16 向下取整，然后由 #95 执行逐级 Q16 四面体与 RGB8 half-up。没有把旧调色 LUT 的训练模型用于新 LUT，也没有运行 LS / max_first 拟合搜索。",'',
'官方提供的是待填实现的框架，原文件直接运行不能验证 #95。本次在 artifacts 生成接入副本，保留原件、官方密集参考计算和误差函数。m=17 对应框架默认参数；m=33 是依据 Readme 允许 17..33 的扩展测试。', '',
'四张图片均为 1024×768 RGB8。Test1 为线性调试 LUT，Readme 明确最终验收不使用；Test2、Test3、Test4 的 SHA256 完全相同，本链只有两种不同 LUT。不能外推至最终未知 LUT、100 张正式图片或所有 LUT 组合。','',
'## 环境、目的与范围','',
f"- 实测：{run['platform']}，{run['cpu']}，MinGW GCC/G++ 8.1.0，C++17，`-O2 -DNDEBUG -Wall -Wextra`。显式 `FLASH_CHROMA_ENABLE_OPENMP=0`，无 `-fopenmp`，所有准备与映射均单线程，CPU-only。",
'- 官方要求的工具链是 MinGW-w64 GCC 13.2.0；本机此次使用 8.1.0，未验证官方版本或 Xeon Gold 6140。正式汇总的热测量固定逻辑 CPU 0，读取子进程亲和确认实际为 [0]，未锁频；数字是本场观察，不授予跨机或稳定加速结论。',
'- 官方首次调用：沿用每图计时，包含适配函数内输出 vector 分配；LUT 解析、稀疏采样与准备在计时外。每种网格跑一次完整四图。',
'- 运行时正确性：每种网格 4 个成功配置各遍历 16,777,216 个 RGB8 输入，与 C99 入口逐字节一致。两入口共用 PR 的整数核心，不把它视作独立算法证明；另用 NumPy 独立从轴节点重算四面体权重，核对全部四图输出，全部一致。',
'- 拟合精度：仅本批 4 张照片，相对官方密集四级参考逐像素计算 RGB 欧氏距离。mean 与官方函数交叉核对；p99/max 为补充指标，p99 使用 nearest-rank。没有完成相对原始密集参考的全色域精度评估。',
'- 热性能：每配置一次预热，9 个正反顺序交错周期；每周期四图，输入输出预分配，计时排除准备/分配/读盘/校验。没有额外 A/A 稳定资格，不与官方首次调用直接算加速比。','',
'首次未固定亲和时，17³ 与 33³ 的多个内核都出现大幅耗时差异，因此有理由增加一次固定 CPU 0 的复测。首次全部原始日志与 summary-unpinned.json 保留；本表统一使用 extended-pinned.log，未混合挑选最快轮次。复测仍逐项重新通过全域正确性，两个网格按 17、33 顺序完成，未做跨网格的独立交错场次，不能据此宣称 33³ 普遍更快。','',
'## 精度结果','',
'| 网格 | 四图像素加权 mean | 合并像素 p99 | max |',
'| --- | ---: | ---: | ---: |']
for m in (17,33):
    q=summary['sets'][str(m)]['quality'];lines.append(f"| {m}³ | {q['mean']:.6f} | {q['p99']:.6f} | {q['max']:.6f} |")
lines += ['',f'本链 33³ 的 mean 相对 17³ 降低 {improvement:.2%}。同一网格所有成功执行表示输出相同，因此精度相同。这里没有官方通过阈值和完整评分公式，不能由程序退出码 0 推断精度达标或得分。','',
'| 图片 | 17³ mean | 33³ mean | 17³ max | 33³ max |','| --- | ---: | ---: | ---: | ---: |']
for a,b in zip(summary['sets']['17']['photos'],summary['sets']['33']['photos']):lines.append(f"| {a['image']} | {a['mean']:.6f} | {b['mean']:.6f} | {a['max']:.6f} | {b['max']:.6f} |")
lines += ['','## 性能与资源','',
'下表均为四图热批次，共 3,145,728 像素；“折合每图”列按批次中位数除以 4，不是逐图中位数。arena 是本配置工作区，另需模型、Runtime 对象和图像缓冲等，不能当作进程 RSS。','',
'| m | 配置 | 四图中位 ms | 四图 min..max ms | 折合每图 ms | 准备 ms（单次） | arena 字节 |','| --- | --- | ---: | ---: | ---: | ---: | ---: |']
for m in (17,33):
    for x in summary['sets'][str(m)]['configs']:
        lines.append(f"| {m} | {x['name']} | {x['batch_median_ms']:.3f} | {x['batch_min_ms']:.3f}..{x['batch_max_ms']:.3f} | {x['per_image_average_ms']:.3f} | {x['prepare_ms']:.3f} | {x['arena']} |")
lines += ['','DirectU8 和 DirectU16 在两种网格、两种后端均返回 Capacity(10)，共 8 项不适用；这不是通过，也不是输出错误。可达颜色超过容量，因此之前调色板专用模型的成绩不能迁移到官方链。全部成功的 RGB24 准备均未启用 suffix-cache 快路径，使用通用准备。', '',
'RGB24 约 48 MiB 的全域表精确保留固定稀疏链，不提升其拟合精度。它是否符合最终参赛对稀疏表示和额外缓存的约束，需要按正式规则确认；本报告只证明本机执行与输出，不能自行判为可提交成绩。Sparse AVX2 是不使用全域 direct 表的对照。', '',
'## 代码与证据','',
'- `code/official-pr95-20261029/prepare.py`：提取 #95 精确头文件、生成官方框架接入副本、记录官方文件哈希。',
'- `adapter.inc`：整数轴采样、SLUT 序列化、四级固定运行时接入；prepare 在第四次 lut_sparse 完成时执行，不读取照片。此适配按官方四次构建顺序绑定一个全局模型组，不是任意模型组并发使用的最终 SDK。',
'- `runner.inc`：保留官方 main，扩展 C99 全色域比较、所有表示资格检查、照片质量和交错热计时。',
'- `run.py`：顺序运行、固定单线程配置并保存环境与退出码。',
'- `pin_and_run.py`：保留首次结果，固定父子进程逻辑 CPU 0 后再次执行扩展验证与计时。',
'- `summarize.py`：独立 NumPy 复算、官方输入完整性检查和本报告生成。',
'- `artifacts/official-pr95-20261029/`：原样头文件、生成 C++、可执行文件、输入 manifest、运行回执、两种网格的 SLUT、参考 / 候选照片输出、原始日志和 summary.json。大文件证据仅本地保存；未提交 GitHub。', '',
'## 复现命令','',
'工作目录为本报告所在 worktree 的根目录：','',
'```powershell',
"$env:PYTHONIOENCODING='utf-8'",
'python code/official-pr95-20261029/prepare.py',
"& 'D:/codeblocks/MinGW/bin/g++.exe' -O2 -DNDEBUG -std=c++17 -Wall -Wextra artifacts/official-pr95-20261029/official_adapter.cpp -o artifacts/official-pr95-20261029/official_adapter.exe",
'python code/official-pr95-20261029/run.py',
'python code/official-pr95-20261029/pin_and_run.py',
'python code/official-pr95-20261029/summarize.py',
'```','',
'复现会覆盖上述固定实验目录，应先复制需要保留的旧记录。官方输入位于 worktree 相对路径 `../../test`；执行前必须存在全部 LUT 与四张 bin。', '',
'## 限制与下一步','',
'1. 优先用 GCC 13.2.0 和最终指定 CPU / 官方评分阈值复验；官方说明禁止多线程，之前 4T 成绩不可直接使用。',
'2. 在保持官方数据契约下尝试 LUT-only 拟合和尾部修正，重点检查图片 2 的大误差；本次仅建立采样基线，不代表 #95 可实现的最优精度。',
'3. 将本次链作为新增测试，后续加入不参与调参、且各级不同的合法 LUT 链；不能只围绕这组重复 LUT 优化。',
'4. 若允许全域缓存，再在目标机复测 RGB24；否则继续在 Sparse AVX2 上优化。切换更大表并不自动保证更快。',
'5. 本机编译成功但 GCC 8.1 对 #95 的 32 字节局部对齐给出 warning，另有上游未使用变量和接入诊断 warning；本场数值检查通过不替代目标编译器验证。没有 C 语言官方框架端到端试跑、最终验收集或正式评分。',
'',
'协作核对：读取了 #95 最新正文，头提交仍为 fb7e195；comments 接口首次传输失败，重试返回空评论。本次未更新 PR、未发布评论、未执行合并。',
]
(REPORT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
evidence=[p for p in OUT.rglob('*') if p.is_file() and p.name!='evidence-manifest.json']
evidence+=list((REPO/'code/official-pr95-20261029').glob('*'))+[REPORT/'report.md']
(OUT/'evidence-manifest.json').write_text(json.dumps({'source_commit':manifest['source_commit'],'files':[{'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in evidence if p.is_file()]},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'quality':{m:s['quality'] for m,s in summary['sets'].items()},'performance':{m:[{k:v for k,v in c.items() if k in ('name','batch_median_ms','per_image_average_ms')} for c in s['configs']] for m,s in summary['sets'].items()},'report':str(REPORT/'report.md')},ensure_ascii=False,indent=2))
