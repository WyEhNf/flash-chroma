"""以固定起点的整体九项预算进行max计数交换；不借用未来批次未取得的余额。"""
from __future__ import annotations
import numpy as np
from . import channel_arrival_nodes as an


def select(change,bad,colours,colour,directions,allowance):
    moves,predicted,local=an.select(change,bad,colours,colour,directions)
    chosen=np.full(len(colours),-1,np.int32)
    for entry in local:chosen[entry['node']]=entry['direction']
    local_choice=chosen.copy();candidates=[]
    for node in np.flatnonzero(colours==colour):
        old=np.zeros(9) if chosen[node]<0 else change[:,chosen[node],node]
        for direction in range(len(directions)):
            new=change[:,direction,node]
            if not bad[direction,node] and new[7]<old[7]:
                candidates.append((new[7]-old[7],new[8]-old[8],new[0]-old[0],int(node),direction))
    candidates.sort()
    for _,_,_,node,direction in candidates:
        old=np.zeros(9) if chosen[node]<0 else change[:,chosen[node],node];new=change[:,direction,node]
        if new[7]>=old[7]:continue
        tentative=predicted+new-old
        if np.all(tentative<=allowance+1e-9):chosen[node],predicted=direction,tentative
    moves=np.zeros((len(colours),3),np.int32);accepted=[]
    for node in np.flatnonzero(chosen>=0):
        moves[node]=directions[chosen[node]]
        accepted.append({'node':int(node),'direction':int(chosen[node]),'uses_prior_budget':bool(chosen[node]!=local_choice[node]),
                         'deltas':change[:,chosen[node],node].tolist()})
    return moves,predicted,accepted
