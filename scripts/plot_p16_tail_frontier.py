"""把既有精度JSON绘成聚合比较图；不调用LUT、不重新计时或拟合。"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/p16-tail-frontier-plot-v1'
SOURCES = {
    'current': ROOT / 'report/data/p16-cinema-current-full-quality-20261024/results-v2.json',
    'max48': ROOT / 'report/data/p16-cinema-max48-pareto-quality-20261024/results.json',
    'max_first': ROOT / 'report/data/p16-cinema-second-nodes-v1/max_first-accuracy.json',
    'p99_first': ROOT / 'report/data/p16-cinema-second-nodes-v1/p99_first-accuracy.json',
}
FIELDS = ('mean', 'rms', 'p99', 'max', 'cvar_1pct')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, value):
    path = OUT / name
    if path.exists():
        raise FileExistsError('图导出不覆盖：' + str(path))
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def pick(row):
    result = {key: float(row[key]) for key in FIELDS}
    result['n'] = int(row['n'])
    assert all(math.isfinite(result[k]) for k in FIELDS)
    assert result['mean'] <= result['rms'] <= result['max'] and result['p99'] <= result['max']
    result['max_squared'] = round(result['max'] ** 2)
    result['p99_squared'] = round(result['p99'] ** 2)
    assert abs(result['max'] ** 2 - result['max_squared']) < 1e-10
    assert abs(result['p99'] ** 2 - result['p99_squared']) < 1e-10
    return result


def equal(left, right):
    a, b = pick(left), pick(right)
    assert a == b, (a, b)


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    import numpy as np
    OUT.mkdir(parents=True, exist_ok=False)
    font = Path('C:/Windows/Fonts/msyh.ttc')
    assert font.is_file()
    identities = {str(path): sha(path) for path in [*SOURCES.values(), Path(__file__),
        ROOT / 'experiments/p16-tail-frontier-plot-v1.md', font]}
    save('identity.json', dict(purpose=__doc__, inputs_sha256=identities, python=sys.version,
        platform=platform.platform(), matplotlib=matplotlib.__version__, numpy=np.__version__,
        native_calls=0, performance_samples=0))
    docs = {name: json.loads(path.read_text(encoding='utf-8')) for name, path in SOURCES.items()}
    current, max48 = docs['current'], docs['max48']
    for population in ('cube', 'photos'):
        for role in ('a399', 'best'):
            equal(current[population][role], max48[population][role])
        equal(current[population]['current741'], max48[population]['candidate'])
        equal(max48[population]['max_first'], docs['max_first'][population])
    rows = {}
    for label, document, role in [('a399', current, 'a399'), ('373a', current, 'best'),
                                   ('max48', max48, 'candidate'), ('max41', current, 'candidate')]:
        rows[label] = {p: pick(document[p][role]) for p in ('cube', 'photos')}
    for label in ('max_first', 'p99_first'):
        rows[label] = {p: pick(docs[label][p]) for p in ('cube', 'photos')}
    labels = ['a399', '373a', 'max_first', 'p99_first', 'max48', 'max41']
    rows = {name: rows[name] for name in labels}
    for row in rows.values():
        assert row['cube']['n'] == 1 << 24 and row['photos']['n'] == 78643200
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family': font_manager.FontProperties(fname=str(font)).get_name(),
        'axes.unicode_minus': False, 'font.size': 11, 'svg.fonttype': 'path'})
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.2))
    fig.subplots_adjust(left=.075, right=.89, bottom=.23, top=.80, wspace=.25)
    cmap, norm = plt.get_cmap('viridis'), plt.Normalize(3.0, math.sqrt(14))
    offsets = {'a399': (-48, 12), '373a': (8, 8), 'max_first': (-76, 10),
               'p99_first': (9, -24), 'max48': (9, -2), 'max41': (9, -3)}
    for ax, population, title in zip(axes, ('cube', 'photos'),
            ('完整 RGB8 色域 · 16,777,216 色', '100 张历史图片合并 · 78,643,200 像素')):
        for name in labels:
            row = rows[name][population]
            color = cmap(norm(row['p99']))
            ax.scatter([row['mean']], [row['max']], s=88,
                marker='s' if name == '373a' else 'o', facecolors=[color], edgecolors='white', linewidths=1.0, zorder=3)
            ax.annotate(name + '\nmax²=' + str(row['max_squared']),
                xy=(row['mean'], row['max']), xytext=offsets[name], textcoords='offset points',
                fontsize=9, color='#24324a', annotation_clip=False)
        ax.set_title(title, fontsize=12, pad=12)
        ax.set_xlabel('平均 RGB 欧式误差（越小越好）', labelpad=9)
        ax.set_ylabel('最大 RGB 欧式误差（越小越好）', labelpad=9)
        ax.set_ylim(6.0, 8.7)
        lo = min(rows[n][population]['mean'] for n in labels)
        hi = max(rows[n][population]['mean'] for n in labels)
        ax.set_xlim(lo - .045, hi + .04)
        ax.grid(alpha=.18, zorder=0)
        ax.spines[['top', 'right']].set_visible(False)
    colorbar_axis = fig.add_axes([.92, .27, .014, .46])
    fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=colorbar_axis,
        label='聚合 p99（颜色越深数值越小）')
    fig.suptitle('精度候选：平均误差、p99 与最差误差一起看', fontsize=18, x=.5, y=.97)
    fig.text(.075, .865, '同一参考输出；点表示群体聚合指标，逐图及其它误差代价仍须分别查看。', fontsize=11, color='#455468')
    fig.text(.075, .13, '方块 373a 有历史同场 90% 速度档；其它点的聚合精度不能代替速度资格。', fontsize=11, color='#455468')
    fig.text(.075, .075, '百图均已见过，非盲测；RGB 代理不是官方 ΔE；逐图及 CVaR 代价另见数据表。', fontsize=11, color='#455468')
    fig.savefig(OUT / 'tail-frontier.png', dpi=160, facecolor='white')
    fig.savefig(OUT / 'tail-frontier.svg', facecolor='white')
    plt.close(fig)
    for name, expected in identities.items():
        assert sha(name) == expected, name
    save('data.json', dict(roles=rows, source_fields=FIELDS, cross_source_shared_roles_identical=True,
        plotting_only=True, native_calls=0, performance_samples=0,
        caveat='聚合mean/p99/max不是逐图支配、CVaR不退或新速度档。'))
    table = ['# 精度候选图的精确聚合数据', '',
        '| 角色 | 群体 | mean | RMS | p99 | max | CVaR1% |', '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for name in labels:
        for p, label in [('cube', '全色域'), ('photos', '百图合并')]:
            r = rows[name][p]
            table.append('| ' + name + ' | ' + label + ' | ' + ' | '.join(format(r[k], '.12g') for k in FIELDS) + ' |')
    table += ['', '数据全部读取既有质量JSON，未运行模型或计时；373a速度档沿用已公布独立性能证据，max41新宽表尚未授档。',
              '聚合图不展示逐图所有退化；不能据此主张任意图片、CVaR或每一级LUT均改善。', '']
    (OUT / 'data.md').write_text('\n'.join(table), encoding='utf-8')
    save('output-manifest.json', {path.name: {'bytes': path.stat().st_size, 'sha256': sha(path)}
        for path in OUT.iterdir() if path.is_file()})
    print(json.dumps({'plotted': True, 'roles': 6, 'populations': 2, 'native_calls': 0,
        'output': str(OUT)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
