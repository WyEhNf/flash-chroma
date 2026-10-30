"""V2只规范化授权artifacts内的三路径，调用未改的V1数学生成器。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import prepare_cinema_first_direct_budget as v1
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    frozen = json.loads((ROOT/'artifacts/cinema-first-direct-budget-frozen-v1.json').read_text(encoding='utf-8'))
    for name, expected in frozen['source_sha256'].items():
        if sha(ROOT/name) != expected: raise ValueError('V1冻结源被修改，拒绝V2：'+name)
    base = json.loads((ROOT/'experiments/p16-cinema-first-direct-budget-cpsat-v1.json').read_text(encoding='utf-8'))
    expected = {'num_search_workers': 1, 'random_seed': 20261024, 'max_time_in_seconds': 20.0,
        'objective': 'none', 'hint': 'none', 'real_solve_count': 1}
    if base['求解'] != expected: raise ValueError('V1求解协议已变')
    protocol = json.loads((ROOT/'experiments/p16-cinema-first-direct-budget-cpsat-v2.json').read_text(encoding='utf-8'))
    if protocol['唯一实际参数'] != expected: raise ValueError('V2不能更改实际求解参数')
    for i in range(1, len(sys.argv)):
        if sys.argv[i] in ('--contract', '--environment-lock', '--output'):
            if i+1 >= len(sys.argv): raise ValueError('路径选项缺值')
            path = Path(sys.argv[i+1]).resolve(strict=sys.argv[i] != '--output')
            path.relative_to((ROOT/'artifacts').resolve())
            sys.argv[i+1] = str(path)
    # 仅扩充身份闭包；有限全集与真实数学生成函数全部沿用V1原字节。
    v1.NEW_SOURCES = (*v1.NEW_SOURCES, 'scripts/prepare_cinema_first_direct_budget_v2.py',
        'experiments/p16-cinema-first-direct-budget-cpsat-v2.json')
    v1.main()


if __name__ == '__main__': main()
