"""只分析分通道四面体的节点地址复用机会，不映射像素或计时运行时。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
from numba import njit, prange
import numpy as np
from PIL import Image
from lutlab import channel_coordinates as cc, study_provenance


def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']: raise ValueError('冻结输入SHA不同')
    return path


@njit(cache=True, parallel=True)
def classify(frac):
    """精确对应已测AVX2高/低轴的严格比较及同值分支，只记录地址轴。"""
    flags = np.empty(256**3, np.uint8)
    for key in prange(256**3):
        r, g, b = key >> 16, (key >> 8)&255, key&255
        first0, last0 = -1, -1
        common_first, common_last = True, True
        for c in range(3):
            x, y, z = frac[c, 0, r], frac[c, 1, g], frac[c, 2, b]
            first = 1 if y > x else 0
            high = max(x, y)
            if z > high: first = 2
            last = 1 if x > y else 0
            low = min(x, y)
            if low > z: last = 2
            if c == 0: first0, last0 = first, last
            else:
                common_first = common_first and first == first0
                common_last = common_last and last == last0
        flags[key] = int(common_first)+2*int(common_last)
    return flags


def summarize(flags, weights=None):
    n = len(flags) if weights is None else int(weights.sum(dtype=np.uint64))
    result = {'pixels': n}
    for name, mask in [('common_first', (flags&1) != 0), ('common_last', (flags&2) != 0), ('common_both', flags == 3)]:
        count = int(np.count_nonzero(mask)) if weights is None else int(weights[mask].sum(dtype=np.uint64))
        result[name+'_pixels'] = count; result[name+'_fraction'] = count/n
    if weights is None:
        if len(flags)%8: raise ValueError('预声明8像素包必须完整')
        packets = flags.reshape(-1, 8)
        result['eight_pixel_packets'] = len(packets)
        for name, mask in [('common_first', np.all((packets&1) != 0, axis=1)),
                           ('common_last', np.all((packets&2) != 0, axis=1)), ('common_both', np.all(packets == 3, axis=1))]:
            result[name+'_whole_packet_count'] = int(mask.sum())
            result[name+'_whole_packet_fraction'] = float(mask.mean())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.plan = args.plan.resolve(); args.output = args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖已有诊断')
    plan = json.loads(args.plan.read_text('utf-8')); paths = {n: checked(s) for n, s in plan['inputs'].items()}
    if plan['threads'] != 4 or plan['packet_pixels'] != 8: raise ValueError('冻结4线程与8像素包')
    numba.set_num_threads(4)
    with np.load(paths['model']) as z:
        model = cc.ChannelLut(z['grid'], z['nodes'], z['shared_idx'], z['channel_frac']); cc.validate(model)
    frequency = np.load(paths['frequency'], mmap_mode='r')
    if frequency.shape != (256**3,) or frequency.dtype != np.uint32 or int(frequency.sum(dtype=np.uint64)) != 60*1024*768:
        raise ValueError('不是原完整60训练图频数')
    with Image.open(paths['image']) as image:
        if image.mode != 'RGB' or image.size != (1024, 768): raise ValueError('固定图片格式不符')
        pixels = np.asarray(image).reshape(-1, 3)
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), args.plan,
        ROOT/'python/lutlab/channel_coordinates.py', ROOT/'python/lutlab/io.py', ROOT/'python/lutlab/study_provenance.py',
        ROOT/'experiments/channel-runtime/channel_avx2.cpp']}
    flags = classify(model.channel_frac)
    uniform, training = summarize(flags), summarize(flags, frequency)
    keys = pixels.astype(np.int64)@np.array([65536, 256, 1], np.int64)
    pilot = summarize(flags[keys])
    feasible = (pilot['common_both_whole_packet_fraction'] >= plan['feasibility']['pilot_packet_common_both_min']
                and training['common_both_fraction'] >= plan['feasibility']['training_pixel_common_both_min'])
    if sources != {n: digest(ROOT/n) for n in sources}: raise ValueError('诊断期间来源变化')
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sources: z.write(ROOT/name, name)
    result = {'purpose': __doc__, 'plan': plan, 'source_sha256': sources,
              'input_sha256': {n: digest(p) for n, p in paths.items()}, 'environment': study_provenance.environment_fingerprint(),
              'numba_threads': 4, 'uniform_canonical_order': uniform, 'training_60_frequency': training,
              'pilot_original_pixel_order': pilot, 'pilot_decoded_pixel_sha256': digest_bytes(pixels),
              'fastpath_feasibility_gate_passed': feasible, 'pixel_mapping_calls': 0, 'native_benchmarks': 0,
              'limits': plan['limits']}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'uniform': uniform, 'training': training, 'pilot': pilot, 'feasible': feasible}, ensure_ascii=False, indent=2))


def digest_bytes(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


if __name__ == '__main__': main()
