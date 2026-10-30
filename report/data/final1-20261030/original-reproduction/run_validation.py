"""单物理P核持锁运行预定验收；输入、源文件和命令留证。"""
import pathlib,subprocess,json,os,time,hashlib,sys,fcntl
root=pathlib.Path(__file__).resolve().parent;os.chdir(root)
fd=int(os.environ['PCORE_LOCK_FD']);allocation=json.loads(os.environ['PCORE_ALLOCATION'])
assert len(os.sched_getaffinity(0))==1
assert os.fstat(fd).st_ino==os.stat(allocation['lock']).st_ino
data=pathlib.Path('/home/admin0299/workspace/zmx/p16-framework-bench-20261030-1200/data')
expected=pathlib.Path('/home/admin0299/workspace/zmx/precision-attempts-20261030-0753/results/prefix_nodes')
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
sources=[p for p in root.rglob('*') if p.is_file() and p.suffix in ('.hpp','.cpp','.py','.slut','.fractions')]
source_hashes={str(p.relative_to(root)):digest(p) for p in sources}
inputs={str(p.relative_to(data)):digest(p) for folder in ['LUT','photos100','official4'] for p in sorted((data/folder).iterdir()) if p.suffix in ('.3DL','.bin')}
record=dict(phase='compiling',allocation=allocation,affinity=sorted(os.sched_getaffinity(0)),sources=source_hashes,inputs=inputs,
 compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],flags=['-O2','-std=c++17'],
 started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),commands=[],load_average_before=os.getloadavg())
def update(): (root/'validation-receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
def run(command,log):
 t=time.monotonic()
 with (root/log).open('w') as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,pass_fds=(fd,))
 record['commands'].append(dict(command=command,log=log,exit=r.returncode,seconds=time.monotonic()-t));update()
 if r.returncode:raise RuntimeError(log)
update()
try:
 run(['g++','-O2','-std=c++17','final1/main.cpp','-o','final1/lut3d'],'compile-main.log')
 run(['g++','-O2','-std=c++17','verify_and_benchmark.cpp','-o','verify_and_benchmark'],'compile-verifier.log')
 record['phase']='testing';update()
 run(['/usr/bin/time','-v','-o','validation-resources.txt','./verify_and_benchmark',str(data),str(expected),'bank','results'],'validation.log')
 record['phase']='official_entry';update()
 official=root/'official-data';official.mkdir();(official/'LUT').symlink_to(data/'LUT',target_is_directory=True);(official/'image').symlink_to(data/'official4',target_is_directory=True)
 run(['./final1/lut3d',str(official),'4'],'official-main.log')
 assert all(digest(root/n)==h for n,h in source_hashes.items())
 assert all(digest(data/n)==h for n,h in inputs.items())
 record.update(complete=True,phase='complete',sources_and_inputs_unchanged=True,
  binary_sha256=digest(root/'final1/lut3d'),verifier_sha256=digest(root/'verify_and_benchmark'),load_average_after=os.getloadavg())
except Exception as e:record.update(complete=False,phase='failed',error=str(e))
record['finished_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());update()
print(json.dumps({k:v for k,v in record.items() if k not in ('inputs','sources','commands')},ensure_ascii=False),flush=True)
sys.exit(0 if record.get('complete') else 1)
