"""99正式前只读身份/进程竞争预检；不加载原生库，不生成颜色，不计时映射。"""
import hashlib
import json
from pathlib import Path
import time
import os
import psutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/p16-b2-packed-performance-preflight-v1.json'
if OUT.exists():raise FileExistsError('99正式前预检原件不覆盖')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
plan_path=ROOT/'experiments/p16-b2-packed-performance-v1.json'
assert sha(plan_path)=='1d99b7f1b5ddde6f667c70dd2e11e6d35eff9a478e033765e2b7f8f8e386e518'
plan=json.loads(plan_path.read_text(encoding='utf-8'))
for row in plan['sources']+list(plan['libraries'].values()):assert sha(Path(row['path']))==row['sha256'],row['path']
names={'python.exe','pythonw.exe','g++.exe','gcc.exe','cc1plus.exe','cc1.exe','cmake.exe','mingw32-make.exe','ninja.exe','git.exe','git-remote-https.exe','git-credential-manager.exe'}
rows=[]
for p in psutil.process_iter(['pid','name','ppid','exe','cmdline','cpu_times']):
    try:
        d=p.info
        if (d['name'] or '').lower() not in names:continue
        cpu=d['cpu_times'].user+d['cpu_times'].system
        args=d['cmdline'] or []
        # 不输出任意原命令行或环境；只保脚本路径和不可逆身份。
        scripts=[v for v in args if v.lower().endswith(('.py','.cpp'))]
        rows.append({'pid':d['pid'],'name':d['name'],'ppid':d['ppid'],'exe':d['exe'],
            'script_paths':scripts,'command_line_sha256':hashlib.sha256('\0'.join(args).encode()).hexdigest(),
            'cpu_seconds_before':cpu})
    except (psutil.NoSuchProcess,psutil.AccessDenied):continue
time.sleep(.5)
active=[]
for row in rows:
    try:
        cpu=psutil.Process(row['pid']).cpu_times()
        row['cpu_seconds_after']=cpu.user+cpu.system
        row['cpu_delta_over_half_second']=row['cpu_seconds_after']-row['cpu_seconds_before']
        row['still_present']=True
        if row['pid']!=os.getpid() and row['cpu_delta_over_half_second']>.1:active.append(row['pid'])
    except (psutil.NoSuchProcess,psutil.AccessDenied):row['still_present']=False
result={'passed':not active,'checked_source_and_library_identities':len(plan['sources'])+len(plan['libraries']),
    'plan_sha256':sha(plan_path),'preflight_script_sha256':sha(Path(__file__)),
    'observed_processes':rows,'unexpected_active_relevant_pids':active,
    'environment':{key:os.environ.get(key) for key in ('PYTHONUTF8','OMP_NUM_THREADS','OMP_DYNAMIC','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')},
    'scope':'仅相关进程0.5秒只读CPU观察，不证明宿主绝对独占。未知PID不杀；独立密集相关进程>0.1CPU秒则本版停止保留。无native/图像映射/性能。'}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert result['passed'],active
print(json.dumps({'passed':True,'checked_identities':result['checked_source_and_library_identities'],
    'pids':[row['pid'] for row in rows],'unexpected_active_relevant_pids':active},ensure_ascii=False))
