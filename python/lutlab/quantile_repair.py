"""固定轴表下，以真实图片分位缺口和完整域证书选择单/双节点修改。"""
import itertools
import numpy as np
from . import error_analysis as ea, full_domain_guard as fg, interp, io, tail_repair as tr


def focus_design(model,points):
    """热点代理只用于排序，实际接受必须重算图片缺口和完整域，不能相加单点收益。"""
    indices,weights = interp.tetra_index_weights_q(points,*model.tables(),model.m)
    nodes = model.nodes.reshape(-1,3)
    acc = np.sum(weights[:,:,None].astype(np.int64)*nodes[indices],axis=1)
    return indices,weights,acc


def ranked_proposals(model,banks,points,priority,truth):
    indices,weights,acc = focus_design(model,points)
    nodes = model.nodes.reshape(-1,3)
    old_prediction = (acc+32768) >> 16
    old_squared = np.sum((old_prediction-truth.astype(np.int64))**2,axis=1)
    ranked = []
    for node in np.unique(indices[weights > 0]):
        current = nodes[node].astype(np.int64)
        values = set()
        for delta in itertools.product((-1,0,1),repeat=3):
            value = np.clip(current+delta,0,255)
            values.add(tuple(map(int,value)))
        for model_alt in banks:
            other = model_alt.nodes.reshape(-1,3)[node].astype(np.int64)
            for divisor in (1,2):
                value = (current*(divisor-1)+other+divisor//2)//divisor
                values.add(tuple(map(int,value)))
                for channel in range(3):
                    partial = current.copy()
                    partial[channel] = value[channel]
                    values.add(tuple(map(int,partial)))
        values.discard(tuple(map(int,current)))
        own_weight = np.where(indices == node,weights,0).sum(axis=1,dtype=np.int64)
        for value in sorted(values):
            prediction = (acc+own_weight[:,None]*(np.asarray(value)-current)+32768) >> 16
            squared = np.sum((prediction-truth.astype(np.int64))**2,axis=1)
            proxy = sum(int(p)*int(delta) for p,delta in zip(priority,squared-old_squared))
            ranked.append((proxy,tr.Move(0,int(node),value)))
    return sorted(ranked)


def repair(model,banks,domain,photos,*,steps=64,focus_count=64,trial_limit=128,pair_nodes=16,on_accept=None,compensation=None,global_search=None,pair_prefix_expected=None):
    """有限、确定性搜索；每次严格降低整数缺口，保持整个阶段固定的均值/RMS预算。"""
    models = [model]
    batch_config = global_search.get("batch") if global_search else None
    if batch_config is not None:
        from . import primary_batch
        primary_batch.validate(batch_config)
        if global_search.get("method") != "primary_budget":raise ValueError("主改批次需要预算感知全局方法")
    for other in banks:
        if other.m != model.m or not all(np.array_equal(a,b) for a,b in zip(other.tables(),model.tables())):
            raise ValueError("节点候选库必须使用完全相同的权威轴表")
    if fg.signature(models) != domain.model_signature or not np.array_equal(domain.squared,photos.current):
        raise ValueError("图片与完整域状态不匹配")
    log,rejections,compensation_log,global_log = [],{},[],[]
    totals = {"single_trials":0,"pair_trials":0,"generated_single_proposals":0,"compensated_pair_trials":0,
        "global_single_trials":0,"global_pair_trials":0,"three_node_trials":0,"proper_subset_trials":0}
    if batch_config is not None:totals.update(global_batch_trials=0,global_batch_confirmations=0)

    def consider(move,trace=None,lower_bound=None):
        full_trial = domain.trial(models,move)
        rows = full_trial["rows"]
        photo_trial = photos.trial(rows,domain.squared[rows],full_trial["squared"])
        if lower_bound is not None and photo_trial.loss-photos.loss < lower_bound:
            raise AssertionError("全节点单通道代理超过真实缺口变化，不再是下界")
        item = {"moves":[{"node":p.node,"value":list(p.value)} for p in fg.components(move)],
            "before_loss":photos.loss,"loss":photo_trial.loss,"photo_failed":list(photo_trial.failed),"lower_bound_delta":lower_bound,
            "full_failed":[],"accepted":False,"decision":None}
        if trace is not None:trace.append(item)
        if photo_trial.loss >= photos.loss:
            item["decision"] = "tail_loss"
            rejections["tail_loss"] = rejections.get("tail_loss",0)+1
            return None
        if photo_trial.failed:
            item["decision"] = "photo_guard"
            for key in photo_trial.failed:rejections[key] = rejections.get(key,0)+1
            return None
        proof = domain.consider(models,move)
        item["full_failed"] = proof["failed"]
        if not proof["accepted"]:
            item["decision"] = "full_guard"
            for key in proof["failed"]:rejections["full."+key] = rejections.get("full."+key,0)+1
            return None
        if photos.stability is not None:
            failed = photos.stability.check_full(full_trial["hist"],proof["candidate"])
            item["stability_full_failed"] = failed
            if failed:
                item["decision"] = "stability_full"
                for key in failed:rejections[key] = rejections.get(key,0)+1
                return None
        item["accepted"] = True
        item["decision"] = "accepted"
        return photo_trial,proof

    stop = "step_limit"
    for step in range(steps):
        if photos.loss == 0:
            stop = "all_tail_constraints_feasible"
            break
        keys,priority = photos.focus(focus_count)
        if not len(keys):raise AssertionError("尾部缺口非零但没有可定位的颜色")
        truth = domain.truth[keys]
        ranked = ranked_proposals(model,banks,domain.points[keys],priority,truth)
        ranked_scope = "hotspot"
        totals["generated_single_proposals"] += len(ranked)
        accepted = None
        accepted_compensation = None
        accepted_batch = None
        accepted_source = "hotspot"
        primary_cache = {}
        for _,move in ranked[:trial_limit]:
            totals["single_trials"] += 1
            result = consider(move)
            if result is not None:
                accepted = (move,*result)
                break
        if accepted is None and pair_nodes > 1:
            # 先按节点去重，防止前16项全来自同一节点而没有可组合的提案。
            diverse,seen = [],set()
            for score,move in ranked:
                if move.node not in seen:
                    diverse.append((score,move))
                    seen.add(move.node)
                if len(diverse) == pair_nodes:break
            pairs = sorted((a[0]+b[0],tuple(sorted((a[1],b[1])))) for a,b in itertools.combinations(diverse,2))
            for _,moves in pairs:
                totals["pair_trials"] += 1
                move = fg.JointMove(moves)
                result = consider(move)
                if result is not None:
                    accepted = (move,*result)
                    break
        if accepted is None and global_search and len(global_log) < global_search["rounds"]:
            method = global_search.get("method","lower_bound")
            if method == "primary_budget":
                from . import primary_budget
                ranked,info = primary_budget.ranked(model,domain,photos,ordering=global_search["ordering"],cache=primary_cache,
                    trial_limit=trial_limit,max_array_bytes=global_search["max_array_bytes"])
            elif method == "lower_bound":
                from . import quantile_global
                ranked,info = quantile_global.ranked(model,domain,photos,max_array_bytes=global_search["max_array_bytes"])
            else:raise ValueError("未知全局主提案方法")
            ranked_scope = "global"
            info.update(accepted=False,trials=[])
            if batch_config is not None:
                def batch_evaluate(move,trace,lower_bound,kind):
                    field = {"single":"global_single_trials","block":"global_batch_trials","confirmation":"global_batch_confirmations"}[kind]
                    totals[field] += 1
                    return consider(move,trace,lower_bound)
                accepted,details = primary_batch.select(model,ranked[:trial_limit],batch_evaluate,info["trials"],before_loss=photos.loss,**batch_config)
                info["batch_search"] = details
                if accepted is not None:
                    accepted_source = "global_batch" if details["selected_node_count"] > 1 else "global_batch_single"
                    accepted_batch = {k:v for k,v in details.items() if k not in ("trials","confirmation","feasible_singles")}
            else:
                for score,move in ranked[:trial_limit]:
                    totals["global_single_trials"] += 1
                    result = consider(move,info["trials"],score)
                    if result is not None:
                        accepted = (move,*result)
                        accepted_source = "global_single"
                        break
            if accepted is None and pair_nodes > 1:
                diverse,seen = [],set()
                for score,move in ranked:
                    if move.node not in seen:
                        diverse.append((score,move))
                        seen.add(move.node)
                    if len(diverse) == pair_nodes:break
                pairs = sorted((a[0]+b[0],tuple(sorted((a[1],b[1])))) for a,b in itertools.combinations(diverse,2))
                for _,moves in pairs:
                    totals["global_pair_trials"] += 1
                    move = fg.JointMove(moves)
                    result = consider(move,info["trials"])
                    if result is not None:
                        accepted = (move,*result)
                        accepted_source = "global_pair"
                        break
            info.update(accepted=accepted is not None,selection=accepted_source if accepted is not None else None)
            global_log.append(info)
        if accepted is None and compensation and len(compensation_log) < compensation["rounds"]:
            method = compensation.get("method","continuous")
            if method == "rounded":
                from . import rounded_budget as helper_backend
            elif method == "continuous":
                from . import quantile_compensation as helper_backend
            else:raise ValueError("未知辅助节点排序方法")
            helper_cache = primary_cache if primary_cache else {}
            kwargs = dict(primary_limit=compensation["primary_limit"],helper_limit=compensation["helper_limit"],
                trial_limit=trial_limit,max_array_bytes=compensation["max_array_bytes"])
            if "primary_order" in compensation:
                if method != "rounded":raise ValueError("指定主提案顺序需要舍入预算辅助")
                kwargs["primary_order"] = compensation["primary_order"]
            if compensation.get("block_order",2) == 3 or helper_cache:
                if method != "rounded":raise ValueError("三节点搜索需要真实舍入预算统计")
                kwargs["cache"] = helper_cache
            candidates,info = helper_backend.pairs(model,domain,photos,ranked,**kwargs)
            info["accepted"] = False
            info["before_loss"] = photos.loss
            info["trials"] = []
            for moves,roles in candidates:
                totals["compensated_pair_trials"] += 1
                move = fg.JointMove(moves)
                result = consider(move,info["trials"])
                info["trials"][-1]["compensation"] = roles
                if result is not None:
                    accepted = (move,*result)
                    accepted_compensation = roles
                    accepted_source = ranked_scope+"_compensation"
                    info.update(accepted=True,selected=roles)
                    break
            if not compensation_log and pair_prefix_expected is not None:
                if info["statistics_sha256"] != pair_prefix_expected["statistics_sha256"] or info["trials"] != pair_prefix_expected["trials"]:
                    raise AssertionError("扩展节点块前原两节点候选前缀不同")
            if accepted is None and compensation.get("block_order",2) == 3:
                from . import rounded_blocks
                blocks,block_info = rounded_blocks.triples(model,domain,photos,helper_cache,
                    first_limit=compensation["first_helpers"],second_limit=compensation["second_helpers"])
                block_info.update(trials=[],subset_trials=[],confirmation=[])
                info["block_search"] = block_info
                for moves,roles in blocks:
                    totals["three_node_trials"] += 1
                    move = fg.combine(moves)
                    result = consider(move,block_info["trials"])
                    block_info["trials"][-1]["compensation"] = roles
                    if result is None:continue
                    feasible = [(result[0].loss,3,moves,move)]
                    for size in (1,2):
                        for subset in itertools.combinations(moves,size):
                            totals["proper_subset_trials"] += 1
                            subset_move = fg.combine(subset)
                            subset_result = consider(subset_move,block_info["subset_trials"])
                            if subset_result is not None:feasible.append((subset_result[0].loss,size,subset,subset_move))
                    _,size,chosen,chosen_move = min(feasible,key=lambda x:x[:3])
                    confirmation = consider(chosen_move,block_info["confirmation"])
                    if confirmation is None:raise AssertionError("节点块子集选择的确认与试探不同")
                    roles = {**roles,"committed_node_count":size,"selected_subset_nodes":[p.node for p in chosen],
                        "all_proper_subsets_rejected":len(feasible) == 1}
                    if size < 3:
                        for field in ("predicted_full_sse_delta","predicted_full_mean_upper_q24_delta"):
                            roles["proposed_"+field] = roles.pop(field)
                    elif roles["disjoint_cell_support_certificate"]:
                        before = fg.summary(domain.hist)
                        after = confirmation[1]["candidate"]
                        if (int(after["sum_squared_error"])-int(before["sum_squared_error"]) != int(roles["predicted_full_sse_delta"])
                                or int(after["sum_upper_q24"])-int(before["sum_upper_q24"]) != int(roles["predicted_full_mean_upper_q24_delta"])):
                            raise AssertionError("三节点不相交预算证书与真实整块不一致")
                        roles["additive_certificate_checked"] = True
                    accepted = (chosen_move,*confirmation)
                    accepted_compensation = roles
                    accepted_source = ranked_scope+("_three_node" if size == 3 else "_block_subset")
                    info.update(accepted=True,selected=roles)
                    block_info.update(accepted=True,selected=roles)
                    break
            helper_cache.clear()
            compensation_log.append(info)
        if accepted is None:
            stop = "no_guarded_improving_move_in_finite_bank"
            break
        primary_cache.clear()
        move,photo_trial,proof = accepted
        before = photos.loss
        moves = fg.components(move)
        changes = []
        for part in moves:
            node = model.nodes.reshape(-1,3)[part.node]
            changes.append({"node":part.node,"before":node.tolist(),"after":list(part.value)})
            node[:] = part.value
        domain.commit(models,move)
        photos.commit(photo_trial)
        if not np.array_equal(photos.current,domain.squared):
            raise AssertionError("接受后图片平方误差与完整域缓存不一致")
        record = {"step":step+1,"moves":changes,"before_loss":before,"after_loss":photos.loss,
            "focus_colours":len(keys),"full_domain":proof,"proposal_source":accepted_source}
        if photos.stability is not None:
            record["stability"] = photos.stability.certificate(photos,domain.hist,proof["candidate"])
            if not record["stability"]["accepted"]:raise AssertionError("接受后固定参考稳定性证书失败")
        if accepted_compensation is not None:record["compensation"] = accepted_compensation
        if accepted_batch is not None:record["primary_batch"] = accepted_batch
        log.append(record)
        print(f"接受第{step+1}步：{len(moves)}节点，整数尾部缺口 {before} → {photos.loss}",flush=True)
        if on_accept is not None:on_accept(record,model)
    photos.recheck()
    return {"stop":stop,"tail_feasible":photos.loss == 0,"accepted":log,"rejections":rejections,
        "compensation_rounds":compensation_log,"global_rounds":global_log,**totals}
