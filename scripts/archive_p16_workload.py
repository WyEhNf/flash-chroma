"""归档92已结束的执行原字节、构建元数据、模型与双Git身份；不重测。"""
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
        raise FileExistsError('原始阶段归档不覆盖')
    a.output.mkdir(parents=True)
    perf = ROOT / 'artifacts/p16-workload-performance-v1'
    quality = ROOT / 'artifacts/p16-workload-quality-v1'
    build = ROOT / 'artifacts/p16-workload-build-v1'
    plan = json.loads((perf / 'executed-plan.json').read_text(encoding='utf-8'))
    assert digest((perf / 'executed-plan.json').read_bytes()) == 'ad777e52927e309d942d579db4de5ba36213c1e8c0db9512746ca7a976e956a8'
    assert digest(Path(plan['quality_proof']['path']).read_bytes()) == plan['quality_proof']['sha256']
    for name in ('executed-plan.json', 'results.json', 'offline-audit.json'):
        shutil.copyfile(perf / name, a.output / name)
    shutil.copyfile(quality / 'correctness.json', a.output / 'correctness.json')
    raw = {str(f.relative_to(perf)).replace('\\', '/'): f for f in perf.rglob('*') if f.is_file()}
    raw.update({'quality/' + str(f.relative_to(quality)).replace('\\', '/'): f for f in quality.rglob('*') if f.is_file()})
    raw['preflight.json'] = ROOT / 'artifacts/p16-workload-performance-preflight-v1.json'
    save(a.output / 'raw-members.json', pack(a.output / 'raw-evidence.zip', raw))

    prior = json.loads((ROOT / 'report/data/p16-shared-domain-v1/identity.json').read_text(encoding='utf-8'))
    sources = {}
    for row in prior['execution_dependencies']:
        if 'p16-shared-domain-runtime' not in row['path']:
            path = ROOT / row['path']
            assert digest(path.read_bytes()) == row['execution_sha256'], str(path)
            sources[row['path']] = path
    for row in plan['sources']:
        path = Path(row['path'])
        assert digest(path.read_bytes()) == row['sha256']
        sources[path.relative_to(ROOT).as_posix()] = path
    own = [*list((ROOT / 'experiments/p16-workload-runtime').glob('*')),
        *[ROOT / 'experiments' / n for n in ('p16-workload-static-v1.json',
            'p16-workload-quality-v1.json', 'p16-workload-performance-v1.json')],
        ROOT / 'scripts/archive_p16_workload.py']
    for path in own:
        assert path.is_file()
        sources[path.relative_to(ROOT).as_posix()] = path
    for path in (ROOT / 'CMakeLists.txt',
                 ROOT / 'experiments/skylake-andn-normal-runtime/CMakeLists.txt'):
        sources[path.relative_to(ROOT).as_posix()] = path
    # 以本次GCC生成的实际依赖补齐项目源；系统头由固定工具链身份负责。
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
                'flags.make', 'link.txt', 'linkLibs.rsp', 'objects1.rsp', 'includes_CXX.rsp') or path.name.endswith('.obj.d')):
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
    identity = {'date_asia_shanghai': '2026-10-24', 'parent_head': '7e3ef88',
        'source_freeze': plan['source_freeze'], 'libraries': plan['libraries'],
        'reference_source_identity': '3210857:report/data/p16-prepare-simd-v1/identity.json',
        'sources': {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in own},
        'execution_dependencies': dependencies, 'actual_compiler_project_dependencies': sorted(compiled),
        'python_source_scope': '沿91实际直接依赖及保守lutlab包源码闭包，补92有类型包装/质量/性能/冻结/audit，不声称包内每个函数执行。',
        'static_core': {'path': str(core), 'sha256': digest(core.read_bytes())},
        'compiler': 'GCC15.2/CMake4.2 MinGW Makefiles Release，实际obj.d/flags/link/rsp和完整构建日志存build-files.zip',
        'source_diff': '独立92只给共享direct构造添加固定uint64总像素门控/显式ABI；默认hint0复用87共享cached，非共享a399资格及所有pixel TU不变。',
        'performance_preflight': '2既有Python GUI/server及PID138404未定归属credential-manager进程仍在；根代理窗口内无本组编译/数值/ZIP/Gitpack并行，不称宿主绝对独占。'}
    save(a.output / 'identity.json', identity)
    readme = '''# 92原字节证据

本目录保留固定2^26像素阈值的新92同旧87配对，不覆盖91无条件构造的失败。全部4worker、320热/80冷记录、1760实际末组输出SHA与8个RSS进程保留；A/A失效全留，没有补测或调整阈值。ordinary首次总墙钟五N均有效并过90档；有效热最劣只到80档；a399冷N1及多热场控制失效，所以all-scene≥50尚未证明。N100 standalone prepare最劣11.4943%低于50，不能称prepare提速。

raw-evidence.zip含所有原始JSON（含partial快照）、完整质量及合成输入、预检；execution-sources.zip保存执行原字节，identity逐项区分父HEAD blob的CRLF/LF/新源。build-files.zip保存实际构建依赖、flags/link/rsp及日志；models.zip为两条固定模型/侧表去重集合。不打包DLL、照片或完整目标LUT；DLL SHA和源身份已固定，可重建，不冒称工具链产物逐bit必同。

离线复算：python scripts/audit_p16_workload.py report/data/p16-workload-v1/raw-evidence.zip。它不加载DLL或重测。已提交归档及冻结源需另按manifest/identity逐Git blob SHA核验。
'''
    (a.output / 'README.md').write_text(readme, encoding='utf-8')
    save(a.output / 'manifest.json', {'files': [{'path': f.relative_to(a.output).as_posix(),
        'bytes': f.stat().st_size, 'sha256': digest(f.read_bytes())} for f in sorted(a.output.rglob('*')) if f.is_file()]})
    print(json.dumps({'output': str(a.output), 'source_members': len(source_rows),
        'compiled_dependencies': len(compiled), 'raw_members': len(raw), 'models': len(models),
        'archive_files': len(list(a.output.iterdir()))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
