"""97归档唯一质量/正式、首构建失败与机械合同修复；不加载DLL或重测。"""
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
            raw = source.read_bytes();z.writestr(name, raw)
            rows.append({'member': name, 'bytes': len(raw), 'sha256': digest(raw)})
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for row in rows:
            assert digest(z.read(row['member'])) == row['sha256']
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('97归档不覆盖')
    a.output.mkdir(parents=True)
    perf, quality = [ROOT / ('artifacts/p16-shared-proven-' + n) for n in ('performance-v1', 'quality-v2')]
    builds = {n: ROOT / ('artifacts/p16-shared-proven-' + n) for n in ('build-v1', 'contract-build-v2')}
    plan = json.loads((perf / 'executed-plan.json').read_text(encoding='utf-8'))
    assert digest((perf / 'executed-plan.json').read_bytes()) == '2534782322401fac5abd33c6c6cacb3062a9bb1aa5d1ca846b3caee52bc5ee77'
    for name in ('executed-plan.json', 'results.json', 'offline-audit.json', 'decimal-audit.json'):
        shutil.copyfile(perf / name, a.output / name)
    for source, name in ((quality / 'correctness.json', 'correctness.json'),
            (quality / 'independent-check.json', 'quality-independent-check.json'),
            (ROOT / 'artifacts/p16-shared-proven-object-audit-v1.json', 'old-objects.json')):
        shutil.copyfile(source, a.output / name)
    raw = {f.relative_to(perf).as_posix(): f for f in perf.rglob('*') if f.is_file()}
    raw.update({'quality/' + f.relative_to(quality).as_posix(): f for f in quality.rglob('*') if f.is_file()})
    for name in ('p16-shared-proven-quality-v2.log', 'p16-shared-proven-object-audit-v1.json',
            'p16-shared-proven-performance-ready-v1.json', 'p16-shared-proven-performance-preflight-v1.json',
            'p16-shared-proven-preflight-process72448-v1.json', 'p16-shared-proven-old-compile-disassembly.txt',
            'p16-shared-proven-new-compile-disassembly.txt'):
        raw['boundary-and-static/' + name] = ROOT / 'artifacts' / name
    save(a.output / 'raw-members.json', pack(a.output / 'raw-evidence.zip', raw))
    sources, checked = {}, []
    for row in plan['sources']:
        path = Path(row['path'])
        assert digest(path.read_bytes()) == row['sha256'], str(path)
        include = path.suffix.lower() not in ('.dll', '.exe', '.png')
        checked.append({**row, 'copied_in_source_archive': include})
        if include:
            sources[path.relative_to(ROOT).as_posix()] = path
    for path in [ROOT / 'scripts/archive_p16_shared_proven.py', ROOT / 'scripts/audit_p16_shared_proven_decimal.py',
            ROOT / 'experiments/p16-shared-proven-performance-v1.json']:
        sources[path.relative_to(ROOT).as_posix()] = path
    metadata, objects, compiled = {}, {}, set()
    for label, folder in builds.items():
        for path in folder.rglob('*'):
            if not path.is_file():
                continue
            name = path.relative_to(folder).as_posix()
            if path.name in ('build-receipt.json', 'build.log', 'CMakeCache.txt', 'flags.make', 'link.txt',
                    'linkLibs.rsp', 'objects1.rsp', 'includes_CXX.rsp', 'libraries-Release.json') or path.name.endswith(('.obj.d', '.su')):
                metadata[label + '/' + name] = path
            if path.name.endswith('.obj') or path.name == 'libjshc_core.a':
                objects[label + '/' + name] = path
        for dependency in folder.rglob('*.obj.d'):
            for line in dependency.read_text(encoding='utf-8').splitlines():
                value = line.strip().removesuffix('\\').strip().replace('\\', '/')
                if value.startswith(ROOT.as_posix() + '/'):
                    path = Path(value);assert path.is_file(), value
                    compiled.add(path.relative_to(ROOT).as_posix());sources[path.relative_to(ROOT).as_posix()] = path
    save(a.output / 'build-members.json', pack(a.output / 'build-files.zip', metadata))
    save(a.output / 'object-members.json', pack(a.output / 'build-objects.zip', objects))
    source_rows = pack(a.output / 'execution-sources.zip', sources)
    save(a.output / 'source-members.json', source_rows)
    query = ''.join('HEAD:' + row['member'] + '\n' for row in source_rows).encode('utf-8')
    blobs = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT, input=query, capture_output=True, check=True).stdout
    position, dependencies = 0, []
    for row in source_rows:
        end = blobs.index(b'\n', position);fields = blobs[position:end].split()
        if fields[-1] == b'missing':
            prior = None;position = end + 1
        else:
            assert fields[1] == b'blob';size = int(fields[2]);prior = digest(blobs[end + 1:end + 1 + size]);position = end + size + 2
        raw_bytes = sources[row['member']].read_bytes()
        relation = 'new-or-untracked-metadata' if prior is None else ('byte-identical' if prior == row['sha256'] else
            ('crlf-to-lf' if digest(raw_bytes.replace(b'\r\n', b'\n')) == prior else 'changed-from-parent'))
        dependencies.append({'path': row['member'], 'copy_member': row['member'], 'execution_sha256': row['sha256'],
            'parent_git_blob_sha256': prior, 'relation': relation})
    assert position == len(blobs)
    models = {}
    for model in plan['models'].values():
        for row in [*model['models'], *[v for v in model['sidecars'] if v]]:
            path = Path(row['path']);assert digest(path.read_bytes()) == row['sha256']
            models[path.relative_to(Path('F:/Hackathon/projects/16-lut-color')).as_posix()] = path
    save(a.output / 'model-members.json', pack(a.output / 'models.zip', models))
    save(a.output / 'identity.json', {'parent_head': '7cf7f371979078bcfda7e2958ec9cf31c92df465',
        'date_asia_shanghai': '2026-10-24', 'libraries': plan['libraries'], 'checked_inputs': checked,
        'execution_dependencies': dependencies, 'actual_compiler_project_dependencies': sorted(compiled),
        'production_build_failure': {'return_code': 2, 'scope': 'DLL成功但原私有合同target缺channel-runtime头路径，失败源码/日志原件保留。'},
        'contract_repair': '独立v2仅补测试include路径，复用v1生产DLL；不重建生产库，不改已冻结质量wrapper。',
        'old_objects': '七旧pixel/bench对象逐字节同95，见old-objects；新compile_shared整体不相同，不声称原nonshared函数机器码完全相同。',
        'static_frame': {'create_workload_impl_bytes': 7568, 'new_shared_kernel_bytes': 240, 'old_cached_dispatch_bytes': 800,
            'scope': '实际GCC.su静态单函数帧，非跨调用峰值或性能归因。'},
        'performance_boundary': 'N1/10/100同场87/95/97双分母，1584实际SHA和全部失效；未知72448先见后消失，无法追溯CPU/归属，不称宿主绝对独占。',
        'postprocessing_sources': {p: digest((ROOT / p).read_bytes()) for p in ('scripts/archive_p16_shared_proven.py',
            'scripts/audit_p16_shared_proven_decimal.py')}})
    (a.output / 'README.md').write_text('''# 97隔离共享已证域路径的完整证据

同场87/95/97，N1真默认/N10低hint/N100高hint，48热与36冷metric、全部1584实际末组SHA/AA/12RSS保留。ordinary N10单线程纯apply对95时间-6.52%，最劣仍更快；同N连续create到首Out4对95有效慢5.0963%。不授全场50，不用95慢分母救87，不恢复旧资格。

raw-evidence.zip含完整质量/正式/partial/预检与未知72448复查/实际反汇编；build-files.zip含首build失败和独立合同修复的完整日志/receipt/flags/link/rsp/所有.su与.obj.d；build-objects.zip保存实际对象和core。execution-sources.zip保存执行原字节，identity区分父Git的CRLF/LF与新源；models.zip为两固定链去重模型。DLL/照片只绑定身份。

首构建生产DLL成功、合同target缺头失败；独立contract-v2只补测试include路径，原生产DLL未重建。质量56完整16M流、20安全cache/ID/palette快照、150私有uint64合同、10080有限/110拒绝/16独立u64/32照片SHA全过。保留旧15静态负证据，不以更少指令/同源或局部胜出称普遍优化。

离线复算：python scripts/audit_p16_shared_proven.py report/data/p16-shared-proven-v1/raw-evidence.zip。不加载DLL或重采。独立50位Decimal核84统计集/1176标量，全部判定一致；具体有效/失效和六档见中文阶段正文。
''', encoding='utf-8')
    save(a.output / 'manifest.json', {'files': [{'path': path.name, 'bytes': path.stat().st_size,
        'sha256': digest(path.read_bytes())} for path in sorted(a.output.iterdir()) if path.is_file()]})
    print(json.dumps({'output': str(a.output), 'raw_members': len(raw), 'source_members': len(source_rows),
        'build_members': len(metadata), 'object_members': len(objects), 'compiled_dependencies': len(compiled),
        'models': len(models), 'archive_files': len(list(a.output.iterdir()))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
