"""按原字节归档两组发射诊断；只查文件，不加载候选库。"""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    folders = {
        'raw': 'artifacts/skylake-dispatch-diagnostic-v1',
        'probe': 'artifacts/skylake-dispatch-diagnostic-probe-v1',
        'preflight': 'artifacts/skylake-dispatch-diagnostic-preflight-v1',
        'independent': 'artifacts/skylake-dispatch-diagnostic-independent-v1',
    }
    for target, source in folders.items():
        if (HERE/target).exists():
            raise ValueError('不得覆盖已归档原件')
        shutil.copytree(ROOT/source, HERE/target)
    policy_path = ROOT/'experiments/skylake-dispatch-diagnostic-v2.json'
    policy = json.loads(policy_path.read_text(encoding='utf-8'))
    dependencies = {}
    for key in ('probe', 'pinning_probe', 'plan', 'build', 'full', 'validation',
                'library', 'driver', 'photos'):
        item = policy[key]
        assert digest(ROOT/item['path']) == item['sha256'], key
        dependencies[key] = item
    for path, expected in policy['source_hashes'].items():
        assert digest(ROOT/path) == expected, path
    result = json.loads((HERE/'raw/results.json').read_text(encoding='utf-8'))
    audit = json.loads((HERE/'independent/results.json').read_text(encoding='utf-8'))
    assert result['pass'] and audit['pass']
    assert result['policy_sha256'] == digest(policy_path)
    files = {p.relative_to(HERE).as_posix(): {
        'bytes': p.stat().st_size, 'sha256': digest(p)}
        for folder in folders for p in sorted((HERE/folder).rglob('*')) if p.is_file()}
    output = {
        'schema': 1, 'files': files, 'policy_sha256': digest(policy_path),
        'dependencies': dependencies, 'source_hashes': policy['source_hashes'],
        'libraries': '复用PR71档案中的冻结78与driver，不重复复制二进制',
        'scope': '保存全部诊断、probe、执行前修正和独立解码原件；无新像素调用或吞吐验收',
    }
    (HERE/'manifest.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'pass': True, 'files': len(files), 'candidate_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
