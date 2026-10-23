"""封存两类质量筛查及7bit实际内核/性能，保留原字节，不打包大型派生ROM。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    output=ROOT/'report/data/p16-palette-input-v1'
    output.mkdir(parents=True,exist_ok=True)
    if (output/'evidence.zip').exists() or (output/'manifest.json').exists():raise FileExistsError('拒绝覆盖归档')
    groups=['p16-palette-bitpack-v1','p16-input-quant-v1','p16-palette-native-rom-v1',
            'p16-palette-native-build-v1','p16-palette-native-verify-v1','p16-palette-native-perf-v1']
    raw=[];omitted=[]
    for group in groups:
        root=ROOT/'artifacts'/group
        assert root.is_dir(),group
        for path in sorted(root.rglob('*')):
            if not path.is_file():continue
            if path.suffix=='.bin' or (path.suffix=='.dll' and path.name not in ['jshc_memory_rom.dll','jshc_memory_c99.dll']):
                omitted.append(dict(path=str(path.relative_to(ROOT)).replace('\\','/'),bytes=path.stat().st_size,sha256=sha(path.read_bytes())))
                continue
            raw.append((path,'raw/'+str(path.relative_to(ROOT/'artifacts')).replace('\\','/')))
    source_paths=set()
    for group in ['p16-palette-bitpack-v1','p16-input-quant-v1']:
        run=json.loads((ROOT/'artifacts'/group/'run.json').read_text(encoding='utf-8'))
        for name,value in run['source_sha256'].items():
            path=ROOT/name;assert sha(path.read_bytes())==value,name;source_paths.add(path)
    build=json.loads((ROOT/'artifacts/p16-palette-native-build-v1/build.json').read_text(encoding='utf-8'))
    for name,value in build['source_sha256'].items():
        path=ROOT/name;assert sha(path.read_bytes())==value,name;source_paths.add(path)
    perf=json.loads((ROOT/'experiments/p16-palette-native-perf-v1.json').read_text(encoding='utf-8'))
    for name,value in perf['source_sha256'].items():
        path=ROOT/name;assert sha(path.read_bytes())==value,name;source_paths.add(path)
    source_paths.update([ROOT/'experiments/p16-palette-bitpack-v1.json',ROOT/'experiments/p16-input-quant-v1.json',
                         ROOT/'experiments/p16-palette-native-perf-v1.json',ROOT/'scripts/audit_palette_quality.py',Path(__file__)])
    raw += [(path,'source/'+str(path.relative_to(ROOT)).replace('\\','/')) for path in sorted(source_paths)]
    manifest=[];archive=output/'evidence.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as packed:
        for path,name in raw:
            data=path.read_bytes();packed.writestr(name,data)
            manifest.append(dict(name=name,bytes=len(data),sha256=sha(data)))
    with zipfile.ZipFile(archive) as packed:
        assert packed.testzip() is None
        for item in manifest:
            data=packed.read(item['name']);assert len(data)==item['bytes'] and sha(data)==item['sha256']
    (output/'manifest.json').write_text(json.dumps(dict(archive_sha256=sha(archive.read_bytes()),members=manifest,omitted_generated_inputs=omitted,
        omission_note='不打包大派生ROM或GCC依赖；两palette/mapping、原模型/ROM来源SHA、精确导出脚本及输入近邻规则均保留。完整参考表/照片同样留本地，孤立克隆需恢复绑定输入。'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(manifest)}原件SHA/CRC通过，{len(omitted)}个大派生输入/运行库只记录恢复身份')


if __name__=='__main__':main()
