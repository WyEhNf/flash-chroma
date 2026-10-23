"""补充核查289编译器真实依赖；保留早先只识别正斜杠路径的收据。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'artifacts/p16-direct-u10-build-v1'
OUTPUT = BUILD / 'dependency-audit-v2.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUTPUT.exists():
        raise ValueError('不覆盖第二版依赖审计')
    frozen_path = ROOT / 'artifacts/p16-direct-u10-frozen-v1/frozen.json'
    frozen = json.loads(frozen_path.read_text(encoding='utf-8'))
    dependencies = {}
    files = sorted(BUILD.rglob('*.obj.d'))
    if not files:
        raise ValueError('没有编译器依赖原件')
    for depfile in files:
        for line in depfile.read_text(encoding='utf-8').splitlines()[1:]:
            token = line.strip()
            if token.endswith(' \\'):
                token = token[:-2].rstrip()
            path = Path(token)
            if not path.is_absolute():
                path = BUILD / path
            path = path.resolve()
            try:
                relative = path.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if not path.is_file():
                raise ValueError('依赖不存在：' + str(path))
            actual = sha(path)
            if relative not in frozen['sources'] or frozen['sources'][relative]['sha256'] != actual:
                raise ValueError('实际依赖没有在编译前冻结：' + relative)
            dependencies[relative] = actual
    for relative, row in frozen['sources'].items():
        if sha(ROOT / relative) != row['sha256']:
            raise ValueError('构建后冻结源改变：' + relative)
    result = {'passed': True, 'frozen_sha256': sha(frozen_path),
              'compiler_dependency_files': {str(p.relative_to(BUILD)): sha(p) for p in files},
              'actual_repository_dependencies_sha256': dict(sorted(dependencies.items())),
              'actual_repository_dependency_count': len(dependencies),
              'frozen_sources_unchanged': len(frozen['sources']),
              'previous_receipt': str(BUILD / 'build-receipt.json'),
              'correction': '第一版只识别F:/路径，漏列F:\\路径；本版逐行兼容两种，旧收据原样保留。',
              'performance_calls': 0}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'dependencies': len(dependencies), 'dependency_files': len(files)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
