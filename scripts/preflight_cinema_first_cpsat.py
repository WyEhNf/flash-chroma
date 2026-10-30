"""隔离环境仅构建/验证热点CP模型并导出字节，不调用求解器。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from cinema_first_cpsat_model import build_model


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--problem', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖CP模型构建预检')
    value = json.loads(args.problem.read_text(encoding='utf-8')); root = Path(__file__).resolve().parents[1]
    for name, expected in value['source_sha256'].items():
        if sha(root/name) != expected: raise ValueError('实际源已变：'+name)
    model, variables = build_model(value); path = args.output.with_suffix('.pb')
    if path.exists() or not model.export_to_file(str(path)): raise ValueError('CP模型导出失败或已有')
    result = {'pass': True, 'solver_called': False, 'problem_sha256': sha(args.problem), 'model_proto_sha256': sha(path),
              'source_sha256': sha(__file__), 'variables': len(variables), 'rounding_rows': len(value['rows']),
              'allowed_tables': len(value['points']), 'allowed_tuples': sum(len(p['allowed_deltas']) for p in value['points']),
              'max_raw_absolute_sum': max(r['int64_audit']['raw_absolute_sum_bound'] for r in value['rows']),
              'max_reduced_absolute_sum': max(r['int64_audit']['absolute_sum_bound'] for r in value['rows']),
              'model_stats': model.model_stats(), 'scope': '仅构建/CPvalidate/模型导出，未执行实际116热点搜索'}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('pass', 'solver_called', 'variables', 'rounding_rows', 'allowed_tables', 'allowed_tuples')}), flush=True)


if __name__ == '__main__': main()
