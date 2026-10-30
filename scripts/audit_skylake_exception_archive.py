"""标准库核对修订23归档成员与测量源SHA，不重做原生计算。"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不得覆盖旧审计')
    manifest = read(args.archive/'manifest.json')
    for name, spec in manifest['files'].items():
        p = args.archive/name
        if p.stat().st_size != spec['bytes'] or digest(p) != spec['sha256']:
            raise ValueError('归档成员不同：'+name)
    members = 0; mappings = []; snapshots = 0
    for zpath in sorted(args.archive.rglob('measured-source.zip')):
        run_path = zpath.parent/('build.json' if (zpath.parent/'build.json').exists() else 'run.json')
        if not run_path.exists():
            raise ValueError('测量源缺少身份回执：'+str(zpath))
        run = read(run_path)
        with zipfile.ZipFile(zpath) as z:
            if z.testzip() is not None:
                raise ValueError('ZIP校验失败')
            for name, sha in run['source_sha256'].items():
                logical = name.replace('\\', '/')
                options = [n for n in z.namelist() if n == logical]
                if not options and ':/' in logical:
                    # 初版packed验证器把__file__绝对路径记入run；保存原记录并显式映射。
                    suffix = logical.split('/16-lut-color/', 1)[-1]
                    options = [n for n in z.namelist() if n.endswith('/'+suffix)]
                    mappings.append({'archive': zpath.relative_to(args.archive).as_posix(),
                                     'recorded': name, 'member': options[0] if len(options) == 1 else options})
                if len(options) != 1 or hashlib.sha256(z.read(options[0])).hexdigest() != sha:
                    raise ValueError('测量源成员不同：'+name)
                members += 1
        snapshots += 1
    full = read(args.archive/'full/results.json')
    linux = read(args.archive/'linux-full/results.json')
    packed = read(args.archive/'packed-contract/results.json')
    perf = read(args.archive/'performance/results.json')
    assert full['pass'] and linux['pass'] and packed['pass'] and perf['accepted_on_this_host']
    assert all(v == 16777216 for v in linux['full_domain_pixels_per_configuration'].values())
    assert len(linux['full_domain_pixels_per_configuration']) == 12
    for r in read(args.archive/'audit/results.json')['paired']:
        assert r['apply_throughput_gain_percent'] >= 50 and r['copy_apply_throughput_gain_percent'] >= 50
    result = {'pass': True, 'purpose': __doc__, 'manifest_files': len(manifest['files']),
        'source_snapshots': snapshots, 'source_members': members, 'preserved_absolute_source_mappings': mappings,
        'new_native_calls': 0, 'new_performance_calls': 0,
        'scope': '归档完整性与既有回执一致；不把审计当成新数值/性能测试'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
