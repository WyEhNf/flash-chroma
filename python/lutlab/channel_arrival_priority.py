"""以已获得的九项预算选择节点；目标可为p99计数或max计数。"""
from __future__ import annotations
import numpy as np


def select(change,bad,colours,colour,directions,allowance,priority):
    if priority not in (6,7):raise ValueError('只接受p99或max计数目标')
    allowance=np.asarray(allowance,np.float64)
    if allowance.shape!=(9,) or np.any(allowance<0):raise ValueError('不能预支尚未获得的预算')
    chosen=np.full(len(colours),-1,np.int32);predicted=np.zeros(9)
    other=13-priority
    for node in np.flatnonzero(colours==colour):
        best=(0.,0.,0.,0.)
        for direction in range(len(directions)):
            value=change[:,direction,node]
            if bad[direction,node] or np.any(value>1e-11):continue
            score=(value[priority],value[other],value[4],value[0])
            if score<best:chosen[node],best=direction,score
        if chosen[node]>=0:predicted+=change[:,chosen[node],node]
    local=chosen.copy();candidates=[]
    for node in np.flatnonzero(colours==colour):
        old=np.zeros(9) if chosen[node]<0 else change[:,chosen[node],node]
        for direction in range(len(directions)):
            new=change[:,direction,node]
            if not bad[direction,node] and new[priority]<old[priority]:
                candidates.append((new[priority]-old[priority],new[other]-old[other],
                    new[4]-old[4],new[0]-old[0],int(node),direction))
    candidates.sort()
    for _,_,_,_,node,direction in candidates:
        old=np.zeros(9) if chosen[node]<0 else change[:,chosen[node],node]
        new=change[:,direction,node]
        if new[priority]>=old[priority]:continue
        tentative=predicted+new-old
        if np.all(tentative<=allowance+1e-9):chosen[node],predicted=direction,tentative
    moves=np.zeros((len(colours),3),np.int32);accepted=[]
    for node in np.flatnonzero(chosen>=0):
        moves[node]=directions[chosen[node]]
        accepted.append({'node':int(node),'direction':int(chosen[node]),
            'uses_prior_budget':bool(chosen[node]!=local[node]),'deltas':change[:,chosen[node],node].tolist()})
    return moves,predicted,accepted
