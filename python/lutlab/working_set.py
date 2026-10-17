"""保留父块实际活跃坐标，以真实历史尾部反馈选择一个新坐标。"""
from . import automatic_compensation as ac


def propose(model,parent_nodes,parent_moves,state,pool,*,channel=2,deltas=(-2,-1,1,2),max_fresh_nodes=8):
    if ac.signature(model) != state.signature:raise ValueError("工作集与冻结状态签名不同")
    changed = {m["node"] for m in parent_moves}
    if len(changed) != len(parent_moves) or not changed <= set(parent_nodes):raise ValueError("父变更节点不是旧工作集的唯一子集")
    for move in parent_moves:
        if model.nodes.reshape(-1,3)[move["node"]].tolist() != move["after"]:raise ValueError("父节点终值与当前模型不同")
    keep = [n for n in parent_nodes if n in changed]
    dropped = [n for n in parent_nodes if n not in changed]
    fresh = sorted(set(pool)-set(parent_nodes))
    if len(dropped) != 1 or not keep or not fresh or len(fresh) > max_fresh_nodes:raise ValueError("本阶段要求恰替换一个不活跃坐标，候选池不截断")
    if channel not in (0,1,2) or len(set(deltas)) != len(deltas) or any(type(d) is not int or not 1 <= abs(d) <= 4 for d in deltas):raise ValueError("工作集探针不是冻结的有限通道/幅度")
    proposals = []
    for node in fresh:
        for delta in deltas:
            old = int(model.nodes.reshape(-1,3)[node,channel])
            if not 0 <= old+delta <= 255:continue
            candidate = ac.clone(model)
            candidate.nodes.reshape(-1,3)[node,channel] = old+delta
            score = state.score(candidate)
            key = [score["primary_loss"],len(score["fixed_failed"]),score["max_squared"],int(score["full_sse_delta"]),node,channel,delta]
            proposals.append({"helper":{"node":node,"channel":channel,"delta":delta},"rank_key":key,"score":score})
    proposals.sort(key=lambda p:tuple(p["rank_key"]))
    if not proposals:raise ValueError("工作集没有合法新坐标探针")
    return {"baseline_signature":state.signature,"control_nodes":list(parent_nodes),"kept_nodes":keep,"dropped_nodes":dropped,"fresh_nodes":fresh,"proposals":proposals,
        "replacement_nodes":keep+[proposals[0]["helper"]["node"]],"scope":"单坐标探针只作新变量提议，不承诺可提交；完整联合箱仍重新满足全部保护，不声称遍历所有工作集"}


def screen(proposal,state,*,max_delta,rgb_max,max_assignments):
    """固定每个探针，让保留坐标自由；必要界失败才排除，未排除不是可行证明。"""
    from . import joint_interval as ji
    if proposal["baseline_signature"] != state.signature:raise ValueError("筛查起点签名不同")
    problems = {}
    eligible = []
    for item in proposal["proposals"]:
        h = item["helper"]
        if h["node"] not in problems:
            problems[h["node"]] = ji.Problem(state.model,state.points,state.truth,state.frequency,state.photos,state.full,
                [h["node"]]+proposal["kept_nodes"],max_delta=max_delta,rgb_max=rgb_max,channel=h["channel"],max_assignments=max_assignments)
        p = problems[h["node"]]
        if h["delta"] not in p.domains[0]:raise ValueError("探针不在冻结联合域中")
        proof = p.certificate([h["delta"]],p.matrix[:,0]*h["delta"])
        item["necessary_screen"] = {"not_excluded":proof is None,"certificate":proof}
        if proof is None:eligible.append(item)
    selected = eligible[0]["helper"] if eligible else None
    proposal.update(selected_proposal=selected,replacement_nodes=proposal["kept_nodes"]+[selected["node"]] if selected else None,
        screening={"max_delta":max_delta,"rgb_max":rgb_max,"probes":len(proposal["proposals"]),"not_excluded":len(eligible),
            "scope":"每个探针固定该新坐标，保留坐标仍自由；整数输出区间必要界排除不能补偿的探针，不证明未排除者可行，不排除整个新节点的其他值"})
    return proposal
