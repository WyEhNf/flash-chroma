"""可显式设置p99阈值的末级局部整数规划；保留旧版本及其执行身份。"""
from __future__ import annotations
import itertools
import math
import numpy as np
from scipy.optimize import Bounds
from . import channel_coordinates as cc,channel_global_nodes as cg,io
from .integer_last_milp import Rows,add_norm_cut


def build(model,arrivals,reference,frequency,mass,baseline,*,target_squared=49,node_radius=2,p99_squared=9):
    if not 0<=p99_squared<target_squared or not 0<=node_radius<=255:raise ValueError('目标阈值或节点盒非法')
    unique,inverse=np.unique(arrivals,axis=0,return_inverse=True)
    indices,weights=cg.design(model,unique);active=np.unique(indices[weights>0]);mapping=np.zeros(model.m**3,np.int32)
    mapping[active]=np.arange(len(active),dtype=np.int32);indices=mapping[indices]
    old_nodes=model.nodes.reshape(-1,3)[active].astype(np.int32);old_output=cc.predict(model,unique)
    nnode,ninput,npair=len(active),len(unique),len(reference);start=0;block={}
    for name,size in (('node',3*nnode),('output',3*ninput),('square',3*npair),('norm',npair),('outlier',npair),('cvar',npair),('movement',3*nnode)):
        block[name]=np.arange(start,start+size,dtype=np.int32);start+=size
    for name in ('node','output','square','movement'):block[name]=block[name].reshape(-1,3)
    lower=np.zeros(start);upper=np.full(start,np.inf);integer=np.zeros(start,np.uint8);cost=np.zeros(start)
    lower[block['node']]=np.maximum(old_nodes-node_radius,0);upper[block['node']]=np.minimum(old_nodes+node_radius,255)
    integer[block['node']]=1;integer[block['output']]=1;integer[block['outlier']]=1
    upper[block['outlier']]=1;upper[block['square']]=target_squared;upper[block['norm']]=math.sqrt(target_squared)
    upper[block['cvar']]=math.sqrt(target_squared);upper[block['movement']]=node_radius;radius=math.isqrt(target_squared)
    for i in range(ninput):
        gold=reference[inverse==i].astype(np.int32)
        lower[block['output'][i]]=np.maximum.reduce((old_output[i].astype(np.int32)-node_radius,gold.max(axis=0)-radius,np.zeros(3,np.int32)))
        upper[block['output'][i]]=np.minimum.reduce((old_output[i].astype(np.int32)+node_radius,gold.min(axis=0)+radius,np.full(3,255,np.int32)))
    if np.any(lower>upper):raise ValueError('目标球必要坐标盒没有交集')
    cost[block['norm']]=frequency/frequency.sum();cost[block['movement']]=1e-8;rows=Rows(start)
    for i in range(ninput):
        for c in range(3):
            terms=[(block['node'][indices[c,i,v],c],weights[c,i,v]/io.ONE) for v in range(4)]
            rows.add([*terms,(block['output'][i,c],-1)],-.5,.5-1/io.ONE)
    for i in range(nnode):
        for c in range(3):
            n,a=block['node'][i,c],block['movement'][i,c];old=int(old_nodes[i,c])
            rows.add([(a,1),(n,-1)],lo=-old);rows.add([(a,1),(n,1)],lo=old)
    outlier_rows=[];cvar_rows=[]
    for p in range(npair):
        y=block['output'][inverse[p]];s=block['square'][p]
        for c in range(3):
            for k in range(-radius-1,radius+1):
                slope=2*k+1;rows.add([(s[c],1),(y[c],-slope)],lo=-slope*int(reference[p,c])-k*(k+1))
        rows.add([(v,1) for v in s],hi=target_squared)
        outlier_rows.append(len(rows.lo))
        rows.add([*[(v,1) for v in s],(block['outlier'][p],-(target_squared-p99_squared))],hi=p99_squared)
        cvar_rows.append(len(rows.lo));rows.add([(block['cvar'][p],1),(block['norm'][p],-1)],lo=-math.sqrt(p99_squared))
    rows.add([(block['norm'][p],frequency[p]) for p in range(npair)],hi=baseline[0])
    rows.add([(block['norm'][p],mass[p]) for p in range(npair)],hi=baseline[1])
    rows.add([(block['square'][p,c],frequency[p]) for p in range(npair) for c in range(3)],hi=baseline[2])
    rows.add([(block['square'][p,c],mass[p]) for p in range(npair) for c in range(3)],hi=baseline[3])
    rows.add([(block['outlier'][p],frequency[p]) for p in range(npair)],hi=baseline[6])
    old_delta=old_output[inverse].astype(np.int32)-reference.astype(np.int32);old_distance=np.sqrt(np.sum(old_delta*old_delta,axis=1))
    old_excess=float(frequency@np.maximum(old_distance-math.sqrt(p99_squared),0));excess_row=len(rows.lo)
    rows.add([(block['cvar'][p],frequency[p]) for p in range(npair)],hi=old_excess)
    state={'rows':rows,'block':block,'active':active,'inverse':inverse,'unique':unique,'reference':reference,
        'bounds':Bounds(lower,upper),'integrality':integer,'cost':cost,'seen':set(),'node_radius':node_radius,
        'target_squared':target_squared,'p99_squared':p99_squared,'outlier_rows':outlier_rows,'cvar_rows':cvar_rows,'excess_row':excess_row}
    for p in range(npair):
        for vector in itertools.product((-1,0,1),repeat=3):
            if any(vector):add_norm_cut(state,p,vector)
        add_norm_cut(state,p,old_delta[p])
    return state
