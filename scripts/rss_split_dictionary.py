"""独立RSS补充：流式1MiB身份预检，同一M16S七角色setup，不分配照片数组。"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import bench_memory_rom as bench
import bench_split_dictionary as split
from study_memory_rom import ROOT,read,save,env

def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while True:
            block=stream.read(1<<20)
            if not block:break
            digest.update(block)
    return digest.hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ('build','roms','ref80','data-root','output'):p.add_argument('--'+field,type=Path,required=True)
    p.add_argument('--rss');p.add_argument('--freeze',action='store_true');a=p.parse_args();path=ROOT/'experiments/split-dictionary-rss-v1.json';parent=ROOT/'experiments/split-dictionary-v1.json';plan=read(parent)
    for name,value in plan['source_sha256'].items():
        if sha(ROOT/name)!=value:raise AssertionError('冻结源不同：'+name)
    for name,value in plan['input_sha256'].items():
        if sha(name)!=value:raise AssertionError('冻结输入不同：'+name)
    if a.freeze:
        if path.exists():raise FileExistsError(path)
        save(path,dict(purpose=__doc__,script_sha256=sha(__file__),parent_plan_sha256=sha(parent),roles=plan['roles'],protocol='原正式计时不改不重跑。七角色各独立新进程，流式1MiB SHA验证相同输入与源后复用bench_split_dictionary.setup及bench_memory_rom.worker的RSS-only分支，不分配照片数组；完整import群相同。原全文件SHA污染peak原件另存，两个群绝对峰不拼接。',scope='Windows进程当前/峰值工作集及private commit，包括Python/NumPy/模块/运行库和流式预检，不当作核心RAM或纯prepare单函数峰值。'))
        print(path,sha(path));return
    frozen=read(path)
    if frozen['script_sha256']!=sha(__file__) or frozen['parent_plan_sha256']!=sha(parent):raise AssertionError('RSS补充冻结身份不同')
    if a.rss:
        if a.rss not in frozen['roles']:raise ValueError('未知角色')
        bench.setup=split.setup;bench.worker(a)
        save(a.output/'rss-driver.json',dict(purpose=__doc__,script_sha256=sha(__file__),plan_sha256=sha(path),environment=env(),preflight='同源同输入，逐文件1MiB流式SHA；未构造照片数组，导入群含bench_memory_rom/bench_compact_dictionary/bench_split_dictionary。'))
        return
    a.output.mkdir(parents=True,exist_ok=False);records=[];common=[sys.executable,'-X','utf8',str(Path(__file__).resolve()),'--build',str(a.build),'--roms',str(a.roms),'--ref80',str(a.ref80),'--data-root',str(a.data_root)]
    for label in frozen['roles']:
        command=common+['--rss',label,'--output',str(a.output/('rss-'+label))];r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8');records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(a.output/'execution.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    save(a.output/'summary.json',dict(purpose=__doc__,plan_sha256=sha(path),script_sha256=sha(__file__),environment=env(),rss={label:read(a.output/('rss-'+label)/'rss.json') for label in frozen['roles']},scope=frozen['scope']))
    print(a.output)
if __name__=='__main__':main()
