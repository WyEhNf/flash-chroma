"""固定前后缀下按(到达RGB,真值RGB)压缩完整支撑，保留精确整数频数。"""
from __future__ import annotations
import numpy as np
from numba import njit,prange
from . import channel_tail_nodes as tail,io

@njit(cache=True,parallel=True)
def gains(indices,weights,acc,reference,suffix,frequency,mass,nodes,colours,colour,caps,root,parts,p99_sq,max_target_sq,directions,max_shift):
    size=len(nodes)
    ndir=len(directions)
    private=np.zeros((parts,9,ndir,size),np.float64)
    bad=np.zeros((parts,ndir,size),np.int64);invalid=np.zeros(parts,np.int64)
    legal=np.ones((ndir,size),np.uint8)
    for node in prange(size):
        for direction in range(ndir):
            for channel in range(3):
                if not 0<=np.int64(nodes[node,channel])+directions[direction,channel]<=255:legal[direction,node]=0
    for part in prange(parts):
        value=np.empty((3,2*max_shift+1),np.int64)
        for point in range(len(reference)*part//parts,len(reference)*(part+1)//parts):
            selected=-1
            for channel in range(3):
                weight=0;channel_node=-1
                for vertex in range(4):
                    node,w=indices[channel,point,vertex],weights[channel,point,vertex]
                    if w>0 and colours[node]==colour:
                        if channel_node>=0:invalid[part]+=1
                        channel_node=node;weight=w
                if channel_node>=0:
                    if selected>=0 and selected!=channel_node:invalid[part]+=1
                    selected=channel_node
                for step in range(2*max_shift+1):value[channel,step]=(np.int64(acc[point,channel])+(step-max_shift)*weight+io.ONE//2)>>io.Q
            if selected<0:continue
            old=tail.chain_square(value[0,max_shift],value[1,max_shift],value[2,max_shift],suffix,reference[point])
            if old>caps[point]:invalid[part]+=1
            for direction in range(ndir):
                if not legal[direction,selected]:continue
                vector=directions[direction]
                new=tail.chain_square(value[0,vector[0]+max_shift],value[1,vector[1]+max_shift],value[2,vector[2]+max_shift],suffix,reference[point])
                distance,square=root[new]-root[old],new-old
                count=frequency[point]
                private[part,0,direction,selected]+=count*distance
                private[part,1,direction,selected]+=mass[point]*distance
                private[part,2,direction,selected]+=count*square
                private[part,3,direction,selected]+=mass[point]*square
                private[part,4,direction,selected]+=count*(max(new-p99_sq,0)-max(old-p99_sq,0))
                private[part,5,direction,selected]+=count*(max(new-36,0)-max(old-36,0))
                private[part,6,direction,selected]+=count*(int(new>p99_sq)-int(old>p99_sq))
                private[part,7,direction,selected]+=count*(int(new>max_target_sq)-int(old>max_target_sq))
                private[part,8,direction,selected]+=count*(max(new-49,0)-max(old-49,0))
                bad[part,direction,selected]+=count*int(new>caps[point])
    result,forbidden=private.sum(axis=0),bad.sum(axis=0)
    for node in prange(size):
        for direction in range(ndir):
            if not legal[direction,node]:forbidden[direction,node]+=1
    return result,forbidden,invalid.sum()


@njit(cache=True,parallel=True)
def apply_accumulator(indices,weights,acc,moves):
    for point in prange(len(acc)):
        for channel in range(3):
            for vertex in range(4):
                acc[point,channel]+=weights[channel,point,vertex]*moves[indices[channel,point,vertex],channel]


def measure(output,reference,suffix,frequency,mass,p99_sq,max_target_sq):
    keys=(output[:,0].astype(np.uint32)<<16)|(output[:,1].astype(np.uint32)<<8)|output[:,2]
    delta=suffix[keys].astype(np.int32)-reference.astype(np.int32)
    square=np.sum(delta*delta,axis=1,dtype=np.int32)
    distance=np.sqrt(square.astype(np.float64))
    values=np.asarray([frequency@distance,mass@distance,frequency@square,mass@square,
        frequency@np.maximum(square-p99_sq,0),frequency@np.maximum(square-36,0),
        frequency@(square>p99_sq),frequency@(square>max_target_sq),frequency@np.maximum(square-49,0)],np.float64)
    return values,square


def select(change,bad,colours,colour,directions):
    """先取得不退局部收益，再以整批九项预算交换减少原最大误差计数。"""
    chosen=np.full(len(colours),-1,np.int32);predicted=np.zeros(9)
    for node in np.flatnonzero(colours==colour):
        best=(0.,0.,0.)
        for direction in range(len(directions)):
            value=change[:,direction,node]
            if bad[direction,node] or np.any(value>1e-11):continue
            score=(value[0],value[7],value[4])
            if score<best:chosen[node],best=direction,score
        if chosen[node]>=0:predicted+=change[:,chosen[node],node]
    local=chosen.copy();candidates=[]
    for node in np.flatnonzero(colours==colour):
        old=np.zeros(9) if chosen[node]<0 else change[:,chosen[node],node]
        for direction in range(len(directions)):
            if not bad[direction,node] and change[7,direction,node]<old[7]:
                candidates.append((change[7,direction,node]-old[7],change[8,direction,node]-old[8],
                    change[0,direction,node]-old[0],int(node),direction))
    candidates.sort()
    for _,_,_,node,direction in candidates:
        old=np.zeros(9) if chosen[node]<0 else change[:,chosen[node],node];new=change[:,direction,node]
        if new[7]>=old[7]:continue
        tentative=predicted+new-old
        if np.all(tentative<=1e-9):chosen[node],predicted=direction,tentative
    moves=np.zeros((len(colours),3),np.int32);accepted=[]
    for node in np.flatnonzero(chosen>=0):
        moves[node]=directions[chosen[node]]
        accepted.append({'node':int(node),'direction':int(chosen[node]),'budget_exchange':bool(chosen[node]!=local[node]),
                         'deltas':change[:,chosen[node],node].tolist()})
    return moves,predicted,accepted
