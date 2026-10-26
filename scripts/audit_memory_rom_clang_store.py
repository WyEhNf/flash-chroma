"""静态核对Clang阶段原字节、复用对象和同场编译器配对比。"""
import hashlib
import io
import json
from pathlib import Path
import statistics
import subprocess
import zipfile
import re

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    prefix='report/data/p16-memory-clang-store-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+n for n in manifest['files']];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+n for n in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('未暂存：'+name)
        blob=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;expected=manifest['files'][path.name]
        if blob!=path.read_bytes() or len(blob)!=expected['bytes'] or sha(blob)!=expected['sha256']:raise AssertionError('原字节不一致：'+name)
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                if z.testzip():raise AssertionError('CRC失败：'+name)
                members+=len(z.infolist())
    plan=read(ROOT/'experiments/memory-rom-clang-store-v1.json')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('所测源码不同')
    build=read(directory/'build.json')
    if build['forbidden_mnemonics']:raise AssertionError('存在禁止ISA')
    for name,value in build['reused_objects'].items():
        if value!=plan['input_sha256'][name]:raise AssertionError('非原字节复用')
    with zipfile.ZipFile(ROOT/'report/data/p16-memory-rom-v1/measured-libraries.zip') as z:
        for name in ('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll'):
            if sha(z.read(name))!=build['libraries'][name]:raise AssertionError('复用依赖包不同')
    pure=Path(next(r['command'][-1] for r in build['commands'] if r['command'][-1].endswith('jshc_memory_c99.dll')))
    if sha(pure.read_bytes())!=build['libraries']['jshc_memory_c99.dll']:raise AssertionError('实际C99 DLL不同')
    imports=re.findall(r'DLL Name:\s+(\S+)',subprocess.check_output(['E:/mingw64/bin/objdump.exe','-p',str(pure)],text=True))
    if not imports or any(n.lower()!='kernel32.dll' and not n.lower().startswith('api-ms-win-crt-') for n in imports):raise AssertionError('独立C99含额外运行库依赖')
    with zipfile.ZipFile(directory/'performance-raw.zip') as z:
        workers=[json.loads(z.read(f'worker-{i}/results.json')) for i in range(4)]
    for pair in read(directory/'compiler-pairs.json')['pairs']:
        ratios=[]
        for w in workers:
            values={x['label']:x['median_seconds'] for x in w['rows'] if x['mode']==pair['mode'] and x['threads']==pair['threads']};ratios.append(values['gcc_store']/values['clang_store'])
        if ratios!=pair['per_worker_gcc_over_clang'] or statistics.median(ratios)!=pair['median'] or min(ratios)!=pair['worst']:raise AssertionError('同场比值不同')
    result=dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,reused_objects=len(build['reused_objects']),pure_c99_imports=imports,dependency_package_matches=True,scope='只核对发布原字节和原始统计，不重跑性能。');(directory/'git-byte-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
