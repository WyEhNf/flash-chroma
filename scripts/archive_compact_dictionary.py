"""归档M16P两种精确索引格式的完整原件及可直接重放的三个ROM。"""
import argparse
from pathlib import Path
from archive_compact_sparse import package
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','roms','full','contract','guard','perf','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    for key in vars(a):setattr(a,key,getattr(a,key).resolve())
    a.output.mkdir(parents=True,exist_ok=False);plan=ROOT/'experiments/compact-dictionary-v1.json';frozen=read(plan)
    inputs={'build.json':a.build/'build.json','export.json':a.roms/'export.json','full.json':a.full/'results.json','contract.json':a.contract/'results.json','rom-end-guard.json':a.guard/'results.json','performance.json':a.perf/'summary.json','old-control-provenance.json':ROOT/'artifacts/p16-compact-dictionary-static-v1/results.json'}
    for name,source in inputs.items():(a.output/name).write_bytes(source.read_bytes())
    sources={n:ROOT/n for n in frozen['source_sha256']}
    for n in ('experiments/compact-dictionary-v1.json','experiments/skylake-andn-split-v1.json','scripts/verify_compact_dictionary_rom_guard.py','scripts/archive_compact_dictionary.py','scripts/archive_compact_sparse.py','scripts/audit_compact_dictionary_provenance.py','artifacts/p16-memory-build-v2/memory_avx2_4.cpp'):sources[n]=ROOT/n
    for path in a.build.glob('*.su'):sources['stack-usage/'+path.name]=path
    package(a.output/'measured-source.zip',sources)
    libraries={n:a.build/n for n in ('jshc_memory_rom.dll','jshc_dict_c99.dll')};libraries['original32-avx2.o']=ROOT/'artifacts/p16-memory-build-v2/memory_avx2_4.o'
    for mode in (17,24):libraries['channel_avx2_'+str(mode)+'.o']=a.build/('channel_avx2_'+str(mode)+'.o')
    package(a.output/'new-libraries.zip',libraries)
    package(a.output/'exact-roms.zip',{'rom-17.bin':a.roms/'rom-17.bin','rom-24.bin':a.roms/'rom-24.bin','original-rom-32.bin':Path(frozen['input_rom_path'])})
    package(a.output/'performance-raw.zip',{x.relative_to(a.perf).as_posix():x for x in a.perf.rglob('*.json') if x.name not in ('summary.json','partial.json')})
    save(a.output/'manifest.json',dict(purpose=__doc__,files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x)) for x in a.output.iterdir() if x.is_file()},references='78/80、原32bit字典AVX2及四MinGW依赖在report/data/p16-memory-rom-v1/measured-libraries.zip；原SHA在plan/build/performance绑定。实际ROM单独压缩，运行容量按解压字节+真实句柄计算，不拿ZIP磁盘字节冒充RAM。'))
    print(a.output)
if __name__=='__main__':main()
