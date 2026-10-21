"""归档60单次构建、全色域和PMU原件；不得覆盖。"""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
NAMES = ('skylake-chroma-delta-linux-build-v1', 'skylake-chroma-delta-static-v1',
         'skylake-chroma-delta-linux-full-v1', 'skylake-chroma-delta-pmu-v1')
BUILD = ('build-log.json', 'build.json', 'compile_commands.json',
         'libjshc_skylake_chroma_delta.so', 'libjshc_skylake_reference.so',
         'libraries-Release.json', 'measured-source.zip')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for name in NAMES:
        dst = HERE / name
        src = ROOT / 'artifacts' / name
        if not dst.exists():
            if name.endswith('linux-build-v1'):
                dst.mkdir()
                for filename in BUILD:
                    shutil.copy2(src / filename, dst / filename)
            else:
                shutil.copytree(src, dst)
        if name.endswith('linux-build-v1') and not (dst / 'build-intermediates.zip').exists():
            with zipfile.ZipFile(dst / 'build-intermediates.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(src.rglob('*')):
                    if path.is_file() and path.name not in BUILD:
                        archive.write(path, path.relative_to(src).as_posix())
    files = {}
    for name in NAMES:
        paths = ([HERE / name / x for x in (*BUILD, 'build-intermediates.zip')]
                 if name.endswith('linux-build-v1') else sorted((HERE / name).rglob('*')))
        for path in paths:
            if path.is_file():
                rel = path.relative_to(HERE).as_posix()
                files[rel] = {'bytes': path.stat().st_size, 'sha256': sha(path)}
    (HERE / 'manifest.json').write_text(json.dumps({'schema': 1, 'files': files}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    records = json.loads((HERE / 'skylake-chroma-delta-pmu-v1/results.json').read_text(encoding='utf-8'))['records']
    by = {(x['variant'], x['requested_threads']): x for x in records}
    ratios = {str(t): by[('chroma_delta60', t)]['cycles_per_pixel'] / by[('reference40', t)]['cycles_per_pixel'] for t in (1, 4)}
    full = json.loads((HERE / 'skylake-chroma-delta-linux-full-v1/results.json').read_text(encoding='utf-8'))
    audit = {'full_rgb8_pass': full['pass'], 'independent_table_colors': full['independent_table_colors'],
             'finite_comparisons': full['finite_backend_offset_comparisons'],
             'cycle_ratios': ratios, 'screen': {'1t_max': 0.95, '4t_max': 1.05},
             'screen_pass': ratios['1'] <= 0.95 and ratios['4'] <= 1.05,
             'all_counters_unmultiplexed': all(x['multiplexing_acceptable'] for x in records),
             'full_wallclock_executed': False,
             'note': '仅离线复核冻结证据；单线程筛查失败，未运行整轮墙钟'}
    (HERE / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(files), 'ratios': ratios, 'screen_pass': audit['screen_pass']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
