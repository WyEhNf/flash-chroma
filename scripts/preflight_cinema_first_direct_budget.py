"""隔离环境只建模/校验/导出直接预算PB，不进行真实搜索。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from cinema_first_direct_budget_model import build_direct_model
from cinema_first_direct_budget_identity import sha, verify_identity, process_memory


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--problem', type=Path, required=True)
    p.add_argument('--environment-lock', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖直接预算无搜索预检')
    value = json.loads(args.problem.read_text(encoding='utf-8')); verify_identity(value, args.environment_lock)
    points = len(value['points']); rows = sum(len(v['allowed_error_rows']) for v in value['points'])
    selectors = sum(len(v['selector_indices']) for v in value['points'])
    if points > 16384 or rows > 500000 or selectors > 131072: raise ValueError('完整资源门超限')
    model, variables = build_direct_model(value); path = args.output.with_suffix('.pb')
    if path.exists() or not model.export_to_file(str(path)): raise ValueError('不覆盖PB或导出失败')
    result = {'pass': True, 'solver_called': False, 'problem_sha256': sha(args.problem),
        'model_proto_sha256': sha(path), 'problem_bytes': args.problem.stat().st_size, 'model_proto_bytes': path.stat().st_size,
        'source_sha256': sha(__file__), 'variables': len(variables), 'rounding_rows': len(value['rows']),
        'allowed_tables': points, 'safe_table_rows': rows, 'selectors': selectors, 'budget_rows': len(value['budget_rows']),
        'maximum_rounding_raw_absolute_bound': max(r['int64_audit']['raw_absolute_sum_bound'] for r in value['rows']),
        'maximum_budget_raw_absolute_bound': max(v['row']['int64_audit']['raw_absolute_sum_bound'] for v in value['budget_rows'] if v['row']),
        'model_stats': model.model_stats(), 'process_memory': process_memory(),
        'scope': '完整直接八预算模型构造、CPvalidate、PB导出和进程峰工作集；尚无真实solver搜索。'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print({k: result[k] for k in ('pass', 'solver_called', 'variables', 'allowed_tables', 'safe_table_rows')}, flush=True)


if __name__ == '__main__': main()
