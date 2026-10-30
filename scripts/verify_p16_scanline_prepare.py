"""100仅新增运行时整链质量；旧已认证cube/照片前缀作只读真值。"""
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import numpy as np
import psutil
import verify_p16_shared_proven as q
from outplace_support import apply_to
from p16_workload_support import HintLibrary


def complete_stored(chain, oracle_path, expected_sha):
    truth=np.memmap(oracle_path,dtype=np.uint8,mode='r',shape=(1<<24,3))
    streams={name:hashlib.sha256() for name in ('avx1','avx4','out1','out4')}
    calls=0
    for begin in range(0,1<<24,1<<18):
        code=np.arange(begin,begin+(1<<18),dtype=np.uint32)
        source=np.stack([code>>16,(code>>8)&255,code&255],axis=1).astype(np.uint8)
        expected=truth[begin:begin+(1<<18)]
        for threads in (1,4):
            actual=chain.apply(source.copy(),kernel='avx2',threads=threads)
            assert np.array_equal(actual,expected)
            streams[f'avx{threads}'].update(memoryview(actual).cast('B'));calls+=1
            output=apply_to(chain.library.dll,chain.handle,source.tobytes(),1,threads)
            assert output==expected.tobytes()
            streams[f'out{threads}'].update(output);calls+=1
    hashes={name:h.hexdigest() for name,h in streams.items()}
    assert set(hashes.values())=={expected_sha}
    return {'colors':1<<24,'byte_mismatches':0,'streams':hashes,'candidate_backend_calls':calls,
        'scope':'四条100新流逐块对已绑定独立cube原件，不新执行旧reference全域。'}


def photograph_checks(library,plan):
    frames,manifest=q.source(json.loads(q.checked(plan['photo_model_plan']).read_text(encoding='utf-8')))
    assert q.sha(frames)==plan['photo_source_sha256']
    work=np.empty_like(frames);records=[];u8=ct.POINTER(ct.c_uint8)
    expected={(r['model'],r['images']):r['sha256'] for r in plan['photo_expected_prefixes']}
    for model,rows in plan['models'].items():
        paths=[q.checked(v) for v in rows['models']];sides=[q.checked(v) if v else None for v in rows['sidecars']]
        for count in (1,10,85,86,100):
            inputs,output=frames[:count],work[:count]
            hint=None if count==1 else count*786432
            with q.create(library,paths,sides,hint) as chain:
                assert bool(q.direct_info(chain)['enabled'])==(model=='anchor' or count>=86)
                q.bind_to(chain.library.dll)
                for threads in (1,4):
                    for separate in (False,True):
                        if separate:
                            output.fill(173);error=ct.create_string_buffer(1024)
                            code=chain.library.dll.jshc_cc_apply_to(chain.handle,inputs.ctypes.data_as(u8),
                                output.ctypes.data_as(u8),inputs.nbytes,1,threads,error,len(error))
                            assert code==0,error.value
                        else:
                            output[:]=inputs;chain.apply(output,kernel='avx2',threads=threads)
                        actual=q.sha(output);assert actual==expected[model,count]
                        records.append({'model':model,'images':count,'hint':hint,'threads':threads,'separate':separate,
                            'expected_prefix_sha256':expected[model,count],'actual_output_sha256':actual})
    assert q.sha(frames)==plan['photo_source_sha256']
    return records


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--plan',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();plan=json.loads(args.plan.read_text(encoding='utf-8'))
    assert q.digest(Path(__file__))==plan['script_sha256']
    for row in plan['sources']:q.checked(row)
    for row in plan['oracles'].values():q.checked(row)
    if args.output.exists():raise FileExistsError('100新增质量不覆盖')
    args.output.mkdir(parents=True);(args.output/'executed-plan.json').write_bytes(args.plan.read_bytes())
    psutil.Process().cpu_affinity(plan['cpus'])
    directory=os.add_dll_directory('E:/mingw64/bin') if os.name=='nt' else None
    finite=json.loads(q.checked(plan['private_native_receipt']).read_text(encoding='utf-8'))
    assert finite['passed'] and finite['return_code']==0 and finite['library_sha256']==plan['libraries']['candidate']['sha256']
    assert finite['native_result']['native_calls']==924 and finite['native_result']['oracle_pixels']==2363136
    libraries={role:q.Library(q.checked(row),row['sha256']) for role,row in plan['libraries'].items()}
    assert [libraries[r].revision for r in ('reference','previous','candidate')]==[87,97,100]
    q.bind_workload(libraries['previous']);q.bind_workload(libraries['candidate'])
    full,table_rows,finite_rows={},{},{}
    table_rows=[];rng=np.random.default_rng(202610240100)
    for model,rows in plan['models'].items():
        paths=[q.checked(v) for v in rows['models']];sides=[q.checked(v) if v else None for v in rows['sidecars']]
        full[model]={};finite_rows[model]={}
        for mode,hint in (('default',None),('high',q.THRESHOLD)):
            with q.create(libraries['previous'],paths,sides,hint) as old,q.create(libraries['candidate'],paths,sides,hint) as new:
                row=q.equal_tables(old,new);row.update({'model':model,'mode':mode,'hint':hint});table_rows.append(row)
                assert bool(q.direct_info(new)['enabled'])==(model=='anchor' or hint is not None)
                full[model][mode]=complete_stored(new,q.checked(plan['oracles'][model]),plan['expected_full_sha256'][model])
                print('100新增四条完整RGB8流/表一致',model,mode,flush=True)
        with libraries['reference'].chain(paths,sides) as truth:
            for hint in (0,q.THRESHOLD-1,q.THRESHOLD,q.THRESHOLD+1,(1<<64)-1):
                with q.create(libraries['previous'],paths,sides,hint) as old,q.create(libraries['candidate'],paths,sides,hint) as new:
                    row=q.equal_tables(old,new);row.update({'model':model,'mode':'hint','hint':hint});table_rows.append(row)
                    assert bool(q.direct_info(new)['enabled'])==(model=='anchor' or hint>=q.THRESHOLD)
                    finite_rows[model][str(hint)]={'comparisons':sum(q.finite(truth,new,rng.integers(0,256,(n,3),np.uint8)) for n in plan['lengths']),
                        'rejects':q.reject_to(new.library.dll,new.handle),'state':q.state(new)}
    folder=args.output/'high-contracts';folder.mkdir()
    contracts=q.contracts({'reference':libraries['reference'],'candidate':HintLibrary(libraries['candidate'],q.THRESHOLD)},
        folder,plan['models']['ordinary'],True)
    arguments=q.argument_contracts(libraries['candidate'])
    photos=photograph_checks(libraries['candidate'],plan)
    counters={'full_streams':sum(len(v['streams']) for m in full.values() for v in m.values()),
        'full_candidate_backend_calls':sum(v['candidate_backend_calls'] for m in full.values() for v in m.values()),
        'table_pairs':len(table_rows),'finite_comparisons':sum(v['comparisons'] for m in finite_rows.values() for v in m.values()),
        'finite_rejects':sum(v['rejects'] for m in finite_rows.values() for v in m.values()),
        'u64_contracts':len(contracts),'u64_candidate_backend_calls':sum(r['backend_comparisons'] for r in contracts),
        'photo_sha_checks':len(photos),'typed_rejects':len(arguments['typed_rejects']),
        'native_create_rejects':len(arguments['native_unsigned_invalid_arguments'])}
    assert counters==plan['expected_counters'],(counters,plan['expected_counters'])
    q.save(args.output/'correctness.json',{'passed':True,'full':full,'table_cases':table_rows,'finite_cases':finite_rows,
        'contracts':contracts,'arguments':arguments,'photos':photos,'counters':counters,
        'private_native_receipt':plan['private_native_receipt'],'environment':q.env(),'libraries':plan['libraries'],
        'scope':'只测100新增16新全域流/14表对/40照片/有限及8高hint独立u64合同；消费旧已认证cube/99照片前缀与924私有合同原回执，不重复旧native全域/99合同。不计性能，未做OOM/noAVX2故障注入。'})
    print('100新增质量闭环通过，无性能',flush=True)


if __name__=='__main__':main()
