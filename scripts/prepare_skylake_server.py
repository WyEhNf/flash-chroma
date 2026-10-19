"""一次准备服务器固定字节包：只导出既有模型、照片和独立整数夹具，不调用原生核、拟合或性能基准。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from PIL import Image, __version__ as pillow_version
from lutlab import channel_coordinates as cc, io
from verify_channel_coordinates import integer_oracle
from skylake_server_support import read, digest, checked, save

LENGTHS=[0,1,7,8,9,15,16,17,4095,4096,4097]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--layout-contract',type=Path,required=True)
    p.add_argument('--full',type=Path,required=True)
    p.add_argument('--prior-worker',type=Path,required=True)
    p.add_argument('--single-oracle-stream',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--zip',action='store_true',help='额外生成完整传输ZIP，保存在忽略目录，不提交原始像素')
    args=p.parse_args();out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖已有服务器字节包')
    plan=read(args.plan);contract=read(args.layout_contract/'results.json');full=read(args.full)
    worker=read(args.prior_worker)
    if (not contract['pass'] or not full['pass'] or contract['plan_sha256']!=digest(args.plan)
        or full['plan_sha256']!=digest(args.plan) or worker['full_acceptance_sha256']!=digest(args.full)):
        raise ValueError('需要同一冻结计划、已通过布局合同和完整照片回执')
    if 'delta16_policy' not in plan:raise ValueError('本次字节包只准备已验delta16模型')
    source_names=set(plan['source_sha256'])
    source_names.update({'scripts/skylake_server_support.py','scripts/prepare_skylake_server.py',
        'scripts/run_skylake_server.py','scripts/verify_skylake_linux_stdlib.py'})
    source_names.update(x.relative_to(ROOT).as_posix() for x in (ROOT/'experiments/skylake-server-driver').iterdir() if x.is_file())
    source_before={name:digest(ROOT/name) for name in sorted(source_names)}
    for name,sha in plan['source_sha256'].items():
        if source_before[name]!=sha:raise ValueError('冻结源码不同：'+name)
    out.mkdir(parents=True)
    def copy(path):
        path=Path(path).resolve();name=path.relative_to(ROOT);dest=out/name
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
        return name.as_posix()
    for name in sorted(source_names):copy(ROOT/name)
    plan_name=copy(args.plan)
    for key in ('base','sidecar','cube','prior_full','model','manifest'):copy(checked(plan['fixed_inputs'][key]))
    for s in plan['suffix_models']:copy(checked(s))
    full_name=copy(args.full)
    copy(args.layout_contract/'results.json');copy(args.prior_worker)
    if args.single_oracle_stream.stat().st_size!=256**3*3 or digest(args.single_oracle_stream)!=full['cube']['single_oracle_sha256']:
        raise ValueError('单级整数oracle完整流不同')
    single_name=copy(args.single_oracle_stream)
    folder=out/'server-inputs';folder.mkdir()
    manifest=read(checked(plan['fixed_inputs']['manifest']))
    if manifest['count']!=100 or len(manifest['images'])!=100:raise ValueError('必须是冻结100图')
    pixels=folder/'photos.rgb';photo_records=[]
    with pixels.open('wb') as f:
        for row in manifest['images']:
            item=row['evaluation'];path=ROOT/item['path']
            if digest(path)!=item['sha256']:raise ValueError('照片编码字节不同：'+row['id'])
            with Image.open(path) as im:
                if im.mode!='RGB' or im.size!=(1024,768):raise ValueError('照片契约不同')
                raw=im.tobytes()
            sha=hashlib.sha256(raw).hexdigest()
            if sha!=item['pixel_sha256']:raise ValueError('照片解码字节不同：'+row['id'])
            f.write(raw);photo_records.append({'id':row['id'],'pixel_sha256':sha,'encoded_sha256':item['sha256']})
    if pixels.stat().st_size!=100*1024*768*3 or digest(pixels)!=worker['source_sha256']:
        raise ValueError('预解码整组与已计时照片不同')
    fixtures=folder/'fixtures';fixtures.mkdir()
    with zipfile.ZipFile(args.layout_contract/'fixtures.zip') as z:
        original={Path(name).name:sha for name,sha in contract['fixture_sha256'].items()}
        for name in z.namelist():
            dest=fixtures/Path(name).name;raw=z.read(name)
            if hashlib.sha256(raw).hexdigest()!=original[dest.name] or dest.exists():raise ValueError('夹具字节不同或重名')
            dest.write_bytes(raw)
    bases=[fixtures/f'model{s}.slut' for s in range(4)]
    bs=[fixtures/f'bounds-{s}.bin' for s in range(4)]
    cases=[('delta_single_bounds',bases[:1],bs[:1],[2]),
        ('delta_shared_shared_shared',bases,[bs[0],None,None,None],[2,1,1,1]),
        ('three_delta',bases[:3],bs[:3],[2,2,2]),
        ('shared_delta_shared_delta',bases,[None,bs[1],None,bs[3]],[1,2,1,2]),
        ('delta_unpacked_shared_delta',bases,[bs[0],fixtures/'over_positive-1.bin',None,bs[3]],[2,0,1,2]),
        ('over_positive_single',bases[:1],[fixtures/'over_positive-0.bin'],[0]),
        ('over_negative_single',bases[:1],[fixtures/'over_negative-0.bin'],[0]),
        ('equal_changed_shared',bases,[fixtures/'equal-changed.bin',None,None,None],[1,1,1,1])]
    seed=2026102005;rng=random.Random(seed)
    raw=bytes(x for r in (0,255) for g in (0,255) for b in (0,255) for x in (r,g,b))
    raw+=bytes(x for i in range(256) for x in (i,(i+17)%256,(i+31)%256))
    raw+=bytes(rng.randrange(256) for _ in range(4097*3-len(raw)))
    (fixtures/'input.rgb').write_bytes(raw);points=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).copy()
    records=[]
    for name,models,sides,flags in cases:
        if {tuple(r['layouts']) for r in contract['cases'] if r['fixture']==name}!={tuple(flags)}:
            raise ValueError('布局定义不同于已验合同')
        result=points.copy()
        for model_path,side in zip(models,sides):
            model=cc.from_sparse(io.load_sparse(model_path,competition=True))
            if side:model.channel_frac[:]=np.fromfile(side,dtype='<u4').reshape(3,3,256)
            cc.validate(model);result=integer_oracle(model,result)
        dest=fixtures/(name+'.rgb');dest.write_bytes(result.tobytes())
        records.append({'name':name,'models':[x.relative_to(out).as_posix() for x in models],
            'sidecars':[x.relative_to(out).as_posix() if x else None for x in sides],
            'layouts':flags,'expected':dest.relative_to(out).as_posix()})
    fixture_manifest={'purpose':'从已通过的布局夹具导出新冻结整数预期，不执行原生像素；服务器不需要NumPy',
        'seed':seed,'input':'server-inputs/fixtures/input.rgb','pixels':4097,'lengths':LENGTHS,'offsets':[0,1,2,3],
        'backend_threads':[[0,1],[1,1],[1,4]],'cases':records,
        'prior_layout_contract_sha256':digest(args.layout_contract/'results.json'),
        'oracle_source_sha256':digest(ROOT/'scripts/verify_channel_coordinates.py'),'new_native_calls':0,'new_fits':0}
    save(fixtures/'manifest.json',fixture_manifest)
    readme='''# Skylake服务器固定测试包

本包保存已经冻结的a399四级模型、100张1024×768 RGB8照片像素、完整整数预期及差值边界夹具。照片来源与限制保存在assets/photos/manifest.json，沿用原素材用途限制，不声明新许可。原始照片像素与完整RGB流只留在本地传输包，不加入Git。

Linux x86_64需要Python 3.11及以上标准库、CMake 3.24及以上、GNU C/C++编译器和OpenMP；无需NumPy、SciPy、Numba或Pillow。进入本目录后执行：

```sh
python3 scripts/run_skylake_server.py --bundle bundle-manifest.json --output artifacts/server-run-v1 --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc --measure
```

省略--measure只做集中正确性和计时器契约，不运行正式性能比较。可用--cpus 0,2,4,6明确指定同L3/NUMA的4个不同物理核；默认根据当前允许集合选择，不修改系统设置。--expected-cpu必须与/proc/cpuinfo的model name原文一致，仅作SKU核对，微架构与实际服务器身份仍须结合硬件说明确认。

入口先校验全部包字节，再在该机器独立构建两库与计时器，执行int16边界/回退/偏移/尾部合同、单级/四级完整256³、100图及原生计时器契约。只有全部通过才执行一次固定AB/BA/BA/AB四进程比较。记录整批100图与100次逐图调用，1/4线程、每配置5轮，排除IO/解码/拟合/准备；创建成本另列。实际库/编译器/CPU/微码/GDS/团队落点均记录。没有自动关闭安全缓解、改频或安装依赖。

输出目录必须全新；失败保留日志，不自动重试或调参。整批毫秒/图是吞吐摊销，逐图原生调用区间才可描述该协议下的单图延迟；两者都不是文件IO端到端。新入口包含公开C ABI调用成本，与旧内部bench绝对时间不混用。AMD/WSL协议验证不代表Skylake成绩，官方数据/Threshold及侧表许可仍未获得。
'''
    (out/'SERVER_README.md').write_text(readme,encoding='utf-8')
    for name,sha in source_before.items():
        if digest(ROOT/name)!=sha:raise ValueError('准备时源码变化：'+name)
    files={p.relative_to(out).as_posix():{'path':p.relative_to(out).as_posix(),'sha256':digest(p),'bytes':p.stat().st_size}
           for p in sorted(out.rglob('*')) if p.is_file()}
    result={'schema':1,'purpose':__doc__,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_tree_status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        'prior_worker_sha256':digest(args.prior_worker),'prior_layout_contract_sha256':digest(args.layout_contract/'results.json'),
        'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__,'Pillow':pillow_version},
        'files':files,'source_sha256':source_before,'plan':plan_name,'full_proof':full_name,
        'single_oracle_stream':single_name,'photo_pixels':'server-inputs/photos.rgb','photo_records':photo_records,
        'photo_output_sha256':full['photos']['output_sha256']['reference'],
        'fixture_manifest':'server-inputs/fixtures/manifest.json','new_native_calls':0,'new_fits':0,'new_performance_calls':0,
        'scope':'字节准备及小型独立整数预期导出；没有目标服务器访问、Linux像素或计时结果'}
    save(out/'bundle-manifest.json',result)
    if args.zip:
        with zipfile.ZipFile(str(out)+'.zip','w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(out.rglob('*')):
                if f.is_file():z.write(f,f.relative_to(out).as_posix())
    print(json.dumps({'files':len(files),'bundle_manifest_sha256':digest(out/'bundle-manifest.json'),
                      'bytes':sum(x['bytes'] for x in files.values()),'photo_source_sha256':digest(pixels)},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
