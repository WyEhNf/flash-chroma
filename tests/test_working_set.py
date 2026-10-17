"""解析例验证旧变量无法改进、新变量可解，并拒绝陈旧工作集。"""
import numpy as np
import pytest
from lutlab import automatic_compensation as ac,interp,io,joint_interval as ji,joint_minimax as jm,working_set as ws


def fixture():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    points = np.array([[255,0,0],[0,0,0]],np.uint8)
    truth = np.array([[100,100,98],[100,100,100]],np.uint8)
    photos = {"groups":[{"histogram":[[4,1]],"constraints":[{"threshold_squared":0,"allowed_tail_pixels":0}],"costs":[4]},
        {"histogram":[[0,1]],"constraints":[{"threshold_squared":0,"allowed_tail_pixels":0}],"costs":[0]}],"loss":4}
    frequency = np.eye(2,dtype=np.int64)
    hist = [[0,1],[4,1]]
    state = ac.ConditionalScorer(model,points,truth,frequency,photos,hist,list(range(8)))
    moves = [{"node":n,"before":[100,100,99],"after":[100,100,100]} for n in (0,1,2)]
    return model,points,truth,frequency,photos,hist,state,moves


def test_replacement_solves_colour_outside_control_node_support():
    model,points,truth,frequency,photos,hist,state,moves = fixture()
    proposal = ws.propose(model,[0,1,2,3],moves,state,range(8))
    assert proposal["kept_nodes"] == [0,1,2] and proposal["dropped_nodes"] == [3]
    assert proposal["proposals"][0]["helper"] == {"node":4,"channel":2,"delta":-2}
    objectives = []
    for nodes in (proposal["control_nodes"],proposal["replacement_nodes"]):
        p = ji.Problem(model,points,truth,frequency,photos,hist,nodes,max_delta=2,rgb_max=2)
        result = jm.solve(p,lambda m,d:{"record":"解析解","accepted":True})
        objectives.append(result["incumbent"]["objective"])
        assert sum(t["covered_assignments"] for t in result["terminals"]) == 625
    assert objectives == [[4,4,4,0],[0,0,0,2]]


def test_stale_model_or_parent_endpoint_cannot_choose_coordinate():
    model,_,_,_,_,_,state,moves = fixture()
    moves[0]["after"][2] = 101
    with pytest.raises(ValueError,match="终值"):ws.propose(model,[0,1,2,3],moves,state,range(8))
    model.nodes[-1,-1,-1,2] = 101
    with pytest.raises(ValueError,match="签名"):ws.propose(model,[0,1,2,3],moves,state,range(8))
