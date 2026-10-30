"""精简封存512bank/6bit唯一失败普查，原始大频数ZIP保留原字节。"""
import argparse
from pathlib import Path
from archive_compact_sparse import package
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);planpath=ROOT/'experiments/rgb3d-palette-census-v1.json';plan=read(planpath);source=ROOT/plan['output_path'];results=read(source/'results.json')
    (a.output/'run.json').write_bytes((source/'run.json').read_bytes());package(a.output/'census-raw.zip',{name:source/name for name in ('run.json','results.json','frequency-support.json')})
    paths={name:ROOT/name for name in plan['source_sha256']}
    for name in ('experiments/rgb3d-palette-census-v1.json','experiments/rgb3d-palette-census-proposed-v1.json','scripts/archive_rgb3d_palette_census.py','scripts/audit_rgb3d_palette_census.py','scripts/archive_compact_sparse.py'):paths[name]=ROOT/name
    package(a.output/'frozen-source.zip',paths)
    summary={key:results[key] for key in ('purpose','environment','plan_sha256','source_rom_sha256','logical_sha256','finite_index_cases','domain_colors','global_reachable_colors','key','bank_count','local_id_bits','max_bank_colors','failing_banks','gate_passed','decision','projected_format','frequency_support_sha256','before','after','resource_wall_seconds','scope')};summary['bank_distinct_output_colors']=[row['distinct_output_colors'] for row in results['banks']];summary['bank_input_counts']=[row['input_colors'] for row in results['banks']];save(a.output/'census-summary.json',summary)
    save(a.output/'environment-note.json',dict(purpose='固定6bit方案失败，静态投影不是部署收益。',execution='root授权非性能窗，一线程；root289/tailbox质量可并行，wall仅调度资源。无候选编译器/ISA、ROM导出/native像素/速度、WASM/实板。',memory='进程峰值含Python/NumPy、原ROM、分块数组和完整512×230频数；不是运行时RAM。',gate='任一bank>64即STOP，54失败、最大95，完整频数封存；未在本协议改key/bit/例外或追加扫描。',sources='source ZIP保留普查前冻结5源/设计和计划；proposed文件为更早静态草案；发布器/审计在普查后写入，不改原源。',rom_reference='原M16D16B完整字节已在p16-tagged-block16-v1/exact-rom.zip源ROM成员归档，SHA904f…；本阶段不重复上传/读取完整源进行分类。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={path.name:dict(bytes=path.stat().st_size,sha256=sha(path)) for path in a.output.iterdir() if path.is_file()},scope='ZIP仅传输归档；不可将压缩包大小当运行时capacity。没有可行6bit ROM或新性能点。'))
    print(a.output)
if __name__=='__main__':main()
