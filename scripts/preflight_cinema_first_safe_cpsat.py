"""仅构建、验证、导出完整危险表最小L1模型，不调用求解器。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from cinema_first_safe_cpsat_model import build_safe_model


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--problem', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖完整危险表CP预检')
    value = json.loads(args.problem.read_text(encoding='utf-8')); root = Path(__file__).resolve().parents[1]
    for name, expected in {**value['source_sha256'], **value['frozen_risk_sha256']}.items():
        if sha(root/name) != expected: raise ValueError('冻结源或风险证据已变：'+name)
    model, variables, absolutes = build_safe_model(value); path = args.output.with_suffix('.pb')
    if path.exists() or not model.export_to_file(str(path)): raise ValueError('不覆盖或未能导出CP模型')
    record = {'pass': True, 'solver_called': False, 'problem_sha256': sha(args.problem),
        'model_proto_sha256': sha(path), 'source_sha256': sha(__file__), 'base_variables': len(variables),
        'abs_variables': len(absolutes), 'total_integer_variables': len(variables)+len(absolutes),
        'rounding_rows': len(value['rows']), 'allowed_tables': len(value['points']),
        'allowed_triples': sum(len(point['allowed_deltas']) for point in value['points']),
        'objective_upper_bound': value['objective_absolute_upper_bound'],
        'maximum_raw_absolute_bound': max(r['int64_audit']['raw_absolute_sum_bound'] for r in value['rows']),
        'maximum_reduced_absolute_bound': max(r['int64_audit']['absolute_sum_bound'] for r in value['rows']),
        'model_stats': model.model_stats(), 'scope': '完整危险表最小L1模型只构建/CPvalidate/导出；没有实际搜索。'}
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: record[k] for k in ('pass', 'solver_called', 'total_integer_variables', 'allowed_tables', 'allowed_triples')}), flush=True)


if __name__ == '__main__': main()
