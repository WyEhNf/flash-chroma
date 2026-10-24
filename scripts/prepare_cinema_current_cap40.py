"""原环境冻结并导出273节点±1完整Q16安全问题，不导入ORTools。"""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'python'),str(ROOT/'scripts')]
from cinema_current_cap40_identity import SOLVE,GATE,sha,signature,validate
from prepare_cinema_first_cpsat import add_point
OUT=ROOT/'artifacts/cinema-current-cap40-cpsat-v1'
UNIT=ROOT/'artifacts/cinema-current-all-max-unit-v1'


def save(path,value):
    if path.exists():raise FileExistsError('不覆盖新cap40首解原件')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def freeze():
    if OUT.exists():raise FileExistsError('不覆盖新cap40首解阶段')
    prior=json.loads((UNIT/'frozen.json').read_text(encoding='utf-8'));summary=json.loads((UNIT/'summary.json').read_text(encoding='utf-8'))
    audit_path=ROOT/'artifacts/cinema-current-all-max-unit-independent-v1.json';audit=json.loads(audit_path.read_text(encoding='utf-8'))
    assert audit['pass'] and audit['summary_sha256']==sha(UNIT/'summary.json') and summary['within_gate'] and summary['zero_safe_rows']==0
    assert (summary['aabb_states'],summary['dangerous_rows'],summary['safe_rows'])==(1400540,4058,74081)
    import numpy as np
    with np.load(UNIT/'danger-allowed.npz') as data:
        offsets,allowed=data['offsets'],data['allowed_rgb']
        assert len(offsets)==4059 and len(allowed)==74081 and int(offsets[0])==0 and int(offsets[-1])==74081 and np.all(np.diff(offsets)>0)
        for begin,end in zip(offsets[:-1],offsets[1:]):
            rows=[tuple(int(v) for v in rgb) for rgb in allowed[int(begin):int(end)]]
            assert rows==sorted(set(rows)), 'CSR安全RGB顺序/去重不同于add_point的lex顺序'
    sources=dict(prior['source_sha256'])
    for name in ['experiments/p16-cinema-current-cap40-feasible-v1.json','experiments/p16-cinema-current-cap40-feasible-proposal-v1.md',
        'scripts/cinema_current_cap40_identity.py','scripts/prepare_cinema_current_cap40.py','scripts/check_cinema_current_cap40.py',
        'scripts/audit_cinema_current_cap40_problem.py','scripts/run_cinema_current_cap40_solver.py','scripts/verify_cinema_current_cap40.py',
        'scripts/prepare_cinema_first_cpsat.py','scripts/cinema_first_cpsat_model.py','scripts/cinema_current_safe_identity.py',
        'scripts/cinema_first_safe_cpsat_model.py','python/lutlab/integer_first_box.py']:sources[name]=sha(ROOT/name)
    for name,expected in sources.items():
        assert sha(ROOT/name)==expected,name
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))
    lock=ROOT/'artifacts/cinema-first-cpsat-environment-v1.json';inputs=dict(prior['inputs_sha256'])
    for path in [UNIT/n for n in ('frozen.json','summary.json','screen.npz','danger-allowed.npz')]+[audit_path,lock]:inputs[str(path)]=sha(path)
    for name,expected in inputs.items():assert sha(name)==expected,name
    save(OUT/'frozen.json',{'ast_pass':True,'source_sha256':sources,'inputs_sha256':inputs,'original_inputs':prior['original_inputs'],
        'unit_screen':str(UNIT/'screen.npz'),'unit_allowed':str(UNIT/'danger-allowed.npz'),'environment_lock':str(lock),
        'plan':json.loads((ROOT/'experiments/p16-cinema-current-cap40-feasible-v1.json').read_text(encoding='utf-8')),
        'csr_order':{'tables':4058,'rows':74081,'all_rgb_lexicographic_and_unique':True,'constant_original_rgb_subtraction_preserves_order':True},'solver_calls':0})
    print({'frozen_sha256':sha(OUT/'frozen.json'),'sources':len(sources),'inputs':len(inputs),'solver_called':False},flush=True)


def problem():
    import numpy as np
    from lutlab import integer_first_box as box
    from run_channel_tail_nodes import load_model
    frozen=json.loads((OUT/'frozen.json').read_text(encoding='utf-8'));contract=json.loads((OUT/'contract.json').read_text(encoding='utf-8'))
    assert contract['pass'] and contract['frozen_sha256']==sha(OUT/'frozen.json')
    for name,expected in frozen['source_sha256'].items():assert sha(ROOT/name)==expected,name
    for name,expected in frozen['inputs_sha256'].items():assert sha(name)==expected,name
    with np.load(frozen['unit_screen']) as data:
        selected=data['selected_nodes'].copy();danger=data['dangerous_rows'].copy();keys=data['keys'][danger].copy();original=data['original_first'][danger].copy()
    with np.load(frozen['unit_allowed']) as data:csr_keys,offsets,allowed=data['source_keys'],data['offsets'],data['allowed_rgb']
    np.testing.assert_array_equal(keys,csr_keys);assert (len(selected),len(keys),len(allowed))==(273,4058,74081)
    model=load_model(frozen['original_inputs']['first']['path']);flat=model.nodes.reshape(-1,3);mapping={int(n):i for i,n in enumerate(selected)}
    variables=[{'name':'d_'+str(int(node))+'_'+str(c),'physical_node':int(node),'channel':c,'original_value':int(flat[node,c]),
        'lower':max(-1,-int(flat[node,c])),'upper':min(1,255-int(flat[node,c]))} for node in selected for c in range(3)]
    result={'schema':'cinema_current_cap40_feasible_v1','variables':variables,'n_node_variables':819,'rows':[],'points':[],
        'solve':SOLVE,'initial_gate':GATE,'source_sha256':frozen['source_sha256'],'inputs_sha256':frozen['inputs_sha256'],
        'original_inputs':frozen['original_inputs'],'unit_screen':frozen['unit_screen'],'unit_allowed':frozen['unit_allowed'],
        'environment_lock_sha256':sha(frozen['environment_lock']),'frozen_sha256':sha(OUT/'frozen.json'),'contract_sha256':sha(OUT/'contract.json')}
    for j,key in enumerate(keys):
        k=int(key);rgb=[k>>16,(k>>8)&255,k&255];basis=[box.scalar_basis(model,rgb,c) for c in range(3)]
        acc=[sum(int(flat[n,c])*w for n,w in basis[c]) for c in range(3)]
        terms=[[[3*mapping[n]+c,int(w)] for n,w in basis[c] if n in mapping] for c in range(3)]
        candidates=allowed[int(offsets[j]):int(offsets[j+1])].tolist();add_point(result,acc,terms,candidates,{'source_key':k,'source_rgb':rgb})
        assert result['points'][-1]['original_rgb']==original[j].tolist() and len(result['points'][-1]['allowed_deltas'])==len(candidates)
    result['constraint_sha256']=signature(result);validate(result);save(OUT/'problem.json',result)
    print({'variables':len(result['variables']),'rounding_rows':len(result['rows']),'tables':len(result['points']),'safe_rows':74081,
        'constraint_sha256':result['constraint_sha256'],'solver_called':False},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['freeze','problem']);a=p.parse_args();{'freeze':freeze,'problem':problem}[a.mode]()
