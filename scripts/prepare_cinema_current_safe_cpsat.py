"""原环境将当前完整4985危险CSR导出精确Q16问题，不导入求解器。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from prepare_cinema_first_cpsat import add_point
from cinema_current_safe_identity import GATE,SOLVE,sha,validate_current


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frozen',type=Path,required=True)
    p.add_argument('--contract',type=Path,required=True);p.add_argument('--environment-lock',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖当前完整安全CP真实问题')
    import numpy as np
    from lutlab import integer_first_box as box
    from run_channel_tail_nodes import load_model
    freeze=json.loads(args.frozen.read_text(encoding='utf-8'));contract=json.loads(args.contract.read_text(encoding='utf-8'))
    if not freeze['ast_pass'] or not contract['pass']:raise ValueError('先冻结源并通过完整有限合同')
    for sources in (freeze['source_sha256'],contract['source_sha256']):
        for name,expected in sources.items():
            if sha(ROOT/name)!=expected:raise ValueError('源身份已变：'+name)
    for spec in freeze['inputs'].values():
        if sha(spec['path'])!=spec['sha256']:raise ValueError('固定输入已变')
    for name,expected in freeze['frozen_risk_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('冻结风险身份已变：'+name)
    inputs=freeze['inputs'];run=json.loads(Path(inputs['risk_run']['path']).read_text(encoding='utf-8'))
    summary=json.loads(Path(inputs['risk_summary']['path']).read_text(encoding='utf-8'));audit=json.loads(Path(inputs['risk_audit']['path']).read_text(encoding='utf-8'))
    if not summary['within_frozen_resource_gate'] or summary['zero_safe_rows'] or not audit['pass']:raise ValueError('完整风险原门或审计未过')
    if (summary['possibly_dangerous_rows'],summary['safe_tuples_in_dangerous_rows'],summary['complete_support_rows'])!=(4985,386612,80751):raise ValueError('不是当前完整风险结果')
    if audit['screen_sha256']!=inputs['screen']['sha256'] or audit['summary_sha256']!=inputs['risk_summary']['sha256']:raise ValueError('完整风险审计身份不符')
    with np.load(inputs['screen']['path']) as data:
        selected=data['selected_nodes'].copy();keys=data['keys'][data['dangerous_rows']].copy();old_first=data['original_first'][data['dangerous_rows']].copy()
    with np.load(inputs['allowed']['path']) as data:csr_keys,offsets,allowed=data['source_keys'],data['offsets'],data['allowed_rgb']
    np.testing.assert_array_equal(keys,csr_keys)
    if len(selected)!=122 or len(keys)!=4985 or len(allowed)!=386612 or len(offsets)!=4986 or int(offsets[0])!=0 or int(offsets[-1])!=len(allowed) or np.any(np.diff(offsets)<=0):raise ValueError('完整安全CSR域不符')
    model=load_model(run['inputs']['first']['path']);flat=model.nodes.reshape(-1,3);gold=np.load(run['inputs']['gold']['path'],mmap_mode='r')
    mapping={int(node):i for i,node in enumerate(selected)}
    variables=[{'name':'d_'+str(int(node))+'_'+str(c),'physical_node':int(node),'channel':c,'original_value':int(flat[node,c]),
        'lower':max(-2,-int(flat[node,c])),'upper':min(2,255-int(flat[node,c]))} for node in selected for c in range(3)]
    problem={'schema':'cinema_first_safe_cpsat_problem_v1','experiment':'cinema_current741_safe_cap47_minl1_v1',
        'variables':variables,'n_node_variables':len(variables),'points':[],'rows':[],'solve':SOLVE,'initial_gate':GATE,
        'objective':{'kind':'minimize_node_delta_l1','node_variables':len(variables)},
        'objective_absolute_upper_bound':sum(max(abs(v['lower']),abs(v['upper'])) for v in variables)}
    for i,source in enumerate(keys):
        key=int(source);rgb=[key>>16,(key>>8)&255,key&255];bounds=box.point_box(model,rgb,selected)
        acc=[int(ch['baseline_acc']) for ch in bounds['channels']]
        terms=[[[3*mapping[node]+c,int(weight)] for node,weight in box.scalar_basis(model,rgb,c) if node in mapping] for c in range(3)]
        candidates=allowed[int(offsets[i]):int(offsets[i+1])].tolist()
        add_point(problem,acc,terms,candidates,{'source_key':key,'source_rgb':rgb,'gold_rgb':gold[key].tolist()})
        if problem['points'][-1]['original_rgb']!=old_first[i].tolist() or len(problem['points'][-1]['allowed_deltas'])!=len(candidates):raise AssertionError('acc原值或完整安全表导出不符')
    validate_current(problem)
    problem.update(source_sha256=freeze['source_sha256'],frozen_risk_sha256=freeze['frozen_risk_sha256'],inputs=run['inputs'],
        environment_lock_sha256=sha(args.environment_lock),contract_sha256=sha(args.contract),frozen_sha256=sha(args.frozen),
        source_inputs=inputs,plan_sha256=sha(ROOT/'experiments/p16-cinema-current-safe-cpsat-v1.json'))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(problem,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'node_variables':366,'output_variables':14955,'abs_variables':366,'rounding_rows':len(problem['rows']),
        'safe_triples':len(allowed),'cp_solver_called':False},flush=True)


if __name__=='__main__':main()
