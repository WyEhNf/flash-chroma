"""真实Q16重叠舍入下，单改违反局部预算而有限联合块同时满足。"""
import numpy as np
import pytest
from lutlab import interp,io,local_compensation as lc


def test_overlapping_block_repairs_single_move_budget_and_exposes_nonadditive_output():
    model = io.SparseLut(io.uniform_grid(2),np.full((2,2,2,3),100,np.uint8))
    config = {"primary":{"node":0,"before":[100,100,100],"after":[100,100,98]},
        "helper":{"node":1,"before":[100,100,100],"channel":2,"deltas":[1,2]}}
    variants = lc.family(model,config)
    points = np.array([[0,0,0],[0,0,64],[0,0,128],[0,0,255]],np.uint8)
    target = np.full(points.shape,100,np.uint8)
    target[:,2] = [98,99,100,102]
    predictions = {name:interp.apply_tetra_q16(value,points) for name,(value,info) in variants.items()}
    squared = {name:np.sum((value.astype(int)-target)**2,axis=1) for name,value in predictions.items()}
    assert np.any(squared["primary"] > squared["baseline"]) and np.any(squared["helper_2"] > squared["baseline"])
    assert np.all(squared["joint_1"] <= squared["baseline"]) and np.all(squared["joint_2"] == 0)
    info = lc.interaction(*(predictions[n] for n in ("baseline","primary","helper_2","joint_2")))
    assert info["output_additivity_mismatch_colours"] == 1 and info["output_additivity_max_component"] == 1
    assert predictions["joint_2"][1,2] == 99 and (predictions["primary"][1].astype(int)+predictions["helper_2"][1]-predictions["baseline"][1])[2] == 100
    assert np.all(model.nodes == 100)
    model.nodes[0,0,1,2] = 101
    with pytest.raises(ValueError,match="冻结节点前值"):lc.family(model,config)
