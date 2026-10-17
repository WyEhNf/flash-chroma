"""小型解析联合解、非平方RGB及不可行箱验证安全剪枝与最小修改。"""
import itertools
import numpy as np
from lutlab import automatic_compensation as ac,interp,io,joint_interval as ji


def problem(model,points,truth,nodes,delta,maximum):
    old = np.sum((interp.apply_tetra_q16(model,points).astype(int)-truth)**2,axis=1)
    groups = [{"histogram":[[int(d),1]],"constraints":[{"threshold_squared":int(d),"allowed_tail_pixels":0}],"costs":[0]} for d in old]
    return ji.Problem(model,points,truth,np.eye(len(points),dtype=np.int64),{"groups":groups,"loss":0},ac.pairs(np.bincount(old)),nodes,max_delta=delta,rgb_max=maximum)


def run(p):return ji.solve(p,lambda model,deltas:{"record":"解_"+"_".join(map(str,deltas)),"accepted":True})


def test_three_nodes_must_change_together_and_minimum_cost_is_proven():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,0],[127,0,0],[0,127,0]],np.uint8)
    target = np.full(points.shape,100,np.uint8)
    target[0,2] = 101
    p = problem(model,points,target,[0,2,4],1,0)
    result = run(p)
    assert result["incumbent"]["deltas"] == [1,-1,-1] and result["incumbent"]["l1"] == 3
    assert result["minimum_l1_proven_within_box"] and sum(t["covered_assignments"] for t in result["terminals"]) == 27
    assert len(result["terminals"]) < 27 and np.all(model.nodes == 100)


def test_rounding_half_step_with_non_square_baseline_matches_independent_enumeration():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,128]],np.uint8)
    target = np.array([[99,100,101]],np.uint8)
    p = problem(model,points,target,[0,1],1,1)
    feasible = []
    for a,b in itertools.product(range(-1,2),repeat=2):
        # B轴128的精确Q16分数为32897，half-up端点区别两个节点的一码值变化。
        blue = ((100+a)*(65536-32897)+(100+b)*32897+32768)//65536
        if 1+(blue-101)**2 <= 1:feasible.append(abs(a)+abs(b))
    result = run(p)
    assert result["incumbent"]["l1"] == min(feasible) == 1
    assert result["incumbent"]["deltas"] == [0,1]


def test_adjacent_two_code_jump_is_infeasible_in_bounded_linear_edge():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[0,0,127],[0,0,128]],np.uint8)
    target = np.array([[100,100,99],[100,100,101]],np.uint8)
    p = problem(model,points,target,[0,1],2,0)
    assert not any([((100+a)*(65536-f)+(100+b)*f+32768)//65536 for f in (32639,32897)] == [99,101]
        for a,b in itertools.product(range(-2,3),repeat=2))
    result = run(p)
    assert result["incumbent"] is None and sum(t["covered_assignments"] for t in result["terminals"]) == 25
