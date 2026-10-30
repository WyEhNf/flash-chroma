"""复用既有固定字节与独立缓存预期，准备四后端服务器包；纯标准库，不拟合/解码/映射或计时。"""
from __future__ import annotations
import argparse
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import zipfile
from skylake_server_support import ROOT,read,save,digest

ROLES={'original':{'pair':'uncached','role':'reference','revision':2,'delta16':False,'cache':False},
       'delta':{'pair':'uncached','role':'candidate','revision':5,'delta16':True,'cache':False},
       'cache':{'pair':'cached','role':'reference','revision':4,'delta16':False,'cache':True},
       'combo':{'pair':'cached','role':'candidate','revision':6,'delta16':True,'cache':True}}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('previous-bundle','cache-gold','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--zip',action='store_true');args=p.parse_args();old=args.previous_bundle.resolve();out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖既有矩阵包')
    previous=read(old/'bundle-manifest.json');gold=read(args.cache_gold/'generation.json')
    if not gold['generation_completed'] or digest(args.cache_gold/'cache-gold.u32')!=gold['gold_sha256']:
        raise ValueError('独立缓存金标准身份不符')
    out.mkdir(parents=True)
    def copy(source,name):
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    # 只复用原清单中的输入，不把先前运行目录或旧源码误带入新包。
    for name,s in previous['files'].items():
        if name.startswith(('artifacts/','assets/','server-inputs/')):
            source=old/name
            if digest(source)!=s['sha256'] or source.stat().st_size!=s['bytes']:raise ValueError('旧输入字节不同：'+name)
            copy(source,name)
    inputs=out/'server-inputs';copy(args.cache_gold/'cache-gold.u32','server-inputs/cache-gold.u32')
    copy(args.cache_gold/'generation.json','server-inputs/cache-gold-generation.json')
    copy(ROOT/'artifacts/skylake-delta-cache-full-v1/results.json','server-inputs/cache-gold-prior-full.json')
    if digest(inputs/'cache-gold-prior-full.json')!=gold['prior_full_sha256']:raise ValueError('金标准前置完整验收不同')
    plans={};native={};upstream=[]
    for key,name in (('uncached','experiments/skylake-delta16-v2.json'),('cached','experiments/skylake-delta-cache-v1.json')):
        source_plan=ROOT/name;original=read(source_plan);current={}
        for file,sha in original['source_sha256'].items():
            if Path(file).suffix not in ('.cpp','.hpp','.h','.c','.cmake') and Path(file).name!='CMakeLists.txt':continue
            if digest(ROOT/file)!=sha:raise ValueError('已验原生源字节变化：'+file)
            current[file]=sha;native[file]=sha
        # 构建脚本按当前身份另冻结；不篡改原计划，派生计划只声明本次来源。
        current['scripts/build_skylake_runtime.py']=digest(ROOT/'scripts/build_skylake_runtime.py')
        derived={**original,'purpose':'四方案矩阵的服务器独立构建计划，原生源码逐字节复用已验版本',
            'fixed_inputs':{k:original['fixed_inputs'][k] for k in ('base','sidecar','cube','prior_full','model','manifest')},
            'source_sha256':current,'server_derivation':{'upstream_plan':{'path':name,'sha256':digest(source_plan)},
                'unchanged_native_sha256':{n:s for n,s in current.items() if not n.startswith('scripts/')},
                'scope':'仅原生源码身份不变；服务器将独立编译和验证，不复用旧库或旧性能结论'}}
        plan_name='server-inputs/plans/'+key+'.json';(out/plan_name).parent.mkdir(parents=True,exist_ok=True)
        save(out/plan_name,derived);plans[key]=plan_name;copy(source_plan,name);upstream.append({'path':name,'sha256':digest(source_plan)})
    first_plan=read(out/plans['uncached']);photo_manifest=read(out/first_plan['fixed_inputs']['manifest']['path'])
    if len(photo_manifest['images'])!=100:raise ValueError('不是固定100图清单')
    import hashlib
    with (out/previous['photo_pixels']).open('rb') as stream:
        for row in photo_manifest['images']:
            raw=stream.read(1024*768*3)
            if len(raw)!=1024*768*3 or hashlib.sha256(raw).hexdigest()!=row['evaluation']['pixel_sha256']:
                raise ValueError('原始像素与冻结照片清单不同：'+row['id'])
        if stream.read(1):raise ValueError('照片流含额外字节')
    extras={'scripts/prepare_skylake_matrix.py','scripts/run_skylake_matrix.py','scripts/skylake_server_support.py',
        'scripts/build_skylake_runtime.py','scripts/verify_skylake_linux_stdlib.py','scripts/run_skylake_server.py'}
    extras.update(x.relative_to(ROOT).as_posix() for x in (ROOT/'experiments/skylake-server-driver').iterdir() if x.is_file())
    sources={**native,**{name:digest(ROOT/name) for name in sorted(extras)}}
    for name in sorted(sources):copy(ROOT/name,name)
    (out/'SERVER_MATRIX_README.md').write_text('''# 四后端固定比较入口

本包只包含已验的原实现、无损坐标差、精确缓存及其组合，修订2/5/4/6；静态停止原型不参与。复用既有a399模型、100图字节及完整整数预期，不重新拟合或变更质量。原照片用途限制保存在assets/photos/manifest.json，不声明新许可，原始大流只在本地传输包。

Linux x86_64需要Python 3.11及以上标准库、CMake 3.24及以上、GNU C/C++和OpenMP，无需NumPy/Pillow。解包进入目录后：

```sh
python3 scripts/run_skylake_matrix.py --bundle bundle-manifest.json --output artifacts/server-matrix-v1 --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc --measure
```

省略--measure只完成集中正确性。--cpus可指定同L3/NUMA的4个不同物理核，默认从实际允许集合选择；--expected-cpu须匹配所选各CPU的完整型号原文，只作SKU核对，不自动判定微架构。

入口逐字节检查包，在该机器独立构建两组共4库和原生计时器。先验有限边界、24组完整256³、缓存全表与100图，再冻结本次库/正确性身份，显式执行唯一四进程同场比较。每角色在每个序位出现一次，1/4线程和整批/逐图模式平衡，每配置5轮，共320轮100图组。准备、apply、copy+apply、外层墙钟和逐图描述性尾部分列，排除IO/解码/拟合。真实C ABI成本与旧内部bench不同，不混用绝对时间。

输出必须新目录；失败保留日志，不自动重跑或调参。实际CPU/微码/GDS、NUMA/缓存、线程落点、编译器及所有已加载库SHA记录；不改安全设置或频率。AMD/WSL的协议验证和计时不能替代Skylake；官方数据/Threshold、侧表/派生缓存许可仍待确认。
''',encoding='utf-8')
    for name,sha in sources.items():
        if digest(ROOT/name)!=sha:raise ValueError('复制期间源码变化')
    files={x.relative_to(out).as_posix():{'path':x.relative_to(out).as_posix(),'sha256':digest(x),'bytes':x.stat().st_size}
           for x in sorted(out.rglob('*')) if x.is_file()}
    result={'schema':2,'purpose':__doc__,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_tree_status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        'environment':{'platform':platform.platform(),'python':sys.version},'source_sha256':sources,'files':files,
        'plans':plans,'roles':ROLES,'upstream_plans':upstream,'prior_bundle_sha256':digest(old/'bundle-manifest.json'),
        'photo_pixels':previous['photo_pixels'],'photo_records':previous['photo_records'],
        'photo_output_sha256':previous['photo_output_sha256'],'single_oracle_stream':previous['single_oracle_stream'],
        'fixture_manifest':previous['fixture_manifest'],'full_proof':previous['full_proof'],
        'cache_gold':'server-inputs/cache-gold.u32','cache_gold_generation':'server-inputs/cache-gold-generation.json',
        'photo_stream_verified_against_manifest':True,
        'new_decodes':0,'new_fits':0,'native_calls':0,'performance_calls':0,
        'scope':'固定字节复制及新源计划准备；尚无本包Linux或Skylake执行结果'}
    save(out/'bundle-manifest.json',result)
    if args.zip:
        with zipfile.ZipFile(str(out)+'.zip','w',zipfile.ZIP_DEFLATED) as z:
            for x in sorted(out.rglob('*')):
                if x.is_file():z.write(x,x.relative_to(out).as_posix())
    print('矩阵包准备完成：',len(files),'项；清单SHA',digest(out/'bundle-manifest.json'),flush=True)

if __name__=='__main__':main()
