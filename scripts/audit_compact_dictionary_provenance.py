"""纯静态核验旧字典二进制/源/ROM同源及新旧loop token；保留跨场波动原值。"""
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def normalized(text):
    text=re.sub(r'//[^\n]*','',text)
    text,count=re.subn(r'inline __attribute__\(\(always_inline\)\) uint32_t lookup_id\([^\n]+\) \{.*?\n\}', '',text,count=1,flags=re.S)
    if count!=1:raise AssertionError('未唯一定位lookup helper')
    text=re.sub(r'\bjshc_(?:mem_4|dict_17|dict_24)\b','jshc_control',text)
    return re.sub(r'\s+','',text)

def main():
    old=ROOT/'artifacts/p16-memory-build-v2';out=ROOT/'artifacts/p16-compact-dictionary-static-v1';out.mkdir(exist_ok=False);plan=read(ROOT/'experiments/compact-dictionary-v1.json');build=read(old/'build.json');oldsha=sha(old/'jshc_memory_rom.dll');source=old/'memory_avx2_4.cpp';source_sha=sha(source)
    if oldsha!=build['libraries']['jshc_memory_rom.dll'] or oldsha!=plan['reference32']['sha256'] or source_sha!=build['sources'][str(source)]:raise AssertionError('旧文件和原构建回执不同')
    with zipfile.ZipFile(ROOT/'report/data/p16-memory-rom-v1/measured-source.zip') as z:
        if hashlib.sha256(z.read(source.relative_to(ROOT).as_posix())).hexdigest()!=source_sha:raise AssertionError('已发布源和旧源不同')
    reference=normalized(source.read_text(encoding='utf-8'));sources={};objects={}
    for mode in (17,24):
        path=ROOT/f'experiments/compact-dictionary-runtime/channel_avx2_{mode}.cpp'
        if normalized(path.read_text(encoding='utf-8'))!=reference:raise AssertionError('除lookup/namespace外loop token不同')
        sources[str(mode)]=sha(path);objects[str(mode)]=sha(ROOT/f'artifacts/p16-compact-dictionary-build-v1/channel_avx2_{mode}.o')
    firstexport=read(ROOT/'report/data/p16-memory-rom-v1/export.json')
    if sha(Path(plan['input_rom_path']))!=firstexport['models']['4']['sha256'] or plan['input_rom_sha256']!=firstexport['models']['4']['sha256']:raise AssertionError('ROM与首场不同')
    histories=[]
    for worker in range(4):
        first=read(ROOT/f'artifacts/p16-memory-perf-v1/worker-{worker}/results.json');current=read(ROOT/f'artifacts/p16-compact-dictionary-perf-v1/worker-{worker}/results.json')
        if first['roles']['avx2_4']['library_sha256']!=oldsha or current['roles']['dict32']['library_sha256']!=oldsha:raise AssertionError('worker实际库身份不同')
        for mode in ('inplace','outplace'):
            for threads in (1,4):
                def subset(result,label):return {('dict32' if row['label']==label else row['label']):row['median_seconds'] for row in result['rows'] if row['label'] in (label,'ref78','ref80') and row['mode']==mode and row['threads']==threads}
                histories.append(dict(worker=worker,mode=mode,threads=threads,first=subset(first,'avx2_4'),current=subset(current,'dict32'),same_reported_environment=first['environment']==current['environment']))
    result=dict(passed=True,purpose=__doc__,old_dll_sha256=oldsha,old_source_sha256=source_sha,old_object_sha256=sha(old/'memory_avx2_4.o'),new_source_sha256=sources,new_object_sha256=objects,normalized_loop_token_sha256=hashlib.sha256(reference.encode()).hexdigest(),same_binary_all_eight_workers=True,same_source_as_published=True,same_rom_sha256=plan['input_rom_sha256'],histories=histories,scope='旧dict32确为首场DLL原字节复测；新17/24仅lookup/namespace之外的源token相同，编译内联/寄存器调度仍可变化。已报告环境相同但跨场耗时差异原因未解释，角色集合仅是协议差别，不能作为已证因果。A/A只证明本轮参考端点复测漂移受控，未证明跨场稳定性；首场拒绝保留。')
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out)
if __name__=='__main__':main()
