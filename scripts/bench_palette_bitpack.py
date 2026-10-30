"""同场六角色/完整百图的7bit容量、精度与吞吐六档；新进程A/A与RSS分列。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import statistics
import subprocess
import sys
import numpy as np
import time
from profile_palette_bitpack import sha,save
from study_memory_rom import Model,U8,romlib,loadrom,read,env
from bench_memory_rom import memory,setup as reference_setup

ROOT=Path(__file__).resolve().parents[1]
ROLES=['ref78','ref80','exact_avx','ward_avx','maximin_avx','ward_c99']
OLD_PHOTO='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'


def setup(args,label):
    if label in ['ref78','ref80']:
        return (*reference_setup(args,label),OLD_PHOTO,1.)
    if label=='exact_avx':
        library=args.exact_build/'jshc_memory_rom.dll';rom=args.original_rom
        expected=OLD_PHOTO;accuracy=1.;kernel=1
    else:
        library=args.build/'jshc_memory_rom.dll'
        name='maximin_original_color7' if label=='maximin_avx' else 'weighted_ward_centroid7'
        rom=args.roms/(name+'.bin');kernel=0 if label=='ward_c99' else 1
        expected=next(row for row in read(args.verification)['models'] if row['name']==name)['photo_oracle_sha256']
        accuracy=next(row for row in read(args.profile/'results.json')['results'] if row['name']==name)['minimum_retention']
    library_object=romlib(library);model,keep=loadrom(library_object,rom)

    def apply(source,target,n,threads,mode):
        return library_object.jshc_mem_apply_parallel(ct.byref(model),target if mode=='inplace' else source,target,n,kernel,threads)

    return apply,(library_object,model,keep),rom.stat().st_size+ct.sizeof(Model),str(library),sha(library),expected,accuracy


def worker(args):
    args.output.mkdir(parents=True,exist_ok=False)
    if args.rss:
        before=memory();operator=setup(args,args.rss);after=memory()
        save(args.output/'rss.json',dict(role=args.rss,before=before,prepared=after,resident_capacity=operator[2],
            scope='新进程准备后立即读取，尚无照片分配；包含Python/NumPy/运行库，非纯模型RSS'))
        return
    photo=args.data_root/'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb'
    assert sha(photo)=='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'
    source_array=np.memmap(photo,np.uint8,mode='r');target_array=np.empty_like(source_array)
    source=source_array.ctypes.data_as(U8);target=target_array.ctypes.data_as(U8);n=len(source_array)//3
    operators={name:setup(args,name) for name in ROLES}
    shift=args.worker_index%len(ROLES);order=ROLES[shift:]+ROLES[:shift]
    if args.worker_index%2:order=list(reversed(order))
    threads=[1,4] if args.worker_index%2==0 else [4,1]
    rows=[];controls=[]
    for count in threads:
        for mode in ['inplace','outplace']:
            for role in order:
                operator=operators[role];times=[]
                for repeat in range(6):
                    np.copyto(target_array,source_array)
                    start=time.perf_counter();error=operator[0](source,target,n,count,mode);elapsed=time.perf_counter()-start
                    assert error==0
                    if repeat:times.append(elapsed)
                    if repeat in [0,5]:assert hashlib.sha256(target_array).hexdigest()==operator[5]
                rows.append(dict(role=role,threads=count,mode=mode,seconds=times,median_seconds=statistics.median(times)))
                save(args.output/'partial.json',dict(rows=rows))
            times=[]
            for repeat in range(5):
                np.copyto(target_array,source_array)
                start=time.perf_counter();assert operators['ref80'][0](source,target,n,count,mode)==0
                times.append(time.perf_counter()-start)
            original=next(row['median_seconds'] for row in rows if row['role']=='ref80' and row['threads']==count and row['mode']==mode)
            controls.append(dict(threads=count,mode=mode,seconds=times,ratio=statistics.median(times)/original))
    save(args.output/'results.json',dict(environment=env(),worker_index=args.worker_index,order=order,thread_order=threads,rows=rows,controls=controls,
        roles={key:dict(resident_capacity=value[2],library=value[3],library_sha256=value[4],output_sha256=value[5],accuracy_retention=value[6]) for key,value in operators.items()},
        scope='每轮完整100图，计时排除prepare/输入恢复/IO/哈希；无绑核/锁频，排他窗口；新有损模型对其独立oracle核对'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['build','exact-build','roms','original-rom','ref80','profile','verification','data-root','output','plan']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--freeze',action='store_true');parser.add_argument('--worker-index',type=int);parser.add_argument('--rss')
    args=parser.parse_args()
    if args.freeze:
        if args.plan.exists():raise FileExistsError('计划已存在，不覆盖')
        source_files=[Path(__file__),ROOT/'scripts/study_memory_rom.py',ROOT/'scripts/bench_memory_rom.py',
                      ROOT/'scripts/profile_palette_bitpack.py',ROOT/'scripts/export_palette_bitpack.py',ROOT/'scripts/build_palette_bitpack.py',ROOT/'scripts/verify_palette_bitpack.py',
                      ROOT/'experiments/palette-bitpack/memory_bitpack.c',ROOT/'experiments/palette-bitpack/parallel.cpp']
        artifacts=[args.build/'jshc_memory_rom.dll',args.build/'jshc_memory_ref78.dll',args.exact_build/'jshc_memory_rom.dll',args.ref80,args.original_rom,
                   args.profile/'results.json',args.verification,*args.roms.glob('*.bin')]
        save(args.plan,dict(purpose=__doc__,source_sha256={str(path.relative_to(ROOT)):sha(path) for path in source_files},
            artifacts_sha256={str(path.resolve()):sha(path) for path in artifacts},
            protocol='六角色，四串行新进程，轮转/反序、1/4线程互换、原地/真分离，每项预热1+完整百图5次；ref80尾部A/A5次；六fresh RSS进程',
            gate='每接口/线程A/A单对0.8..1.25且四worker中位1/1.1..1.1；最劣worker吞吐=min(同场78,80时间)/候选时间，精度=min全域/照片合并/最劣单图mean,p99,max旧新比。六档100/90/80/70/60/50，不拼历史轮次，不重测择优。'))
        print('性能计划已冻结');return
    plan=read(args.plan)
    assert all(sha(ROOT/name)==value for name,value in plan['source_sha256'].items())
    assert all(sha(Path(name))==value for name,value in plan['artifacts_sha256'].items())
    if args.worker_index is not None or args.rss:return worker(args)
    args.output.mkdir(parents=True,exist_ok=False);save(args.output/'executed-plan.json',plan)
    common=[sys.executable,'-X','utf8',str(Path(__file__).resolve())]
    for name in ['build','exact-build','roms','original-rom','ref80','profile','verification','data-root','plan']:
        common+=['--'+name,str(getattr(args,name.replace('-','_')).resolve())]
    execution=[]
    for tag in [*range(4),*ROLES]:
        target=args.output/(f'worker-{tag}' if isinstance(tag,int) else 'rss-'+tag)
        command=common+(['--worker-index',str(tag)] if isinstance(tag,int) else ['--rss',tag])+['--output',str(target.resolve())]
        result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
        execution.append(dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr));save(args.output/'execution.json',execution);result.check_returncode()
    workers=[read(args.output/f'worker-{index}/results.json') for index in range(4)]
    controls={};comparisons=[];grids={}
    for mode in ['inplace','outplace']:
        for threads in [1,4]:
            control=[next(row['ratio'] for row in data['controls'] if row['mode']==mode and row['threads']==threads) for data in workers]
            valid=all(.8<=value<=1.25 for value in control) and 1/1.1<=statistics.median(control)<=1.1
            key=f'{mode}_{threads}';controls[key]=dict(values=control,median=statistics.median(control),passed=valid)
            lookup=[{row['role']:row['median_seconds'] for row in data['rows'] if row['mode']==mode and row['threads']==threads} for data in workers]
            cases=[]
            for role in ROLES[2:]:
                ratios=[min(row['ref78'],row['ref80'])/row[role] for row in lookup]
                identity=workers[0]['roles'][role]
                row=dict(role=role,mode=mode,threads=threads,per_worker=ratios,speed_median=statistics.median(ratios),speed_worst=min(ratios),
                    accuracy_retention=identity['accuracy_retention'],resident_capacity=identity['resident_capacity'],control_passed=valid)
                comparisons.append(row);cases.append(row)
            grids[key]={f'accuracy{quality}_speed{speed}':min([row for row in cases if valid and row['accuracy_retention']+1e-12>=quality/100 and row['speed_worst']+1e-12>=speed/100],
                key=lambda row:row['resident_capacity'],default=None) for quality in [100,90,80,70,60,50] for speed in [100,90,80,70,60,50]}
    save(args.output/'summary.json',dict(purpose=__doc__,controls=controls,comparisons=comparisons,grids=grids,
        rss={role:read(args.output/('rss-'+role)/'rss.json') for role in ROLES},
        scope='按接口/线程分别六乘六档，空值表示无新合格点，不把不同场次或不同接口拼成全局候选'))
    print('四worker六角色百图及A/A/RSS完成')


if __name__=='__main__':main()
