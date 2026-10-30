"""101唯一finite外部RSS旁观，不改冻结runner/合同且不重跑。"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/p16-early-index-finite-observation-v1'
NATIVE=ROOT/'artifacts/p16-early-index-finite-v1'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
row=lambda path:{'path':str(path),'sha256':sha(path)}


def main():
    if OUT.exists() or NATIVE.exists():raise FileExistsError('101唯一finite/RSS不覆盖')
    frozen=ROOT/'experiments/p16-early-index-static-v1.json'
    assert sha(frozen)=='0803366eafad0bcfd00c69398572fcab518871ff57141fe2b50d6cf47b209e78'
    plan=json.loads(frozen.read_text(encoding='utf-8'))
    for entry in plan['sources']:assert sha(Path(entry['path']))==entry['sha256']
    runner=ROOT/'scripts/run_p16_early_index_finite.py'
    executable=ROOT/'artifacts/p16-early-index-build-v1/p16_early_index_contract.exe'
    command=[sys.executable,'-X','utf8',str(runner),'--output',str(NATIVE)]
    OUT.mkdir(parents=True)
    execution={'purpose':'外部旁观101唯一finite的RSS，不更改已冻结执行源','observer':row(Path(__file__)),
        'source_freeze':row(frozen),'runner':row(runner),'executable':row(executable),'command':command,
        'poll_seconds':.01,'native_reruns':0,'full_chain_calls':0,'photo_calls':0,'performance_calls':0}
    (OUT/'executed-plan.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    environment=dict(os.environ);environment['PYTHONUTF8']='1'
    process=subprocess.Popen(command,cwd=ROOT,env=environment,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
    samples=[];native_pids=set();failures=[]
    while process.poll() is None:
        try:
            children=psutil.Process(process.pid).children(recursive=False)
            for child in children:
                try:
                    if child.name().lower()!=executable.name.lower():continue
                    assert Path(child.exe()).resolve()==executable.resolve()
                    memory=child.memory_info();native_pids.add(child.pid)
                    samples.append({'pid':child.pid,'rss':memory.rss,'peak_wset':getattr(memory,'peak_wset',None),
                        'vms':memory.vms,'peak_pagefile':getattr(memory,'peak_pagefile',None)})
                except (psutil.NoSuchProcess,psutil.AccessDenied) as error:failures.append(type(error).__name__)
        except (psutil.NoSuchProcess,psutil.AccessDenied) as error:failures.append(type(error).__name__)
        time.sleep(.01)
    stdout,stderr=process.communicate()
    (OUT/'runner-stdout.txt').write_text(stdout,encoding='utf-8');(OUT/'runner-stderr.txt').write_text(stderr,encoding='utf-8')
    native_result=json.loads((NATIVE/'results.json').read_text(encoding='utf-8')) if (NATIVE/'results.json').is_file() else None
    result={'return_code':process.returncode,'passed':process.returncode==0 and bool(native_result and native_result['passed']),
        'execution_plan_sha256':sha(OUT/'executed-plan.json'),'native_result_sha256':sha(NATIVE/'results.json') if native_result else None,
        'native_pid_count':len(native_pids),'native_pids':sorted(native_pids),'sample_count':len(samples),'samples':samples,
        'sampled_rss_max_bytes':max((s['rss'] for s in samples),default=None),
        'observed_os_peak_wset_max_bytes':max((s['peak_wset'] for s in samples if s['peak_wset'] is not None),default=None),
        'observation_races_or_access_failures':failures,'native_reruns':0,'full_chain_calls':0,'photo_calls':0,'performance_calls':0,
        'scope':'只旁观冻结runner唯一子EXE；RSS为采样最大、peak_wset为存活期间所读OS峰值字段，不保证采到退出前全生命周期最终峰值。未捕获时保留缺口、不补跑。'}
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='samples'},ensure_ascii=False))
    assert result['passed'] and len(native_pids)<=1,'101唯一finite或进程身份失败，保留STOP'


if __name__=='__main__':main()
