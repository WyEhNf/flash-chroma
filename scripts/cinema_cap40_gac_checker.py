"""独立列表笛卡尔实现重放删值，不信主程序支持mask或CP状态。"""
from __future__ import annotations
import itertools


def independent_support(point,domains,n):
    channels=[];seen=set();local=set()
    for c in range(3):
        coeff={}
        for index,weight in point['node_terms'][c]:
            if not 0<=index<n or weight<=0:raise ValueError('独立证书系数/变量非法')
            coeff[index]=coeff.get(index,0)+weight
        ids=sorted(coeff)
        if len(ids)>4 or seen.intersection(ids) or sum(coeff.values())>65536:raise ValueError('独立通道因式分解合同不成立')
        seen.update(ids);local.update(ids);rows=[]
        for assigned in itertools.product(*[sorted(domains[i]) for i in ids]):
            acc=int(point['original_acc'][c])
            for index,value in zip(ids,assigned):acc+=coeff[index]*value
            if not 0<=acc<=255*65536:raise ValueError('独立实际节点域acc越界')
            output=(acc+32768)//65536-int(point['original_rgb'][c]);rows.append((output,dict(zip(ids,assigned))))
        channels.append(rows)
    reachable=[{z for z,_ in rows} for rows in channels]
    allowed=[tuple(row) for row in point['allowed_deltas'] if all(row[c] in reachable[c] for c in range(3))]
    result={i:set() for i in local}
    for c,rows in enumerate(channels):
        good={row[c] for row in allowed}
        for z,assignment in rows:
            if z in good:
                for index,value in assignment.items():result[index].add(value)
    return result,len(allowed),sum(len(rows) for rows in channels)


def mask(values):return sum(1<<(v+1) for v in values)


def verify_certificate(problem,result):
    n=problem['n_node_variables'];domains=[set(range(v['lower'],v['upper']+1)) for v in problem['variables'][:n]]
    if any(not d or not d.issubset({-1,0,1}) for d in domains):raise ValueError('独立初始域不符')
    checked=assignments=0;contradiction=False;reason_points=set();reason_variables=set()
    for j,record in enumerate(result['certificate']):
        p=record['point'];point=problem['points'][p];supported,retained,count=independent_support(point,domains,n);assignments+=count;reason_points.add(p)
        reason_variables.update(i for terms in point['node_terms'] for i,_ in terms)
        if record['kind']=='constant_point_empty':
            if retained or supported or j+1!=len(result['certificate']):raise AssertionError('常量空表证书不成立')
            contradiction=True
        elif record['kind']=='remove_value':
            i,value=record['variable'],record['value']
            if i not in supported or value not in domains[i] or value in supported[i]:raise AssertionError('删值仍有局部支持或变量不属于该point')
            if record['domain_before']!=mask(domains[i]):raise AssertionError('删值前域链不符')
            domains[i].remove(value)
            if record['domain_after']!=mask(domains[i]):raise AssertionError('删值后域链不符')
            checked+=1
            if not domains[i]:
                if j+1!=len(result['certificate']):raise AssertionError('空域后还有删值')
                contradiction=True
        else:raise ValueError('未知证书记录')
    if [mask(d) for d in domains]!=result['domain_masks']:raise AssertionError('最终全域mask不符')
    if result['status']=='GAC_CONTRADICTION':
        if not contradiction:raise AssertionError('未重放得到矛盾')
    elif result['status']=='GAC_FIXPOINT_UNDECIDED':
        if contradiction or any(not d for d in domains):raise AssertionError('固定点域不合法')
        for point in problem['points']:
            supported,retained,count=independent_support(point,domains,n);assignments+=count
            if not retained or any(values!=domains[i] for i,values in supported.items()):raise AssertionError('非空固定点仍有可删值')
    elif result['status']=='GAC_RESOURCE_STOP':
        if contradiction:raise AssertionError('资源停止错标已得矛盾')
    else:raise ValueError('未知GAC终态')
    return {'pass':True,'status':result['status'],'independently_checked_deletions':checked,'independent_local_assignments':assignments,
        'reason_point_indices':sorted(reason_points),'reason_variable_indices':sorted(reason_variables),'contradiction_replayed':contradiction,
        'scope':'逐条独立整数笛卡尔无支持性证明；非空固定点不代表SAT，未用CP状态作前提。'}
