"""99独立整链质量；新增owner账单明确核，不把旧参考资格当原生覆盖。"""
import argparse
from contextlib import contextmanager
import ctypes as ct
import json
import os
from pathlib import Path
import struct
import subprocess
import numpy as np
import psutil
import verify_p16_shared_proven as q
from p16_b2_quality_contracts import contracts as owner_contracts


def expected_active(paths, sides, chain):
    if len(paths) != 4 or not q.domain_info(chain)['eligible'] or q.direct_info(chain)['enabled']:
        return False
    if struct.unpack_from('<I', Path(paths[0]).read_bytes(), 8)[0] != 33:
        return False
    if q.palette_tables(chain)[0].size:
        return False
    for side in sides:
        if side is not None:
            values = np.frombuffer(Path(side).read_bytes(), '<u4').reshape(3, 768)
            if not np.array_equal(values[0], values[1]) or not np.array_equal(values[0], values[2]):
                return False
    return True


def equal_tables(old, new, active):
    old_direct, new_direct = q.direct_info(old), q.direct_info(new)
    assert old_direct == new_direct
    delta = new.model_bytes-old.model_bytes
    assert delta == 8+(160320 if active else 0), (delta, active)
    wa, pa = q.palette_tables(old);wb, pb = q.palette_tables(new)
    assert np.array_equal(wa, wb) and np.array_equal(pa, pb)
    ta, tb = q.direct_table(old), q.direct_table(new)
    assert np.array_equal(ta, tb)
    ca, cb = q.cache_info(old), q.cache_info(new)
    assert {k:v for k,v in ca.items() if k != 'prepare_seconds'} == {k:v for k,v in cb.items() if k != 'prepare_seconds'}
    old_cache, new_cache = q.cache_table(old, ca), q.cache_table(new, cb)
    assert np.array_equal(old_cache, new_cache) and q.domain_info(old) == q.domain_info(new)
    return {'direct_enabled': bool(old_direct['enabled']), 'direct_table_sha256': q.sha(tb),
        'palette_sha256': q.sha(pb), 'cache_sha256': q.sha(new_cache), 'table_mismatches': 0,
        'expected_b2_private_qualification': active, 'measured_model_bytes_delta': delta,
        'expected_new_aligned_request_bytes': 160320 if active else 0,
        'measured_empty_owner_handle_difference': delta-(160320 if active else 0),
        'scope': '保留原安全copy ABI逐表核对；新增账单含实际Handle差。未通过生产ABI读取私有指针或CRT真实保留。'}


class ContractLibrary:
    def __init__(self, old, new, hint, rows):
        self.old, self.new, self.hint, self.rows = old, new, hint, rows

    @contextmanager
    def chain(self, paths, sides):
        with q.create(self.old, paths, sides, self.hint) as old, q.create(self.new, paths, sides, self.hint) as new:
            row = equal_tables(old, new, expected_active(paths, sides, old))
            row.update({'models': [str(p) for p in paths], 'hint': self.hint})
            self.rows.append(row)
            yield new


def boundary_photos(libraries, plan):
    frames, manifest = q.source(json.loads(q.checked(plan['photo_model_plan']).read_text(encoding='utf-8')))
    assert q.sha(frames) == plan['photo_source_sha256']
    work = np.empty_like(frames);records=[]
    u8=ct.POINTER(ct.c_uint8)
    for name, rows in plan['models'].items():
        paths=[q.checked(v) for v in rows['models']];sides=[q.checked(v) if v else None for v in rows['sidecars']]
        with libraries['reference'].chain(paths, sides) as truth:
            for count in (85, 86):
                source, output=frames[:count],work[:count]
                output[:]=source;truth.apply(output,kernel='scalar',threads=1)
                expected=q.sha(output);hint=count*786432
                with q.create(libraries['candidate'],paths,sides,hint) as new:
                    q.bind_to(new.library.dll)
                    for threads in (1,4):
                        for separate in (False,True):
                            if separate:
                                output.fill(173);error=ct.create_string_buffer(1024)
                                code=new.library.dll.jshc_cc_apply_to(new.handle,source.ctypes.data_as(u8),
                                    output.ctypes.data_as(u8),source.nbytes,1,threads,error,len(error))
                                assert code==0,error.value
                            else:
                                output[:]=source;new.apply(output,kernel='avx2',threads=threads)
                            actual=q.sha(output);assert actual==expected
                            records.append({'model':name,'images':count,'hint':hint,'threads':threads,'separate':separate,
                                'scalar87_reference_sha256':expected,'actual_output_sha256':actual})
    assert q.sha(frames)==plan['photo_source_sha256']
    return records


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();plan=json.loads(a.plan.read_text(encoding='utf-8'))
    assert q.digest(Path(__file__))==plan['script_sha256']
    for row in plan['sources']:q.checked(row)
    q.checked(plan['source_freeze'])
    if a.output.exists():raise FileExistsError('99整链首次质量不覆盖')
    a.output.mkdir(parents=True);(a.output/'executed-plan.json').write_bytes(a.plan.read_bytes())
    psutil.Process().cpu_affinity(plan['cpus'])
    directory=os.add_dll_directory('E:/mingw64/bin') if os.name=='nt' else None
    environment=dict(os.environ);environment['PATH']='E:/mingw64/bin'+os.pathsep+environment.get('PATH','')
    executable=q.checked(plan['private_kernel_contract_executable'])
    private=json.loads(subprocess.check_output([str(executable),str(q.checked(plan['models']['ordinary']['models'][0]))],
        env=environment,encoding='utf-8'))
    assert private['passed'] and private['first_stage_u64_pixels']==33554432 and private['canary_cases']==36
    assert private['private_reject_cases']==8 and private['owner_size']==8 and private['axis_and_nodes_mod64']==0
    libraries={role:q.Library(q.checked(row),row['sha256']) for role,row in plan['libraries'].items()}
    assert [libraries[r].revision for r in ('reference','previous','isolated','candidate')]==[87,95,97,99]
    for role in ('previous','isolated','candidate'):q.bind_workload(libraries[role])
    full,states,finite,table_rows={},{},{},[];rng=np.random.default_rng(202610240099)
    for name, rows in plan['models'].items():
        paths=[q.checked(v) for v in rows['models']];sides=[q.checked(v) if v else None for v in rows['sidecars']]
        full[name],states[name],finite[name]={},{},{}
        with libraries['reference'].chain(paths,sides) as truth:
            for mode,hint in (('default',None),('high',q.THRESHOLD)):
                full[name][mode]={}
                with q.create(libraries['previous'],paths,sides,hint) as old, q.create(libraries['isolated'],paths,sides,hint) as iso, q.create(libraries['candidate'],paths,sides,hint) as new:
                    active=expected_active(paths,sides,iso)
                    assert active==(name=='ordinary' and hint is None)
                    for role,chain in (('previous',old),('isolated',iso),('candidate',new)):
                        full[name][mode][role]=q.complete(truth,chain)
                        assert full[name][mode][role]['streams']['reference']==plan['expected_full_sha256'][name]
                    states[name][mode]={'previous':q.state(old),'isolated':q.state(iso),'candidate':q.state(new)}
                    for role,chain in (('previous',old),('isolated',iso)):
                        row=equal_tables(chain,new,active);row.update({'model':name,'mode':mode,'old_role':role});table_rows.append(row)
                    print('99四库完整RGB8/原表字节/容量通过',name,mode,flush=True)
            for hint in (0,q.THRESHOLD-1,q.THRESHOLD,q.THRESHOLD+1,(1<<64)-1):
                with q.create(libraries['isolated'],paths,sides,hint) as old, q.create(libraries['candidate'],paths,sides,hint) as new:
                    row=equal_tables(old,new,expected_active(paths,sides,old));row.update({'model':name,'hint':hint});table_rows.append(row)
                    finite[name][str(hint)]={'comparisons':sum(q.finite(truth,new,rng.integers(0,256,(n,3),np.uint8)) for n in plan['lengths']),
                        'rejects':q.reject_to(new.library.dll,new.handle),'state':q.state(new)}
    contracts,contract_tables={},[]
    for mode,hint in (('low',q.THRESHOLD-1),('high',q.THRESHOLD)):
        folder=a.output/mode;folder.mkdir()
        proxy=ContractLibrary(libraries['isolated'],libraries['candidate'],hint,contract_tables)
        contracts[mode]=owner_contracts({'reference':libraries['reference'],'candidate':proxy},folder,plan['models']['ordinary'],hint>=q.THRESHOLD)
    arguments=q.argument_contracts(libraries['candidate'])
    photos=q.photos(libraries,plan)
    boundary=boundary_photos(libraries,plan)
    q.save(a.output/'correctness.json',{'passed':True,'full':full,'states':states,'finite_cases':finite,
        'table_cases':table_rows,'contracts':contracts,'contract_tables':contract_tables,'arguments':arguments,
        'photos':photos,'boundary_photos':boundary,'libraries':plan['libraries'],'private_kernel_contract':private,
        'environment':q.env(),'scope':'所有实际角色/流与原始计数保留；33554432私有首级u64、36偏移canary、8坏View、整链全域/有限/拒绝/u64回退/五N照片。生产whole-create OOM/noAVX2硬件未注入；不计性能，compiled非空动态覆盖需从快照实际字段判断。'})
    print('99完整质量通过，无正式性能',flush=True)


if __name__=='__main__':
    main()
