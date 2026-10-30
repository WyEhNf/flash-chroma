"""保留V1重叠标签图；独立V2只改标签布局，不改数据或指标。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'scripts/plot_p16_tail_frontier.py'
output = ROOT / 'scripts/plot_p16_tail_frontier_v2.py'
if output.exists():
    raise FileExistsError('不覆盖V2绘图源')
source = path.read_text(encoding='utf-8')
changes = {
    'artifacts/p16-tail-frontier-plot-v1': 'artifacts/p16-tail-frontier-plot-v2',
    'figsize=(13.2, 6.2)': 'figsize=(13.2, 7.0)',
    'bottom=.23': 'bottom=.27',
    "textcoords='offset points',": "textcoords='axes fraction', arrowprops=dict(arrowstyle='-', color='#8d98a9', lw=.7),",
    'fig.text(.075, .13': 'fig.text(.075, .125',
    'fig.text(.075, .075': 'fig.text(.075, .065',
}
old = """    offsets = {'a399': (-48, 12), '373a': (8, 8), 'max_first': (-76, 10),
               'p99_first': (9, -24), 'max48': (9, -2), 'max41': (9, -3)}"""
new = """    offsets = {'a399': (.70, .85), '373a': (.30, .64), 'max_first': (.04, .48),
               'p99_first': (.40, .34), 'max48': (.08, .23), 'max41': (.30, .085)}"""
changes[old] = new
for before, after in changes.items():
    assert source.count(before) == 1, before
    source = source.replace(before, after)
output.write_text(source, encoding='utf-8')
print({'new_renderer': str(output), 'changed_fragments': len(changes), 'data_changes': 0})
