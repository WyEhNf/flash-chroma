"""归档94执行原字节、双分母原始数据和构建闭包；不加载DLL或重测。"""
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
        raise FileExistsError('94原始归档不覆盖')
    a.output.mkdir(parents=True)
    perf = ROOT / 'artifacts/p16-shared-prepare-performance-v1'
    quality = ROOT / 'artifacts/p16-shared-prepare-quality-v1'
    build = ROOT / 'artifacts/p16-shared-prepare-build-v1'
    plan = json.loads((perf / 'executed-plan.json').read_text(encoding='utf-8'))
    assert digest((perf / 'executed-plan.json').read_bytes()) == '9bfaaba25a2c51ed9a4943d96cadb860cf33bcf8acd2ec161f1793c16ac63852'
    assert digest(Path(plan['quality_proof']['path']).read_bytes()) == plan['quality_proof']['sha256']
    for name in ('executed-plan.json', 'results.json', 'offline-audit.json'):
        shutil.copyfile(perf / name, a.output / name)
    shutil.copyfile(quality / 'correctness.json', a.output / 'correctness.json')
    raw = {str(f.relative_to(perf)).replace('\\', '/'): f for f in perf.rglob('*') if f.is_file()}
    raw.update({'quality/' + str(f.relative_to(quality)).replace('\\', '/'): f
        for f in quality.rglob('*') if f.is_file()})
    raw['preflight.json'] = ROOT / 'artifacts/p16-shared-prepare-performance-preflight-v1.json'
    save(a.output / 'raw-members.json', pack(a.output / 'raw-evidence.zip', raw))

    prior = json.loads((ROOT / 'report/data/p16-workload-v1/identity.json').read_text(encoding='utf-8'))
    sources = {}
    for row in prior['execution_dependencies']:
        path = ROOT / row['path']
        assert digest(path.read_bytes()) == row['execution_sha256'], str(path)
        sources[row['path']] = path
    for row in plan['sources']:
        path = Path(row['path'])
        assert digest(path.read_bytes()) == row['sha256']
        sources[path.relative_to(ROOT).as_posix()] = path
    own = [*list((ROOT / 'experiments/p16-shared-prepare-runtime').glob('*')),
        *[ROOT / 'experiments' / n for n in ('p16-shared-prepare-static-v1.json',
            'p16-shared-prepare-quality-v1.json', 'p16-shared-prepare-performance-v1.json')],
        ROOT / 'scripts/archive_p16_shared_prepare.py']
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
    for row in source_rows:
        result = subprocess.run(['git', 'show', 'HEAD:' + row['member']], cwd=ROOT, capture_output=True)
        git_sha = digest(result.stdout) if result.returncode == 0 else None
        raw_bytes = sources[row['member']].read_bytes()
        relation = 'new-uncommitted' if git_sha is None else ('byte-identical' if git_sha == row['sha256']
            else ('crlf-to-lf' if digest(raw_bytes.replace(b'\r\n', b'\n')) == git_sha else 'changed-from-parent'))
        dependencies.append({'path': row['member'], 'copy_member': row['member'], 'bytes': row['bytes'],
            'execution_sha256': row['sha256'], 'parent_git_blob_sha256': git_sha, 'relation': relation})

    metadata = {}
    for path in build.rglob('*'):
        if path.is_file() and (path.name in ('CMakeCache.txt', 'build.log', 'configure.log',
                'flags.make', 'link.txt', 'linkLibs.rsp', 'objects1.rsp', 'includes_CXX.rsp', 'libraries-Release.json')
                or path.name.endswith('.obj.d')):
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
    identity = {'date_asia_shanghai': '2026-10-24', 'parent_head': '8351db18ce422babc82e3765a81ac5647a6fd1e8',
        'source_freeze': plan['source_freeze'], 'libraries': plan['libraries'],
        'reference_source_identity': '3210857:report/data/p16-prepare-simd-v1/identity.json',
        'previous_source_identity': '7c904ea2:report/data/p16-workload-v1/identity.json',
        'sources': {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in own},
        'execution_dependencies': dependencies, 'actual_compiler_project_dependencies': sorted(compiled),
        'python_source_scope': '沿92实际直接依赖及保守lutlab包闭包，补94冻结/质量/性能/独立审计；不声称闭包内所有函数执行。',
        'static_core': {'path': str(core), 'sha256': digest(core.read_bytes())},
        'compiler': 'GCC15.2/CMake4.2 MinGW Makefiles Release，实际obj.d/flags/link/rsp和完整构建日志见build-files.zip',
        'source_diff': '独立94仅将direct完整域编译批入口按已验证shared分派现有transform<true/false>；runtime只revision92→94，阈值/ABI/表布局/全部hot TU不变。',
        'performance_preflight': '预检原件在raw-evidence.zip；根代理窗口内本组无编译/数值/ZIP/Gitpack并行，保留宿主既有进程事实，不声称宿主绝对独占。'}
    save(a.output / 'identity.json', identity)
    readme = '''# 94共享prepare原字节证据

固定87/92/94三角色、2模型、N1/10/86/100、4worker。N1三库真默认create；其余92/94沿原2^26 hint。两分母的全部冷/热结果、控制失效和最劣轮次保留；不将92→94准备机制比较替代87→94完整作业门槛。

raw-evidence.zip保存全部原始JSON、partial、56完整输出流质量结果、20表字节快照、16独立u64合同、2112实际组末SHA和12新进程RSS及预检。execution-sources.zip保存执行原字节，identity逐项区分父HEAD的CRLF/LF/新源；build-files.zip存编译依赖和日志；models.zip为两固定模型/侧表去重集合。不打包DLL、照片和完整目标LUT，DLL SHA与来源已固定。

离线复算：python scripts/audit_p16_shared_prepare.py report/data/p16-shared-prepare-v1/raw-evidence.zip。该入口不加载DLL或重测。具体有效/失效项和各档结论见阶段中文文档，不按新结果重选分母或补测。
'''
    (a.output / 'README.md').write_text(readme, encoding='utf-8')
    save(a.output / 'manifest.json', {'files': [{'path': f.relative_to(a.output).as_posix(),
        'bytes': f.stat().st_size, 'sha256': digest(f.read_bytes())} for f in sorted(a.output.rglob('*')) if f.is_file()]})
    print(json.dumps({'output': str(a.output), 'source_members': len(source_rows),
        'compiled_dependencies': len(compiled), 'raw_members': len(raw), 'models': len(models),
        'archive_files': len(list(a.output.iterdir()))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
