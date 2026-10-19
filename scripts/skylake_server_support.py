"""服务器入口的纯标准库工具：固定字节、CPU拓扑、实际库来源与原生计时回执。"""
from __future__ import annotations
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from verify_skylake_linux_stdlib import bind, create, apply

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def checked(spec):
    path=Path(spec['path']);path=path if path.is_absolute() else ROOT/path
    if digest(path)!=spec['sha256'] or ('bytes' in spec and path.stat().st_size!=spec['bytes']):
        raise ValueError('冻结字节不同：'+str(path))
    return path
def spec(path):
    path=Path(path).resolve()
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path),'bytes':path.stat().st_size}
def cpu_list(text):
    result=[]
    for part in text.strip().split(','):
        ends=part.split('-');result.extend(range(int(ends[0]),int(ends[-1])+1))
    return sorted(set(result))
def topology(explicit=None):
    if platform.system()!='Linux' or platform.machine().lower() not in ('x86_64','amd64'):
        raise ValueError('需要Linux x86_64实际环境')
    allowed=sorted(os.sched_getaffinity(0)); rows=[]
    for cpu in allowed:
        base=Path(f'/sys/devices/system/cpu/cpu{cpu}')
        top={n:(base/'topology'/n).read_text().strip() for n in ('physical_package_id','core_id','thread_siblings_list')}
        caches=[]
        for p in sorted((base/'cache').glob('index*')):
            caches.append({n:(p/n).read_text().strip() for n in ('level','type','size','shared_cpu_list')})
        l3=[c['shared_cpu_list'] for c in caches if c['level']=='3' and c['type']=='Unified']
        if len(l3)!=1:raise ValueError('无法唯一确定L3域：'+str(cpu))
        nodes=[p.name for p in base.glob('node[0-9]*')]
        rows.append({'cpu':cpu,'topology':top,'caches':caches,'l3':l3[0],'numa':nodes})
    groups={}
    for row in rows:
        key=(row['l3'],tuple(row['numa']));physical=(row['topology']['physical_package_id'],row['topology']['core_id'])
        groups.setdefault(key,{}).setdefault(physical,row['cpu'])
    if explicit is None:
        candidates=[sorted(v.values())[:4] for v in groups.values() if len(v)>=4]
        if not candidates:raise ValueError('允许集合中没有同L3/NUMA域的4个物理核')
        selected=min(candidates)
    else:selected=list(explicit)
    chosen=[r for r in rows if r['cpu'] in selected]
    if len(selected)!=4 or len(set(selected))!=4 or len(chosen)!=4:
        raise ValueError('需要允许集合中的4个不同CPU')
    if len({(r['topology']['physical_package_id'],r['topology']['core_id']) for r in chosen})!=4:
        raise ValueError('不能把SMT兄弟当成4个物理核')
    if len({(r['l3'],tuple(r['numa'])) for r in chosen})!=1:raise ValueError('CPU必须在同L3与NUMA域')
    return {'initial_allowed_cpus':allowed,'selected_cpus':selected,'rows':rows,'selection':'固定同L3/NUMA的4个不同物理核，不更改系统拓扑'}
def environment():
    cpu=Path('/proc/cpuinfo').read_text().split('\n\n')[0]
    details={k.strip():v.strip() for line in cpu.splitlines() if ':' in line for k,v in [line.split(':',1)]}
    gds=Path('/sys/devices/system/cpu/vulnerabilities/gather_data_sampling')
    return {'platform':platform.platform(),'python':sys.version,'machine':platform.machine(),'cpu':details,
        'loadavg':os.getloadavg(),'gather_data_sampling':gds.read_text().strip() if gds.is_file() else '系统未提供',
        'thread_environment':{k:v for k,v in sorted(os.environ.items()) if k.startswith(('OMP_','GOMP_','KMP_'))},
        'frequency_temperature_security_changes':'本入口不修改频率、温度或安全缓解设置',
        'target_scope':'报告实际CPU/微码/系统；不根据AVX2、型号数字或编译参数自动认定为Skylake'}
def loaded(expected):
    paths={Path(line.split(maxsplit=5)[-1]).resolve() for line in Path('/proc/self/maps').read_text().splitlines()
           if '/' in line and Path(line.split(maxsplit=5)[-1]).is_file()}
    for s in expected:
        if checked(s).resolve() not in paths:raise ValueError('实际映射缺少冻结库：'+s['path'])
    gomp={p for p in paths if p.name.startswith('libgomp.')}
    if len(gomp)!=1:raise ValueError('后端与探针必须共享唯一libgomp运行库')
    return [{'path':str(p),'sha256':digest(p)} for p in sorted(paths)
            if p in {checked(s).resolve() for s in expected} or p.name.startswith(('libgomp.','libstdc++.','libgcc_s.','libc.','libm.'))]
def layouts(d,handle,count):
    if not hasattr(d,'jshc_cc_get_layouts'):return None
    f=d.jshc_cc_get_layouts;f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
    values=(ct.c_uint32*count)()
    if f(handle,values,count):raise ValueError('布局诊断失败')
    return list(values)
def driver_bind(path):
    d=ct.CDLL(str(path));d.jshc_sb_abi_version.restype=ct.c_uint32
    if d.jshc_sb_abi_version()!=1:raise ValueError('计时器ABI不匹配')
    d.jshc_sb_run.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_void_p,ct.c_void_p,ct.c_size_t,ct.c_size_t,
        ct.c_int,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_double),ct.POINTER(ct.c_double),ct.c_void_p,ct.c_size_t]
    d.jshc_sb_run.restype=ct.c_int
    d.jshc_sb_probe_team.argtypes=[ct.c_int,ct.POINTER(ct.c_int),ct.c_size_t,ct.POINTER(ct.c_int),ct.c_void_p,ct.c_size_t]
    d.jshc_sb_probe_team.restype=ct.c_int
    return d
def team(driver,threads,selected):
    cpus=(ct.c_int*threads)(*([-1]*threads));actual=ct.c_int();error=ct.create_string_buffer(1024)
    if driver.jshc_sb_probe_team(threads,cpus,threads,ct.byref(actual),error,len(error)):
        raise ValueError(error.value.decode('utf-8',errors='replace'))
    values=list(cpus)
    if actual.value!=threads or len(set(values))!=threads or not set(values)<=set(selected):
        raise ValueError('实际团队没有落在固定的不同物理核')
    return {'requested':threads,'actual':actual.value,'cpus':values,'main_allowed_cpus_after_openmp':sorted(os.sched_getaffinity(0))}
def measure(driver,d,handle,source,work,image_bytes,images,threads,mode,repeats):
    count=repeats*(images if mode else 1)
    a=(ct.c_double*count)();c=(ct.c_double*count)();w=(ct.c_double*repeats)();error=ct.create_string_buffer(1024)
    rc=driver.jshc_sb_run(ct.cast(d.jshc_cc_apply,ct.c_void_p),handle,ct.addressof(source),ct.addressof(work),
        image_bytes,images,1,threads,mode,repeats,a,c,w,error,len(error))
    if rc:raise RuntimeError('原生基准失败：'+error.value.decode('utf-8',errors='replace'))
    import math
    if any(not math.isfinite(x) or x<=0 for x in [*a,*c,*w]) or any(y<x for x,y in zip(a,c)):
        raise ValueError('计时回执无效')
    segments=images if mode else 1
    aa=[sum(a[r*segments:(r+1)*segments]) for r in range(repeats)]
    cc=[sum(c[r*segments:(r+1)*segments]) for r in range(repeats)]
    if any(total<part for total,part in zip(w,cc)):raise ValueError('分段计时不能大于外层墙钟')
    return {'segment_apply_seconds':list(a),'segment_copy_apply_seconds':list(c),
            'round_apply_seconds':aa,'round_copy_apply_seconds':cc,'round_wall_seconds':list(w)}
