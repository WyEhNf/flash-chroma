"""完整危险表CP模型的整数L1目标；导入不加载NumPy/Numba。"""
from __future__ import annotations
from cinema_first_cpsat_model import build_model, checked, validate_problem


def validate_safe_problem(problem):
    if problem['schema'] != 'cinema_first_safe_cpsat_problem_v1':
        raise ValueError('不是完整危险表单轮模型')
    validate_problem(problem)
    count = problem['n_node_variables']
    if problem['objective'] != {'kind': 'minimize_node_delta_l1', 'node_variables': count}:
        raise ValueError('不是冻结最小节点L1目标')
    bound = 0
    for domain in problem['variables'][:count]:
        bound = checked(bound+max(abs(domain['lower']), abs(domain['upper'])), 'L1最大总和')
    if bound != problem['objective_absolute_upper_bound']:
        raise ValueError('L1总界不符')


def build_safe_model(problem):
    validate_safe_problem(problem)
    model, variables = build_model(problem)
    absolutes = []
    for i, domain in enumerate(problem['variables'][:problem['n_node_variables']]):
        upper = max(abs(domain['lower']), abs(domain['upper']))
        value = model.new_int_var(0, upper, 'abs_node_delta_'+str(i))
        model.add_abs_equality(value, variables[i]); absolutes.append(value)
    model.minimize(sum(absolutes))
    error = model.validate()
    if error: raise ValueError('最小L1模型验证失败：'+error)
    return model, variables, absolutes
