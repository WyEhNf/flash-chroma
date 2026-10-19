"""复用已验字节，准备缓存布局双库服务器包与独立小型预期；生成端需要NumPy，目标端仅标准库。"""
from __future__ import annotations
import argparse
import ast
import hashlib
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import zipfile
import numpy as np
from skylake_server_support import ROOT,read,save,digest
sys.path.insert(0,str(ROOT/'python'))
from lutlab import channel_coordinates as cc,io
from verify_channel_coordinates import integer_oracle

ROLES={'cache':{'pair':'layout','role':'reference','revision':4,'delta16':False,'cache':True},
       'r_contiguous':{'pair':'layout','role':'candidate','revision':13,'delta16':False,'cache':True}}

def runtime_sources():
    # 只闭包目标端入口的本地导入；生成端NumPy不进入运行依赖。
    pending=['scripts/run_skylake_layout_server.py'];seen=set()
    while pending:
        source_name=pending.pop()
        if source_name in seen:continue
        seen.add(source_name);tree=ast.parse((ROOT/source_name).read_text(encoding='utf-8'))
        modules=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):modules.extend(n.name.split('.')[0] for n in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:modules.append(node.module.split('.')[0])
        for module_name in modules:
            local='scripts/'+module_name+'.py'
            if (ROOT/local).is_file():pending.append(local)
            elif module_name not in sys.stdlib_module_names:raise ValueError('目标端出现未冻结的非标准库依赖：'+module_name)
    return seen


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('previous-bundle','archive','plan','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--zip',action='store_true');args=p.parse_args();old=args.previous_bundle.resolve();out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖旧服务器包')
    previous=read(old/'bundle-manifest.json');original=read(args.plan);archive=args.archive.resolve();manifest=read(archive/'manifest.json')
    if original['revisions']!={'reference':4,'candidate':13}:raise ValueError('本次固定比较4/13')
    def archived(name):
        path=archive/name;s=manifest['files'][name]
        if digest(path)!=s['sha256'] or path.stat().st_size!=s['bytes']:raise ValueError('已归档字节不同：'+name)
        return path
    for n in ('contract-results.json','cache-contract-results.json','layout-contract-results.json','full-results.json'):
        if not read(archived(n))['pass']:raise ValueError('前置正确性未通过')
    local=read(archived('performance-results.json'))
    if not local['measurement_completed'] or local['accepted_on_this_host'] is not False:raise ValueError('应保留本机未通过的真实状态')
    upstream_plan=archived('plan.json')
    if digest(upstream_plan)!=digest(args.plan):raise ValueError('当前原生计划不是该次已验计划')
    native={n:sha for n,sha in original['source_sha256'].items() if Path(n).suffix in ('.cpp','.hpp','.h','.c','.cmake') or Path(n).name=='CMakeLists.txt'}
    for name,sha in native.items():
        if digest(ROOT/name)!=sha:raise ValueError('已验原生源变化：'+name)
    out.mkdir(parents=True)
    def copy(path,name):
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest);return name
    def oldcopy(name):
        s=previous['files'][name];path=old/name
        if digest(path)!=s['sha256'] or path.stat().st_size!=s['bytes']:raise ValueError('旧包输入字节不同：'+name)
        return copy(path,name)
    for key in ('base','sidecar','cube','prior_full','model','manifest'):
        s=original['fixed_inputs'][key]
        if digest(ROOT/s['path'])!=s['sha256']:raise ValueError('固定模型或完整流不同')
        copy(ROOT/s['path'],s['path'])
    for s in original['suffix_models']:
        if digest(ROOT/s['path'])!=s['sha256']:raise ValueError('固定后缀不同')
        copy(ROOT/s['path'],s['path'])
    for name in (previous['photo_pixels'],previous['single_oracle_stream'],previous['cache_gold'],previous['cache_gold_generation']):oldcopy(name)
    fixture=read(old/previous['fixture_manifest'])
    for name in previous['files']:
        if name.startswith('server-inputs/fixtures/'):oldcopy(name)
    photo_manifest=read(out/original['fixed_inputs']['manifest']['path'])
    if len(photo_manifest['images'])!=100:raise ValueError('固定照片不是100张')
    with (out/previous['photo_pixels']).open('rb') as stream:
        for row in photo_manifest['images']:
            raw=stream.read(1024*768*3)
            if len(raw)!=1024*768*3 or hashlib.sha256(raw).hexdigest()!=row['evaluation']['pixel_sha256']:raise ValueError('原始照片像素不同')
        if stream.read(1):raise ValueError('照片流有额外字节')
    gold=read(out/previous['cache_gold_generation']);actual=np.fromfile(out/previous['cache_gold'],dtype='<u4');b=gold['bounds']
    nr=b['r_max']-b['r_min']+1;ng=b['dg_max']-b['dg_min']+1;nb=b['db_max']-b['db_min']+1
    storage=out/'server-inputs/cache-storage-gold.u32';actual.reshape(nr,ng,nb).transpose(2,1,0).copy().tofile(storage)
    directory=out/'server-inputs/layout-fixtures';directory.mkdir()
    fixture_archive=archived('fixture-bytes.zip')
    with zipfile.ZipFile(fixture_archive) as z:
        for name in z.namelist():
            if name.startswith('skylake-r-contiguous-cache-contract-v1/'):
                dest=directory/Path(name).name
                if dest.exists() or dest.suffix not in ('.slut','.bin'):raise ValueError('缓存夹具文件重名或格式非法')
                dest.write_bytes(z.read(name))
    paths=[directory/f'model{i}.slut' for i in range(4)];sides=[directory/f'side{i}.bin' for i in range(4)]
    cases=[('shared_shared',[None]*4,False),('unshared_shared',[sides[0],None,None,None],True),
        ('shared_mixed',[None,sides[1],None,sides[3]],False),('unshared_mixed',sides,True),
        ('equal_changed_shared',[directory/'equal-changed.bin',None,None,None],False)]
    cache_windows=read(archived('cache-contract-results.json'));cache_expect={r['fixture']:r['cache_info'] for r in cache_windows['cache_entry_audits']}
    seed=2026102013;rng=np.random.default_rng(seed);probes=rng.integers(0,256,(8192,3),np.uint8);new_cases=[]
    def relative(path):return path.relative_to(out).as_posix()
    for label,side_paths,mixed in cases:
        models=[]
        for path,side in zip(paths,side_paths):
            model=cc.from_sparse(io.load_sparse(path,competition=True))
            if side:model.channel_frac[:]=np.fromfile(side,dtype='<u4').reshape(3,3,256)
            cc.validate(model);models.append(model)
        info=cache_expect[label];bounds={k:info[k] for k in ('r_min','r_max','dg_min','dg_max','db_min','db_max')}
        first=integer_oracle(models[0],probes).astype(np.int32);r=first[:,0];dg=first[:,1]-r;db=first[:,2]-r
        hits=(r>=bounds['r_min'])&(r<=bounds['r_max'])&(dg>=bounds['dg_min'])&(dg<=bounds['dg_max'])&(db>=bounds['db_min'])&(db<=bounds['db_max'])
        if not hits.any() or (mixed and hits.all()) or (not mixed and not hits.all()):raise ValueError('冻结seed没有预期命中覆盖，不扫描seed')
        packet=np.resize(probes[hits][:8],(8,3)).copy();second=packet.copy()
        if mixed:second[-1]=probes[np.flatnonzero(~hits)[0]]
        source=np.resize(np.concatenate((packet,second)),(4097,3)).astype(np.uint8);truth=source.copy();stage1=integer_oracle(models[0],source)
        for model in models:truth=integer_oracle(model,truth)
        input_path=directory/(label+'-input.rgb');expected_path=directory/(label+'-expected.rgb');first_path=directory/(label+'-first.rgb')
        source.tofile(input_path);truth.tofile(expected_path);stage1.tofile(first_path)
        rr,gg,bb=np.meshgrid(*[np.arange(bounds[a],bounds[z]+1,dtype=np.int32) for a,z in
            [('r_min','r_max'),('dg_min','dg_max'),('db_min','db_max')]],indexing='ij')
        colours=np.column_stack((rr.ravel(),(rr+gg).ravel(),(rr+bb).ravel()));valid=((colours>=0)&(colours<=255)).all(axis=1)
        values=colours[valid].astype(np.uint8)
        for model in models[1:]:values=integer_oracle(model,values)
        packed=np.zeros(len(colours),dtype='<u4');packed[valid]=values[:,0].astype(np.uint32)|(values[:,1].astype(np.uint32)<<8)|(values[:,2].astype(np.uint32)<<16)
        if len(packed)!=info['entries'] or int(valid.sum())!=info['valid_entries']:raise ValueError('独立窄带表计数不同')
        canonical=directory/(label+'-gold.u32');physical=directory/(label+'-storage.u32');packed.tofile(canonical)
        packed.reshape(rr.shape).transpose(2,1,0).copy().tofile(physical)
        new_cases.append({'name':'cache_'+label,'models':[relative(x) for x in paths],'sidecars':[relative(x) if x else None for x in side_paths],
            'layouts':None,'input':relative(input_path),'expected':relative(expected_path),'first_expected':relative(first_path),
            'first_two_packet_hits':[8,7 if mixed else 8],'cache_gold':relative(canonical),'storage_gold':relative(physical),
            'cache_expected':{'enabled':1,'entries':info['entries'],'valid_entries':info['valid_entries'],'table_capacity_bytes':info['table_capacity_bytes'],'bounds':bounds}})
    combined={**fixture,'purpose':'复用8个分通道边界输入，追加5个既有窄带模型的全命中/混合命中/真实存储独立预期，不调用原生核',
        'cases':[*fixture['cases'],*new_cases],'narrow_seed':seed,'upstream_cache_fixture_archive_sha256':digest(fixture_archive),
        'oracle_source_sha256':digest(ROOT/'scripts/verify_channel_coordinates.py')}
    fixture_name='server-inputs/layout-fixtures/manifest.json';save(out/fixture_name,combined)
    extras={'scripts/prepare_skylake_layout_server.py','scripts/run_skylake_layout_server.py','scripts/skylake_server_support.py',
        'scripts/run_skylake_server.py','scripts/build_skylake_runtime.py'}
    runtime=runtime_sources();extras.update(runtime)
    extras.update(x.relative_to(ROOT).as_posix() for x in (ROOT/'experiments/skylake-server-driver').iterdir() if x.is_file())
    sources={**native,**{n:digest(ROOT/n) for n in sorted(extras)}}
    for n in sources:copy(ROOT/n,n)
    derived={**original,'purpose':'R连续缓存双库服务器独立构建，逐字节复用修订4/13原生源码，采用判定在服务器重做',
        'fixed_inputs':{k:original['fixed_inputs'][k] for k in ('base','sidecar','cube','prior_full','model','manifest')},
        'source_sha256':{**native,'scripts/build_skylake_runtime.py':sources['scripts/build_skylake_runtime.py']},
        'server_derivation':{'upstream_plan_sha256':digest(args.plan),'native_source_unchanged':True,'local_performance_accepted':False}}
    plan_name='server-inputs/plans/layout.json';(out/plan_name).parent.mkdir(parents=True);save(out/plan_name,derived)
    copy(args.plan,args.plan.resolve().relative_to(ROOT).as_posix());copy(archived('performance-results.json'),'server-inputs/windows-performance.json')
    (out/'SERVER_LAYOUT_README.md').write_text('''# 缓存布局双库服务器验收

本包比较原缓存修订4与R连续缓存修订13。模型、范围、表值及容量相同，Windows本机唯一比较因一个四线程进程回退超2%而未通过；本包不升级默认，不改旧四方案包，不把本机结果当Skylake成绩。照片用途限制保留在assets/photos/manifest.json。

目标Linux x86_64需Python3.11及以上标准库、CMake3.24及以上、GNU C/C++和OpenMP，无需NumPy/Pillow。解包后运行：

```sh
python3 scripts/run_skylake_layout_server.py --bundle bundle-manifest.json --output artifacts/layout-server-v1 --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc
```

默认只构建和集中正确性，不运行性能比较。正式Skylake验收需先记录真实SKU、系统、微码/GDS和允许CPU集合；可加--expected-cpu完整型号及--cpus四个同L3/NUMA不同物理核。确认后显式加--measure，执行唯一固定四串行新进程AB/BA/BA/AB、1/4线程、整批/逐图、每配置5轮，共160组100图。每轮完整输出SHA在原生计时之外核验，源、库、团队落点及容量均记录。该逐轮校验协议不同于旧内部bench，不混用绝对时间。

先验13个固定边界/窄带布局的3432次偏移/尾部比较，完整物理缓存与独立表、12组完整256³、两种调度的8个配置各两轮百图和计时器拒绝契约。调度验证经过计时器但时长不用于性能结论。所有场景须同时满足apply配对中位改善至少3%、任一进程回退不超过2%、copy+apply及准备+已预热首100图不退化，才可通过本次机器门槛。没有自动重试、扫描、安装依赖、改安全缓解或改频。输出必须新目录；失败日志保留。

生成端使用NumPy导出少量独立预期，服务器只读冻结字节。原始100图/完整流只放本地传输包，不入Git。AMD/WSL验证不是Skylake实测，官方数据/Threshold和派生表许可仍待确认。
''',encoding='utf-8')
    for n,sha in sources.items():
        if digest(ROOT/n)!=sha:raise ValueError('打包时源改变')
    files={x.relative_to(out).as_posix():{'path':x.relative_to(out).as_posix(),'sha256':digest(x),'bytes':x.stat().st_size} for x in sorted(out.rglob('*')) if x.is_file()}
    result={'schema':3,'purpose':__doc__,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},'source_sha256':sources,'files':files,
        'plans':{'layout':plan_name},'roles':ROLES,'photo_pixels':previous['photo_pixels'],'photo_records':previous['photo_records'],
        'photo_output_sha256':previous['photo_output_sha256'],'single_oracle_stream':previous['single_oracle_stream'],
        'fixture_manifest':fixture_name,'cache_gold':previous['cache_gold'],'cache_gold_generation':previous['cache_gold_generation'],
        'cache_storage_gold':relative(storage),'prior_bundle_sha256':digest(old/'bundle-manifest.json'),'runtime_local_modules':sorted(runtime),
        'upstream_correctness_sha256':digest(archived('full-results.json')),'upstream_performance_sha256':digest(archived('performance-results.json')),
        'local_performance_accepted':False,'new_decodes':0,'new_fits':0,'project_native_calls':0,'performance_comparisons':0,
        'scope':'冻结字节复制及5个小型独立整数预期导出，不构成服务器正确性或性能通过'}
    save(out/'bundle-manifest.json',result)
    if args.zip:
        with zipfile.ZipFile(str(out)+'.zip','w',zipfile.ZIP_DEFLATED) as z:
            for x in sorted(out.rglob('*')):
                if x.is_file():z.write(x,x.relative_to(out).as_posix())
    print('布局服务器包准备完成：',len(files),'文件，SHA',digest(out/'bundle-manifest.json'),flush=True)


if __name__=='__main__':main()
