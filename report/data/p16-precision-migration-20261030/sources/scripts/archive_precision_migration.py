"""归档本阶段原始回执、冻结模型与执行源码，或只读核对归档。"""
import argparse
import hashlib
import json
import platform
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'report/data/p16-precision-migration-20261030'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def pe_sections(path):
    data = path.read_bytes()
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    count = struct.unpack_from('<H', data, pe+6)[0]
    optional = struct.unpack_from('<H', data, pe+20)[0]
    result = {}
    for i in range(count):
        at = pe+24+optional+40*i
        name = data[at:at+8].rstrip(b'\0').decode('ascii')
        size, offset = struct.unpack_from('<II', data, at+16)
        result[name] = hashlib.sha256(data[offset:offset+size]).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--artifacts', type=Path, default=ROOT/'artifacts/precision')
    parser.add_argument('--delivery', type=Path, default=Path('F:/Hackathon/极速焕彩测试框架/FlashChromaHistory'))
    args = parser.parse_args()
    if args.verify:
        manifest = read(DEST/'manifest.json')
        for name, item in manifest['files'].items():
            path = DEST/name
            assert path.stat().st_size == item['bytes'] and digest(path) == item['sha256'], name
        print(f"归档验证通过：{len(manifest['files'])}份文件")
        return
    if DEST.exists():
        raise FileExistsError('归档已存在，拒绝覆盖')
    artifacts = args.artifacts
    final = read(artifacts/'final/fit.json'); photos = read(artifacts/'final/photos.json')
    independent = read(artifacts/'independent.json')
    assert final['result']['sse'] == independent['domain']['sse']
    previous = ROOT/'report/data/p16-framework-20261029/evidence/framework-grid-confirmation-20261030'
    baseline = next(c for c in read(previous/'native/results.json')['candidates'] if c['id']=='chain-framework')
    executed = read(previous/'execution.json')['executed_images']
    photo_manifest = read(Path('F:/Hackathon/worktrees/p16-frontier-header-20261027/artifacts/framework-photos-100-20261029/manifest.json'))
    assert [x['sha256'] for x in executed] == [x['raw_sha256'] for x in photo_manifest['images']]
    differences = [x['quality']['mean']-y['mean'] for x, y in zip(photos['images'], baseline['quality'])]
    delivery_log = (artifacts/'delivery-run.log').read_text(encoding='utf-8-sig')
    lines = [x[len('HistoryReport='):] for x in delivery_log.splitlines() if x.startswith('HistoryReport=')]
    assert len(lines) == 1 and len([x for x in delivery_log.splitlines() if x.startswith('Img:')]) == 4
    actual = json.loads(lines[0]); assert actual['result'] == final['result']
    old_sections = pe_sections(artifacts/'benchmark-final.exe')
    formatted_sections = pe_sections(artifacts/'benchmark-formatted.exe')
    assert old_sections['.text'] == formatted_sections['.text']
    DEST.mkdir(parents=True)
    for name in ('run1', 'final', 'run1-sources', 'final-sources'):
        for path in (artifacts/name).iterdir():
            if path.is_file() and path.name not in ('domain.rgb', 'progress.json'):
                target = DEST/name/path.name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
    for pattern in ('*.log', '*.py', 'independent.json', 'collaboration.json', 'delivery-check.json'):
        for path in artifacts.glob(pattern):
            shutil.copyfile(path, DEST/path.name)
    sources = ['framework/flash_chroma_adapter.hpp', 'framework/fit_experiment.hpp', 'framework/preference_selection.hpp',
               'framework/benchmark.cpp', 'framework/precision_benchmark.cpp', 'framework/precision_geometry.hpp',
               'framework/precision_search.hpp', 'framework/precision_fit.hpp', 'framework/precision_pipeline.hpp',
               'scripts/install_framework.py', 'scripts/check_framework_delivery.py', 'scripts/verify_precision_migration.py',
               'scripts/archive_precision_migration.py', 'tests/framework_precision_contract.cpp',
               'tests/test_framework_preferences.py', 'single_header/CMakeLists.txt']
    for name in sources:
        target = DEST/'sources'/name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT/name, target)
    for name in ('main.cpp', 'flash_chroma_framework.hpp', 'run.ps1', 'README.md', 'source-manifest.json', 'build-config.json'):
        target = DEST/'delivery'/name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(args.delivery/name, target)
    write(DEST/'comparison.json', dict(domain_before=final['baseline'], domain_after=final['result'],
          photo_mean_before=sum(x['mean'] for x in baseline['quality'])/100, photo_mean_after=photos['mean'],
          worst_image_mean_before=baseline['worst_image_mean'], worst_image_mean_after=photos['worst_image_mean'],
          same_100_image_sha256=True, improved=sum(x<0 for x in differences), regressed=sum(x>0 for x in differences),
          per_image_mean_delta=differences, baseline_results_sha256=digest(previous/'native/results.json'),
          baseline_execution_sha256=digest(previous/'execution.json'), candidate_steps=len(final['steps']),
          accepted_steps=sum(x['accepted'] for x in final['steps']), delivery_result=actual['result']))
    write(DEST/'execution.json', dict(platform=platform.platform(), cpu='AMD Ryzen 9 8945HX', python=platform.python_version(),
          compiler='MinGW GCC 15.2.0', flags=['-O3', '-DNDEBUG', '-std=c++17', '-static'], openmp=0, threads=1,
          scope='算法单线程；正确性/拟合验证期间可并行构建其他合同。不授予稳定性能资格。',
          prepare_seconds_observation=read(artifacts/'final/model.json')['prepare_seconds'], peak_rss_measured=False,
          executed_sources='final-sources', formatted_sources='sources', final_executable_sha256=digest(artifacts/'benchmark-final.exe'),
          formatted_executable_sha256=digest(artifacts/'benchmark-formatted.exe'), sections_before=old_sections,
          sections_after=formatted_sections, code_section_equal=True,
          delivery_executable_sha256=digest(args.delivery/'main_flash_chroma.exe'), source_hashes={n:digest(ROOT/n) for n in sources}))
    write(DEST/'manifest.json', dict(schema='precision_migration_archive_v1',
          files={p.relative_to(DEST).as_posix():dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(DEST.rglob('*')) if p.is_file()}))
    print(f'已归档：{DEST}')


if __name__ == '__main__':
    main()
