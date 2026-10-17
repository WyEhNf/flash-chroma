"""在同一冻结节点状态构造有限主改/辅助/联合反事实；联合输出必须整块重放。"""
import numpy as np
from . import io


def family(model,config):
    primary,helper = config["primary"],config["helper"]
    p,h = primary["node"],helper["node"]
    if any(type(n) is not int or not 0 <= n < model.m**3 for n in (p,h)) or p == h:
        raise ValueError("主改与辅助必须是两个不同的合法节点")
    current = model.nodes.reshape(-1,3)
    for item in (primary,helper):
        before = item["before"]
        if len(before) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in before) or current[item["node"]].tolist() != before:
            raise ValueError("冻结节点前值不匹配，不能沿用旧补偿")
    after = primary["after"]
    if len(after) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in after) or after == primary["before"]:
        raise ValueError("主改后值必须是不同的合法RGB8")
    channel,deltas = helper["channel"],helper["deltas"]
    if type(channel) is not int or channel not in (0,1,2) or not 1 <= len(deltas) <= 4 or len(set(deltas)) != len(deltas):
        raise ValueError("辅助只允许一个通道的1至4个固定幅度")
    if any(type(d) is not int or not 1 <= abs(d) <= 4 or not 0 <= helper["before"][channel]+d <= 255 for d in deltas):
        raise ValueError("辅助幅度越界，不允许uint8绕回或隐式裁剪")
    idx,frac = model.tables()
    def candidate(moves):
        value = io.SparseLut(model.grid.copy(),model.nodes.copy(),idx.copy(),frac.copy())
        for node,rgb in moves:value.nodes.reshape(-1,3)[node] = rgb
        return value
    outputs = {"baseline":(candidate([]),{"role":"control"}),
        "primary":(candidate([(p,after)]),{"role":"primary","scope":"仅固定主改，不能使用旧辅助收益判定"})}
    for i,delta in enumerate(deltas,1):
        value = helper["before"].copy()
        value[channel] += delta
        info = {"helper_delta":delta,"primary_node":p,"helper_node":h,"scope":"同一冻结起点的反事实；支撑重叠时不能相加单改RGB输出或预算"}
        outputs[f"helper_{i}"] = (candidate([(h,value)]),{"role":"helper",**info})
        outputs[f"joint_{i}"] = (candidate([(p,after),(h,value)]),{"role":"joint",**info})
    return outputs


def interaction(baseline,primary,helper,joint):
    arrays = [np.asarray(a,np.int16) for a in (baseline,primary,helper,joint)]
    if any(a.shape != arrays[0].shape for a in arrays) or arrays[0].ndim != 2 or arrays[0].shape[1] != 3:
        raise ValueError("联合舍入归因需要同一批RGB输出")
    residue = arrays[3]-(arrays[1]+arrays[2]-arrays[0])
    return {"output_additivity_mismatch_colours":int(np.count_nonzero(np.any(residue != 0,axis=1))),
        "output_additivity_max_component":int(np.max(np.abs(residue),initial=0)),
        "scope":"实际整块输出减去两单改输出之和再减基线的预测；只诊断舍入非可加，不作接受代理"}
