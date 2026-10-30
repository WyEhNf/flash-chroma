"""封存native页指针构建/有限/完整质量与所有机械STOP，不含正式性能。"""
import argparse
import hashlib
import io
from pathlib import Path
import subprocess
import zipfile
from study_memory_rom import ROOT, read, save, sha

PLANS = tuple(ROOT / 'experiments' / name for name in (
    'page-id16-native-pages-build-v1.json', 'page-id16-native-pages-observer-v2.json',
    'page-id16-native-pages-finite-v1.json', 'page-id16-native-pages-finite-v2.json',
    'page-id16-native-pages-full-v1.json'))


def package(path, files):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, source in sorted(files.items()):
            archive.write(source, name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check-index', action='store_true')
    args = parser.parse_args()
    copies = {
        'finite-audit.json': ROOT / 'artifacts/p16-page-native-pages-finite-v2/independent-audit-v3.json',
        'full-result.json': ROOT / 'artifacts/p16-page-native-pages-full-v1/quality/results.json',
        'full-audit.json': ROOT / 'artifacts/p16-page-native-pages-full-v1/independent-audit.json',
        'build-result.json': ROOT / 'artifacts/p16-page-native-pages-observer-v2/build/build.json',
    }
    if args.check_index:
        manifest = read(args.output / 'manifest.json')
        paths = [args.output / name for name in manifest['files']] + [args.output / 'manifest.json']
        request = '\n'.join(':' + path.resolve().relative_to(ROOT).as_posix() for path in paths) + '\n'
        stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], input=request.encode(), cwd=ROOT))
        members = 0
        for path in paths:
            header = stream.readline().split()
            if len(header) != 3:
                raise AssertionError('质量发布件未暂存')
            raw = stream.read(int(header[2]))
            if stream.read(1) != b'\n' or raw != path.read_bytes():
                raise AssertionError('暂存字节被换行转换')
            if path.name in manifest['files']:
                item = manifest['files'][path.name]
                if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
                    raise AssertionError('manifest大小/SHA不符')
            if path.suffix == '.zip':
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    if archive.testzip():
                        raise AssertionError('ZIP CRC错误')
                    members += len(archive.infolist())
        with zipfile.ZipFile(args.output / 'frozen-source.zip') as archive:
            for plan in PLANS:
                if archive.read(plan.relative_to(ROOT).as_posix()) != plan.read_bytes():
                    raise AssertionError('冻结计划副本不同')
                for name, expected in read(plan)['source_sha256'].items():
                    if hashlib.sha256(archive.read(name)).hexdigest() != expected or sha(ROOT / name) != expected:
                        raise AssertionError('冻结执行源码不同')
        for name, original in copies.items():
            if (args.output / name).read_bytes() != original.read_bytes():
                raise AssertionError('发布摘要不是原件字节')
        save(args.output / 'git-byte-audit.json', dict(passed=True, files=len(paths), zip_members=members,
            scope='暂存原字节/manifest/CRC/冻结执行源与真实摘要核对，没有native重采或性能授档。'))
        print(dict(passed=True, files=len(paths), zip_members=members), flush=True)
        return
    args.output.mkdir(parents=True, exist_ok=False)
    raw = {}
    for label in ('p16-page-native-pages-v1', 'p16-page-native-pages-observer-v2',
                  'p16-page-native-pages-finite-v1', 'p16-page-native-pages-finite-v2',
                  'p16-page-native-pages-full-v1'):
        directory = ROOT / 'artifacts' / label
        for path in directory.rglob('*'):
            if path.is_file():
                raw[label + '/' + path.relative_to(directory).as_posix()] = path
    package(args.output / 'experiment-raw.zip', raw)
    sources = {}
    for plan in PLANS:
        sources[plan.relative_to(ROOT).as_posix()] = plan
        for name in read(plan)['source_sha256']:
            sources[name] = ROOT / name
    for name in ('scripts/archive_page_id16_native_pages_quality.py',
                 'scripts/audit_page_id16_native_pages_full.py',
                 'scripts/audit_page_id16_native_pages_finite_v2.py'):
        sources[name] = ROOT / name
    package(args.output / 'frozen-source.zip', sources)
    for name, original in copies.items():
        (args.output / name).write_bytes(original.read_bytes())
    save(args.output / 'manifest.json', dict(purpose=__doc__,
        files={path.name: dict(bytes=path.stat().st_size, sha256=sha(path)) for path in args.output.iterdir()},
        references='原P4 ROM a953eef0…沿report/data/p16-page-id16-v1保存，不重导出。新包含唯一Clang对象、两DLL与依赖、实码、原false gate、finite V1 fixture STOP、V2全部raw/两次审计STOP及V3通过、5full/百图raw。未包含新性能/WASM，不能给速度档。'))
    print(dict(output=str(args.output), bytes=sum(path.stat().st_size for path in args.output.iterdir())), flush=True)


if __name__ == '__main__':
    main()
