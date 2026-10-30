"""双环境纯整数桥：真实Q16表、误差平方选择器与八精度预算。"""
from __future__ import annotations
from cinema_first_cpsat_model import checked, reduce_row, validate_problem

BUDGETS = ('uniform_mean', 'training_mean', 'uniform_rms', 'training_rms',
           'uniform_p99', 'training_p99', 'uniform_cvar', 'training_cvar')


def empty_problem(node_variables, limits):
    return {'schema': 'cinema_first_direct_budget_problem_v1', 'variables': list(node_variables),
        'n_node_variables': len(node_variables), 'points': [], 'rows': [], 'budget_limits': list(limits),
        'solve': {'num_search_workers': 1, 'random_seed': 20261024, 'max_time_in_seconds': 20.0},
        'objective': 'none', 'hint': 'none'}


def attach_error_cost(problem, point, allowed_rgb_q, coefficients):
    original = point['original_rgb']; rows = []
    for row in allowed_rgb_q:
        if len(row) != 4 or any(type(v) is not int for v in row): raise ValueError('安全表需整数RGB与误差平方')
        rows.append([row[c]-original[c] for c in range(3)]+[row[3]])
    if len({tuple(row[:3]) for row in rows}) != len(rows): raise ValueError('同一首级RGB对应多个误差平方')
    if sorted(row[:3] for row in rows) != point['allowed_deltas']: raise ValueError('安全误差表与原舍入输出表不一致')
    options = sorted({row[3] for row in rows})
    if not options or min(options) < 0 or max(options) > 49: raise ValueError('新误差平方须在cap49内')
    point.update(allowed_error_rows=sorted(rows), error_options=options,
        coefficients={str(q): list(coefficients[q]) for q in options}, selector_indices=[])
    if len(options) == 1:
        point.update(q_index=None, q_constant=options[0])
        return
    point['q_index'] = len(problem['variables']); point['q_constant'] = None
    problem['variables'].append({'name': 'q_'+str(len(problem['points'])-1), 'lower': min(options), 'upper': max(options)})
    for q in options:
        index = len(problem['variables']); point['selector_indices'].append([q, index])
        problem['variables'].append({'name': 's_'+str(len(problem['points'])-1)+'_'+str(q), 'lower': 0, 'upper': 1})


def budget_rows(problem):
    terms, constants = [[] for _ in BUDGETS], [0]*len(BUDGETS)
    for point in problem['points']:
        if point['q_index'] is None:
            for b, coefficient in enumerate(point['coefficients'][str(point['q_constant'])]):
                constants[b] = checked(constants[b]+coefficient, '固定误差预算累加')
        else:
            for q, index in point['selector_indices']:
                for b, coefficient in enumerate(point['coefficients'][str(q)]):
                    if coefficient: terms[b].append([index, coefficient])
    result = []
    for b, name in enumerate(BUDGETS):
        # 所有预算项变量为0/1，独立最小界只作无条件下界。
        lower = checked(sum(min(0, c) for _, c in terms[b]), '预算独立下界')
        upper = checked(problem['budget_limits'][b]-constants[b], '预算上界减固定贡献')
        row = None if lower > upper else reduce_row(terms[b], lower, upper, problem['variables'])
        result.append({'name': name, 'constant': constants[b], 'limit': problem['budget_limits'][b],
            'terms': terms[b], 'infeasible_by_independent_bounds': lower > upper, 'row': row})
    return result


def finish_problem(problem):
    problem['budget_rows'] = budget_rows(problem)
    validate_direct_problem(problem)
    return problem


def validate_direct_problem(problem):
    if len(problem['budget_limits']) != 8: raise ValueError('需要八项原始精度预算')
    for limit in problem['budget_limits']: checked(limit, '预算limit')
    validate_problem(problem)
    used = set(range(problem['n_node_variables']))
    for point in problem['points']:
        if len(set(point['z_indices'])) != 3 or any(index in used for index in point['z_indices']):
            raise ValueError('输出delta索引重复')
        used.update(point['z_indices'])
        rows = point['allowed_error_rows']; options = sorted({row[3] for row in rows})
        if not rows or point['error_options'] != options or sorted(row[:3] for row in rows) != point['allowed_deltas']:
            raise ValueError('误差表、q域与输出delta不一致')
        for row in rows:
            if any(type(v) is not int for v in row) or not 0 <= row[3] <= 49: raise ValueError('非法安全表整数')
        if len({tuple(row[:3]) for row in rows}) != len(rows): raise ValueError('安全RGB误差不是函数')
        if set(point['coefficients']) != {str(q) for q in options}: raise ValueError('成本未完整覆盖安全q')
        for coefficients in point['coefficients'].values():
            if len(coefficients) != 8: raise ValueError('误差成本不是八维')
            for coefficient in coefficients: checked(coefficient, '点误差预算系数')
        q_index = point['q_index']
        if len(options) == 1:
            if q_index is not None or point['q_constant'] != options[0] or point['selector_indices']:
                raise ValueError('固定q不应新增选择器')
        else:
            if point['q_constant'] is not None or q_index is None: raise ValueError('多q缺整数变量')
            if [q for q, _ in point['selector_indices']] != options: raise ValueError('q与one-hot未完全绑定')
            domain = problem['variables'][q_index]
            if [domain['lower'], domain['upper']] != [min(options), max(options)]: raise ValueError('q域不符')
            if q_index in used: raise ValueError('q索引重复')
            used.add(q_index)
            for _, index in point['selector_indices']:
                domain = problem['variables'][index]
                if index in used or [domain['lower'], domain['upper']] != [0, 1]: raise ValueError('选择器索引/域不符')
                used.add(index)
    if used != set(range(len(problem['variables']))): raise ValueError('变量有遗漏或重复占用')
    if problem['budget_rows'] != budget_rows(problem): raise ValueError('预算行不是全部点成本的准确累加')


def build_direct_model(problem):
    from ortools.sat.python import cp_model
    validate_direct_problem(problem)
    model = cp_model.CpModel(); variables = [model.new_int_var(v['lower'], v['upper'], v['name']) for v in problem['variables']]
    for row in problem['rows']:
        expression = sum(c*variables[i] for i, c in row['terms'])
        if row['lower'] > row['upper']: model.add_bool_or([])
        else: model.add_linear_constraint(expression, row['lower'], row['upper'])
    for point in problem['points']:
        z = [variables[i] for i in point['z_indices']]
        if point['q_index'] is None:
            model.add_allowed_assignments(z, [row[:3] for row in point['allowed_error_rows']])
        else:
            q = variables[point['q_index']]; selectors = point['selector_indices']
            model.add_allowed_assignments(z+[q], point['allowed_error_rows'])
            model.add(sum(variables[index] for _, index in selectors) == 1)
            model.add(q == sum(value*variables[index] for value, index in selectors))
    for item in problem['budget_rows']:
        if item['infeasible_by_independent_bounds']: model.add_bool_or([]); continue
        row = item['row']; expression = sum(c*variables[i] for i, c in row['terms'])
        model.add_linear_constraint(expression, row['lower'], row['upper'])
    error = model.validate()
    if error: raise ValueError('直接预算CP模型校验失败：'+error)
    return model, variables
