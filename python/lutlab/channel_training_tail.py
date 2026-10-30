"""在旧九项完整域预算之外显式控制原训练整数频数的尾部。"""
from __future__ import annotations
import numpy as np
from numba import njit,prange
from . import channel_arrival_nodes as an,channel_tail_nodes as tail,io


@njit(cache=True,parallel=True)
def training_gains(indices,weights,acc,reference,suffix,training_count,nodes,colours,colour,parts,target_sq,directions,max_shift):
    size=len(nodes);ndir=len(directions)
    private=np.zeros((parts,2,ndir,size),np.float64);invalid=np.zeros(parts,np.int64)
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
            for direction in range(ndir):
                if not legal[direction,selected]:continue
                vector=directions[direction]
                new=tail.chain_square(value[0,vector[0]+max_shift],value[1,vector[1]+max_shift],value[2,vector[2]+max_shift],suffix,reference[point])
                count=training_count[point]
                private[part,0,direction,selected]+=count*(int(new>target_sq)-int(old>target_sq))
                private[part,1,direction,selected]+=count*(max(new-target_sq,0)-max(old-target_sq,0))
    return private.sum(axis=0),invalid.sum()


def measure(output,reference,suffix,frequency,mass,training_count,p99_sq,max_target_sq,training_target_sq):
    nine,squared=an.measure(output,reference,suffix,frequency,mass,p99_sq,max_target_sq)
    training_count=np.asarray(training_count)
    if training_count.dtype!=np.int64 or training_count.shape!=squared.shape or np.any(training_count<0):
        raise ValueError('训练计数必须为逐支撑非负int64')
    extra=np.asarray([training_count@(squared>training_target_sq),training_count@np.maximum(squared-training_target_sq,0)],np.float64)
    return np.concatenate((nine,extra)),squared


def select(change,bad,colours,colour,directions,allowance):
    """仅用已经取得的十一项余额交换训练尾部计数；不改旧选择器。"""
    change=np.asarray(change,np.float64);allowance=np.asarray(allowance,np.float64)
    if change.shape!=(11,len(directions),len(colours)) or bad.shape!=(len(directions),len(colours)):
        raise ValueError('十一项收益与节点维度不符')
    if allowance.shape!=(11,) or np.any(allowance<0) or not np.all(np.isfinite(allowance)) or not np.all(np.isfinite(change)):
        raise ValueError('不能预支或使用非有限预算')
    chosen=np.full(len(colours),-1,np.int32);predicted=np.zeros(11)
    for node in np.flatnonzero(colours==colour):
        best=(0.,0.,0.,0.)
        for direction in range(len(directions)):
            value=change[:,direction,node]
            if bad[direction,node] or np.any(value>1e-11):continue
            score=(value[9],value[10],value[7],value[0])
            if score<best:chosen[node],best=direction,score
        if chosen[node]>=0:predicted+=change[:,chosen[node],node]
    local=chosen.copy();candidates=[]
    for node in np.flatnonzero(colours==colour):
        old=np.zeros(11) if chosen[node]<0 else change[:,chosen[node],node]
        for direction in range(len(directions)):
            new=change[:,direction,node]
            if not bad[direction,node] and new[9]<old[9]:
                candidates.append((new[9]-old[9],new[10]-old[10],new[7]-old[7],new[0]-old[0],int(node),direction))
    candidates.sort()
    for _,_,_,_,node,direction in candidates:
        old=np.zeros(11) if chosen[node]<0 else change[:,chosen[node],node];new=change[:,direction,node]
        if new[9]>=old[9]:continue
        tentative=predicted+new-old
        if np.all(tentative<=allowance+1e-9):chosen[node],predicted=direction,tentative
    moves=np.zeros((len(colours),3),np.int32);accepted=[]
    for node in np.flatnonzero(chosen>=0):
        moves[node]=directions[chosen[node]]
        accepted.append({'node':int(node),'direction':int(chosen[node]),'uses_prior_budget':bool(chosen[node]!=local[node]),
            'deltas':change[:,chosen[node],node].tolist()})
    return moves,predicted,accepted
