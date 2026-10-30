"""封存RO部署三fresh、完整质量及八角色正式原件，不重跑。"""
import argparse
from pathlib import Path
from archive_compact_sparse import package
from study_memory_rom import ROOT,read,save,sha
from audit_readonly_rom_performance import compute
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('quality','perf','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);plan=ROOT/'experiments/memory-rom-readonly-performance-v1.json';spec=read(plan)
    originals={'quality-execution.json':a.quality/'execution.json','commit-summary.json':a.quality/'commit-summary.json','original-cow.json':a.quality/'original_cow/results.json','win-cow.json':a.quality/'cow/results.json','win-readonly.json':a.quality/'readonly/results.json','quality.json':a.quality/'quality/results.json','performance.json':a.perf/'summary.json','benchmark-driver.json':a.perf/'driver.json'}
    for name,path in originals.items():(a.output/name).write_bytes(path.read_bytes())
    for index in (1,2):(a.output/f'host-preflight-v{index}.json').write_bytes((ROOT/f'artifacts/p16-readonly-rom-performance-preflight-v{index}.json').read_bytes())
    sources={name:ROOT/name for name in spec['source_sha256']}
    for path in (plan,ROOT/'scripts/archive_readonly_rom.py',ROOT/'scripts/audit_readonly_rom_package.py',ROOT/'scripts/archive_compact_sparse.py'):sources[path.relative_to(ROOT).as_posix()]=path
    package(a.output/'measured-source.zip',sources)
    package(a.output/'performance-raw.zip',{path.relative_to(a.perf).as_posix():path for path in a.perf.rglob('*.json') if path.name not in ('partial.json','decimal-audit.json')})
    save(a.output/'decimal-audit.json',compute(a.perf,spec))
    save(a.output/'environment-note.json',dict(purpose='保留旧计算库/ROM及模型容量，只验证Windows只读映射提交与吞吐。',identity='a399原linear M16D16778272B+1056B对象=16779328B；计算DLL/所有ISA未变。既有库及ROM按SHA复用旧阶段，不重复上传235MB照片。',quality='三fresh各一次、5阶段；门槛通过后8域/8百图、IO/ROM guard和生命周期合同。不计吞吐；原COW close句柄+1原因未知原样保留。',performance='root另授排他、8角色4worker0x55、848调用+8RSS；RO/COW辅助配对不能代替较快78/80主分母，AA无效全档清空。',memory='COW与RO区别是提交保留，不是ROM capacity或物理工作集。全部RSS包含Python/库，微实验与正式导入群不同，不直接拼绝对峰。',scope='Windows专属loader，不冒充跨平台改善；portable C99未改，官方派生表许可和目标实机限制仍在。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={path.name:dict(bytes=path.stat().st_size,sha256=sha(path)) for path in a.output.iterdir() if path.is_file()},references='旧Clang计算DLL/ROM和78/80按两个冻结计划输入SHA复用原发布；新loader无新编译，无新ROM。'))
    print(a.output)
if __name__=='__main__':main()
