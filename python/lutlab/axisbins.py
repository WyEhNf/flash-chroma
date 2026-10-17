"""Monotone vertex bins and proved two-stage lookahead, experimental epoch.

Each contiguous input bin owns one existing grid vertex. Representatives lie
inside their bins (0/255 at the extremes). A bin's vertex is always one of the
canonical cell endpoints, so only geometry-derived Q16 0/65536 selectors are
needed. Unlike lower-cell hold, the last constant interval needs no duplicate
endpoint vertex. Nodes always sample their own original RGB8 LUT.

Lookahead uses the following original LUT only to prove input partitions and
then requires an exact next model on every possible stored prefix output. It
never trains current-stage RGB nodes on composite/residual labels, and always
executes all four independently sourced models with integer stage outputs.
"""
from __future__ import annotations

import copy
import hashlib
import time

import numpy as np

from . import fit,interp,io,step

PROFILES={"adaptive_bins":(False,False),"lookahead_bins":(True,False),
          "reachable_bins":(False,True),"lookahead_reachable":(True,True)}


def _validate_table(table,m):
    if (table.shape!=io.FULL_SHAPE or table.dtype!=np.uint8 or not isinstance(m,(int,np.integer))
            or isinstance(m,bool) or not 17<=m<=33):
        raise ValueError("expected a complete RGB8 LUT and 17<=m<=33")


def _digest(table):
    return hashlib.sha256(memoryview(np.ascontiguousarray(table))).hexdigest()


def partitions(table,m,*,diagnostics=None):
    """Prove up to m constant-slice bins independently on each axis.

    A rejected axis has only a lower bound, not an inferred full partition.
    Positive results inspect every adjacent slice in every other coordinate.
    """
    _validate_table(table,m);report={} if diagnostics is None else diagnostics
    axes=[];details=[]
    for axis in range(3):
        cuts=[0];checked=0
        for position in range(1,256):
            before=[slice(None)]*4;after=before.copy();before[axis]=position-1;after[axis]=position
            checked+=1
            if not np.array_equal(table[tuple(before)],table[tuple(after)]):
                cuts.append(position)
                if len(cuts)>m:break
        if len(cuts)>m:
            axes.append(None);details.append({"axis":axis,"proved":False,"required_bins_lower_bound":len(cuts),"adjacent_slices_checked":checked})
        else:
            cuts.append(256);axes.append(np.array(cuts,np.int16))
            details.append({"axis":axis,"proved":True,"required_bins":len(cuts)-1,"boundaries":cuts,"adjacent_slices_checked":255})
    report.update(axes=details,all_axes_proved=all(cuts is not None for cuts in axes),
        scope="complete own-source adjacent-slice equality; rejected axes have no exactness guarantee")
    return axes


def bin_geometry(boundaries,m):
    """Refine whole integer bins and choose one representative per vertex.

    Vertex selection is monotone. Fraction tables store no target channel values;
    their only nonzero value is 65536, selecting the cell's upper endpoint.
    """
    bounds=np.asarray(boundaries)
    if (bounds.ndim!=1 or len(bounds)<2 or bounds[0]!=0 or bounds[-1]!=256
            or not np.all(bounds==np.rint(bounds)) or np.any(np.diff(bounds)<=0)
            or not isinstance(m,(int,np.integer)) or not 17<=m<=33 or len(bounds)-1>m):
        raise ValueError("expected at most m nonempty consecutive bins covering 0..255")
    cuts=list(map(int,bounds))
    while len(cuts)<m+1:
        index=int(np.argmax(np.diff(cuts)))
        if cuts[index+1]-cuts[index]<2:raise RuntimeError("cannot refine bins to the requested size")
        cuts.insert(index+1,(cuts[index]+cuts[index+1])//2)
    cuts=np.array(cuts,np.int16)
    grid=((cuts[:-1]+cuts[1:]-1)//2).astype(np.float64)
    grid[0],grid[-1]=0,255
    index,_=io.axis_tables(np.stack([grid]*3))
    selector=np.searchsorted(cuts[1:-1],np.arange(256),side="right")
    upper=selector-index[0].astype(np.int32)
    if np.any((upper!=0)&(upper!=1)):raise RuntimeError("bin representative is not a canonical neighbouring vertex")
    fraction=(upper.astype(np.uint32)*io.ONE)
    if (np.any(np.diff(grid)<=0) or np.any(grid<cuts[:-1]) or np.any(grid>=cuts[1:])
            or set(selector)!=set(range(m))):raise RuntimeError("invalid representative, empty bin, or unobserved vertex")
    return grid,index[0].copy(),fraction,{"boundaries":cuts.tolist(),"representatives":grid.astype(int).tolist(),
        "bin_counts":np.bincount(selector,minlength=m).tolist(),"policy":"monotone_neighbour_vertex_switch"}


def exact_bins(table,m,*,diagnostics=None):
    """An exact own-LUT model when all three contiguous partitions fit m."""
    report={} if diagnostics is None else diagnostics
    axes=partitions(table,m,diagnostics=report.setdefault("partition",{}))
    if any(cuts is None for cuts in axes):
        report.update(proved=False,reason="one or more complete slice partitions exceed m")
        return None
    geometry=[bin_geometry(cuts,m) for cuts in axes]
    grid=np.stack([row[0] for row in geometry])
    index=np.stack([row[1] for row in geometry]);fraction=np.stack([row[2] for row in geometry])
    nodes=np.ascontiguousarray(table[np.ix_(*(row.astype(np.intp) for row in grid))])
    model=io.SparseLut(grid,nodes,index,fraction);io.validate_sparse(model,competition=True)
    report.update(proved=True,source_rgb_sha256=_digest(table),verified_source_colors=256**3,
        geometry=[row[3] for row in geometry],node_labels="sampled from this original LUT only",
        guarantee="exact own-LUT RGB8 output on every RGB8 input",uses_one_vertex_per_monotone_bin=True,
        required_vertices=[len(cuts)-1 for cuts in axes],
        lower_hold_required_knots=[len({0,255,*map(int,cuts[1:-1])}) for cuts in axes])
    return model


def _sample_own(table,signature,m):
    report={};axes=partitions(signature,m,diagnostics=report.setdefault("partition",{}))
    if any(cuts is None for cuts in axes):return None,report
    geometry=[bin_geometry(cuts,m) for cuts in axes]
    grid=np.stack([row[0] for row in geometry])
    index=np.stack([row[1] for row in geometry]);fraction=np.stack([row[2] for row in geometry])
    nodes=np.ascontiguousarray(table[np.ix_(*(row.astype(np.intp) for row in grid))])
    model=io.SparseLut(grid,nodes,index,fraction)
    report.update(criterion="following_original_LUT_of_current_original_LUT",node_labels="current original LUT at representative inputs",
        guarantee="next original LUT applied to these stored outputs reproduces the two-original-LUT signature",
        own_stage_exactness_claim=False,current_source_rgb_sha256=_digest(table),signature_rgb_sha256=_digest(signature))
    return model,report


def prefix_constant(table,m,palette,*,diagnostics=None):
    """A constant own-source label on the complete known input superset.

    This model is exact only on that superset. It makes no global own-LUT claim
    and does not substitute a final/composite label for this stage's target.
    """
    report={} if diagnostics is None else diagnostics
    _validate_table(table,m)
    if palette is None:
        report.update(proved=False,reason="no known finite input superset")
        return None
    target=io.apply_full(table,palette)
    if not np.all(target==target[:1]):
        report.update(proved=False,reason="own-source labels on the finite input set are not constant")
        return None
    grid=np.rint(io.uniform_grid(m));nodes=np.empty((m,m,m,3),np.uint8);nodes[:]=target[0]
    model=io.SparseLut(grid,nodes)
    report.update(proved=True,verified_palette_entries=len(palette),input_palette_sha256=_digest(palette),
        own_source_label=target[0].tolist(),guarantee="exact own-LUT output on the complete supplied prefix-output superset only")
    return model


def exact_prefix_fit(table,m,palette,*,diagnostics=None):
    """Try a source-labelled sparse interpolant, accept only exact Q16 bytes.

    All distinct reachable inputs are checked. A continuous solver success alone
    never certifies this model. The regularizer is a source-sampled prior; there
    are no true-final/composite/residual RGB labels. Outside the supplied complete
    input superset, no own-LUT accuracy guarantee is made.
    """
    import scipy.sparse as sp
    report={} if diagnostics is None else diagnostics
    _validate_table(table,m)
    if palette is None:
        report.update(proved=False,reason="no known finite input superset")
        return None
    palette=np.asarray(palette)
    if palette.dtype!=np.uint8 or palette.ndim!=2 or palette.shape[1]!=3 or not len(palette):
        raise ValueError("expected a nonempty complete uint8 RGB prefix-output superset")
    points=np.unique(palette,axis=0)
    if len(points)>m**3:
        report.update(proved=False,reason="predeclared reachable-row budget exceeded",unique_points=len(points),vertices=m**3)
        return None
    grid=fit.adaptive_dp_grid(table,m);index,fraction=io.axis_tables(grid)
    prior=np.ascontiguousarray(table[np.ix_(*(axis.astype(np.intp) for axis in grid))])
    target=io.apply_full(table,points);report.update(unique_points=len(points),vertices=m**3,
        input_palette_sha256=_digest(palette),unique_point_sha256=_digest(points),
        label_scope="this original LUT applied to every distinct known prefix output",attempts=[])
    def check(nodes):
        model=io.SparseLut(grid,nodes,index,fraction)
        predicted=interp.apply_tetra_q16(model,points)
        wrong=int(np.count_nonzero(np.any(predicted!=target,axis=1)))
        return model,wrong
    initial,wrong=check(prior)
    report["sampled_prior_wrong_points"]=wrong
    if not wrong:
        report.update(proved=True,route="source_grid_samples_already_exact",verified_entries=len(points))
        return initial
    I,W=interp.tetra_index_weights_q(points,index,fraction,m)
    A=sp.csr_matrix((W.astype(np.float64).ravel()/io.ONE,I.ravel(),np.arange(0,4*(len(points)+1),4)),shape=(len(points),m**3))
    A.eliminate_zeros();A.sort_indices();H=(A.T@A).tocsr();H.sort_indices();b=np.asarray(A.T@target.astype(np.float64))
    x0=prior.reshape(-1,3).astype(np.float64);D=H.diagonal()+1.
    report.update(basis_nnz=int(A.nnz),hessian_nnz=int(H.nnz),unobserved_vertices=int(np.count_nonzero(H.diagonal()==0)),
        moment_scope="uniform unique reachable inputs; exact dyadic moments because N<2^16 and Q16 products sum below 2^48",
        regularisation_candidates=[1e-4,1e-6,1e-8],acceptance="all actual Q16 outputs exactly equal own-source labels")
    for lam in (1e-4,1e-6,1e-8):
        attempt={"lambda":lam};report["attempts"].append(attempt)
        try:raw=fit.solve_spd(H,b,x0,lam=lam,tol=1e-10,maxiter=1000,diagnostics=attempt.setdefault("solver",{}))
        except fit.FitConvergenceError:
            attempt["accepted"]=False;continue
        candidate,wrong=check(fit.quantize(raw).reshape(m,m,m,3));attempt["rounded_wrong_points"]=wrong
        if not wrong:
            report.update(proved=True,route="regularised_continuous_fit_then_integer_rounding",verified_entries=len(points));attempt["accepted"]=True
            return candidate
        # Include the same positive ridge in the integer problem; unsupported
        # nodes remain well-defined and the tetrahedron parity proof still holds.
        regular=H+sp.diags(lam*D);rhs=b+lam*D[:,None]*x0
        refined=fit.quantize(fit.int_refine(raw,regular,rhs,sweeps=8)).reshape(m,m,m,3)
        candidate,wrong=check(refined);attempt.update(refined_wrong_points=wrong,accepted=wrong==0)
        if not wrong:
            report.update(proved=True,route="regularised_integer_refinement",verified_entries=len(points))
            return candidate
    report.update(proved=False,reason="no candidate met the complete integer-output certificate")
    return None


def fit_chain(tables,m,*,lookahead=False,reachable=False,stage_cache=None):
    """New candidate, independent targets and unchanged SLUT/tetra runtime.

    Feasible exact own-source/finite-input models take precedence. A lookahead
    pair is accepted only after its actual second model equals its own full LUT
    on the entire first model's stored output superset. General fallback is the
    unchanged R27 fitter. stage_cache is process-local and source-content keyed.
    """
    if len(tables)!=4:raise ValueError("four independently sourced LUTs required")
    for table in tables:_validate_table(table,m)
    started=time.perf_counter();memo={} if stage_cache is None else stage_cache
    hashes=[_digest(table) for table in tables]
    chain=[];information=[];palette=None;stage=0
    def fit_one(k,incoming):
        key=(hashes[k],int(m),None if incoming is None else _digest(incoming),bool(reachable),"exact_route")
        if key in memo:
            model,info=memo[key]
            return model,{**copy.deepcopy(info),"process_local_source_cache_hit":True}
        detail={};model=exact_bins(tables[k],m,diagnostics=detail.setdefault("exact_bins",{}))
        if model is not None:detail["route"]="exact_own_monotone_bins"
        else:
            model=prefix_constant(tables[k],m,incoming,diagnostics=detail.setdefault("prefix_constant",{}))
            if model is not None:detail["route"]="exact_own_constant_on_prefix"
            else:
                model=step.aligned_vertices(tables[k],m,incoming,diagnostics=detail.setdefault("reachable_vertices",{}))
                if model is not None:detail["route"]="exact_own_reachable_vertices"
        if model is None and reachable:
            model=exact_prefix_fit(tables[k],m,incoming,diagnostics=detail.setdefault("reachable_fit",{}))
            if model is not None:detail["route"]="certified_own_reachable_fit"
        if model is not None:
            for array in (model.grid,model.nodes,model.idx,model.frac):
                if array is not None:array.setflags(write=False)
        memo[key]=(model,copy.deepcopy(detail))
        return model,detail
    while stage<4:
        model,detail=fit_one(stage,palette)
        if model is None and lookahead and stage<3:
            key=(hashes[stage],hashes[stage+1],int(m),"lookahead_geometry")
            if key in memo:
                first,old=memo[key];pair_info=copy.deepcopy(old)
            else:
                signature=io.compose([tables[stage],tables[stage+1]])
                first,pair_info=_sample_own(tables[stage],signature,m)
                del signature
                if first is not None:
                    for array in (first.grid,first.nodes,first.idx,first.frac):array.setflags(write=False)
                memo[key]=(first,copy.deepcopy(pair_info))
            if first is not None:
                node_palette=np.ascontiguousarray(first.nodes.reshape(-1,3))
                second,second_info=fit_one(stage+1,node_palette)
                if second is not None:
                    actual=interp.apply_tetra_q16(second,node_palette);exact=io.apply_full(tables[stage+1],node_palette)
                    if not np.array_equal(actual,exact):raise RuntimeError("constructed next-stage model failed its complete prefix-node oracle")
                    pair_info.update(accepted=True,second_model_verified_entries=len(node_palette),
                        input_domain_colors=256**3,pair_output_exact_on_any_rgb_input=True,
                        next_original_rgb_sha256=hashes[stage+1])
                    first_info={"route":"proved_own_label_lookahead_bins","lookahead":pair_info}
                    chain.extend([first,second]);information.extend([first_info,second_info])
                    palette=step.next_palette(first,palette,diagnostics=first_info.setdefault("output_palette",{}))
                    palette=step.next_palette(second,palette,diagnostics=second_info.setdefault("output_palette",{}))
                    stage+=2;continue
                pair_info.update(accepted=False,reason="no cheap exact own-source or finite-input second model",next_model=second_info)
            detail["lookahead_trial"]=pair_info
        if model is None:
            # New global bins dominate old lower-hold feasibility, and the
            # finite-input routes have already failed. The remaining R27 route
            # is source-only; cache it across different rejected prefix sets.
            key=(hashes[stage],int(m),"R27_source_only_fallback")
            if key in memo:
                model,old=memo[key];fallback={**copy.deepcopy(old),"process_local_source_cache_hit":True}
            else:
                model,fallback=fit.fit_model(tables[stage],m,"adaptive_full",reachable_inputs=None)
                for array in (model.grid,model.nodes,model.idx,model.frac):
                    if array is not None:array.setflags(write=False)
                memo[key]=(model,copy.deepcopy(fallback))
            detail.update(route="unchanged_R27_fallback",fallback=fallback)
        chain.append(model);information.append(detail)
        palette=step.next_palette(model,palette,diagnostics=detail.setdefault("output_palette",{}));stage+=1
    name={(False,False):"adaptive_bins",(True,False):"lookahead_bins",(False,True):"reachable_bins",(True,True):"lookahead_reachable"}[bool(lookahead),bool(reachable)]
    return chain,{"fit_s":time.perf_counter()-started,"stage_semantics":"independent_lut_fits",
        "method":name,"m":int(m),"stage_info":information,
        "labels":"every model samples/fits its own original LUT; lookahead is a geometry/equivalence criterion only",
        "runtime":"four ordinary Q16 tetra maps with integer output after each stage; no format/kernel change"}
