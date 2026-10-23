"""为已封存字典首轮的跨场稳定性疑点预先冻结一次独立确认，不执行性能。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','roms','ref80','data-root','first'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();original=ROOT/'experiments/compact-dictionary-v1.json';policy=read(original);files={str(original):sha(original)}
    paths=[a.build/'build.json',*[a.build/n for n in ('jshc_memory_rom.dll','jshc_dict_c99.dll','jshc_memory_ref78.dll')],*[a.roms/f'rom-{i}.bin' for i in (17,24)],a.ref80,a.first/'summary.json',Path(policy['reference32']['path']),Path(policy['input_rom_path']),ROOT/'artifacts/p16-compact-dictionary-static-v1/results.json']
    for path in paths:files[str(path.resolve())]=sha(path)
    sources=dict(policy['source_sha256'])
    for n in ('scripts/confirm_compact_dictionary.py','scripts/freeze_compact_dictionary_confirmation.py'):sources[n]=sha(ROOT/n)
    arguments=[]
    for key in ('build','roms','ref80','data-root'):arguments+=['--'+key,str(getattr(a,key.replace('-','_')).resolve())]
    arguments+=['--repeats','5']
    plan=dict(purpose=__doc__,trigger='同一旧32bit DLL跨场4线程原地33..35ms变20..22ms，原因未解释，3B首轮全局最低50.4771%距底线仅0.4771pp；确认用于排除稳定性疑点，不择优。',original_plan_sha256=sha(original),first_directory=str(a.first.resolve()),files_sha256=files,source_sha256=sources,benchmark_arguments=arguments,environment=dict(OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_WAIT_POLICY='PASSIVE',OPENBLAS_NUM_THREADS='1',NUMBA_NUM_THREADS='1'),protocol='原7角色、同二进制、同源、同100图、相同4新进程轮换反序、相同单/四线程原地/分离与预热1+5完整轮，只有新输出目录；原bench脚本在同一父进程runpy执行，不增加idle包装进程。',decision='首轮和本轮全部8worker取最劣；两轮A/A全部有效且最劣满足门槛才给稳健资格。任何A/A有效worker越50则撤销稳健全局50推荐。无效原样保留且不反复重跑，不挑轮次、不替换首轮结果。',roles=policy['roles'],iterations=1)
    path=ROOT/'experiments/compact-dictionary-confirm-v1.json'
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(sha(path))
if __name__=='__main__':main()
