"""98纯模型结构/地址普查按原字节平铺归档；不压缩、不重算颜色或重测。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('98原件归档不覆盖')
    a.output.mkdir(parents=True)
    structure = json.loads((ROOT/'experiments/p16-first-structure-v1.json').read_text(encoding='utf-8'))
    stencil = json.loads((ROOT/'experiments/p16-node-tiling-census-v1.json').read_text(encoding='utf-8'))
    for plan, script in ((structure, 'census_p16_first_structure.py'), (stencil, 'census_p16_node_tiling.py')):
        assert sha((ROOT/'scripts'/script).read_bytes()) == plan['script_sha256']
    sources = {}
    for label, directory in (('structure', 'p16-first-structure-v1'), ('stencil', 'p16-node-tiling-census-v1')):
        for name in ('executed-plan.json', 'results.json'):
            sources[f'{label}-{name}'] = ROOT/'artifacts'/directory/name
    sources['independent-check.json'] = ROOT/'artifacts/p16-structure-independent-check-v1.json'
    check = json.loads(sources['independent-check.json'].read_text(encoding='utf-8'))
    assert check['passed'] and check['native_calls'] == check['performance_calls'] == 0
    models = {}
    for row in [structure['model'], *stencil['models']]:
        path = Path(row['path']);assert sha(path.read_bytes()) == row['sha256']
        models[row['sha256']] = path
    for digest, path in models.items():
        sources[f'models/{digest}.slut'] = path
    dependency_paths = [Path(row['path']) for row in structure['code_sources']]
    for row in structure['code_sources']:
        assert sha(Path(row['path']).read_bytes()) == row['sha256']
    for path in dependency_paths:
        sources['reference-sources/' + path.relative_to(ROOT).as_posix()] = path
    for name in ('census_p16_first_structure.py', 'census_p16_node_tiling.py', 'audit_p16_structure_census.py', 'archive_p16_structure_census.py'):
        sources['post-and-executed-sources/scripts/' + name] = ROOT/'scripts'/name
    rows = []
    for name, path in sorted(sources.items()):
        target = a.output/name;target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        raw = path.read_bytes();assert target.read_bytes() == raw
        rows.append({'member': name, 'bytes': len(raw), 'sha256': sha(raw), 'source_path': str(path)})
    dependencies = []
    paths = dependency_paths + [ROOT/'scripts'/n for n in ('census_p16_first_structure.py', 'census_p16_node_tiling.py', 'audit_p16_structure_census.py')]
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        old = subprocess.run(['git', 'show', 'HEAD:' + relative], cwd=ROOT, capture_output=True)
        assert old.returncode in (0, 128)
        dependencies.append({'path': relative, 'execution_sha256': sha(path.read_bytes()),
            'parent_git_blob_sha256': sha(old.stdout) if old.returncode == 0 else None,
            'role': '只读数学来源；未运行原生core' if path in dependency_paths else '纯模型执行或后加独立审计'})
    identity = {'parent_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'archive_script_sha256': sha(Path(__file__).read_bytes()), 'plain_files': rows,
        'execution_dependencies': dependencies, 'native_calls': 0, 'performance_calls': 0,
        'scope': '两次已冻结单版纯模型普查；独立审计与本归档为事后检查，不伪称预冻结闭包；无ZIP、原生加载或性能。'}
    (a.output/'identity.json').write_text(json.dumps(identity, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for row in rows:
        assert sha((a.output/row['member']).read_bytes()) == row['sha256']
    print(json.dumps({'plain_exact_files': len(rows), 'parent_head': identity['parent_head'], 'all_sha256_passed': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
