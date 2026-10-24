"""100正式前只读身份及相关进程竞争观察，不加载native/照片。"""
import hashlib
import json
import os
from pathlib import Path
import time
import psutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/p16-scanline-prepare-performance-preflight-v1.json'
if OUT.exists():raise FileExistsError('100正式预检不覆盖')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan_path=ROOT/'experiments/p16-scanline-prepare-performance-v1.json';plan=json.loads(plan_path.read_text(encoding='utf-8'))
assert plan['candidate_revision']==100
entries=plan['sources']+list(plan['libraries'].values())
for entry in entries:assert sha(Path(entry['path']))==entry['sha256'],entry['path']
assert next(r['sha256'] for r in plan['sources'] if Path(r['path'])==Path(__file__))==sha(Path(__file__))
names={'python.exe','pythonw.exe','g++.exe','gcc.exe','cc1plus.exe','cc1.exe','cmake.exe','mingw32-make.exe','ninja.exe','git.exe','git-remote-https.exe','git-credential-manager.exe'}
rows=[]
for process in psutil.process_iter(['pid','name','ppid','exe','cmdline','cpu_times']):
    try:
        data=process.info
        if (data['name'] or '').lower() not in names:continue
        args=data['cmdline'] or [];cpu=data['cpu_times'].user+data['cpu_times'].system
        rows.append({'pid':data['pid'],'name':data['name'],'ppid':data['ppid'],'exe':data['exe'],
            'script_paths':[v for v in args if v.lower().endswith(('.py','.cpp'))],
            'command_line_sha256':hashlib.sha256('\0'.join(args).encode()).hexdigest(),'cpu_seconds_before':cpu})
    except (psutil.NoSuchProcess,psutil.AccessDenied):continue
time.sleep(.5);active=[]
for row in rows:
    try:
        cpu=psutil.Process(row['pid']).cpu_times();row['cpu_seconds_after']=cpu.user+cpu.system
        row['cpu_delta_over_half_second']=row['cpu_seconds_after']-row['cpu_seconds_before'];row['still_present']=True
        if row['pid']!=os.getpid() and row['cpu_delta_over_half_second']>.1:active.append(row['pid'])
    except (psutil.NoSuchProcess,psutil.AccessDenied):row['still_present']=False
result={'passed':not active,'checked_source_and_library_identities':len(entries),'plan_sha256':sha(plan_path),
    'preflight_script_sha256':sha(Path(__file__)),'observed_processes':rows,'unexpected_active_relevant_pids':active,
    'environment':{key:os.environ.get(key) for key in ('PYTHONUTF8','OMP_NUM_THREADS','OMP_DYNAMIC','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')},
    'scope':'仅相关进程0.5秒CPU观察，非self>0.1秒则STOP；未知PID不杀，不证明宿主绝对独占。'}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert result['passed'],active
print(json.dumps({'passed':True,'checked_identities':len(entries),'pids':[row['pid'] for row in rows],'unexpected_active_relevant_pids':active},ensure_ascii=False))
