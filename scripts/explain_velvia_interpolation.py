"""固定小样本比较Velvia插值表达，不拟合、不输出新模型、不重新映射全色域。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import interp, io, study_provenance


PLAN = {
    'schema': 1,
    'purpose': '固定模型、固定探针，区分插值算子、节点取值/量化与粗网格表达误差；不是matched最优拟合比较',
    'model': {'path': 'artifacts/joint-grid-budget-v2/joint_grid_iter1600/model.slut',
              'sha256': '2dd467b040a4ed25f9000e7debd085af4a07f08d780be2fbcd156c9aa8118947'},
    'grid': {'path': 'artifacts/joint-grid-full-prepare/baseline-grid.npy',
             'sha256': '1b62bbc42278fc9deb993e1dc3b1c1973fbc9a47aa7e108d891c51cec26d2eb3'},
    'table': {'path': 'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256',
              'sha256': '6c4387352bd0845ce597f13dca32f2f808b39439d06ce78b4881922a4fc294b7'},
    'source': {'path': 'assets/LUT/sources/filmsim/Velvia_Vivid_v2.tif',
               'sha256': '1b347b4c5afec78ad7f79103bf04b319e182b7133ffe2a8864c732a7003b7eea'},
    'stream': {'path': 'artifacts/joint-grid-budget-v2/joint_grid_iter1600/cube.rgb',
               'sha256': 'd5453bd8ab99eea82582b3f9710e9b9c40c79ea78e0e58f0c1d818d0910e74d7'},
    'partition': 'artifacts/full-photo-v1/photo-partition.json',
    'frequency_metadata': 'artifacts/cinema-prefix-stage1-v1/training.json',
    'frequency': {'path': 'artifacts/cinema-prefix-stage1-v1/photo-arrival-frequency.npy',
                   'sha256': '1eff7aab15715845bbc3efda68043a62a5c2dd9162f33717cee8bea5d36b756e'},
    'frequency_array_sha256': '20af718acb2868e9d2c1453aea7193bbbaac4c6cf91d8eff79c8185430dac300',
    'probe_rows_each': 16384, 'uniform_seed': 2026101909, 'photo_seed': 2026101910,
    'worst_rows': 16,
    'worst_order': '旧已验全域流误差平方降序，再按B最快RGB整数键升序；只读取既有流与参考',
    'scope': '只映射两组固定16384探针和旧流top16；顶点诊断读取33³小数坐标的原表三线性值；不新增来源、不拟合、不做性能比较或完整验收',
}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']:
        raise ValueError(f'输入SHA不符：{path}')
    return path


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def colours(keys):
    keys = np.asarray(keys, np.int64)
    return np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)


def rounded(values):
    return np.clip(np.floor(np.asarray(values)+.5), 0, 255).astype(np.uint8)


def full_trilinear(table, positions):
    """以真实小数坐标读取完整RGB8表，保留浮点值；绝不先取整坐标。"""
    positions = np.asarray(positions, np.float64)
    lower = np.floor(positions).astype(np.intp)
    upper = np.minimum(lower+1, 255)
    fraction = positions-lower
    output = np.zeros((len(positions), 3), np.float64)
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                bits = np.array((dr, dg, db))
                index = np.where(bits, upper, lower)
                weight = np.prod(np.where(bits, fraction, 1-fraction), axis=1)
                output += weight[:, None]*table[index[:, 0], index[:, 1], index[:, 2]]
    return output


def evaluate(nodes, model, points, kind):
    function = interp.tetra_weights if kind == 'tetra' else interp.tri_weights
    indices, weight = function(points, *model.tables(), model.m)
    if not np.all(np.abs(weight.sum(axis=1)-1) < 2e-15) or np.any(weight < 0):
        raise AssertionError('不是凸插值权重')
    return np.einsum('nk,nkc->nc', weight, nodes.reshape(-1, 3)[indices])


def metrics(prediction, target):
    squared = np.sum((np.asarray(prediction, np.float64)-target.astype(np.float64))**2, axis=1)
    distance = np.sqrt(squared)
    return {'n': len(squared), 'mean': float(distance.mean()), 'rms': float(np.sqrt(squared.mean())),
            'p99': float(np.percentile(distance, 99)), 'max': float(distance.max()),
            'fraction_gt_6': float(np.mean(squared > 36))}


def old_worst(stream, table, count):
    """只比较已保存字节，不调用任何模型；固定并列顺序。"""
    truth = table.reshape(-1, 3)
    best_keys, best_d2 = np.empty(0, np.int64), np.empty(0, np.int64)
    for start in range(0, len(stream), 1 << 18):
        stop = min(start+(1 << 18), len(stream))
        delta = stream[start:stop].astype(np.int32)-truth[start:stop].astype(np.int32)
        squared = np.sum(delta*delta, axis=1, dtype=np.int32)
        cutoff = np.partition(squared, -count)[-count]
        local = np.flatnonzero(squared >= cutoff)
        local = local[np.lexsort((local, -squared[local]))[:count]]
        keys = np.concatenate((best_keys, local+start))
        d2 = np.concatenate((best_d2, squared[local]))
        order = np.lexsort((keys, -d2))[:count]
        best_keys, best_d2 = keys[order], d2[order]
    return best_keys, best_d2


def probe(nodes_by_name, model, table, stream, keys):
    points = colours(keys)
    truth = table[points[:, 0], points[:, 1], points[:, 2]]
    variants, outputs = {}, {}
    for node_name, nodes in nodes_by_name.items():
        for kind in ('tetra', 'tri'):
            values = evaluate(nodes, model, points, kind)
            output = rounded(values)
            name = f'{node_name}_{kind}'
            variants[name] = {'rgb8': metrics(output, truth), 'continuous': metrics(values, truth)}
            outputs[name] = {'continuous': values, 'rgb8': output}
    old = outputs['fitted_rgb8_tetra']['rgb8']
    direct = interp.apply_tetra_q16(model, points)
    if not np.array_equal(old, direct) or not np.array_equal(old, stream[keys]):
        raise AssertionError('诊断基线不同于已验收权威Q16/已存全域流')
    baseline_d2 = np.sum((old.astype(np.int32)-truth.astype(np.int32))**2, axis=1)
    tail = baseline_d2 >= np.percentile(baseline_d2, 99)
    for name, result in variants.items():
        output = outputs[name]['rgb8']
        d2 = np.sum((output.astype(np.int32)-truth.astype(np.int32))**2, axis=1)
        result['fixed_baseline_tail'] = metrics(output[tail], truth[tail])
        result['change_counts_vs_fitted_tetra'] = {
            'better': int(np.count_nonzero(d2 < baseline_d2)),
            'equal': int(np.count_nonzero(d2 == baseline_d2)),
            'worse': int(np.count_nonzero(d2 > baseline_d2))}
    return {'rows': len(points), 'points_sha256': hashlib.sha256(points.tobytes()).hexdigest(),
            'baseline_stream_mismatches': 0, 'integer_oracle_mismatches': 0,
            'fixed_tail_rows': int(tail.sum()), 'variants': variants}, outputs, truth


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖既有诊断')
    paths = {name: checked(PLAN[name]) for name in ('model', 'grid', 'table', 'source', 'stream', 'frequency')}
    model = io.load_sparse(paths['model'], competition=True)
    grid = np.load(paths['grid'])
    if not np.array_equal(grid, model.grid) or not all(
            np.array_equal(a, b) for a, b in zip(io.axis_tables(grid), model.tables())):
        raise ValueError('小数网格与权威模型坐标不同')
    table = io.load_full(paths['table'], mmap=True)
    stream = np.memmap(paths['stream'], dtype=np.uint8, mode='r', shape=(256**3, 3))
    training = read(ROOT/PLAN['frequency_metadata'])
    partition = read(ROOT/PLAN['partition'])
    frequency = np.load(paths['frequency'], mmap_mode='r')
    if (training['prefix_model_sha256'] != [] or frequency.dtype != np.uint32
            or frequency.shape != (256**3,)
            or digest(paths['frequency']) != training['artifact_sha256']['photo-arrival-frequency.npy']
            or hashlib.sha256(frequency.astype('<u4', copy=False).tobytes()).hexdigest() != PLAN['frequency_array_sha256']
            or int(frequency.sum(dtype=np.uint64)) != 60*1024*768
            or [r['id'] for r in training['training_images']] != [r['id'] for r in partition['training']['images']]
            or [r['sha256'] for r in training['training_images']] != [r['file_sha256'] for r in partition['training']['images']]):
        raise ValueError('频数没有绑定原60图原色测度')
    vertices = np.stack(np.meshgrid(*grid, indexing='ij'), axis=-1).reshape(-1, 3)
    source_nodes = full_trilinear(table, vertices).reshape(model.m, model.m, model.m, 3)
    nodes_by_name = {'fitted_rgb8': model.nodes, 'source_float': source_nodes,
                     'source_rounded_rgb8': rounded(source_nodes)}
    # 两组颜色与旧流最坏色在所有诊断中完全相同，不按诊断结果重选样本。
    uniform_keys = np.random.default_rng(PLAN['uniform_seed']).choice(256**3, PLAN['probe_rows_each'], replace=False)
    ranks = np.random.default_rng(PLAN['photo_seed']).integers(0, int(frequency.sum(dtype=np.uint64)), PLAN['probe_rows_each'])
    photo_keys = np.searchsorted(np.cumsum(frequency, dtype=np.uint64), ranks, side='right')
    worst_keys, worst_d2 = old_worst(stream, table, PLAN['worst_rows'])
    source_files = [Path(__file__), ROOT/'python/lutlab/interp.py', ROOT/'python/lutlab/io.py',
                    ROOT/'python/lutlab/study_provenance.py']
    result = {'plan': PLAN, 'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in source_files},
        'environment': study_provenance.environment_fingerprint(),
        'input_sha256': {name: digest(path) for name, path in paths.items()},
        'frequency_metadata_sha256': digest(ROOT/PLAN['frequency_metadata']),
        'partition_sha256': digest(ROOT/PLAN['partition']),
        'node_sampling': {'method': '完整RGB8原表在当前小数网格顶点的浮点三线性读取',
            'vertices': len(vertices), 'fractional_coordinate_count': int(np.count_nonzero(vertices != np.floor(vertices))),
            'source_float_nodes_sha256': hashlib.sha256(source_nodes.astype('<f8').tobytes()).hexdigest(),
            'maximum_single_channel_quantization_error': float(np.abs(source_nodes-rounded(source_nodes)).max()),
            'fitted_vs_sampled_node_distance': metrics(model.nodes.reshape(-1, 3), source_nodes.reshape(-1, 3))},
        'interpretation': '现节点专为四面体拟合；换三线性不是各方法matched最优。浮点节点只是不可部署控制；原拟合节点换成采样浮点节点同时改变拟合/采样策略，不可将差值全称节点量化。source_float与source_rounded对照才单独观察采样节点量化。无新模型、全域映射或性能比较。',
        'results': {}}
    all_outputs = {}
    for name, keys in (('uniform_probe', uniform_keys), ('training_photo_probe', photo_keys), ('old_stream_worst16', worst_keys)):
        details, outputs, truth = probe(nodes_by_name, model, table, stream, keys)
        result['results'][name] = details
        all_outputs[name] = (outputs, truth)
    result['results']['uniform_probe']['seed'] = PLAN['uniform_seed']
    result['results']['training_photo_probe']['seed'] = PLAN['photo_seed']
    outputs, truth = all_outputs['old_stream_worst16']
    points = colours(worst_keys)
    idx, frac = model.tables()
    traces = []
    for row, point in enumerate(points):
        cell = np.array([idx[a, point[a]] for a in range(3)], dtype=np.intp)
        corners = []
        for dr in (0, 1):
            for dg in (0, 1):
                for db in (0, 1):
                    vertex = cell+np.array((dr, dg, db))
                    corners.append({'bits': [dr, dg, db], 'node_index': vertex.tolist(),
                        'coordinate': [float(grid[a, vertex[a]]) for a in range(3)],
                        'source_float': source_nodes[tuple(vertex)].tolist(),
                        'source_rounded_rgb8': rounded(source_nodes[tuple(vertex)]).tolist(),
                        'fitted_rgb8': model.nodes[tuple(vertex)].tolist()})
        physical = (point.astype(np.float64)-grid[np.arange(3), cell])/(grid[np.arange(3), cell+1]-grid[np.arange(3), cell])
        traces.append({'rank': row+1, 'rgb_key': int(worst_keys[row]), 'rgb': point.tolist(),
            'target': truth[row].tolist(), 'old_error_squared': int(worst_d2[row]),
            'training_pixel_frequency': int(frequency[worst_keys[row]]), 'cell': cell.tolist(),
            'q16_fraction': [int(frac[a, point[a]]) for a in range(3)],
            'physical_fraction': physical.tolist(),
            'outputs': {name: {'rgb8': value['rgb8'][row].tolist(), 'continuous': value['continuous'][row].tolist(),
                'rgb8_distance': float(np.linalg.norm(value['rgb8'][row].astype(np.float64)-truth[row]))}
                for name, value in outputs.items()}, 'eight_corners': corners})
    result['worst_traces'] = traces
    args.output.mkdir(parents=True)
    np.savez_compressed(args.output/'fixed-probes.npz', uniform_keys=uniform_keys, photo_keys=photo_keys, worst_keys=worst_keys)
    result['fixed_probes_sha256'] = digest(args.output/'fixed-probes.npz')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in source_files:
            if digest(path) != result['source_sha256'][path.relative_to(ROOT).as_posix()]:
                raise ValueError('诊断运行中相关源码改变')
            archive.write(path, path.relative_to(ROOT).as_posix())
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({name: {key: value['rgb8'] for key, value in details['variants'].items()}
        for name, details in result['results'].items()}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
