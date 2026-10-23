"""封存字典独立确认、八worker合并和零worker的v1 preflight技术失败。"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import zipfile
from archive_compact_sparse import package
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.run=a.run.resolve();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=False)
    v1=ROOT/'experiments/compact-dictionary-confirm-v1.json';v2=ROOT/'experiments/compact-dictionary-confirm-v2.json';plan=read(v2)
    files={'combined.json':a.run/'combined.json','second-performance.json':a.run/'measurement/summary.json','preflight-v2.json':a.run/'preflight.json','failed-preflight-v1.json':ROOT/'artifacts/p16-compact-dictionary-confirm-v1/failed-preflight.json','first-performance.json':Path(plan['first_directory'])/'summary.json'}
    for name,path in files.items():(a.output/name).write_bytes(path.read_bytes())
    sources={n:ROOT/n for n in plan['source_sha256']}
    for path in (v1,v2,ROOT/'scripts/archive_compact_dictionary_confirmation.py',ROOT/'scripts/archive_compact_sparse.py'):sources[path.relative_to(ROOT).as_posix()]=path
    package(a.output/'measured-source.zip',sources)
    old=read(v1)
    with zipfile.ZipFile(a.output/'failed-v1-frozen-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in ('scripts/confirm_compact_dictionary.py','scripts/freeze_compact_dictionary_confirmation.py'):
            raw=subprocess.check_output(['git','show','d97ded6:'+name],cwd=ROOT)
            if hashlib.sha256(raw).hexdigest()!=old['source_sha256'][name]:raise AssertionError('原v1源码SHA不符')
            z.writestr(name,raw)
        z.write(v1,'experiments/'+v1.name)
    package(a.output/'second-raw.zip',{x.relative_to(a.run/'measurement').as_posix():x for x in (a.run/'measurement').rglob('*.json') if x.name not in ('partial.json','summary.json')})
    save(a.output/'manifest.json',dict(purpose=__doc__,files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x)) for x in a.output.iterdir() if x.is_file()},references='首轮源/二进制/实际ROM、身份审计见report/data/p16-compact-dictionary-v1；确认原样复用，只有新输出目录。v1未启动任何worker；v2只执行一次正式确认。'))
    print(a.output)
if __name__=='__main__':main()
