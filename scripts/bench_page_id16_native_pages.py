"""静态六角色近邻配对：1920调用/240自身AA/480组末SHA；待formal grant。"""
import argparse
import json
import os
from pathlib import Path
import sys

# 只有stdlib读取协议/核环境；NumPy、候选DLL及OMP桥必须在0x55后导入。
_BOOT_PARSER = argparse.ArgumentParser(add_help=False)
_BOOT_PARSER.add_argument('--plan', type=Path, required=True)
_BOOT_ARGS, _BOOT_UNUSED = _BOOT_PARSER.parse_known_args()
_BOOT_PLAN_PATH = _BOOT_ARGS.plan.resolve()
_BOOT_PLAN = json.loads(_BOOT_PLAN_PATH.read_text(encoding='utf-8'))
_BOOT_PYTHON = sys.version.split()[0]
if _BOOT_PYTHON != _BOOT_PLAN['expected_versions']['python']:
    raise AssertionError('NumPy/native导入前Python版本不匹配，STOP')
_BOOT_ENV = {name: os.environ.get(name) for name in _BOOT_PLAN['required_environment']}
if _BOOT_ENV != _BOOT_PLAN['required_environment']:
    raise AssertionError('NumPy/native导入前冻结环境不匹配，STOP')
_BOOT_CPUS = list(_BOOT_PLAN['allowed_cpus'])
_BOOT_MASK = sum(1 << cpu for cpu in _BOOT_CPUS)
if _BOOT_CPUS != [0, 2, 4, 6] or _BOOT_MASK != _BOOT_PLAN['process_allowed_mask'] or _BOOT_MASK != 85:
    raise AssertionError('固定允许CPU协议不匹配，STOP')
import ctypes as ct
_BOOT_K32 = ct.WinDLL('kernel32', use_last_error=True)
_BOOT_PROCESS = _BOOT_K32.GetCurrentProcess
_BOOT_PROCESS.restype = ct.c_void_p
_BOOT_GET = _BOOT_K32.GetProcessAffinityMask
_BOOT_GET.argtypes = [ct.c_void_p, ct.POINTER(ct.c_size_t), ct.POINTER(ct.c_size_t)]
_BOOT_GET.restype = ct.c_int
_BOOT_SET = _BOOT_K32.SetProcessAffinityMask
_BOOT_SET.argtypes = [ct.c_void_p, ct.c_size_t]
_BOOT_SET.restype = ct.c_int
_BOOT_ALLOWED, _BOOT_SYSTEM = ct.c_size_t(), ct.c_size_t()
if not _BOOT_GET(_BOOT_PROCESS(), ct.byref(_BOOT_ALLOWED), ct.byref(_BOOT_SYSTEM)) or _BOOT_SYSTEM.value & _BOOT_MASK != _BOOT_MASK or not _BOOT_SET(_BOOT_PROCESS(), _BOOT_MASK):
    raise AssertionError('NumPy/native导入前不能设置固定允许集，STOP')
if not _BOOT_GET(_BOOT_PROCESS(), ct.byref(_BOOT_ALLOWED), ct.byref(_BOOT_SYSTEM)) or _BOOT_ALLOWED.value != _BOOT_MASK:
    raise AssertionError('NumPy/native导入前允许集读回不匹配，STOP')
import numpy as np
if np.__version__ != _BOOT_PLAN['expected_versions']['numpy']:
    raise AssertionError('NumPy导入后实际版本不匹配，STOP')
_AFTER_NUMPY_ENV = {name: os.environ.get(name) for name in _BOOT_PLAN['required_environment']}
if _AFTER_NUMPY_ENV != _BOOT_ENV:
    raise AssertionError('NumPy导入改变冻结环境，STOP')
RUNTIME_CONTRACT = dict(python=_BOOT_PYTHON, numpy=np.__version__,
    environment_before_numpy=_BOOT_ENV, environment_after_numpy=_AFTER_NUMPY_ENV,
    allowed_before_numpy=_BOOT_ALLOWED.value, system_before_numpy=_BOOT_SYSTEM.value,
    allowed_cpus=_BOOT_CPUS, plan_path=str(_BOOT_PLAN_PATH),
    scope='stdlib/ctypes仅调用WinAPI设置允许集；随后才导入NumPy及本仓native/OMP桥。')
import hashlib
import time
import bench_page_id16 as base
import observe_page_id16_modules as modules
from page_id16_copy4_common import library as copy_library
from page_id16_common import Borrowed, PageModel
from page_id16_native_pages_common import BorrowedPages, PagesView, library as pages_library
from win_readonly_rom import query

ROOT = base.ROOT
PLAN = _BOOT_PLAN_PATH
base.PLAN = PLAN
MODULE_FAILURE = None


def setup(role, plan):
    if role not in ('copy4_c99', 'pages_c99'):
        return base.setup(role, plan)
    if role == 'copy4_c99':
        lib = copy_library(plan['libraries']['copy4'], True)
        owner = Borrowed(plan['page_rom'], lib)
        model = owner.model
        capacity = owner.view.length + ct.sizeof(PageModel)
        symbol = 'jshc_p4_apply_copy4_parallel'
        path = plan['libraries']['copy4']

        def apply(src, dst, pixels, threads, mode):
            return lib.jshc_p4_apply_copy4_parallel(ct.byref(model), src, dst, pixels, 0, threads)
    else:
        lib = pages_library(plan['libraries']['pages'], True)
        owner = BorrowedPages(Path(plan['page_rom']), lib)
        model = owner.model
        capacity = owner.file_view.length + ct.sizeof(PagesView) + ct.sizeof(owner.slots)
        symbol = 'jshc_p4_pages_apply_parallel'
        path = plan['libraries']['pages']

        def apply(src, dst, pixels, threads, mode):
            return lib.jshc_p4_pages_apply_parallel(ct.byref(model), src, dst, pixels, threads)
    if capacity != plan['capacities'][role]:
        owner.close()
        raise AssertionError('新角色实际capacity与冻结值不同')
    metadata = dict(role=role, capacity=capacity, library=path, library_sha256=base.sha(path),
        rom_sha256=base.sha(plan['page_rom']), model_bytes=ct.sizeof(model),
        entrypoint=dict(symbol=symbol, address=int(ct.cast(getattr(lib, symbol), ct.c_void_p).value),
                        scope='计时直接固定新入口，不用质量包装计数；实际调用由rows记录。'))
    if role == 'pages_c99':
        metadata.update(blob_address=model.base.blob, pages_address=model.pages,
                        slots_bytes=ct.sizeof(owner.slots), selected_kernel='new_c99_only')
    else:
        metadata.update(blob_address=model.blob, selected_kernel=0)
    return apply, owner.close, metadata


def checked_modules(label, plan):
    result = modules.snapshot(label)
    if label != 'same-imports-before-setup':
        known = {str(Path(path)).casefold(): value for path, value in plan['input_sha256'].items()}
        for name, rows in result['dependencies'].items():
            if len(rows) != 1 or known.get(str(Path(rows[0]['path'])).casefold()) != rows[0]['sha256']:
                if MODULE_FAILURE is not None and not MODULE_FAILURE.exists():
                    base.save(MODULE_FAILURE, result)
                raise AssertionError('实际依赖路径/SHA/数量不属于冻结输入：' + name)
    return result


def readonly_master(source):
    begin, end = int(source.ctypes.data), int(source.ctypes.data) + len(source)
    cursor, regions = begin, []
    while cursor < end:
        result = query(cursor)
        limit = result['BaseAddress'] + result['RegionSize']
        if result['Protect'] != 2 or result['State'] != 0x1000 or limit <= cursor:
            raise AssertionError('master全区间实际不是已提交READONLY')
        regions.append(result)
        cursor = min(end, limit)
    if source.flags.writeable:
        raise AssertionError('master NumPy视图可写')
    return dict(address=begin, bytes=len(source), regions=regions, numpy_writeable=False)


def stage_end_environment(plan, output):
    actual = {name: os.environ.get(name) for name in plan['required_environment']}
    base.save(output / 'environment-end.json', dict(actual=actual,
        expected=plan['required_environment'], matches=actual == plan['required_environment'],
        scope='该worker/RSS全部model close及末模块观察后实录，不在apply或copy_total计时内。'))
    return actual


def main():
    global MODULE_FAILURE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker', type=int)
    parser.add_argument('--rss')
    args = parser.parse_args()
    if args.plan.resolve() != PLAN:
        raise AssertionError('bootstrap与main协议路径不一致')
    plan = base.checked()
    control = base.affinity()
    args.output.mkdir(parents=True, exist_ok=False)
    MODULE_FAILURE = args.output / 'module-failure.json'
    if args.rss:
        if args.worker is not None or args.rss not in plan['roles']:
            raise ValueError('固定单一RSS角色')
        observations = [checked_modules('same-imports-before-setup', plan)]
        before = base.snapshot()
        operation, close, metadata = setup(args.rss, plan)
        try:
            observations.append(checked_modules('after-prepare', plan))
            prepared = base.snapshot()
        finally:
            close()
        closed = base.snapshot()
        observations.append(checked_modules('after-close', plan))
        final_env = stage_end_environment(plan, args.output)
        base.save(args.output / 'rss.json', dict(plan_sha256=base.sha(PLAN), role=args.rss,
            before=before, prepared=prepared, closed=closed, identity=metadata,
            module_observations=observations, affinity=control, environment=base.env(),
            runtime_contract=dict(**RUNTIME_CONTRACT, environment_end=final_env),
            scope='fresh同imports/流式身份/无图；含模块枚举和Python，非prepare专属峰或纯模型RAM。'))
        if final_env != plan['required_environment']:
            raise AssertionError('RSS结束冻结环境不符，保存后STOP')
        print(dict(rss=args.rss, capacity=metadata['capacity']), flush=True)
        return
    if args.worker not in range(4):
        raise ValueError('固定四worker')
    source = np.memmap(plan['photos'], dtype=np.uint8, mode='r')
    if len(source) != 235929600:
        raise AssertionError('完整100图长度不同')
    target = np.empty(len(source), dtype=np.uint8)
    src, dst = source.ctypes.data_as(base.U8), target.ctypes.data_as(base.U8)
    pixels = len(source) // 3
    operators, rows, inputs, module_rows = {}, [], [], []
    failure = None
    controls = list(plan['pair_controls'])
    shift = args.worker % len(controls)
    controls = controls[shift:] + controls[:shift]
    if args.worker % 2:
        controls.reverse()
    thread_order = (1, 4) if args.worker % 2 == 0 else (4, 1)
    mode_order = ('in', 'out') if args.worker % 2 == 0 else ('out', 'in')
    with (args.output / 'calls.jsonl').open('x', encoding='utf-8', newline='\n') as event_stream:
        def emit(row):
            event_stream.write(json.dumps(row, ensure_ascii=False) + '\n')
            event_stream.flush()

        def input_identity(label):
            row = dict(label=label, sha256=hashlib.sha256(source).hexdigest(), protection=readonly_master(source))
            inputs.append(row)
            emit(dict(event='input_identity', **row))
            if row['sha256'] != plan['expected_input_sha256']:
                raise AssertionError('master输入身份变化，STOP')

        def measure(role, threads, mode, pair, kind, group, round_index, hash_end):
            emit(dict(event='call_attempt', sequence=len(rows), pair=pair, role=role,
                threads=threads, mode=mode, kind=kind, group=group, round=round_index,
                pixels=pixels, hash_expected=hash_end))
            cpu_copy_before = int(base.GET_CPU())
            copy_start = time.perf_counter_ns() if mode == 'in' else None
            if mode == 'in':
                np.copyto(target, source)
                copy_end = time.perf_counter_ns()
            else:
                copy_end = None
            native_cpu_before = int(base.GET_CPU())
            actual_src = dst if mode == 'in' else src
            started = time.perf_counter_ns()
            result = int(operators[role][0](actual_src, dst, pixels, threads, mode))
            ended = time.perf_counter_ns()
            cpu_after = int(base.GET_CPU())
            digest = hashlib.sha256(target).hexdigest() if hash_end else None
            row = dict(sequence=len(rows), pair=pair, role=role, threads=threads, mode=mode,
                kind=kind, group=group, round=round_index, apply_ns=ended - started,
                copy_ns=copy_end - copy_start if mode == 'in' else None,
                gap_ns=started - copy_end if mode == 'in' else None,
                copy_apply_ns=ended - copy_start if mode == 'in' else None,
                cpu_copy_before=cpu_copy_before, cpu_native_before=native_cpu_before, cpu_native_after=cpu_after,
                source_address=int(ct.cast(actual_src, ct.c_void_p).value), target_address=int(target.ctypes.data),
                returncode=result, sha256=digest, hash_checked=hash_end)
            rows.append(row)
            emit(dict(event='call', **row))
            if result or any(cpu not in (0, 2, 4, 6) for cpu in (cpu_copy_before, native_cpu_before, cpu_after)) or hash_end and digest != plan['expected_output_sha256']:
                raise AssertionError('native/末输出SHA/CPU允许集首失败STOP')

        try:
            input_identity('worker-start')
            module_rows.append(checked_modules('same-imports-before-setup', plan))
            for role in plan['roles']:
                operators[role] = setup(role, plan)
            module_rows.append(checked_modules('after-all-prepare', plan))
            for threads in thread_order:
                for mode in mode_order:
                    for peer in controls:
                        pair = 'pages_c99/' + peer
                        mirrored = (args.worker + int(threads == 4) + int(mode == 'out')) % 2
                        a, b = 'pages_c99', peer
                        warm = (b, a, b, a) if mirrored else (a, b, a, b)
                        timed = (b, a, a, b) if mirrored else (a, b, b, a)
                        for index, role in enumerate(warm):
                            measure(role, threads, mode, pair, 'warm', -1, index, index >= 2)
                        for group, role in enumerate(timed):
                            for round_index in range(5):
                                measure(role, threads, mode, pair, 'timed', group, round_index, round_index == 4)
                        input_identity(f'cell-end/{threads}/{mode}/{peer}')
                        base.save(args.output / 'partial.json', dict(worker=args.worker, rows=rows, inputs=inputs))
            input_identity('worker-end')
        except BaseException as error:
            failure = error
        finally:
            for role, value in reversed(list(operators.items())):
                try:
                    value[1]()
                except BaseException as error:
                    if failure is None:
                        failure = error
        try:
            module_rows.append(checked_modules('after-all-close', plan))
        except BaseException as error:
            if failure is None:
                failure = error
    final_env = stage_end_environment(plan, args.output)
    if final_env != plan['required_environment'] and failure is None:
        failure = AssertionError('worker结束冻结环境不符，保存后STOP')
    value = dict(worker=args.worker, passed=failure is None, plan_sha256=base.sha(PLAN),
        environment=base.env(), runtime_contract=dict(**RUNTIME_CONTRACT, environment_end=final_env), affinity=control,
        identities={role: item[2] for role, item in operators.items()},
        module_observations=module_rows, pair_controls=controls, thread_order=thread_order, mode_order=mode_order,
        source_address=int(source.ctypes.data), target_address=int(target.ctypes.data), rows=rows,
        input_identities=inputs, scope='每worker480调用，四worker1920；只有组末120输出SHA/worker。原地双metric、分离仅apply；所有六模型热驻留，AA失效不补跑。')
    if failure is not None:
        value['failure'] = dict(type=type(failure).__name__, message=str(failure))
    base.save(args.output / 'results.json', value)
    print(dict(worker=args.worker, passed=failure is None, calls=len(rows), hashes=sum(row['hash_checked'] for row in rows)), flush=True)
    if failure is not None:
        raise failure


if __name__ == '__main__':
    main()
