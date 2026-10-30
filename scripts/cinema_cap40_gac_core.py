"""纯整数无搜索GAC，按通道聚合可达输出与节点值mask。"""
from __future__ import annotations
from collections import deque
import itertools
import math


def values(mask):return tuple(v for v in (-1,0,1) if mask & (1<<(v+1)))


def compile_points(problem):
    n=problem['n_node_variables'];domains=[]
    for var in problem['variables'][:n]:
        if not -1<=var['lower']<=var['upper']<=1:raise ValueError('GAC只处理冻结±1/clip域')
        domains.append(sum(1<<(v+1) for v in range(var['lower'],var['upper']+1)))
    points=[];incidence=[[] for _ in range(n)]
    for p,point in enumerate(problem['points']):
        channels=[];seen=set()
        for c in range(3):
            combined={}
            for i,w in point['node_terms'][c]:
                if type(i) is not int or type(w) is not int or not 0<=i<n or w<=0:raise ValueError('局部变量或Q16正系数非法')
                combined[i]=combined.get(i,0)+w
            terms=sorted(combined.items());variables={i for i,_ in terms}
            if len(terms)>4 or seen & variables or sum(w for _,w in terms)>65536:raise ValueError('通道因式分解合同不成立')
            if not 0<=point['original_acc'][c]<=255*65536 or point['original_rgb'][c]!=(point['original_acc'][c]+32768)//65536:raise ValueError('完整原acc/half舍入非法')
            seen|=variables;channels.append(terms)
        for i in sorted(seen):incidence[i].append(p)
        allowed=[tuple(row) for row in point['allowed_deltas']]
        if any(len(row)!=3 or any(type(v) is not int for v in row) for row in allowed):raise ValueError('安全表不是整数RGB delta')
        points.append({'terms':channels,'variables':sorted(seen),'acc':point['original_acc'],'rgb':point['original_rgb'],'allowed':allowed})
    return domains,points,incidence


def supported_masks(point,domains):
    groups=[];assignments=0
    for c,terms in enumerate(point['terms']):
        choices=[values(domains[i]) for i,_ in terms];number=math.prod(len(v) for v in choices)
        if number>81:raise ValueError('单通道局部赋值超过81')
        assignments+=number;by_z={}
        for assignment in itertools.product(*choices):
            acc=point['acc'][c]+sum(w*v for (_,w),v in zip(terms,assignment))
            if not 0<=acc<=255*65536:raise ValueError('实际clip域下局部acc越RGB8')
            z=(acc+32768)//65536-point['rgb'][c];masks=by_z.setdefault(z,{i:0 for i,_ in terms})
            for (i,_),v in zip(terms,assignment):masks[i]|=1<<(v+1)
        groups.append(by_z)
    retained=[triple for triple in point['allowed'] if all(triple[c] in groups[c] for c in range(3))]
    supports={i:0 for i in point['variables']}
    for c in range(3):
        for z in sorted({row[c] for row in retained}):
            for i,mask in groups[c][z].items():supports[i]|=mask
    return supports,len(retained),assignments


def propagate(problem,gates):
    domains,points,incidence=compile_points(problem)
    if len(domains)>gates['node_variables_max'] or len(points)>gates['points_max']:raise ValueError('问题规模超过GAC预定门')
    queue=deque(range(len(points)));queued=set(queue);certificate=[];revisions=assignments=0
    def finish(status,reason,**extra):
        return {'status':status,'reason':reason,'domain_masks':domains,'certificate':certificate,'point_revisions':revisions,
            'local_assignments':assignments,'deletions':sum(r['kind']=='remove_value' for r in certificate),'search_calls':0,**extra}
    while queue:
        if revisions>=gates['point_revisions_max']:return finish('GAC_RESOURCE_STOP','point_revisions_gate')
        p=queue.popleft();queued.remove(p);point=points[p]
        needed=sum(math.prod(len(values(domains[i])) for i,_ in terms) for terms in point['terms'])
        if assignments+needed>gates['local_assignments_max']:return finish('GAC_RESOURCE_STOP','local_assignments_gate')
        support,retained,used=supported_masks(point,domains);assert used==needed;revisions+=1;assignments+=used
        if retained==0 and not point['variables']:
            certificate.append({'kind':'constant_point_empty','point':p});return finish('GAC_CONTRADICTION','constant_point_empty',empty_point=p)
        for i in point['variables']:
            for value in values(domains[i] & ~support[i]):
                if len(certificate)>=gates['deletions_max']:return finish('GAC_RESOURCE_STOP','deletions_gate')
                before=domains[i];domains[i]&=~(1<<(value+1))
                certificate.append({'kind':'remove_value','point':p,'variable':i,'value':value,'domain_before':before,
                    'domain_after':domains[i],'supported_mask_primary':support[i]})
                if not domains[i]:return finish('GAC_CONTRADICTION','empty_domain',empty_variable=i)
                for neighbor in incidence[i]:
                    if neighbor not in queued:queue.append(neighbor);queued.add(neighbor)
    return finish('GAC_FIXPOINT_UNDECIDED','nonempty_fixpoint')
