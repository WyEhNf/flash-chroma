"""独立8例观察器执行前冻结，不覆盖前置v1或重导出。"""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    output=ROOT/'experiments/page-alias-handle-observer-v1.json'
    if output.exists():raise FileExistsError('不能覆写冻结观察协议')
    previous=json.loads((ROOT/'experiments/page-alias-runtime-v1.json').read_text(encoding='utf-8'));names=['scripts/observe_page_alias_handles.py','scripts/freeze_page_alias_handle_observer.py','experiments/page-alias-handle-observer-design-v1.md',*previous['source_sha256']]
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    if any(sha(ROOT/name)!=value for name,value in previous['source_sha256'].items()):raise AssertionError('前置v1冻结源被改动')
    root=ROOT/'artifacts/p16-page-alias-runtime-v1';alias=root/'export/alias.bin';aligned=root/'export/aligned.bin';inputs={**previous['input_sha256'],**{str(path):sha(path) for path in (alias,aligned,ROOT/'experiments/page-alias-runtime-v1.json',root/'export/export.json',root/'contracts/failure.json',root/'run.json')}}
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_sha256=inputs,alias=str(alias),aligned=str(aligned),library=previous['library'],original_rom=previous['original_rom'],original_rom_sha256=previous['original_rom_sha256'],protocol='唯一fresh固定前8例；无新增warmup，不重置原baseline；预分配32768事件记录每次loader API/注入前后count/owned/原返回值/LastError及Model/VA闭环，首偏移STOP。保留v1失败，不export/三fresh/其余格式或图像/速度。',scope='原因观察无资格；不复现不撤销v1。日志在计数区结束后写出；必要owned未回收则保留子进程等显式retry。')
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dict(plan=str(output),sha256=sha(output),sources=len(names),inputs=len(inputs)))
if __name__=='__main__':main()
