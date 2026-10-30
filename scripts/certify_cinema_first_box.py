"""对原max_first全部116热点枚举首级±2输出包围盒，求固定后缀必要误差下界。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import integer_first_box as box, study_provenance
from run_channel_tail_nodes import digest, save, load_model


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--contract', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖首级盒必要条件证书')
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass']: raise ValueError('有限盒合同未通过')
    for name, sha in contract['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('有限合同执行源已变：'+name)
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'
    run = json.loads((prior/'run.json').read_text(encoding='utf-8'))
    summary = json.loads((prior/'summary.json').read_text(encoding='utf-8'))
    independent = json.loads((ROOT/'artifacts/cinema-first-hotspot-independent-v1.json').read_text(encoding='utf-8'))
    if not independent['pass'] or digest(prior/'support-index.npz') != independent['support_index_sha256']:
        raise ValueError('已认证116热点/86节点支撑已变')
    for spec in run['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('原max_first或原数据字节已变')
    if digest(prior/'suffix.npy') != summary['suffix_sha256']: raise ValueError('原904e/95cb/5b8后缀已变')
    with np.load(prior/'support-index.npz') as data: hotspots, selected = data['hotspot_keys'], data['selected_nodes']
    if len(hotspots) != 116 or len(selected) != 86: raise ValueError('不是冻结116点/86节点')
    model = load_model(run['inputs']['first']['path']); gold = np.load(run['inputs']['reference']['path'], mmap_mode='r')
    baseline = np.memmap(run['inputs']['cube']['path'], dtype=np.uint8, mode='r', shape=(256**3, 3))
    suffix = np.load(prior/'suffix.npy', mmap_mode='r'); records = []; queries = 0
    plan = ROOT/'experiments/p16-cinema-first-box-v1.json'
    sources = [Path(__file__), plan, ROOT/'python/lutlab/integer_first_box.py', ROOT/'scripts/check_cinema_first_box.py',
               ROOT/'scripts/audit_cinema_first_box.py', ROOT/'scripts/run_channel_tail_nodes.py',
               ROOT/'python/lutlab/channel_coordinates.py', ROOT/'python/lutlab/io.py',
               ROOT/'python/lutlab/channel_hotspot_support.py', ROOT/'python/lutlab/interp.py',
               ROOT/'scripts/verify_channel_coordinates.py', ROOT/'python/lutlab/study_provenance.py']
    frozen = {'inputs': run['inputs'], 'support_index_sha256': digest(prior/'support-index.npz'),
              'suffix_sha256': summary['suffix_sha256'], 'contract_sha256': digest(args.contract),
              'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
              'environment': study_provenance.environment_fingerprint(), 'plan': json.loads(plan.read_text(encoding='utf-8'))}
    frozen_path = args.output.with_name(args.output.stem+'-frozen.json')
    if frozen_path.exists(): raise ValueError('不覆盖必要条件证书执行前冻结身份')
    save(frozen_path, frozen)
    for source in hotspots:
        k = int(source); point = [k>>16, (k>>8)&255, k&255]
        bounds = box.point_box(model, point, selected)
        baseline_first = [(channel['baseline_acc']+32768)//65536 for channel in bounds['channels']]
        first_key = (baseline_first[0]<<16)|(baseline_first[1]<<8)|baseline_first[2]
        np.testing.assert_array_equal(suffix[first_key], baseline[k])
        original_error = baseline[k].astype(np.int32)-gold[k].astype(np.int32)
        if int(original_error@original_error) != 50: raise AssertionError('不是原max50输入')
        rgb_values = list(itertools.product(*[range(lo, hi+1) for lo, hi in zip(bounds['lower_rgb'], bounds['upper_rgb'])]))
        if len(rgb_values) > 125: raise AssertionError('盒大小超预注册125')
        errors = []; finals = []
        for r, g, b in rgb_values:
            final = suffix[(r<<16)|(g<<8)|b]
            error = [int(final[c])-int(gold[k, c]) for c in range(3)]
            errors.append(sum(v*v for v in error)); finals.append(final.tolist())
        minimum = min(errors); best = errors.index(minimum); queries += len(errors)
        records.append({'source_key': k, 'source_rgb': point, 'gold_rgb': gold[k].tolist(),
                        'baseline_first_rgb': baseline_first, 'baseline_final_rgb': baseline[k].tolist(), 'baseline_squared': 50, 'first_box': bounds,
                        'enumerated_integer_rgb_count': len(errors), 'relaxed_minimum_squared': minimum,
                        'argmin_first_rgb': list(rgb_values[best]), 'argmin_final_rgb': finals[best],
                        'blocks_entire_node_component_box_at_49': minimum > 49,
                        'error_histogram': {str(v): errors.count(v) for v in sorted(set(errors))}})
    blocked = [r for r in records if r['relaxed_minimum_squared'] > 49]
    save(args.output, {**frozen, 'frozen_identity_sha256': digest(frozen_path),
         'hotspots': len(records), 'selected_nodes': len(selected), 'total_suffix_queries': queries,
         'blocked_hotspots': len(blocked), 'entire_component_box_cannot_reach_max49': bool(blocked),
         'records': records, 'scope': '盒内全部整数RGB是放松集合，忽略整数可达间隙和共享节点跨源耦合；任一下界>49才证明固定节点分量±2盒不可能。全部≤49不代表可行，无新模型或性能结论。'})


if __name__ == '__main__': main()
