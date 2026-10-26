"""独立V2仅修自重叠夹具及追加记录器；不改原计数/C/ROM/DLL。"""
import argparse
import ctypes as ct
import hashlib
import json
from pathlib import Path
import struct
import numpy as np
from page_id16_native_pages_common import (ROOT, BUILD, PagesView, BorrowedPages,
    library, prepare, clear, call, sha, save, env, snapshot, query, read)
import page_id16_native_pages_common as bridge
from verify_page_id16 import Guard, fixture, codes, pixels

PLAN = ROOT / 'experiments/page-id16-native-pages-finite-v2.json'
RECORDER = None
OBSERVATION = {}
ATTEMPTS = 0
CASE_HINT = 'setup'
original_prepare, original_clear, original_call = prepare, clear, call


def append_event(value):
    if RECORDER is not None:
        RECORDER.write(json.dumps(value, ensure_ascii=False) + '\n')
        RECORDER.flush()


def view_address(view):
    return ct.addressof(view) if isinstance(view, PagesView) else int(view or 0)


def native_event(lib, entry, view, **parameters):
    global ATTEMPTS
    ATTEMPTS += 1
    append_event(dict(event='native_attempt', ordinal=ATTEMPTS, entry=entry,
        case_hint=CASE_HINT, view_address=view_address(view), parameters=parameters,
        library_sha256=lib.pages_receipt['sha256'],
        counts_before=dict(OBSERVATION.get('counts', {}))))
    return ATTEMPTS


def prepare(lib, view, blob, byte_count, slots, count=4096):
    ordinal = native_event(lib, 'jshc_p4_pages_prepare', view,
        blob=int(blob or 0), bytes=int(byte_count), slots=int(slots or 0), count=int(count))
    value = original_prepare(lib, view, blob, byte_count, slots, count)
    append_event(dict(event='native_return', ordinal=ordinal, returncode=value))
    return value


def clear(lib, view):
    ordinal = native_event(lib, 'jshc_p4_pages_clear', view)
    value = original_clear(lib, view)
    append_event(dict(event='native_return', ordinal=ordinal, returncode=value))
    return value


def call(lib, view, source, target, pixels, threads=None):
    entry = 'jshc_p4_pages_apply' if threads is None else 'jshc_p4_pages_apply_parallel'
    ordinal = native_event(lib, entry, view, source=int(source or 0), target=int(target or 0),
        pixels=int(pixels), threads=threads)
    value = original_call(lib, view, source, target, pixels, threads)
    append_event(dict(event='native_return', ordinal=ordinal, returncode=value))
    return value


# 仅本进程代理原调用；BorrowedPages的setup/clear也经过同一追加记录器。
bridge.prepare, bridge.clear, bridge.call = prepare, clear, call


def main():
    global RECORDER, CASE_HINT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan = read(PLAN)
    for name, expected in plan['source_sha256'].items():
        if sha(ROOT / name) != expected:
            raise AssertionError('有限冻结源不同：' + name)
    for name, expected in plan['input_sha256'].items():
        if sha(name) != expected:
            raise AssertionError('有限冻结输入不同：' + name)
    args.output.mkdir(parents=True, exist_ok=False)
    RECORDER = (args.output / 'events.jsonl').open('x', encoding='utf-8', newline='\n')
    OBSERVATION['output'] = str(args.output)
    before = snapshot()
    OBSERVATION['before'] = before
    d = library(BUILD / 'jshc_page_native_pages.dll', True)
    c = library(BUILD / 'jshc_page_native_pages_c99.dll', False)
    OBSERVATION['native_entry_receipts'] = [d.pages_receipt, c.pages_receipt]
    for lib in (d, c):
        actual = (lib.jshc_p4_pages_view_size(), lib.jshc_p4_pages_pointer_alignment(),
                  lib.jshc_p4_pages_view_alignment(), lib.jshc_p4_pages_slots_bytes())
        if actual != (48, 8, 8, 32768) or ct.sizeof(PagesView) != 48 or PagesView.pages.offset != 40:
            raise AssertionError('新视图实际ABI与冻结值不同')
    rom = Path(plan['page_rom'])
    old = np.memmap(plan['original_rom'], dtype=np.uint8, mode='r')
    palette = old[32:1056].reshape(256, 4)

    def oracle(values):
        key = codes(values)
        return palette[old[1056 + key], :3].reshape(-1).copy()

    counts = {name: 0 for name in plan['expected_counts']}
    events = []
    OBSERVATION['counts'] = counts

    def receipt(kind, label):
        counts[kind] += 1
        events.append(dict(kind=kind, label=label))
        append_event(dict(event='receipt', kind=kind, label=label, count=counts[kind]))

    maximum = (1 << (8 * ct.sizeof(ct.c_void_p))) - 1
    rng = np.random.default_rng(20261024)
    CASE_HINT = 'owner-setup'
    with BorrowedPages(rom, d) as owner, BorrowedPages(rom, c) as portable:
        if query(owner.model.base.blob)['Protect'] != 2:
            raise AssertionError('原ROM实际保护不是READONLY')
        configs = [('core_out', c, portable.model, None, False)]
        for threads in (1, 4):
            for same in (False, True):
                configs.append(('c99' + str(threads) + ('_in' if same else '_out'),
                                d, owner.model, threads, same))
        finite_configs = configs + [('core_in', c, portable.model, None, True)]
        for n in (0, 1, 7, 8, 9, 31, 32, 40, 64, 72, 73, 405, 406, 1023,
                  1024, 1025, 4095, 4096, 4097, 65535, 65536, 65537):
            values = rng.integers(0, 256, 3 * n, dtype=np.uint8)
            expected = oracle(values)
            for label, lib, model, threads, same in finite_configs:
                for offset in (0, 1, 3, 7):
                    source = np.full(3 * n + offset + 17, 0xa7, dtype=np.uint8)
                    source[offset:offset + 3 * n] = values
                    target = source if same else np.full_like(source, 0xa7)
                    CASE_HINT = f'finite/{label}/{n}/{offset}'
                    if call(lib, model, source.ctypes.data + offset, target.ctypes.data + offset, n, threads) or not np.array_equal(target[offset:offset + 3 * n], expected) or np.any(target[:offset] != 0xa7) or np.any(target[offset + 3 * n:] != 0xa7):
                        raise AssertionError('有限/u64/哨兵失败：' + label)
                    receipt('finite', f'{label}/{n}/{offset}')
        for label, lib, model, threads, same in finite_configs:
            CASE_HINT = label + '/null-zero'
            if call(lib, model, 0, 0, 0, threads):
                raise AssertionError('合法零长NULL失败：' + label)
            receipt('finite', label + '/null-zero')

        storage = np.full(256, 0x5a, dtype=np.uint8)
        address = storage.ctypes.data

        def reject_io(label, lib, view, src, dst, n, threads):
            global CASE_HINT
            CASE_HINT = label
            prior_storage = bytes(storage)
            prior_views = bytes(owner.model), bytes(portable.model)
            prior_slots = bytes(owner.slots), bytes(portable.slots)
            if not call(lib, view, src, dst, n, threads):
                raise AssertionError('应拒绝的IO成功：' + label)
            if bytes(storage) != prior_storage or (bytes(owner.model), bytes(portable.model)) != prior_views or (bytes(owner.slots), bytes(portable.slots)) != prior_slots:
                raise AssertionError('拒绝IO写坏已知对象：' + label)
            receipt('io_rejections', label)

        for label, lib, model, threads, same in finite_configs:
            basic = [(0, address, 1), (address, 0, 1), (address, address + 1, 16),
                     (address + 1, address, 16), (ct.addressof(model), address, 1),
                     (address, ct.addressof(model), 1), (model.base.blob, address, 1),
                     (address, model.base.blob, 1), (address, address, maximum // 3 + 1),
                     (maximum - 1, address, 1)]
            for index, (src, dst, n) in enumerate(basic):
                reject_io(f'{label}/basic{index}', lib, model, src, dst, n, threads)
            points = [ct.addressof(model) + 40, ct.addressof(model) + 47,
                      model.pages, model.pages + 32767, model.pages - 2]
            for index, point in enumerate(points):
                reject_io(f'{label}/new-src{index}', lib, model, point, address, 1, threads)
                reject_io(f'{label}/new-dst{index}', lib, model, address, point, 1, threads)
            reject_io(label + '/closed', lib, PagesView(), address, address, 1, threads)
            reject_io(label + '/null-view', lib, 0, address, address, 1, threads)
            for offset in range(1, 8):
                reject_io(f'{label}/view-unaligned{offset}', lib, ct.addressof(model) + offset, address, address, 1, threads)
                bad = PagesView.from_buffer_copy(bytes(model))
                bad.pages += offset
                reject_io(f'{label}/slots-unaligned{offset}', lib, bad, address, address, 1, threads)
            for name, value in [('null', 0), ('overflow', maximum - 7),
                                ('rom', model.base.blob), ('view', ct.addressof(model))]:
                bad = PagesView.from_buffer_copy(bytes(model))
                bad.pages = ct.addressof(bad) if name == 'view' else value
                reject_io(f'{label}/slots-{name}', lib, bad, address, address, 1, threads)
        for threads in (-1, 0, 257):
            reject_io('bad-threads' + str(threads), d, owner.model, address, address, 1, threads)

        replay = pixels(np.array([0, 4095, 4096, (1 << 24) - 1], dtype=np.uint64))
        expected_replay = oracle(replay).tobytes()
        states = []
        for prepared in (False, True):
            CASE_HINT = 'failure-state-setup/' + str(prepared)
            view = PagesView()
            slots = (ct.c_void_p * 4096)()
            ct.memset(ct.addressof(slots), 0xa5, ct.sizeof(slots))
            if prepared and prepare(d, view, owner.model.base.blob, owner.model.base.blob_bytes, ct.addressof(slots)):
                raise AssertionError('失败保留测试的合法setup失败')
            states.append((prepared, view, slots))

        def reject_prepare(kind, label, arguments):
            global CASE_HINT
            CASE_HINT = label
            for prepared, view, slots in states:
                old_view, old_slots = bytes(view), bytes(slots)
                old_owner, old_owner_slots = bytes(owner.model), bytes(owner.slots)
                args_for_state = arguments(view, slots)
                if not prepare(d, *args_for_state):
                    raise AssertionError('异常prepare未拒绝：' + label)
                if bytes(view) != old_view or bytes(slots) != old_slots or bytes(owner.model) != old_owner or bytes(owner.slots) != old_owner_slots:
                    raise AssertionError('异常prepare未保留所有旧对象：' + label)
                receipt(kind, label + ('/prepared' if prepared else '/zero'))
                if prepared:
                    target = np.empty_like(replay)
                    CASE_HINT = 'failure-replay/' + label
                    if call(c, view, replay.ctypes.data, target.ctypes.data, len(replay) // 3) or bytes(target) != expected_replay:
                        raise AssertionError('异常prepare破坏旧可用状态：' + label)
                    receipt('failure_state_replays', label)

        small = fixture(1, 1)
        mutations = [('magic', 0, b'X'), ('version', 4, struct.pack('<I', 2)),
            ('shift', 8, struct.pack('<I', 11)), ('count0', 12, struct.pack('<I', 0)),
            ('count257', 12, struct.pack('<I', 257)), ('logical', 16, struct.pack('<I', 0)),
            ('unique0', 20, struct.pack('<I', 0)), ('unique4097', 20, struct.pack('<I', 4097)),
            ('reserved1', 24, b'\x01'), ('reserved2', 28, b'\x01'),
            ('palette-alpha', 35, b'\xff'), ('unused-palette', 36, b'\x01'),
            ('first-map4096', 1056, struct.pack('<H', 4096)),
            ('last-map65535', 1056 + 8190, struct.pack('<H', 65535)),
            ('pool-id', 9248, b'\x01'), ('guard', len(small) - 1, b'\x01')]
        for label, offset, raw in mutations:
            content = bytearray(small)
            content[offset:offset + len(raw)] = raw
            buf = (ct.c_uint8 * len(content)).from_buffer(content)
            reject_prepare('format_prepare_rejections', label,
                lambda view, slots: (view, ct.addressof(buf), len(content), ct.addressof(slots), 4096))
        content = bytearray(small) + b'\x00'
        buf = (ct.c_uint8 * len(content)).from_buffer(content)
        for length in (0, 31, 9247, len(small) - 1, len(small) + 1):
            reject_prepare('format_prepare_rejections', 'length' + str(length),
                lambda view, slots: (view, ct.addressof(buf), length, ct.addressof(slots), 4096))

        def normal(view, slots):
            return [view, owner.model.base.blob, owner.model.base.blob_bytes, ct.addressof(slots), 4096]

        other = []
        for count in (0, 1, 4095, 4097, maximum):
            other.append(('count' + str(count), 4, count))
        other += [('null-view', 0, 0), ('null-slots', 3, 0),
                  ('overflow-view', 0, maximum - 7), ('overflow-slots', 3, maximum - 7),
                  ('overflow-blob', 1, maximum - 7)]
        for label, index, value in other:
            def arguments(view, slots, index=index, value=value):
                args_for_state = normal(view, slots)
                args_for_state[index] = value
                return args_for_state
            reject_prepare('other_prepare_rejections', label, arguments)
        for length in (0, owner.model.base.blob_bytes):
            reject_prepare('other_prepare_rejections', 'null-blob' + str(length),
                lambda view, slots: (view, 0, length, ct.addressof(slots), 4096))
        for offset in range(1, 8):
            reject_prepare('other_prepare_rejections', 'unaligned-view' + str(offset),
                lambda view, slots: (ct.addressof(view) + offset, owner.model.base.blob,
                                     owner.model.base.blob_bytes, ct.addressof(slots), 4096))
            reject_prepare('other_prepare_rejections', 'unaligned-slots' + str(offset),
                lambda view, slots: (view, owner.model.base.blob, owner.model.base.blob_bytes,
                                     ct.addressof(slots) + offset, 4096))
        for pair in ('view-slots', 'view-blob', 'slots-blob'):
            for partial in (False, True):
                def arguments(view, slots, pair=pair, partial=partial):
                    args_for_state = normal(view, slots)
                    if pair == 'view-slots':
                        args_for_state[3] = ct.addressof(view) + (40 if partial else 0)
                    elif pair == 'view-blob':
                        args_for_state[1] = ct.addressof(view) + (40 if partial else 0)
                    else:
                        args_for_state[1] = ct.addressof(slots) + (32760 if partial else 0)
                    return args_for_state
                reject_prepare('other_prepare_rejections', pair + ('-partial' if partial else '-full'), arguments)

        shared = PagesView.from_buffer_copy(bytes(owner.model))
        target = np.empty_like(replay)
        CASE_HINT = 'lifecycle/copy-apply'
        if call(c, shared, replay.ctypes.data, target.ctypes.data, len(replay) // 3) or bytes(target) != expected_replay:
            raise AssertionError('只读view副本apply失败')
        receipt('lifecycle_scenarios', 'copy-apply')
        saved_slots = bytes(owner.slots)
        CASE_HINT = 'lifecycle/clear-copy'
        if clear(d, shared) or any(bytes(shared)) or bytes(owner.slots) != saved_slots:
            raise AssertionError('clear副本未零或擦写共享表')
        receipt('lifecycle_scenarios', 'clear-copy')
        CASE_HINT = 'lifecycle/original-still-usable'
        if call(c, owner.model, replay.ctypes.data, target.ctypes.data, len(replay) // 3) or bytes(target) != expected_replay:
            raise AssertionError('clear副本损坏原view')
        receipt('lifecycle_scenarios', 'original-still-usable')
        CASE_HINT = 'lifecycle/clear-again'
        if clear(d, shared) or any(bytes(shared)) or bytes(owner.slots) != saved_slots:
            raise AssertionError('重复clear非幂等')
        receipt('lifecycle_scenarios', 'clear-again')
        for value in [0, *[ct.addressof(shared) + offset for offset in range(1, 8)]]:
            prior = bytes(shared)
            CASE_HINT = 'clear-reject/' + str(value)
            if not clear(d, value) or bytes(shared) != prior:
                raise AssertionError('clear NULL/错位未无写拒绝')
            receipt('clear_rejections', str(value))

        for n in (0, 1, 2, 3, 7, 8, 9, 15, 16, 17, 31, 32, 33, 65535, 65536, 65537, 131071, 131072):
            values = rng.integers(0, 256, 3 * n, dtype=np.uint8)
            expected = oracle(values).tobytes()
            with Guard(3 * n) as source, Guard(3 * n) as target_guard:
                for label, lib, model, threads, same in finite_configs:
                    ct.memmove(source.start, values.ctypes.data, 3 * n)
                    dest = source.start if same else target_guard.start
                    CASE_HINT = f'image-guard/{label}/{n}'
                    if call(lib, model, source.start, dest, n, threads) or ct.string_at(dest, 3 * n) != expected:
                        raise AssertionError('图像NOACCESS guard失败：' + label)
                    receipt('image_guards', f'{label}/{n}')

        actual = rom.read_bytes()
        probe = np.concatenate([pixels(np.array([0, 1, 4094, 4095, 4096, 4097,
                     (1 << 24) - 2, (1 << 24) - 1], dtype=np.uint64)),
                     pixels((np.arange(4096, dtype=np.uint64) << 12) | 4095)])
        fixture_receipts = {}
        for kind in ('actual', 'count1', 'count256', 'max4096'):
            content = actual if kind == 'actual' else fixture(1 if kind == 'count1' else 256, 4096 if kind == 'max4096' else 1)
            data = np.frombuffer(content, dtype=np.uint8)
            maps = np.frombuffer(content, dtype='<u2', count=4096, offset=1056).astype(np.uint64)
            key = codes(probe)
            ids = data[9248 + maps[key >> 12] * 4096 + (key & 4095)]
            expected = data[32:1056].reshape(256, 4)[ids, :3].reshape(-1).tobytes()
            if kind in ('count256', 'max4096') and expected[21:24] != b'\xff\xff\xff':
                raise AssertionError('fixture未触达palette255')
            with Guard(len(content)) as area:
                buffer = (ct.c_uint8 * len(content)).from_buffer_copy(content)
                ct.memmove(area.start, buffer, len(content))
                area.readonly()
                view = PagesView()
                slots = (ct.c_void_p * 4096)()
                ct.memset(ct.addressof(slots), 0xa5, ct.sizeof(slots))
                CASE_HINT = 'rom-guard-prepare/' + kind
                if prepare(d, view, area.start, len(content), ct.addressof(slots)):
                    raise AssertionError('精确ROM guard prepare失败')
                for index in range(4096):
                    if slots[index] != view.base.pool + int(maps[index]) * 4096:
                        raise AssertionError('prepare未完整覆盖合法4096槽')
                    receipt('fixture_pointer_equalities', f'{kind}/{index}')
                for label, lib, unused, threads, same in configs:
                    target = probe.copy() if same else np.empty_like(probe)
                    src = target.ctypes.data if same else probe.ctypes.data
                    CASE_HINT = 'rom-guard/' + kind + '/' + label
                    if call(lib, view, src, target.ctypes.data, len(probe) // 3, threads) or bytes(target) != expected:
                        raise AssertionError('ROM末端NOACCESS失败：' + kind + label)
                    receipt('rom_guards', kind + '/' + label)
                CASE_HINT = 'rom-guard-clear/' + kind
                if clear(d, view):
                    raise AssertionError('ROM guard view清理失败')
            with Guard(32768) as slot_area:
                buffer = (ct.c_uint8 * len(content)).from_buffer_copy(content)
                view = PagesView()
                CASE_HINT = 'pointer-guard-prepare/' + kind
                if prepare(d, view, ct.addressof(buffer), len(content), slot_area.start):
                    raise AssertionError('末槽NOACCESS prepare失败')
                slot_area.readonly()
                for label, lib, unused, threads, same in configs:
                    target = probe.copy() if same else np.empty_like(probe)
                    src = target.ctypes.data if same else probe.ctypes.data
                    CASE_HINT = 'pointer-guard/' + kind + '/' + label
                    if call(lib, view, src, target.ctypes.data, len(probe) // 3, threads) or bytes(target) != expected:
                        raise AssertionError('native表末槽NOACCESS失败：' + kind + label)
                    receipt('pointer_table_guards', kind + '/' + label)
                CASE_HINT = 'pointer-guard-clear/' + kind
                if clear(d, view):
                    raise AssertionError('pointer guard view清理失败')
            fixture_receipts[kind] = dict(bytes=len(content), sha256=hashlib.sha256(content).hexdigest(),
                expected_sha256=hashlib.sha256(expected).hexdigest(), probe_pixels=len(probe) // 3)

        expected = oracle(probe).tobytes()
        for offset in range(8):
            content = bytearray(len(actual) + offset)
            content[offset:] = actual
            buffer = (ct.c_uint8 * len(content)).from_buffer(content)
            view = PagesView()
            slots = (ct.c_void_p * 4096)()
            CASE_HINT = 'unaligned-prepare/' + str(offset)
            if prepare(d, view, ct.addressof(buffer) + offset, len(actual), ct.addressof(slots)):
                raise AssertionError('合法非对齐ROM prepare失败')
            for label, lib, unused, threads, same in configs:
                target = probe.copy() if same else np.empty_like(probe)
                src = target.ctypes.data if same else probe.ctypes.data
                CASE_HINT = f'unaligned/{offset}/{label}'
                if call(lib, view, src, target.ctypes.data, len(probe) // 3, threads) or bytes(target) != expected:
                    raise AssertionError('合法非对齐ROM输出失败：' + label)
                receipt('unaligned_rom', f'{offset}/{label}')
            CASE_HINT = 'unaligned-clear/' + str(offset)
            if clear(d, view):
                raise AssertionError('非对齐ROM view清理失败')
        for prepared, view, slots in states:
            CASE_HINT = 'failure-state-clear/' + str(prepared)
            if clear(d, view):
                raise AssertionError('失败保留夹具清理失败')
        CASE_HINT = 'owner-close'
    if any(bytes(owner.model)) or any(bytes(portable.model)) or not owner.file_view.closed or not portable.file_view.closed:
        raise AssertionError('借用owner未清零/关闭')
    if counts != plan['expected_counts']:
        save(args.output / 'count-failure.json', dict(actual=counts, expected=plan['expected_counts']))
        raise AssertionError('有限计数不等于构建前冻结值')
    for name, expected in plan['input_sha256'].items():
        if sha(name) != expected:
            raise AssertionError('有限期间原输入改变')
    save(args.output / 'results.json', dict(passed=True, purpose=__doc__, plan_sha256=sha(PLAN),
        environment=env(), counts=counts, events=events, fixtures=fixture_receipts,
        native_entry_receipts=[d.pages_receipt, c.pages_receipt], before=before, after=snapshot(),
        actual_capacity=12665940, scope='只有预注册有限/拒绝/生命周期/guard，不是完整色域/百图/吞吐/WASM。峰包含Python/库/oracle/夹具，非prepare峰。'))
    print(dict(passed=True, counts=counts, capacity=12665940), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        OBSERVATION['failure'] = dict(type=type(error).__name__, message=str(error))
        raise
    finally:
        if RECORDER is not None:
            OBSERVATION['native_attempts'] = ATTEMPTS
            OBSERVATION['scope'] = '逐模型native调用前与逐receipt追加flush；finally保存累计/入口/快照。4个布局getter各DLL另调用，不混入模型尝试数。native硬fault或进程强退可能跳过finally，JSONL只证明已flush的尝试，不承诺系统断电持久性。原v1 STOP不撤销。'
            try:
                OBSERVATION['after'] = snapshot()
            except BaseException as snapshot_error:
                OBSERVATION['snapshot_error'] = str(snapshot_error)
            append_event(dict(event='finally', native_attempts=ATTEMPTS,
                              failed='failure' in OBSERVATION))
            RECORDER.close()
            save(Path(OBSERVATION['output']) / 'observations.json', OBSERVATION)
