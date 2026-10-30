"""新页指针5完整域/5×100逐图u64等价质量；无拟合、性能或跨平台运行。"""
import argparse
import ctypes as ct
import hashlib
import json
from pathlib import Path
import numpy as np
from page_id16_native_pages_common import (ROOT, BUILD, PagesView, BorrowedPages,
    library, call, sha, save, env, snapshot, query, read)

PLAN = ROOT / 'experiments/page-id16-native-pages-full-v1.json'
OBSERVATION = {}
STREAM = None
APPLY_ATTEMPTS = 0


def emit(value):
    STREAM.write(json.dumps(value, ensure_ascii=False) + '\n')
    STREAM.flush()


def main():
    global STREAM, APPLY_ATTEMPTS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan = read(PLAN)
    for name, expected in plan['source_sha256'].items():
        if sha(ROOT / name) != expected:
            raise AssertionError('完整质量冻结源不同：' + name)
    for name, expected in plan['input_sha256'].items():
        if sha(name) != expected:
            raise AssertionError('完整质量冻结输入不同：' + name)
    args.output.mkdir(parents=True, exist_ok=False)
    OBSERVATION['output'] = str(args.output)
    STREAM = (args.output / 'apply-events.jsonl').open('x', encoding='utf-8', newline='\n')
    before = snapshot()
    OBSERVATION['before'] = before
    d = library(BUILD / 'jshc_page_native_pages.dll', True)
    c = library(BUILD / 'jshc_page_native_pages_c99.dll', False)
    OBSERVATION['native_entry_receipts'] = [d.pages_receipt, c.pages_receipt]
    for lib in (d, c):
        actual = (lib.jshc_p4_pages_view_size(), lib.jshc_p4_pages_pointer_alignment(),
                  lib.jshc_p4_pages_view_alignment(), lib.jshc_p4_pages_slots_bytes())
        if actual != (48, 8, 8, 32768) or ct.sizeof(PagesView) != 48:
            raise AssertionError('实际新ABI改变')
    old = np.memmap(plan['original_rom'], dtype=np.uint8, mode='r')
    palette = old[32:1056].reshape(256, 4)

    def oracle(values):
        rgb = values.reshape(-1, 3).astype(np.uint64)
        key = rgb[:, 0] | (rgb[:, 1] << 8) | (rgb[:, 2] << 16)
        return palette[old[1056 + key], :3].reshape(-1).copy()

    per_mode = {}
    full_rows, photo_rows = [], []
    OBSERVATION['per_mode_apply_attempts'] = per_mode
    with BorrowedPages(Path(plan['page_rom']), d) as owner, BorrowedPages(Path(plan['page_rom']), c) as portable:
        for holder in (owner, portable):
            if query(holder.model.base.blob)['Protect'] != 2 or query(holder.model.base.blob + holder.model.base.blob_bytes - 1)['Protect'] != 2:
                raise AssertionError('ROM不是实际只读映射')
            if holder.model.base.blob_bytes != 12633124 or holder.model.pages != ct.addressof(holder.slots):
                raise AssertionError('实际借用字段不同')
        configs = [('core_out', c, portable.model, None, False)]
        for threads in (1, 4):
            for same in (False, True):
                configs.append(('c99' + str(threads) + ('_in' if same else '_out'), d, owner.model, threads, same))
        per_mode.update({label: 0 for label, *_ in configs})

        def invoke(config, source, expected, case):
            global APPLY_ATTEMPTS
            label, lib, model, threads, same = config
            target = source.copy() if same else np.empty_like(source)
            src = target.ctypes.data if same else source.ctypes.data
            APPLY_ATTEMPTS += 1
            per_mode[label] += 1
            symbol = 'jshc_p4_pages_apply' if threads is None else 'jshc_p4_pages_apply_parallel'
            emit(dict(event='apply_attempt', ordinal=APPLY_ATTEMPTS, mode=label, case=case,
                symbol=symbol, symbol_address=lib.pages_receipt['addresses'][symbol],
                library_sha256=lib.pages_receipt['sha256'], view_address=ct.addressof(model),
                pages_address=model.pages, source=src, target=target.ctypes.data,
                pixels=len(source) // 3, threads=threads))
            code = call(lib, model, src, target.ctypes.data, len(source) // 3, threads)
            output_sha = hashlib.sha256(target).hexdigest() if code == 0 else None
            equal = code == 0 and np.array_equal(target, expected)
            emit(dict(event='apply_return', ordinal=APPLY_ATTEMPTS, returncode=code,
                      output_sha256=output_sha, equal_to_independent_u64=bool(equal)))
            if not equal:
                raise AssertionError('新完整质量首错STOP：' + case + '/' + label)
            return target, output_sha

        full_hashes = {label: hashlib.sha256() for label, *_ in configs}
        reference = hashlib.sha256()
        for begin in range(0, 1 << 24, 1 << 18):
            enumerated = np.arange(begin, begin + (1 << 18), dtype=np.uint64)
            rgb = np.empty((len(enumerated), 3), dtype=np.uint8)
            rgb[:, 0], rgb[:, 1], rgb[:, 2] = enumerated >> 16, enumerated >> 8, enumerated
            source = rgb.reshape(-1)
            expected = oracle(source)
            reference.update(expected)
            row = dict(begin=begin, pixels=len(enumerated), oracle_sha256=hashlib.sha256(expected).hexdigest(), modes={})
            for config in configs:
                target, output_sha = invoke(config, source, expected, 'full/' + str(begin))
                full_hashes[config[0]].update(target)
                row['modes'][config[0]] = output_sha
            full_rows.append(row)
        full = {label: value.hexdigest() for label, value in full_hashes.items()}
        if reference.hexdigest() != '3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22' or set(full.values()) != {reference.hexdigest()}:
            raise AssertionError('完整域SHA不是原a399输出')
        photo_hashes = {label: hashlib.sha256() for label, *_ in configs}
        input_hash = hashlib.sha256()
        with Path(plan['photos']).open('rb') as stream:
            for index in range(100):
                raw = stream.read(1024 * 768 * 3)
                if len(raw) != 1024 * 768 * 3:
                    raise AssertionError('照片输入截断')
                input_hash.update(raw)
                source = np.frombuffer(raw, dtype=np.uint8)
                expected = oracle(source)
                row = dict(image=index, oracle_sha256=hashlib.sha256(expected).hexdigest(), modes={})
                for config in configs:
                    target, output_sha = invoke(config, source, expected, 'photo/' + str(index))
                    photo_hashes[config[0]].update(target)
                    row['modes'][config[0]] = output_sha
                photo_rows.append(row)
            if stream.read(1):
                raise AssertionError('照片文件多余字节')
        photos = {label: value.hexdigest() for label, value in photo_hashes.items()}
        if input_hash.hexdigest() != 'e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd' or set(photos.values()) != {'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'}:
            raise AssertionError('百图原输入/输出身份不同')
    if any(bytes(owner.model)) or any(bytes(portable.model)) or not owner.file_view.closed or not portable.file_view.closed:
        raise AssertionError('完整质量owner未清零/关闭')
    if APPLY_ATTEMPTS != 820 or per_mode != {label: 164 for label in per_mode} or len(full_rows) != 64 or len(photo_rows) != 100:
        raise AssertionError('完整域/逐图次数与原预注册不同')
    for name, expected in plan['input_sha256'].items():
        if sha(name) != expected:
            raise AssertionError('完整质量期间原输入改变')
    save(args.output / 'results.json', dict(passed=True, purpose=__doc__, plan_sha256=sha(PLAN),
        environment=env(), full_hashes=full, photos_hashes=photos, full_rows=full_rows,
        photo_rows=photo_rows, photos_input_sha256=input_hash.hexdigest(),
        per_mode_apply_attempts=per_mode, total_apply_attempts=APPLY_ATTEMPTS,
        native_entry_receipts=[d.pages_receipt, c.pages_receipt], before=before, after=snapshot(),
        actual_rom_bytes=12633124, actual_view_bytes=48, actual_slots_bytes=32768,
        actual_capacity=12665940,
        scope='只有本机x64新C99 5完整域和5×100逐图u64/SHA质量，精确复现原输出而非误差为零；不是速度/可移植实机/WASM。峰含两实例/两映射/Python/库/oracle/照片/日志，不称prepare峰。'))
    print(dict(passed=True, full_modes=len(full), photos_per_mode=100,
               new_apply_attempts=APPLY_ATTEMPTS, capacity=12665940), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        OBSERVATION['failure'] = dict(type=type(error).__name__, message=str(error))
        raise
    finally:
        if STREAM is not None:
            OBSERVATION['total_apply_attempts'] = APPLY_ATTEMPTS
            try:
                OBSERVATION['after'] = snapshot()
            except BaseException as error:
                OBSERVATION['snapshot_error'] = str(error)
            emit(dict(event='finally', apply_attempts=APPLY_ATTEMPTS, failed='failure' in OBSERVATION))
            STREAM.close()
            save(Path(OBSERVATION['output']) / 'observations.json', OBSERVATION)
