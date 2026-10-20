"""复用已验输入/预期准备4对16服务器包；生成与目标均只需标准库，不重新生成数值预期。"""
from __future__ import annotations
import argparse,ast,hashlib,json,platform,shutil,subprocess,sys,zipfile
from pathlib import Path
from skylake_server_support import ROOT,read,save,digest

ROLES={'cache':{'pair':'domain','role':'reference','revision':4,'delta16':False,'cache':True},
       'domain_isolated':{'pair':'domain','role':'candidate','revision':16,'delta16':False,'cache':True}}


def runtime_sources():
    pending=['scripts/run_skylake_domain_server.py'];seen=set()
    while pending:
        name=pending.pop()
        if name in seen:continue
        seen.add(name);tree=ast.parse((ROOT/name).read_text(encoding='utf-8'));modules=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):modules.extend(n.name.split('.')[0] for n in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:modules.append(node.module.split('.')[0])
        for module in modules:
            local='scripts/'+module+'.py'
            if (ROOT/local).is_file():pending.append(local)
            elif module not in sys.stdlib_module_names:raise ValueError('目标非标准库导入：'+module)
    return seen


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('previous-bundle','plan','full','cache-contract','domain-contract','performance','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--zip',action='store_true');args=p.parse_args();old=args.previous_bundle.resolve();out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖已生成包')
    previous=read(old/'bundle-manifest.json');plan=read(args.plan);full=read(args.full);domain=read(args.domain_contract);perf=read(args.performance)
    if plan['revisions']!={'reference':4,'candidate':16} or not full['pass'] or not domain['pass'] or not perf['accepted_on_this_host']:
        raise ValueError('需要固定4/16和同机已通过回执')
    if full['plan_sha256']!=digest(args.plan) or domain['plan_sha256']!=digest(args.plan) or full['build_sha256']!=domain['build_sha256']:
        raise ValueError('正确性回执身份不同')
    if digest(args.cache_contract)!=domain['cache_contract_sha256']:
        raise ValueError('窄带夹具不是域诊断使用的同一缓存合同')
    if not full['cache_domain_certificate']['chain']['fast_path_enabled']:raise ValueError('实际候选未启用域证明快路径')
    native={n:s for n,s in plan['source_sha256'].items() if Path(n).suffix in ('.cpp','.hpp','.h','.c','.cmake') or Path(n).name=='CMakeLists.txt'}
    for name,s in native.items():
        if digest(ROOT/name)!=s:raise ValueError('原生源码变化：'+name)
    out.mkdir(parents=True)
    def copy(path,name):
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
    def oldcopy(name):
        entry=previous['files'][name]
        if digest(old/name)!=entry['sha256'] or (old/name).stat().st_size!=entry['bytes']:raise ValueError('旧包字节不同：'+name)
        copy(old/name,name)
    for key in ('base','sidecar','cube','prior_full','model','manifest'):
        spec=plan['fixed_inputs'][key]
        if digest(ROOT/spec['path'])!=spec['sha256']:raise ValueError('固定输入不同')
        copy(ROOT/spec['path'],spec['path'])
    for spec in plan['suffix_models']:
        if digest(ROOT/spec['path'])!=spec['sha256']:raise ValueError('后缀输入不同')
        copy(ROOT/spec['path'],spec['path'])
    for name in (previous['photo_pixels'],previous['single_oracle_stream'],previous['cache_gold'],previous['cache_gold_generation']):oldcopy(name)
    fixture=read(old/previous['fixture_manifest'])
    for name in previous['files']:
        if name.startswith(('server-inputs/fixtures/','server-inputs/layout-fixtures/')) and name!=previous['fixture_manifest'] and 'storage' not in Path(name).name:
            oldcopy(name)
    by_label={row['fixture']:row['certificate'] for row in domain['cases']}
    fixture_bindings=[]
    for case in fixture['cases']:
        case.pop('storage_gold',None)
        if case['name'].startswith('cache_'):
            label=case['name'].removeprefix('cache_')
            if label not in by_label:raise ValueError('缺少窄带诊断')
            evidence={}
            for name in [*case['models'],*[p for p in case['sidecars'] if p]]:
                local=args.cache_contract.parent/Path(name).name
                if not local.is_file() or digest(local)!=digest(out/name):raise ValueError('同名夹具字节不一致，不能绑定域预期：'+name)
                evidence[name]=digest(local)
            case['domain_certificate_expected']=by_label[label]
            fixture_bindings.append({'case':case['name'],'model_sidecar_sha256':evidence})
    fixture['purpose']='13个既有有限整数/窄带预期原字节复用，补入Windows已验域诊断；不重新拟合或生成输出'
    fixture_name='server-inputs/domain-fixtures.json';save(out/fixture_name,fixture)
    runtime=runtime_sources();extras=runtime|{'scripts/prepare_skylake_domain_server.py','scripts/build_skylake_runtime.py'}
    extras|={p.relative_to(ROOT).as_posix() for p in (ROOT/'experiments/skylake-server-driver').iterdir() if p.is_file()}
    sources={**native,**{name:digest(ROOT/name) for name in sorted(extras)}}
    for name in sources:copy(ROOT/name,name)
    derived={**plan,'purpose':'域证明4/16服务器独立构建；原生源码与已验Windows候选逐字节相同，正式判定在服务器重做',
        'fixed_inputs':{k:plan['fixed_inputs'][k] for k in ('base','sidecar','cube','prior_full','model','manifest')},
        'source_sha256':{**native,'scripts/build_skylake_runtime.py':sources['scripts/build_skylake_runtime.py']},
        'server_derivation':{'upstream_plan_sha256':digest(args.plan),'native_source_unchanged':True,'local_performance_accepted':True}}
    plan_name='server-inputs/plans/domain.json';(out/plan_name).parent.mkdir(parents=True);save(out/plan_name,derived)
    for path,label in ((args.full,'full'),(args.domain_contract,'domain-contract'),(args.performance,'performance')):
        copy(path,'server-inputs/windows-'+label+'.json')
    with (out/previous['photo_pixels']).open('rb') as stream:
        for row in previous['photo_records']:
            raw=stream.read(1024*768*3)
            expected=row.get('pixel_sha256',row.get('sha256'))
            if len(raw)!=1024*768*3 or hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('固定100图逐图原字节不同')
        if stream.read(1):raise ValueError('照片流有多余数据')
    readme='''# 域证明4/16服务器验收

目标Linux x86_64需Python3.11+标准库、CMake3.24+、GNU C/C++及OpenMP；无需NumPy/Pillow。默认仅正确性：

```sh
python3 scripts/run_skylake_domain_server.py --bundle bundle-manifest.json --output artifacts/domain-server-v1 --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc
```

正式Skylake先核对实际SKU/系统/微码/GDS/NUMA及同L3不同物理核，可加--expected-cpu完整型号及--cpus四个核号，再显式加--measure。四串行新进程AB/BA/BA/AB，1/4线程及整批/逐图，每配置5轮，共160组百图；每轮输出SHA在原生计时外核验。四种场景全部达到中位改善3%、最差apply进程回退不超2%、copy+apply和准备加已预热首轮不退化才通过，不重试或扫描。

先执行3432项有限字节比较、域证明诊断/拒绝、原缓存全槽、12组完整256³、8个调度配置各两轮百图、14项计时器拒绝及回调中止。正确性阶段调用计时器，但时长不作性能比较。

Windows/AMD的7.07%/5.10%是该轮同机描述，不代替Skylake结果；Linux新编译必须重验。原回退内核逐字节保留只证明其对象，不表示新准备/入口成本为零。默认、模型、题目误差口径不变；官方数据、Threshold和派生缓存许可待取得，不改安全或频率设置。
'''
    (out/'SERVER_DOMAIN_README.md').write_text(readme,encoding='utf-8')
    for name,s in sources.items():
        if digest(ROOT/name)!=s:raise ValueError('打包期间源变化')
    files={p.relative_to(out).as_posix():{'path':p.relative_to(out).as_posix(),'sha256':digest(p),'bytes':p.stat().st_size}
           for p in sorted(out.rglob('*')) if p.is_file()}
    result={'schema':3,'purpose':__doc__,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'environment':{'platform':platform.platform(),'python':sys.version},'files':files,'source_sha256':sources,
        'plans':{'domain':plan_name},'roles':ROLES,'photo_pixels':previous['photo_pixels'],'photo_records':previous['photo_records'],
        'photo_output_sha256':previous['photo_output_sha256'],'single_oracle_stream':previous['single_oracle_stream'],
        'fixture_manifest':fixture_name,'cache_gold':previous['cache_gold'],'cache_gold_generation':previous['cache_gold_generation'],
        'domain_expected_actual':full['cache_domain_certificate']['chain'],'domain_expected_single':full['cache_domain_certificate']['single'],
        'domain_fixture_identity_bindings':fixture_bindings,
        'runtime_local_modules':sorted(runtime),'prior_bundle_sha256':digest(old/'bundle-manifest.json'),
        'upstream_plan_sha256':digest(args.plan),'upstream_correctness_sha256':digest(args.full),'upstream_performance_sha256':digest(args.performance),
        'local_performance_accepted':True,'new_decodes':0,'new_fits':0,'new_pixel_mappings':0,'project_native_calls':0,'performance_comparisons':0,
        'scope':'复用字节/诊断与依赖闭包，不代表目标端运行通过；所有原4方案/4对13包保持不变'}
    save(out/'bundle-manifest.json',result)
    if args.zip:
        with zipfile.ZipFile(str(out)+'.zip','w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():z.write(p,p.relative_to(out).as_posix())
    print('域证明服务器包完成：',len(files),'文件，SHA',digest(out/'bundle-manifest.json'),flush=True)


if __name__=='__main__':main()
