"""唯一只读统计的开始、输出和退出留证；禁止自动重试。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'artifacts/skylake-xor-chroma-profile-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,obj):
    with (HERE/name).open('x',encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False,indent=2)
        f.write('\n')
p=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'))
assert sha(HERE/'analyze.py')==p['script_sha256']
compile((HERE/'analyze.py').read_bytes(),str(HERE/'analyze.py'),'exec')
write('execution-start.json',{'utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(HERE/'protocol.json'),'script_sha256':p['script_sha256'],'runner_sha256':sha(Path(__file__)),'command':[sys.executable,str(HERE/'analyze.py')],'native_calls':0,'performance_calls':0})
with (HERE/'stdout.log').open('xb') as out,(HERE/'stderr.log').open('xb') as err:
    rc=subprocess.run([sys.executable,str(HERE/'analyze.py')],cwd=ROOT,stdout=out,stderr=err).returncode
write('exit.json',{'utc':datetime.now(timezone.utc).isoformat(),'exit_code':rc,'protocol_sha256':sha(HERE/'protocol.json'),'script_sha256':p['script_sha256'],'results_sha256':sha(HERE/'results.json') if (HERE/'results.json').exists() else None,'stdout_sha256':sha(HERE/'stdout.log'),'stderr_sha256':sha(HERE/'stderr.log'),'native_calls':0,'performance_calls':0})
print((HERE/'stdout.log').read_text(encoding='utf-8'))
sys.exit(rc)
