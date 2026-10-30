"""归档95固定字典执行原字节、双分母原数据和实际栈帧；不加载DLL或重测。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def pack(path, members):
    rows = []
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_STORED) as z:
        for name, source in sorted(members.items()):
            raw = source.read_bytes()
            z.writestr(name, raw)
            rows.append({'member': name, 'bytes': len(raw), 'sha256': digest(raw)})
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for row in rows:
            assert digest(z.read(row['member'])) == row['sha256']
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('95原始归档不覆盖')
    a.output.mkdir(parents=True)
    perf = ROOT / 'artifacts/p16-palette-prepare-performance-v1'
    quality = ROOT / 'artifacts/p16-palette-prepare-quality-v1'
    build = ROOT / 'artifacts/p16-palette-prepare-build-v1'
    plan = json.loads((perf / 'executed-plan.json').read_text(encoding='utf-8'))
    assert digest((perf / 'executed-plan.json').read_bytes()) == '2b802c6353ef0fc2a185ae435c1fc3786d38667308e2a0ca31a3df895efd1ed1'
    assert digest(Path(plan['quality_proof']['path']).read_bytes()) == plan['quality_proof']['sha256']
    for name in ('executed-plan.json', 'results.json', 'offline-audit.json'):
        shutil.copyfile(perf / name, a.output / name)
    shutil.copyfile(quality / 'correctness.json', a.output / 'correctness.json')
    raw = {str(f.relative_to(perf)).replace('\\', '/'): f for f in perf.rglob('*') if f.is_file()}
    raw.update({'quality/' + str(f.relative_to(quality)).replace('\\', '/'): f
        for f in quality.rglob('*') if f.is_file()})
    raw['preflight.json'] = ROOT / 'artifacts/p16-palette-prepare-performance-preflight-v1.json'
    raw['quality/full-run.log'] = ROOT / 'artifacts/p16-palette-prepare-quality-v1.log'
    raw['static-stack.json'] = ROOT / 'artifacts/p16-palette-prepare-stack-v1.json'
    save(a.output / 'raw-members.json', pack(a.output / 'raw-evidence.zip', raw))

    prior = json.loads((ROOT / 'report/data/p16-shared-prepare-v1/identity.json').read_text(encoding='utf-8'))
    sources = {}
    for row in prior['execution_dependencies']:
        path = ROOT / row['path']
        assert digest(path.read_bytes()) == row['execution_sha256'], str(path)
        sources[row['path']] = path
    for row in plan['sources']:
        path = Path(row['path'])
        assert digest(path.read_bytes()) == row['sha256']
        sources[path.relative_to(ROOT).as_posix()] = path
    own = [*list((ROOT / 'experiments/p16-palette-prepare-runtime').glob('*')),
        *[ROOT / 'experiments' / n for n in ('p16-palette-prepare-static-v1.json',
            'p16-palette-prepare-quality-v1.json', 'p16-palette-prepare-performance-v1.json')],
        ROOT / 'scripts/archive_p16_palette_prepare.py', ROOT / 'scripts/freeze_p16_palette_performance.py']
    for path in own:
        assert path.is_file()
        sources[path.relative_to(ROOT).as_posix()] = path
    compiled = set()
    for dep in build.rglob('*.obj.d'):
        for line in dep.read_text(encoding='utf-8').splitlines():
            text = line.strip().removesuffix('\\').strip().replace('\\', '/')
            if text.startswith(ROOT.as_posix() + '/'):
                path = Path(text)
                assert path.is_file(), text
                compiled.add(path.relative_to(ROOT).as_posix())
                sources[path.relative_to(ROOT).as_posix()] = path
    source_rows = pack(a.output / 'execution-sources.zip', sources)
    dependencies = []
    queries=''.join('HEAD:'+row['member']+'\n' for row in source_rows).encode('utf-8')
    blobs=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=queries,capture_output=True,check=True).stdout
    position=0
    parents={}
    for row in source_rows:
        end=blobs.index(b'\n',position)
        header=blobs[position:end]
        if header.endswith(b' missing'):
            parents[row['member']]=None;position=end+1
        else:
            fields=header.split();assert fields[1]==b'blob'
            size=int(fields[2]);parents[row['member']]=digest(blobs[end+1:end+1+size]);position=end+size+2
    assert position==len(blobs)
    for row in source_rows:
        git_sha=parents[row['member']]
        raw_bytes = sources[row['member']].read_bytes()
        relation = 'new-uncommitted' if git_sha is None else ('byte-identical' if git_sha == row['sha256']
            else ('crlf-to-lf' if digest(raw_bytes.replace(b'\r\n', b'\n')) == git_sha else 'changed-from-parent'))
        dependencies.append({'path': row['member'], 'copy_member': row['member'], 'bytes': row['bytes'],
            'execution_sha256': row['sha256'], 'parent_git_blob_sha256': git_sha, 'relation': relation})

    metadata = {}
    for path in build.rglob('*'):
        if path.is_file() and (path.name in ('CMakeCache.txt', 'build.log', 'configure.log',
                'flags.make', 'link.txt', 'linkLibs.rsp', 'objects1.rsp', 'includes_CXX.rsp', 'libraries-Release.json')
                or path.name.endswith(('.obj.d', '.su'))):
            metadata[path.relative_to(build).as_posix()] = path
    save(a.output / 'build-members.json', pack(a.output / 'build-files.zip', metadata))
    models = {}
    for model in plan['models'].values():
        for row in [*model['models'], *[v for v in model['sidecars'] if v]]:
            path = Path(row['path'])
            assert digest(path.read_bytes()) == row['sha256']
            name = path.relative_to(Path('F:/Hackathon/projects/16-lut-color')).as_posix()
            models[name] = path
    save(a.output / 'model-members.json', pack(a.output / 'models.zip', models))
    core = next(build.rglob('libjshc_core.a'))
    identity = {'date_asia_shanghai': '2026-10-24', 'parent_head': '0d2fa16328441c5ba966c7f2062224b3d6f54025',
        'source_freeze': plan['source_freeze'], 'libraries': plan['libraries'],
        'reference_source_identity': '3210857:report/data/p16-prepare-simd-v1/identity.json',
        'previous_source_identity': '0d2fa16:report/data/p16-shared-prepare-v1/identity.json',
        'sources': {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in own},
        'execution_dependencies': dependencies, 'actual_compiler_project_dependencies': sorted(compiled),
        'python_source_scope': '沿94实际直接依赖及保守lutlab包闭包，补95冻结/质量/性能/独立审计；不声称闭包内所有函数执行。',
        'static_core': {'path': str(core), 'sha256': digest(core.read_bytes())},
        'compiler': 'GCC15.2/CMake4.2 MinGW Makefiles Release，实际obj.d/flags/link/rsp和完整构建日志见build-files.zip',
        'source_diff': '独立95仅以512槽完整RGB24键字典替换direct资格段whole-cache去重和排序ID映射；复用94共享编译、阈值、ABI、表布局、全部hot TU及旧回退。三个数组3580B、对象3584B，实际GCC create总帧7568B见.su。',
        'performance_preflight': '预检原件在raw-evidence.zip；根代理窗口内本组无编译/数值/ZIP/Gitpack并行，保留宿主既有进程事实，不声称宿主绝对独占。'}
    save(a.output / 'identity.json', identity)
    readme = '''# 95固定字典准备原字节证据

固定87/94/95三角色、两模型、四worker。冷N1/10/86/100保留完整nativecreate及连续首Out4 wall；热只N1/100 in/out1/4，中间N热未重测不授档。全部1536实际末SHA、双方独立AA/最劣档、失效及12RSS保留，不用94慢分母救87底线。

raw-evidence.zip保存全部原始JSON、partial、56完整流/20表字节快照/13最坏碰撞有限合同/16独立u64/32照片SHA的质量结果与日志及预检。execution-sources.zip保存执行原字节，identity区分父Git CRLF/LF/新源；build-files.zip含实际obj.d、全部.su、flags/link/rsp与构建日志；models.zip为两固定链去重模型。固定数组3580B、对象3584B及生产create总静态帧7568B分别披露，不声称无内存成本。不打包DLL、照片和完整源LUT。

离线复算：python scripts/audit_p16_palette_prepare.py report/data/p16-palette-prepare-v1/raw-evidence.zip。它不加载DLL或重测。具体有效与失效项见阶段中文文档，已提交归档与冻结源另核Git blob SHA。
'''
    (a.output / 'README.md').write_text(readme, encoding='utf-8')
    save(a.output / 'manifest.json', {'files': [{'path': f.relative_to(a.output).as_posix(),
        'bytes': f.stat().st_size, 'sha256': digest(f.read_bytes())} for f in sorted(a.output.rglob('*')) if f.is_file()]})
    print(json.dumps({'output': str(a.output), 'source_members': len(source_rows),
        'compiled_dependencies': len(compiled), 'raw_members': len(raw), 'models': len(models),
        'archive_files': len(list(a.output.iterdir()))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
