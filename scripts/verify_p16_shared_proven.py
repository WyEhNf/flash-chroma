"""97隔离shared已证域：同场87/95/97全域、私有核及旧精确回退合同。"""
import argparse
from contextlib import contextmanager
import ctypes as ct
import hashlib
import json
import os
import subprocess
from pathlib import Path
import numpy as np
import psutil
from bench_p16_model_pair import checked, source
from study_p16_direct_compile import Library, save, digest, env
from verify_p16_workload import complete, finite, contracts, state, argument_contracts
from p16_workload_support import THRESHOLD, workload_chain, bind_workload
from outplace_support import bind_to, reject_to
from direct16_support import info as direct_info, table as direct_table
from palette_support import tables as palette_tables
from suffix_cache_support import cache_info, cache_table
from domain_cache_support import info as domain_info


def sha(value):
    return hashlib.sha256(memoryview(value).cast('B')).hexdigest()


def create(library, paths, sides, hint):
    return library.chain(paths, sides) if hint is None else workload_chain(library, paths, sides, expected_pixels=hint)


def equal_tables(previous, candidate):
    a, b = direct_info(previous), direct_info(candidate)
    assert a == b and previous.model_bytes == candidate.model_bytes
    wa, pa = palette_tables(previous)
    wb, pb = palette_tables(candidate)
    assert np.array_equal(wa, wb) and np.array_equal(pa, pb)
    ta, tb = direct_table(previous), direct_table(candidate)
    assert np.array_equal(ta, tb)
    ca, cb = cache_info(previous), cache_info(candidate)
    assert {k: v for k, v in ca.items() if k != 'prepare_seconds'} == {
        k: v for k, v in cb.items() if k != 'prepare_seconds'}
    old_cache, new_cache = cache_table(previous, ca), cache_table(candidate, cb)
    assert np.array_equal(old_cache, new_cache)
    assert domain_info(previous) == domain_info(candidate)
    return {'enabled': bool(a['enabled']), 'entries_u32': len(ta), 'table_bytes': ta.nbytes,
        'previous_sha256': sha(ta), 'candidate_sha256': sha(tb),
        'palette_sha256': sha(pa), 'byte_mismatches': 0,
        'cache_sha256': sha(new_cache), 'cache_entries': len(new_cache),
        'scope': '既有安全copy逐字节核cache/direct/palette与原domain诊断，不读取内部指针或修改旧ABI；不比较动态prepare_seconds。'}


class ContractLibrary:
    def __init__(self, previous, candidate, hint, rows):
        self.previous, self.candidate, self.hint, self.rows = previous, candidate, hint, rows

    @contextmanager
    def chain(self, paths, sides):
        with create(self.previous, paths, sides, self.hint) as a, create(self.candidate, paths, sides, self.hint) as b:
            row = equal_tables(a, b)
            row.update({'models': [str(p) for p in paths], 'hint': self.hint})
            self.rows.append(row)
            yield b


def photos(libraries, plan):
    frames, manifest = source(json.loads(checked(plan['photo_model_plan']).read_text(encoding='utf-8')))
    assert sha(frames) == plan['photo_source_sha256']
    expected = {(v['role'], v['images']): v['output_sha256'] for v in plan['photo_expected']}
    work = np.empty_like(frames)
    records = []
    u8 = ct.POINTER(ct.c_uint8)
    for model, rows in plan['models'].items():
        paths = [checked(v) for v in rows['models']]
        sides = [checked(v) if v else None for v in rows['sidecars']]
        for images in plan['images']:
            inputs, output = frames[:images], work[:images]
            hint = None if images == 1 else images * 768 * 1024
            with create(libraries['candidate'], paths, sides, hint) as chain:
                bind_to(chain.library.dll)
                for threads in (1, 4):
                    for separate in (False, True):
                        if separate:
                            output.fill(173)
                            error = ct.create_string_buffer(1024)
                            rc = chain.library.dll.jshc_cc_apply_to(chain.handle, inputs.ctypes.data_as(u8),
                                output.ctypes.data_as(u8), inputs.nbytes, 1, threads, error, len(error))
                            assert rc == 0, error.value
                        else:
                            output[:] = inputs
                            chain.apply(output, kernel='avx2', threads=threads)
                        actual = sha(output)
                        assert actual == expected[model, images]
                        records.append({'model': model, 'images': images, 'hint': hint, 'threads': threads,
                            'separate': separate, 'actual_output_sha256': actual})
    assert sha(frames) == plan['photo_source_sha256']
    return records


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__)) == plan['script_sha256']
    for row in plan['sources']:
        checked(row)
    checked(plan['source_freeze'])
    if a.output.exists():
        raise FileExistsError('97首次质量不覆盖')
    a.output.mkdir(parents=True)
    psutil.Process().cpu_affinity(plan['cpus'])
    directory = os.add_dll_directory('E:/mingw64/bin') if os.name == 'nt' else None
    contract_exe = checked(plan['dictionary_contract_executable'])
    contract_env = dict(os.environ)
    contract_env['PATH'] = 'E:/mingw64/bin' + os.pathsep + contract_env.get('PATH', '')
    native_contract = json.loads(subprocess.check_output([str(contract_exe)], env=contract_env, encoding='utf-8'))
    assert native_contract['passed'] and native_contract['finite_cases'] == 13
    assert native_contract['fixed_array_bytes'] == 3580 and native_contract['worst_same_bucket_distinct_keys'] == 256
    private_exe = checked(plan['private_kernel_contract_executable'])
    private_contract = json.loads(subprocess.check_output([str(private_exe)], env=contract_env, encoding='utf-8'))
    assert private_contract['passed'] and private_contract['cases'] == 150
    assert private_contract['production_c_abi_changes'] == 0
    libraries = {role: Library(checked(row), row['sha256']) for role, row in plan['libraries'].items()}
    assert [libraries[r].revision for r in ('reference', 'previous', 'candidate')] == [87, 95, 97]
    bind_workload(libraries['previous'])
    bind_workload(libraries['candidate'])
    full, states, finite_cases, table_cases = {}, {}, {}, []
    rng = np.random.default_rng(202610240097)
    for model, rows in plan['models'].items():
        paths = [checked(v) for v in rows['models']]
        sides = [checked(v) if v else None for v in rows['sidecars']]
        full[model], states[model], finite_cases[model] = {}, {}, {}
        with libraries['reference'].chain(paths, sides) as truth:
            for mode, hint in (('default', None), ('high', THRESHOLD)):
                with create(libraries['previous'], paths, sides, hint) as old, create(libraries['candidate'], paths, sides, hint) as new:
                    assert old.model_bytes == new.model_bytes
                    expected = model == 'anchor' or hint is not None
                    assert bool(direct_info(new)['enabled']) == expected
                    states[model][mode] = {'previous': state(old), 'candidate': state(new)}
                    full[model][mode] = {'previous': complete(truth, old), 'candidate': complete(truth, new)}
                    assert all(v['streams']['reference'] == plan['expected_full_sha256'][model]
                        for v in full[model][mode].values())
                    row = equal_tables(old, new)
                    row.update({'model': model, 'mode': mode})
                    table_cases.append(row)
                    print('97同场完整RGB8及ID字节通过', model, mode, flush=True)
            for hint in (0, THRESHOLD - 1, THRESHOLD, THRESHOLD + 1, (1 << 64) - 1):
                with create(libraries['candidate'], paths, sides, hint) as new:
                    assert bool(direct_info(new)['enabled']) == (model == 'anchor' or hint >= THRESHOLD)
                    expected_bytes = 18579204 if model == 'anchor' else 1852824 + ((1 << 24) if hint >= THRESHOLD else 0)
                    assert new.model_bytes == expected_bytes
                    finite_cases[model][str(hint)] = {'comparisons': sum(finite(truth, new,
                        rng.integers(0, 256, (n, 3), np.uint8)) for n in plan['lengths']),
                        'rejects': reject_to(new.library.dll, new.handle), 'state': state(new)}
    contract_rows, contract_tables = {}, []
    for mode, hint in (('low', THRESHOLD - 1), ('high', THRESHOLD)):
        folder = a.output / mode
        folder.mkdir()
        proxy = ContractLibrary(libraries['previous'], libraries['candidate'], hint, contract_tables)
        contract_rows[mode] = contracts({'reference': libraries['reference'], 'candidate': proxy},
            folder, plan['models']['ordinary'], hint >= THRESHOLD)
    arguments = argument_contracts(libraries['candidate'])
    photo_rows = photos(libraries, plan)
    save(a.output / 'correctness.json', {'passed': True, 'full': full, 'states': states,
        'finite_cases': finite_cases, 'table_cases': table_cases, 'contracts': contract_rows,
        'contract_tables': contract_tables, 'arguments': arguments, 'photos': photo_rows,
        'libraries': plan['libraries'], 'environment': env(), 'dictionary_contract': native_contract, 'private_kernel_contract': private_contract,
        'scope': '56全域RGB8流逐字节；20个实/合成快照含空表对95；10080有限比较/110拒绝/16独立u64合同；32真实照片SHA；新私有核150显式整数/偏移合同。无性能声明，无OOM或无AVX2硬件故障注入。'})
    save(a.output / 'executed-plan.json', plan)
    print('97完整质量通过，未做正式性能', flush=True)


if __name__ == '__main__':
    main()
