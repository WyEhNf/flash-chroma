"""96归档v2补原repo照片manifest来源；保留v1归档失败，未重测。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TAIL = Path('F:/Hackathon/worktrees/p16-tail-20261023')
ORIGINAL = Path('F:/Hackathon/projects/16-lut-color')


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


def git_blobs(root, ref, paths):
    queries = ''.join(ref + ':' + p + '\n' for p in paths).encode('utf-8')
    raw = subprocess.run(['git', 'cat-file', '--batch'], cwd=root, input=queries,
        capture_output=True, check=True).stdout
    position, result = 0, {}
    for path in paths:
        end = raw.index(b'\n', position)
        fields = raw[position:end].split()
        if fields[-1] == b'missing':
            result[path] = None
            position = end + 1
        else:
            assert fields[1] == b'blob'
            size = int(fields[2])
            result[path] = digest(raw[end + 1:end + 1 + size])
            position = end + size + 2
    assert position == len(raw)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('96归档不覆盖')
    a.output.mkdir(parents=True)
    perf = ROOT / 'artifacts/p16-omp-policy-performance-v1'
    quality = ROOT / 'artifacts/p16-omp-policy-quality-v1'
    plan = json.loads((perf / 'executed-plan.json').read_text(encoding='utf-8'))
    assert digest((perf / 'executed-plan.json').read_bytes()) == '778d1bd210aa843e96460e7fdebd105fede380fbd16a1510f804250963f8d9b1'
    for phase in (quality, perf):
        output = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/audit_p16_omp_policy.py'), str(phase)],
            cwd=ROOT, capture_output=True, text=True, check=True)
        receipt = json.loads(output.stdout)
        target = phase / 'offline-audit.json'
        if target.exists():
            assert json.loads(target.read_text(encoding='utf-8')) == receipt
        else:
            save(target, receipt)
    assert json.loads((perf / 'decimal-audit.json').read_text(encoding='utf-8'))['statistic_sets'] == 72
    for name in ('executed-plan.json', 'results.json', 'offline-audit.json', 'decimal-audit.json'):
        shutil.copyfile(perf / name, a.output / name)
    shutil.copyfile(quality / 'results.json', a.output / 'quality.json')
    shutil.copyfile(quality / 'offline-audit.json', a.output / 'quality-audit.json')

    raw = {}
    for label, folder in (('performance', perf), ('quality', quality)):
        raw.update({label + '/' + f.relative_to(folder).as_posix(): f for f in folder.rglob('*') if f.is_file()})
    for name in ('p16-omp-policy-performance-preflight-v1.json', 'p16-omp-policy-preflight-git-recheck-v1.json',
            'p16-omp-policy-quality-v1.log'):
        raw['preflight-and-log/' + name] = ROOT / 'artifacts' / name
    helper_archive = TAIL / 'report/data/p16-omp-affinity-control-v1'
    for f in helper_archive.iterdir():
        if f.is_file():
            raw['helper-root-77cdbfc/' + f.name] = f
    failure = ROOT / 'artifacts/p16-omp-policy-archive-failure-v1'
    raw.update({'archive-failure-v1/' + f.relative_to(failure).as_posix(): f
        for f in failure.rglob('*') if f.is_file()})
    save(a.output / 'raw-members.json', pack(a.output / 'raw-evidence.zip', raw))

    checked, sources = [], {}
    for row in plan['sources']:
        path = Path(row['path'])
        assert digest(path.read_bytes()) == row['sha256'], str(path)
        included = path.suffix.lower() not in ('.dll', '.exe', '.png')
        checked.append({**row, 'copy_in_source_archive': included})
        if included:
            if path.is_relative_to(ROOT):
                member = 'speed/' + path.relative_to(ROOT).as_posix()
            elif path.is_relative_to(TAIL):
                member = 'helper-tail/' + path.relative_to(TAIL).as_posix()
            elif path.is_relative_to(ORIGINAL):
                member = 'original-input/' + path.relative_to(ORIGINAL).as_posix()
            else:
                raise AssertionError(str(path))
            sources[member] = path
    own = [ROOT / 'experiments' / n for n in ('p16-omp-policy-quality-v1.json', 'p16-omp-policy-performance-v1.json')]
    own += [ROOT / 'scripts' / n for n in ('archive_p16_omp_policy.py', 'archive_p16_omp_policy_v2.py', 'audit_p16_omp_policy_decimal.py')]
    for path in own:
        sources['speed/' + path.relative_to(ROOT).as_posix()] = path
    source_rows = pack(a.output / 'execution-sources.zip', sources)
    speed_paths = [r['member'].removeprefix('speed/') for r in source_rows if r['member'].startswith('speed/')]
    tail_paths = [r['member'].removeprefix('helper-tail/') for r in source_rows if r['member'].startswith('helper-tail/')]
    input_paths = [r['member'].removeprefix('original-input/') for r in source_rows if r['member'].startswith('original-input/')]
    parents = {'speed': git_blobs(ROOT, 'HEAD', speed_paths), 'helper-tail': git_blobs(TAIL, '77cdbfc', tail_paths),
        'original-input': git_blobs(ORIGINAL, 'HEAD', input_paths)}
    dependencies = []
    for row in source_rows:
        origin, path = row['member'].split('/', 1)
        prior = parents[origin][path]
        execution = sources[row['member']].read_bytes()
        relation = 'new-or-untracked-metadata' if prior is None else ('byte-identical' if prior == row['sha256'] else
            ('crlf-to-lf' if digest(execution.replace(b'\r\n', b'\n')) == prior else 'changed-from-parent'))
        dependencies.append({'origin': origin, 'path': path, 'copy_member': row['member'], 'bytes': row['bytes'],
            'execution_sha256': row['sha256'], 'parent_git_blob_sha256': prior, 'relation': relation})
    save(a.output / 'source-members.json', source_rows)
    models = {}
    for model in plan['models'].values():
        for row in [*model['models'], *[v for v in model['sidecars'] if v]]:
            path = Path(row['path'])
            assert digest(path.read_bytes()) == row['sha256']
            models[path.relative_to(Path('F:/Hackathon/projects/16-lut-color')).as_posix()] = path
    save(a.output / 'model-members.json', pack(a.output / 'models.zip', models))
    save(a.output / 'identity.json', {'date_asia_shanghai': '2026-10-24',
        'parent_speed_head': '9e49ac10f61dc68864b5372caf70ae7749a050bd', 'helper_source_commit': '77cdbfc',
        'checked_inputs': checked, 'execution_dependencies': dependencies,
        'libraries': plan['libraries'], 'affinity_helper': plan['affinity_helper'], 'libgomp': plan['libgomp'],
        'independent_quality_proof': plan['independent_quality_proof'],
        'performance_plan_sha256': digest((perf / 'executed-plan.json').read_bytes()),
        'postprocessing_sources': {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in own[2:]},
        'scope': 'sources中207项逐一核执行原字节；源和metadata打包，DLL/EXE/照片只存身份。外部helper源对77cdbfc查Git，speed源对父HEAD查Git，原repo输入manifest独立来源查Git，CRLF/LF分别列，不将外部artifact冒充当前树Git源码。',
        'method': '逐TID U/P只用于独立默认N1诊断，不修改三库、模型、阈值或热核；不恢复旧阶段资格；setup只描述不冷配对。'})
    (a.output / 'README.md').write_text('''# 96逐线程绑定的独立原因诊断证据

唯一质量与唯一正式均8fresh进程，T1/T4分开、同进程6句柄/source/work不变，UPPU/PUUP与四角色镜像。正式warm2/63/AA63，32同policy角色比、24同句柄P/U、16交互和全部失败AA保留；1200实际末组SHA全过。逐线程绑定未证明能普遍消除漂移，不追授92/94/95或其他旧阶段资格。

raw-evidence.zip保存全部质量/正式JSON与partial、预检、git瞬时进程复检、质量日志，以及根代理77cdbfc helper完整已发布原件（含v1构建元数据失败与2worker质量失败）。6参数拒绝只复用根代理已有证据，不称96重新执行。execution-sources.zip保存执行源和metadata，identity逐项核207冻结输入并区分外部helper和本树父Git原字节。models.zip保存两固定链去重模型。DLL/EXE/照片只保存SHA身份，不打包。

事后归档v1因来源分类漏原repo照片manifest而停止，其源码、部分产物及失败回执保留在raw的archive-failure-v1。v2仅补该metadata来源，未改已冻结driver/support/audit、未重跑质量或性能。

python scripts/audit_p16_omp_policy.py artifacts/p16-omp-policy-performance-v1 可离线重算原始数据及所有线程endpoint；script不加载DLL。独立50位Decimal另核72统计集、2176标量，误差<1e-14；其源明确属于事后离线审计，不假称预冻结执行源。具体有效/失效和所有最劣档见阶段中文正文。
''', encoding='utf-8')
    save(a.output / 'manifest.json', {'files': [{'path': f.relative_to(a.output).as_posix(),
        'bytes': f.stat().st_size, 'sha256': digest(f.read_bytes())} for f in sorted(a.output.rglob('*')) if f.is_file()]})
    print(json.dumps({'output': str(a.output), 'checked_frozen_inputs': len(checked), 'source_members': len(source_rows),
        'raw_members': len(raw), 'model_members': len(models), 'archive_files': len(list(a.output.iterdir()))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
