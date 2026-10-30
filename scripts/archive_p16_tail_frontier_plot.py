"""封存只读指标图及首次布局；所有ZIP成员回读，不执行模型或性能。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report/data/p16-tail-frontier-plot-20261024'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    versions = [ROOT / ('artifacts/p16-tail-frontier-plot-v' + str(v)) for v in (1, 2)]
    current = json.loads((versions[1] / 'data.json').read_text(encoding='utf-8'))
    before = json.loads((versions[0] / 'data.json').read_text(encoding='utf-8'))
    assert current == before and len(current['roles']) == 6
    for folder in versions:
        manifest = json.loads((folder / 'output-manifest.json').read_text(encoding='utf-8'))
        for name, expected in manifest.items():
            raw = (folder / name).read_bytes()
            assert len(raw) == expected['bytes'] and digest(raw) == expected['sha256']
    sources = [ROOT / n for n in (
        'experiments/p16-tail-frontier-plot-v1.md',
        'scripts/plot_p16_tail_frontier.py', 'scripts/plot_p16_tail_frontier_v2.py',
        'scripts/prepare_p16_tail_frontier_layout_v2.py',
        'scripts/archive_p16_tail_frontier_plot.py', 'scripts/audit_p16_tail_frontier_plot_git.py',
        'docs/stages/2026-10-24-p16-tail-frontier-plot.md')]
    prior_files = [ROOT / n for n in (
        'report/data/p16-cinema-current-full-quality-20261024/results-v2.json',
        'report/data/p16-cinema-max48-pareto-quality-20261024/results.json',
        'report/data/p16-cinema-second-nodes-v1/max_first-accuracy.json',
        'report/data/p16-cinema-second-nodes-v1/p99_first-accuracy.json')]
    zips = {}
    for filename, members in [('sources.zip', sources), ('raw.zip',
            [p for folder in versions for p in folder.iterdir() if p.is_file()] + prior_files)]:
        index = {}
        with zipfile.ZipFile(OUT / filename, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in members:
                name = path.relative_to(ROOT).as_posix()
                raw = path.read_bytes()
                archive.writestr(name, raw)
                index[name] = {'bytes': len(raw), 'sha256': digest(raw)}
        with zipfile.ZipFile(OUT / filename) as archive:
            assert archive.testzip() is None and len(archive.namelist()) == len(index)
            for name, expected in index.items():
                raw = archive.read(name)
                assert len(raw) == expected['bytes'] and digest(raw) == expected['sha256']
        zips[filename] = dict(sha256=digest((OUT / filename).read_bytes()), members=index)
    for name in ('data.json', 'data.md', 'tail-frontier.png', 'tail-frontier.svg'):
        shutil.copyfile(versions[1] / name, OUT / name)
    save(OUT / 'manifest.json', dict(purpose=__doc__, zip_files=zips,
        exact_same_v1_v2_metrics=True, visual_qa='V1标签重叠保留；独立V2只改标注位置/画布高度，经PNG目视无重叠裁切。',
        native_calls=0, performance_samples=0, roles=6, populations=2,
        font='只记录Windows字体SHA，不分发字体二进制；SVG轮廓与PNG是已渲染图形。'))
    files = sources + sorted(OUT.iterdir())
    whitelist = {p.relative_to(ROOT).as_posix(): dict(bytes=p.stat().st_size, sha256=digest(p.read_bytes()))
                 for p in files if p.is_file()}
    save(OUT / 'git-whitelist.json', dict(files=whitelist,
        scope='本文件自身另列于暂存命令；白名单不含AGENTS、其它研究或性能静态稿。'))
    print(json.dumps({'files_excluding_whitelist': len(whitelist),
        'zip_members': sum(len(v['members']) for v in zips.values()), 'metrics_identical': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
