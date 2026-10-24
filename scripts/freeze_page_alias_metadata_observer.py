"""最后一次metadata观察前冻结，旧两次STOP与源不改。"""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    output=ROOT/'experiments/page-alias-metadata-observer-v1.json'
    if output.exists():raise FileExistsError('不能覆写冻结协议')
    previous=json.loads((ROOT/'experiments/page-alias-handle-observer-v1.json').read_text(encoding='utf-8'));names=['scripts/observe_page_alias_metadata.py','scripts/freeze_page_alias_metadata_observer.py','experiments/page-alias-metadata-observer-design-v1.md',*previous['source_sha256']]
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    if any(sha(ROOT/name)!=value for name,value in previous['source_sha256'].items()):raise AssertionError('前次冻结源不同')
    earlier=ROOT/'artifacts/p16-page-alias-handle-observer-v1';inputs={**previous['input_sha256'],**{str(path):sha(path) for path in (ROOT/'experiments/page-alias-handle-observer-v1.json',earlier/'results.json',earlier/'events.bin',earlier/'events.csv',earlier/'event-schema.json')}}
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_sha256=inputs,alias=previous['alias'],aligned=previous['aligned'],library=previous['library'],original_rom=previous['original_rom'],original_rom_sha256=previous['original_rom_sha256'],protocol='唯一fresh同8例、无新增warmup/不改baseline；metadata context代理委托原reader和__exit__，记录fd/WinHANDLE/closed/closefd/count及只读GetHandleInformation；原owned API逐调用记录不变，首漂移STOP。',scope='不重export/三fresh/其它质量/图像/性能，不授资格；仍不明则结束该alias机制unknown。')
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dict(plan=str(output),sha256=sha(output),sources=len(names),inputs=len(inputs)))
if __name__=='__main__':main()
