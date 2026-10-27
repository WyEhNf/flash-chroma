"""连续偏好、预算约束与三维前沿；离线拟合和待测任务计划使用同一入口。"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'flash_chroma_frontier_v1'
TARGETS = ('desktop', 'mobile', 'embedded', 'portable')
BACKENDS = ('scalar', 'avx2')
REPRESENTATIONS = ('sparse', 'direct_u8', 'direct_u16', 'direct_rgb24')
GOALS = ('balanced', 'fastest', 'accurate', 'compact')
CONTEXT_FIELDS = ('source_luts_sha256', 'dataset_sha256', 'platform_id', 'timing_scope', 'image_mode', 'build_id')
VERIFICATIONS = ('correctness', 'accuracy', 'resources', 'time', 'time_stable')
SIZE_MAX = (1 << 64) - 1
FIT_METHODS = ('sample', 'sample_interp', 'ls_tetra_int', 'ls_tetra_jitter')
GRIDS = ('uniform', 'curvature', 'dp')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save_new(path, value):
    """拒绝覆盖已有证据或计划。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def _number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _integer(value, minimum=0, maximum=SIZE_MAX):
    return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _sha(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def validate_catalog(value):
    """只校验结构与自洽；调用者仍需审计引用证据，不能据此新增数值验收资格。"""
    if not isinstance(value, dict) or value.get('schema') != SCHEMA:
        raise ValueError('catalog版本错误')
    contexts, models, candidates = (value.get(name) for name in ('contexts', 'models', 'candidates'))
    if not isinstance(contexts, dict) or not isinstance(models, dict) or not isinstance(candidates, list):
        raise ValueError('catalog需要contexts/models对象与candidates数组')
    for name, context in contexts.items():
        if not _text(name) or not isinstance(context, dict) or any(key not in context for key in CONTEXT_FIELDS):
            raise ValueError('每个上下文必须绑定原LUT、数据、平台、计时、图像模式及构建')
        sources = context['source_luts_sha256']
        if not isinstance(sources, list) or len(sources) != 4 or not all(map(_sha, sources)):
            raise ValueError('上下文必须绑定按阶段排序的四个原LUT摘要')
        if not _sha(context['dataset_sha256']) or any(not _text(context[key]) for key in CONTEXT_FIELDS[2:]):
            raise ValueError('上下文身份字段为空或非法')
    for name, model in models.items():
        if not _text(name) or not isinstance(model, dict):
            raise ValueError('模型身份非法')
    identities = set()
    for row in candidates:
        if not isinstance(row, dict) or not _text(row.get('id')) or row['id'] in identities:
            raise ValueError('候选id必须唯一且非空')
        identities.add(row['id'])
        if row.get('context') not in contexts or row.get('model_id') not in models or not _text(row.get('evidence')):
            raise ValueError('候选必须引用已有上下文、模型及证据')
        model_sources = models[row['model_id']].get('source_luts_sha256')
        if model_sources is not None and model_sources != contexts[row['context']]['source_luts_sha256']:
            raise ValueError('模型原LUT与候选上下文不一致')
        config, metrics, verified = (row.get(key) for key in ('config', 'metrics', 'verified'))
        if not all(isinstance(item, dict) for item in (config, metrics, verified)):
            raise ValueError('候选缺少config/metrics/verified')
        if (config.get('target') not in TARGETS or config.get('backend') not in BACKENDS
                or config.get('representation') not in REPRESENTATIONS
                or not _integer(config.get('threads'), 1, 256)
                or not _integer(config.get('block_pixels'), 1)
                or not _integer(config.get('max_workspace_bytes'))):
            raise ValueError('执行配置非法，backend须记录实际执行值')
        if config['target'] in ('embedded', 'portable') and (config['backend'] != 'scalar'
                or config['representation'] != 'sparse' or config['threads'] != 1):
            raise ValueError('embedded/portable仅允许已实现的单线程稀疏标量路径')
        if any(type(verified.get(key)) is not bool for key in VERIFICATIONS):
            raise ValueError('所有验证标志必须显式为bool')
        if verified['time_stable'] and not verified['time']:
            raise ValueError('未执行计时不能声称时间稳定')
        if verified['accuracy'] and (not _number(metrics.get('mean_error'))
                or not _number(metrics.get('worst_image_mean')) or metrics['worst_image_mean'] < metrics['mean_error']):
            raise ValueError('精度指标无效')
        if verified['time'] and (not _number(metrics.get('batch_ms')) or metrics['batch_ms'] == 0):
            raise ValueError('计时必须为已测正有限值')
        if verified['resources'] and (not _integer(metrics.get('runtime_bytes'))
                or not _integer(metrics.get('workspace_bytes'))
                or metrics['workspace_bytes'] > metrics['runtime_bytes']
                or metrics['workspace_bytes'] > config['max_workspace_bytes']):
            raise ValueError('运行内存与工作区容量不自洽')
        for key in ('mean_error', 'worst_image_mean', 'batch_ms'):
            if metrics.get(key) is not None and not _number(metrics[key]):
                raise ValueError('即使尚未验收，也不能记录NaN/负数作为测量值')
        for key in ('runtime_bytes', 'workspace_bytes'):
            if metrics.get(key) is not None and not _integer(metrics[key]):
                raise ValueError('容量必须为非负整数字节，未知值使用null')
    return value


def _request(value, context, target, goal, weights, max_error, max_ms, max_runtime_bytes,
             max_workspace_bytes, allow_unstable_time, ignore_time, backends, max_threads):
    validate_catalog(value)
    if context is None:
        if len(value['contexts']) != 1:
            raise ValueError('存在多个或零个上下文，必须显式指定--context')
        context = next(iter(value['contexts']))
    if context not in value['contexts'] or target not in TARGETS or goal not in GOALS:
        raise ValueError('上下文、部署目标或优化目标非法')
    if len(weights) != 3 or any(not _number(w) or w > 1 for w in weights) or sum(weights) <= 0:
        raise ValueError('三项连续权重均须位于[0,1]，且不能全为0')
    if any(limit is not None and not _number(limit) for limit in (max_error, max_ms)):
        raise ValueError('误差/时间预算必须为非负有限值')
    if any(limit is not None and not _integer(limit) for limit in (max_runtime_bytes, max_workspace_bytes)):
        raise ValueError('内存预算必须为非负整数字节数')
    if ignore_time and (goal == 'fastest' or max_ms is not None or (goal == 'balanced' and weights[1] != 0)):
        raise ValueError('忽略时间时不能使用速度权重、速度目标或时间预算')
    if not backends or any(backend not in BACKENDS for backend in backends) or not _integer(max_threads, 1, 256):
        raise ValueError('后端集合或线程上限非法')
    return dict(context=context, target=target, goal=goal, weights=tuple(weights), max_error=max_error,
                max_ms=max_ms, max_runtime_bytes=max_runtime_bytes, max_workspace_bytes=max_workspace_bytes,
                allow_unstable_time=allow_unstable_time, ignore_time=ignore_time,
                backends=tuple(backends), max_threads=max_threads)


def _eligible(row, request):
    config, metrics, verified = row['config'], row['metrics'], row['verified']
    if row['context'] != request['context']:
        return 'context'
    if config['target'] != request['target']:
        return 'target'
    if config['backend'] not in request['backends'] or config['threads'] > request['max_threads']:
        return 'capability'
    if not all(verified[key] for key in ('correctness', 'accuracy', 'resources')):
        return 'unverified'
    if not request['ignore_time'] and not verified['time']:
        return 'unverified'
    if not request['ignore_time'] and not request['allow_unstable_time'] and not verified['time_stable']:
        return 'unstable_time'
    for limit, metric in (('max_error', 'worst_image_mean'), ('max_ms', 'batch_ms'),
                          ('max_runtime_bytes', 'runtime_bytes'), ('max_workspace_bytes', 'workspace_bytes')):
        maximum = request[limit]
        if maximum is not None and (metrics[metric] >= maximum if limit == 'max_error' else metrics[metric] > maximum):
            return 'budget'
    return None


def _dominates(a, b, ignore_time):
    axes = ('mean_error', 'runtime_bytes') if ignore_time else ('mean_error', 'batch_ms', 'runtime_bytes')
    return all(a['metrics'][axis] <= b['metrics'][axis] for axis in axes) and any(
        a['metrics'][axis] < b['metrics'][axis] for axis in axes)


def tradeoff(value, *, context=None, target='desktop', goal='balanced', weights=(1, 1, 1),
             max_error=None, max_ms=None, max_runtime_bytes=None, max_workspace_bytes=None,
             allow_unstable_time=False, ignore_time=False, backends=BACKENDS, max_threads=256):
    """预算先过滤，再重算前沿；原始catalog必须保留被其他请求支配的记录。"""
    request = _request(value, context, target, goal, weights, max_error, max_ms, max_runtime_bytes,
                       max_workspace_bytes, allow_unstable_time, ignore_time, backends, max_threads)
    rejected = dict.fromkeys(('context', 'target', 'capability', 'unverified', 'unstable_time', 'budget'), 0)
    eligible = []
    for row in value['candidates']:
        reason = _eligible(row, request)
        if reason:
            rejected[reason] += 1
        else:
            eligible.append(row)
    frontier_rows = [row for row in eligible if not any(_dominates(other, row, ignore_time) for other in eligible)]
    result = {'schema': 'flash_chroma_selection_v1', 'request': request, 'rejected': rejected,
              'eligible_count': len(eligible), 'frontier_ids': [row['id'] for row in frontier_rows],
              'frontier': frontier_rows, 'selected': None, 'status': 'no_feasible',
              'official_score_available': False, 'unseen_data_accuracy_guaranteed': False}
    if not frontier_rows:
        result['reason'] = '没有同时满足上下文、验证、部署能力与预算的配置'
        return result
    effective = {'fastest': (0, 1, 0), 'accurate': (1, 0, 0), 'compact': (0, 0, 1)}.get(goal, weights)
    total = sum(effective)
    effective = [weight / total for weight in effective]
    ranges = {key: (min(row['metrics'][key] for row in eligible), max(row['metrics'][key] for row in eligible))
              for key in ('mean_error', 'runtime_bytes', *(('batch_ms',) if not ignore_time else ()))}

    def score(row):
        components = []
        for key in ('mean_error', 'batch_ms', 'runtime_bytes'):
            if key not in ranges:
                components.append(0.0)
                continue
            minimum, maximum = ranges[key]
            components.append((row['metrics'][key] - minimum) / (maximum - minimum) if maximum > minimum else 0.0)
        return sum(a*b for a, b in zip(effective, components))

    def key(row):
        m = row['metrics']
        return (score(row), m['mean_error'], m['worst_image_mean'], 0 if ignore_time else m['batch_ms'],
                m['runtime_bytes'], m['workspace_bytes'], row['id'])

    chosen = min(frontier_rows, key=key)
    result.update(status='ok', selected=chosen, score=score(chosen), normalized_weights=effective,
                  provisional=ignore_time or not chosen['verified']['time_stable'],
                  reason='依据绑定验证数据和平台选择；执行参数保持候选原值，未推断未知LUT或目标机成绩')
    return result


def source_records(paths):
    if len(paths) != 4:
        raise ValueError('必须提供按阶段顺序排列的四张原始LUT')
    records = []
    for path in paths:
        path = Path(path).resolve()
        if path.stat().st_size != 256**3*3:
            raise ValueError('原始LUT必须恰为256³×3 RGB8字节：' + str(path))
        records.append({'path': str(path), 'sha256': digest(path)})
    if len({row['sha256'] for row in records}) != 4:
        raise ValueError('四个原LUT须不同；重复源不能声称四个不同映射')
    return records


def make_plan(sources, *, m_values=(17, 25, 33), methods=('sample_interp',), grids=('uniform',),
              threads=(1, 4), block_pixels=(4096, 65536), targets=TARGETS,
              representations=REPRESENTATIONS, max_models=10000):
    if len(sources) != 4 or not all(_sha(row.get('sha256')) and _text(row.get('path')) for row in sources):
        raise ValueError('计划源必须含四项路径及SHA')
    if (not m_values or any(not _integer(m, 17, 33) for m in m_values)
            or any(method not in FIT_METHODS for method in methods) or not methods
            or any(grid not in GRIDS for grid in grids) or not grids
            or any(not _integer(n, 1, 256) for n in threads) or not threads
            or any(not _integer(n, 1) for n in block_pixels) or not block_pixels
            or not targets or any(t not in TARGETS for t in targets)
            or not representations or any(rep not in REPRESENTATIONS for rep in representations)):
        raise ValueError('任务计划参数域非法')
    sizes = sorted(set(m_values))
    count = len(sizes)**4 * len(set(methods)) * len(set(grids))
    if not _integer(max_models, 1) or count > max_models:
        raise ValueError('模型任务数量超过显式max_models预算')
    runtime = []
    for target, representation, nthreads, block in itertools.product(
            dict.fromkeys(targets), dict.fromkeys(representations), sorted(set(threads)), sorted(set(block_pixels))):
        for backend in BACKENDS:
            if target in ('embedded', 'portable') and (representation != 'sparse' or backend != 'scalar' or nthreads != 1):
                continue
            runtime.append(dict(target=target, representation=representation, backend=backend,
                                threads=nthreads, block_pixels=block))
    models = []
    for method, grid, sizes4 in itertools.product(dict.fromkeys(methods), dict.fromkeys(grids), itertools.product(sizes, repeat=4)):
        name = method + '-' + grid + '-' + '-'.join(map(str, sizes4))
        models.append({'id': name, 'm': list(sizes4), 'method': method, 'grid': grid,
                       'status': 'planned_unverified', 'command': [sys.executable, 'scripts/p16_frontier.py', 'fit',
                           '--source-luts', *(row['path'] for row in sources), '--m', *map(str, sizes4),
                           '--method', method, '--grid', grid, '--output', 'artifacts/frontier-fit/' + name]})
    return {'schema': 'flash_chroma_search_plan_v1', 'sources': sources, 'models': models,
            'runtime_domain': runtime, 'planned_combinations': len(models)*len(runtime),
            'continuous_domains': {'preference': {'accuracy': [0, 1], 'speed': [0, 1], 'compactness': [0, 1],
                                                   'reject_all_zero': True},
                                   'curvature_alpha': [0, 1], 'curvature_exponent': {'exclusive_minimum': 0},
                                   'budgets': '非负有限误差/时间及整数字节；硬约束不静默放宽'},
            'validation_required': ['原始LUT到四级最终输出的逐图全像素误差', '部署后端输出一致性',
                                    '指定环境/工作负载/计时范围的性能与A/A控制', '准备峰值与常驻/图像容量'],
            'note': '计划未执行，不产生verified候选；m可各级不同，运行时配置需分别实际验收。'}


def fit_candidate(paths, sizes, method, grid_mode, output, *, alpha=0.5, exponent=0.4):
    """实际调用已有拟合器，支持混合m；拟合成功不代替四级图像精度验收。"""
    if len(sizes) != 4 or any(not _integer(m, 17, 33) for m in sizes) or method not in FIT_METHODS or grid_mode not in GRIDS:
        raise ValueError('拟合需要四个17..33的m及支持的tetra_q16拟合器')
    if not _number(alpha) or alpha > 1 or not _number(exponent) or exponent == 0:
        raise ValueError('curvature alpha须在[0,1]，exponent须为正有限数')
    output = Path(output)
    if output.exists():
        raise FileExistsError('输出目录已存在，保留原结果：' + str(output))
    sources = source_records(paths)
    sys.path.insert(0, str(ROOT / 'python'))
    from lutlab import fit, io
    output.mkdir(parents=True)
    code_sources = {str(path.relative_to(ROOT)): digest(path) for path in
                    (Path(__file__).resolve(), ROOT / 'python/lutlab/fit.py', ROOT / 'python/lutlab/io.py')}
    save_new(output / 'started.json', {'sources': sources, 'm': list(sizes), 'method': method, 'grid': grid_mode,
                                      'alpha': alpha, 'exponent': exponent, 'source_sha256': code_sources,
                                      'status': 'started_pending_fit_and_validation'})
    models, diagnostics = [], []
    try:
        for index, (source, m) in enumerate(zip(sources, sizes), 1):
            table = io.load_full(source['path'], mmap=True)
            if grid_mode == 'uniform':
                positions = io.uniform_grid(m)
            elif grid_mode == 'curvature':
                positions = fit.adaptive_grid(table, m, alpha=alpha, expo=exponent)
            else:
                positions = fit.adaptive_dp_grid(table, m)
            model, info = fit.fit_model(table, m, method, grid=positions)
            path = output / f'stage{index}.slut'
            io.save_sparse(path, model)
            loaded = io.load_sparse(path, competition=True)
            models.append({'path': path.name, 'sha256': digest(path), 'm': loaded.m, 'bytes': path.stat().st_size})
            diagnostics.append(info)
            del table
        if sources != source_records(paths) or any(digest(ROOT / name) != sha for name, sha in code_sources.items()):
            raise RuntimeError('拟合期间原LUT或源码改变，拒绝发布模型清单')
        profile = {'models': models, 'sidecars': [None]*4, 'interpolation_basis': 'tetra_q16',
                   'source_luts_sha256': [source['sha256'] for source in sources],
                   'm': list(sizes), 'fixed_for_entire_batch': True}
        manifest = {'default_profile': 'fitted', 'path_root': '.', 'interpolation_basis': 'tetra_q16',
                    'profiles': {'fitted': profile}, 'original_luts': sources,
                    'parameters': {'m': list(sizes), 'method': method, 'grid': grid_mode, 'alpha': alpha, 'exponent': exponent},
                    'status': 'fitted_pending_chain_accuracy_and_runtime_validation', 'source_sha256': code_sources,
                    'diagnostics': diagnostics}
        save_new(output / 'source-manifest.json', manifest)
        return manifest
    except Exception as error:
        save_new(output / 'failure.json', {'status': 'failed_preserved', 'error': str(error), 'completed_stages': len(models)})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    validation = commands.add_parser('validate', help='检查catalog结构；不新增数值验证资格')
    validation.add_argument('--catalog', type=Path, required=True)
    for name in ('select', 'frontier'):
        command = commands.add_parser(name, help='按连续偏好及硬预算选择，或返回完整前沿')
        command.add_argument('--catalog', type=Path, required=True)
        command.add_argument('--context')
        command.add_argument('--target', choices=TARGETS, default='desktop')
        command.add_argument('--goal', choices=GOALS, default='balanced')
        command.add_argument('--weights', type=float, nargs=3, default=(1, 1, 1), metavar=('A', 'B', 'C'))
        command.add_argument('--max-error', type=float)
        command.add_argument('--max-ms', type=float)
        command.add_argument('--max-runtime-bytes', type=int)
        command.add_argument('--max-workspace-bytes', type=int)
        command.add_argument('--allow-unstable-time', action='store_true')
        command.add_argument('--ignore-time', action='store_true')
        command.add_argument('--backends', nargs='+', choices=BACKENDS, default=list(BACKENDS))
        command.add_argument('--max-threads', type=int, default=256)
        command.add_argument('--output', type=Path)
    planning = commands.add_parser('plan', help='生成混合m和运行时参数域；不执行或声称验收')
    planning.add_argument('--source-luts', type=Path, nargs=4, required=True)
    planning.add_argument('--m-values', type=int, nargs='+', default=(17, 25, 33))
    planning.add_argument('--methods', choices=FIT_METHODS, nargs='+', default=('sample_interp',))
    planning.add_argument('--grids', choices=GRIDS, nargs='+', default=('uniform',))
    planning.add_argument('--threads', type=int, nargs='+', default=(1, 4))
    planning.add_argument('--block-pixels', type=int, nargs='+', default=(4096, 65536))
    planning.add_argument('--targets', choices=TARGETS, nargs='+', default=TARGETS)
    planning.add_argument('--representations', choices=REPRESENTATIONS, nargs='+', default=REPRESENTATIONS)
    planning.add_argument('--max-models', type=int, default=10000)
    planning.add_argument('--output', type=Path, required=True)
    fitting = commands.add_parser('fit', help='实际离线拟合四级混合m，输出待验收模型清单')
    fitting.add_argument('--source-luts', type=Path, nargs=4, required=True)
    fitting.add_argument('--m', type=int, nargs=4, required=True)
    fitting.add_argument('--method', choices=FIT_METHODS, default='sample_interp')
    fitting.add_argument('--grid', choices=GRIDS, default='uniform')
    fitting.add_argument('--grid-alpha', type=float, default=0.5)
    fitting.add_argument('--grid-exponent', type=float, default=0.4)
    fitting.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'validate':
        value = validate_catalog(json.loads(args.catalog.read_text(encoding='utf-8')))
        result = {'structure_valid': True, 'numeric_evidence_revalidated': False,
                  'contexts': len(value['contexts']), 'candidates': len(value['candidates'])}
    elif args.command in ('select', 'frontier'):
        value = json.loads(args.catalog.read_text(encoding='utf-8'))
        result = tradeoff(value, context=args.context, target=args.target, goal=args.goal, weights=args.weights,
                          max_error=args.max_error, max_ms=args.max_ms, max_runtime_bytes=args.max_runtime_bytes,
                          max_workspace_bytes=args.max_workspace_bytes, allow_unstable_time=args.allow_unstable_time,
                          ignore_time=args.ignore_time, backends=args.backends, max_threads=args.max_threads)
        result['catalog_sha256'] = digest(args.catalog)
        if args.output:
            save_new(args.output, result)
    elif args.command == 'plan':
        result = make_plan(source_records(args.source_luts), m_values=args.m_values, methods=args.methods,
                           grids=args.grids, threads=args.threads, block_pixels=args.block_pixels,
                           targets=args.targets, representations=args.representations, max_models=args.max_models)
        save_new(args.output, result)
        result = {'output': str(args.output), 'models': len(result['models']),
                  'runtime_configs': len(result['runtime_domain']), 'planned_combinations': result['planned_combinations']}
    else:
        value = fit_candidate(args.source_luts, args.m, args.method, args.grid, args.output,
                              alpha=args.grid_alpha, exponent=args.grid_exponent)
        result = {'output': str(args.output), 'status': value['status'], 'm': args.m}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 2 if result.get('status') == 'no_feasible' else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError) as error:
        print('失败：' + str(error), file=sys.stderr)
        raise SystemExit(1)
