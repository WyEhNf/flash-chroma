"""双环境可读的纯整数行约简与CP-SAT模型桥，模块导入不加载NumPy/Numba。"""
from __future__ import annotations
import math

SAFE = (1 << 62)-1


def ceil_div(numerator, denominator):
    if denominator <= 0: raise ValueError('约简除数必须正')
    return -((-numerator)//denominator)


def checked(value, label):
    if type(value) is not int or not -SAFE <= value <= SAFE:
        raise OverflowError('超出保守signed int64范围：'+label)
    return value


def reduce_row(terms, lower, upper, variables):
    lower, upper = checked(lower, '原lower'), checked(upper, '原upper')
    if lower > upper: raise ValueError('原始约束区间反转')
    combined = {}
    for variable, coefficient in terms:
        checked(coefficient, '原系数'); combined[variable] = combined.get(variable, 0)+coefficient
    terms = [[i, c] for i, c in sorted(combined.items()) if c]
    raw_abs_bound = 0
    for index, coefficient in terms:
        checked(coefficient, '合并后原系数')
        if not 0 <= index < len(variables): raise ValueError('原变量索引越界')
        domain = variables[index]
        raw_a = checked(coefficient*domain['lower'], '原系数乘lower')
        raw_b = checked(coefficient*domain['upper'], '原系数乘upper')
        raw_abs_bound = checked(raw_abs_bound+max(abs(raw_a), abs(raw_b)), '原绝对乘积总界')
    divisor = math.gcd(*(abs(c) for _, c in terms)) if terms else 1
    normalized = [[i, c//divisor] for i, c in terms]
    lo, hi = ceil_div(lower, divisor), upper//divisor
    low_sum, high_sum, absolute_sum, products = 0, 0, 0, []
    for index, coefficient in normalized:
        if not 0 <= index < len(variables): raise ValueError('变量索引越界')
        checked(coefficient, '约简系数')
        bounds = variables[index]
        low, high = checked(bounds['lower'], '变量lower'), checked(bounds['upper'], '变量upper')
        if low > high: raise ValueError('变量域反转')
        first, second = checked(coefficient*low, '系数乘lower'), checked(coefficient*high, '系数乘upper')
        a, b = min(first, second), max(first, second)
        low_sum = checked(low_sum+a, 'LHS最小累加'); high_sum = checked(high_sum+b, 'LHS最大累加')
        absolute_sum = checked(absolute_sum+max(abs(first), abs(second)), '绝对乘积总界')
        products.append({'variable': index, 'coefficient': coefficient, 'product_lower': a, 'product_upper': b})
    checked(lo, '约简lower'); checked(hi, '约简upper')
    return {'raw_terms': terms, 'raw_lower': lower, 'raw_upper': upper, 'gcd': divisor,
            'terms': normalized, 'lower': lo, 'upper': hi,
            'int64_audit': {'raw_absolute_sum_bound': raw_abs_bound, 'lhs_lower': low_sum, 'lhs_upper': high_sum, 'absolute_sum_bound': absolute_sum,
                            'term_products': products, 'safe_absolute_limit': SAFE, 'pass': True}}


def validate_problem(problem):
    variables = problem['variables']
    for row in problem['rows']:
        fresh = reduce_row(row['raw_terms'], row['raw_lower'], row['raw_upper'], variables)
        if fresh != row: raise ValueError('整数gcd约简/区间/域乘积审计不一致')
    for point in problem['points']:
        if len(point['z_indices']) != 3: raise ValueError('热点需要三个整数输出delta')
        for triple in point['allowed_deltas']:
            if len(triple) != 3 or any(type(v) is not int for v in triple): raise ValueError('AllowedAssignments需要整数RGB三元组')
            if any(not variables[index]['lower'] <= v <= variables[index]['upper'] for index, v in zip(point['z_indices'], triple)):
                raise ValueError('AllowedAssignments超出输出delta域')


def build_model(problem):
    from ortools.sat.python import cp_model
    validate_problem(problem); model = cp_model.CpModel()
    variables = [model.new_int_var(v['lower'], v['upper'], v['name']) for v in problem['variables']]
    for row in problem['rows']:
        expression = sum(coefficient*variables[index] for index, coefficient in row['terms'])
        if row['lower'] > row['upper']: model.add_bool_or([])
        else: model.add_linear_constraint(expression, row['lower'], row['upper'])
    for point in problem['points']:
        model.add_allowed_assignments([variables[i] for i in point['z_indices']], point['allowed_deltas'])
    error = model.validate()
    if error: raise ValueError('CP-SAT模型验证失败：'+error)
    return model, variables
