"""质量目标不能因修改量提前停止；同max下仍改善原历史缺口。"""
import numpy as np
from lutlab import automatic_compensation as ac,interp,io,joint_interval as ji,joint_minimax as jm


def test_direct_quality_search_reaches_exact_map_beyond_one_step_minimum_change():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[0,0,128],[0,0,255]],np.uint8)
    truth = np.array([[100,100,98],[100,100,100],[100,100,102]],np.uint8)
    old = np.sum((interp.apply_tetra_q16(model,points).astype(int)-truth)**2,axis=1)
    groups = [{"histogram":[[int(d),1]],"constraints":[{"threshold_squared":int(d),"allowed_tail_pixels":0}],"costs":[0]} for d in old]
    p = ji.Problem(model,points,truth,np.eye(3,dtype=np.int64),{"groups":groups,"loss":0},ac.pairs(np.bincount(old)),[0,1],max_delta=2,rgb_max=2)
    result = jm.solve(p,lambda m,d:{"record":"解"+str(d),"accepted":True})
    assert result["incumbent"]["objective"] == [0,0,0,4] and result["incumbent"]["deltas"] == [-2,2]
    assert sum(t["covered_assignments"] for t in result["terminals"]) == 25


def test_same_maximum_can_reduce_historical_loss_with_exact_equal_mean():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[0,0,1],[255,255,255]],np.uint8)
    truth = np.array([[100,100,80],[100,100,130],[100,100,50]],np.uint8)
    hist = [[400,1],[900,1],[2500,1]]
    group = {"histogram":hist,"constraints":[{"threshold_squared":400,"allowed_tail_pixels":1}],"costs":[500]}
    p = ji.Problem(model,points,truth,np.ones((1,3),np.int64),{"groups":[group],"loss":500},hist,[0],max_delta=1,rgb_max=50)
    result = jm.solve(p,lambda m,d:{"record":"联合","accepted":True})
    assert result["incumbent"]["objective"] == [2500,482,3782,1] and result["incumbent"]["deltas"] == [1]
