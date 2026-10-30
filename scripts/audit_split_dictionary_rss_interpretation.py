"""核对M16S实际导入链/冻结源及原峰值，纠正整文件SHA分配的错误解释。"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    prefix='report/data/p16-split-dictionary-v1';directory=ROOT/prefix;correction=read(directory/'rss-interpretation-correction.json');plan=read(ROOT/'experiments/split-dictionary-v1.json');sources={}
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name in ('scripts/bench_split_dictionary.py','scripts/study_memory_rom.py','scripts/bench_memory_rom.py','scripts/bench_compact_dictionary.py'):
            raw=z.read(name)
            if sha(raw)!=plan['source_sha256'][name] or raw!=(ROOT/name).read_bytes():raise AssertionError('执行源码身份变化')
            sources[name]=raw
    for name in ('scripts/bench_split_dictionary.py','scripts/bench_memory_rom.py','scripts/bench_compact_dictionary.py'):
        tree=ast.parse(sources[name])
        if not any(isinstance(node,ast.ImportFrom) and node.module=='study_memory_rom' and any(alias.name=='sha' and alias.asname is None for alias in node.names) for node in tree.body):raise AssertionError('未直接导入同一sha')
        if any(isinstance(node,ast.FunctionDef) and node.name=='sha' for node in tree.body):raise AssertionError('sha存在同名覆盖')
    tree=ast.parse(sources['scripts/study_memory_rom.py']);helper=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='sha');calls=[node for node in ast.walk(helper) if isinstance(node,ast.Call)]
    if not any(isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='hashlib' and node.func.attr=='file_digest' for node in calls) or any(isinstance(node.func,ast.Attribute) and node.func.attr=='read_bytes' for node in calls):raise AssertionError('实际sha并非所述流式实现')
    for key,name in (('wrapper','scripts/bench_split_dictionary.py'),('helper','scripts/study_memory_rom.py')):
        if correction['executed_source'][key+'_sha256']!=sha(sources[name]):raise AssertionError('纠正中的SHA不同')
    performance=read(directory/'performance.json')
    for label,expected in correction['original_peak_working_set_bytes'].items():
        if performance['rss'][label]['prepared']['PeakWorkingSetSize']!=expected:raise AssertionError('原峰值复算不同')
    relative=prefix+'/rss-interpretation-correction.json';cached=subprocess.check_output(['git','show',':'+relative],cwd=ROOT)
    if cached!=(ROOT/relative).read_bytes():raise AssertionError('纠正原字节未暂存')
    result=dict(passed=True,purpose=__doc__,source_sha256={name:sha(raw) for name,raw in sources.items()},correction_sha256=sha(cached),conclusion='原SHA已流式；第二组仅额外观察。未改正式计时、原冻结源或原ZIP。',scope='静态AST/原字节/原RSS复算，不运行模型/性能。');(directory/'rss-interpretation-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
