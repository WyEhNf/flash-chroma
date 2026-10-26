"""分块研究前向补全失败trial的RMS/p99/CVaR观察量；非独立oracle或终验。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import oriented_tetra as ot, io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from accept_channel_tail_nodes import histogram
from accept_channel_coordinates import hist_metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖研究观察直方图')
    numba.set_num_threads(4)
    reference_path = args.cache_root/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256'
    if digest(reference_path) != '6c4387352bd0845ce597f13dca32f2f808b39439d06ce78b4881922a4fc294b7':
        raise ValueError('不是冻结Velvia原表')
    reference = io.load_full(reference_path, mmap=True).reshape(-1, 3)
    result = {'baseline': json.loads((ROOT/'report/data/velvia-body-diagonals-20261024/results.json').read_text(encoding='utf-8'))['variants']['0']['cube'],
        'variants': {}, 'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), ROOT/'python/lutlab/oriented_tetra.py']},
        'scope': '两项失败节点模型的完整域研究核观察量，只补RMS/p99/CVaR；没有独立u64、照片、边界、native、性能或新候选选择。'}
    for name, folder in [('previous_five_budget', 'velvia-stripe-nodes-v1'), ('mean_first', 'velvia-mean-first-nodes-v1')]:
        path = ROOT/'artifacts'/folder
        summary = json.loads((path/'summary.json').read_text(encoding='utf-8'))
        if digest(path/'model.npz') != summary['model_sha256']:
            raise ValueError('失败模型发生改变')
        model = load_model(path/'model.npz')
        choices = np.fromfile(path/'cell-orientation.bin', np.uint8)
        hist = np.zeros(3*255**2+1, np.int64)
        hasher = hashlib.sha256()
        for start in range(0, len(reference), 1 << 18):
            keys = np.arange(start, start+(1 << 18), dtype=np.int64)
            rgb = np.column_stack((keys >> 16, (keys >> 8)&255, keys&255)).astype(np.uint8)
            value = ot.predict(model, rgb, choices)
            hist += histogram(value, reference[start:start+len(keys)])
            hasher.update(value.tobytes())
        metrics = hist_metrics(hist)
        np.testing.assert_allclose([metrics['mean'], metrics['rms'], metrics['max']],
            [summary['after'][0]/256**3, np.sqrt(summary['after'][2]/256**3), np.sqrt(summary['max_squared'])], rtol=0, atol=1e-10)
        result['variants'][name] = {'cube': metrics, 'research_stream_sha256': hasher.hexdigest(), 'model_sha256': summary['model_sha256']}
        print(json.dumps({'name': name, 'cube': metrics}, ensure_ascii=False), flush=True)
    save(args.output, result)


if __name__ == '__main__':
    main()
