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


def screening_fixture():
    model,_,_,_,_,_,_,moves = fixture()
    points = np.array([[255,0,0],[255,127,0],[0,0,0]],np.uint8)
    truth = np.array([[100,100,98],[100,100,100],[100,100,100]],np.uint8)
    photos = {"groups":[{"histogram":[[d,1]],"constraints":[{"threshold_squared":0,"allowed_tail_pixels":0}],"costs":[d]} for d in (4,0,0)],"loss":4}
    state = ac.ConditionalScorer(model,points,truth,np.eye(3,dtype=np.int64),photos,[[0,2],[4,1]],range(8))
    return model,state,moves


def test_screen_excludes_attractive_uncompensable_probe_before_ranking():
    model,state,moves = screening_fixture()
    proposal = ws.propose(model,[0,1,2,3],moves,state,range(8))
    assert proposal["proposals"][0]["helper"] == {"node":4,"channel":2,"delta":-2}
    result = ws.screen(proposal,state,max_delta=2,rgb_max=2,max_assignments=1000)
    assert result["proposals"][0]["necessary_screen"] == {"not_excluded":False,"certificate":{"kind":"rms","group":1,"sse_delta_lower":"1"}}
    assert result["selected_proposal"]["node"] != 4
    # 独立解析权重：G=127混合点只受新4和旧6影响，三个保留坐标完全不能补偿。
    for delta in (-2,-1,1,2):
        blue = ((100+delta)*32897+100*32639+32768)//65536
        assert blue != 100
    assert np.all(model.nodes == 100)


def test_all_probes_excluded_returns_no_replacement_without_relaxing_guard():
    model,state,moves = screening_fixture()
    proposal = ws.propose(model,[0,1,2,3],moves,state,range(5))
    result = ws.screen(proposal,state,max_delta=2,rgb_max=2,max_assignments=1000)
    assert result["screening"]["not_excluded"] == 0
    assert result["selected_proposal"] is None and result["replacement_nodes"] is None
