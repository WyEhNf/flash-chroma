"""复核固定G分bank普查的三份已完成负例及第四项前置失败；不重跑普查或像素。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'artifacts/p16-direct-gbank8-census-v1'
OUT = ROOT / 'artifacts/p16-direct-gbank8-partial-audit-v1.json'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError('不覆盖离线复核')
    frozen = json.loads((SOURCE / 'frozen.json').read_text(encoding='utf-8'))
    checked = 0
    for name, expected in frozen['sources_sha256'].items():
        assert sha(ROOT / name) == expected, name
        checked += 1
    for name, expected in frozen['inputs_sha256'].items():
        assert sha(name) == expected, name
        checked += 1
    rows = []
    for name in ('max_first', 'p99_first', 'max48'):
        path = SOURCE / name / 'results.json'
        row = json.loads(path.read_text(encoding='utf-8'))
        assert row['model'] == name and len(row['banks']) == 256
        assert [v['green'] for v in row['banks']] == list(range(256))
        over = {v['green']: v for v in row['overflow_banks']}
        assert row['maximum_colors'] == max(v['colors'] for v in row['banks'])
        assert set(over) == {v['green'] for v in row['banks'] if v['colors'] > 256}
        for bank in row['banks']:
            n = bank['colors']
            assert 1 <= n <= 65536
            assert bank['maximum_id_if_representable'] == (n - 1 if n <= 256 else None)
            if n > 256:
                witness = over[bank['green']]
                assert witness['colors'] == n and len(witness['first257_rgb32']) == 257
                colors = witness['first257_rgb32']
                assert colors == sorted(set(colors)) and 0 <= colors[0] <= colors[-1] <= 0xffffff
        assert not row['representable'] and over and row['products'] == {}
        assert row['full_replay_mismatches'] is None and not row['production_model_bytes_measured']
        rows.append({'model': name, 'maximum_colors': row['maximum_colors'],
                     'overflow_banks': len(over), 'first_overflow_bank': min(over),
                     'result_sha256': sha(path), 'status': '固定G分区不可表示，保留独立逐bank计数证据'})
    assert not (SOURCE / 'results.json').exists()
    assert (SOURCE / 'max41').is_dir() and not list((SOURCE / 'max41').iterdir())
    observer = ROOT / 'artifacts/p16-direct-gbank8-max41-observer-v1/results.json'
    observed = json.loads(observer.read_text(encoding='utf-8'))
    assert observed['wide']['enabled'] == 0 and observed['wide']['reason'] == 2
    assert observed['domain']['cache_enabled'] == 0 and observed['pixel_apply_calls'] == 0
    result = {'passed': True, 'purpose': __doc__, 'frozen_sha256': sha(SOURCE / 'frozen.json'),
              'checked_source_input_identities': checked, 'models_completed': rows,
              'max41_status': '288纯表前置失败，尚未取得该模型bank基数；不能计作表示性负例',
              'max41_observer_sha256': sha(observer),
              'original_failure_log_sha256': sha(ROOT / 'artifacts/p16-direct-gbank8-census-driver-v1.log'),
              'pixel_apply_calls': 0, 'performance_calls': 0,
              'limitations': '只消费原三份普查和观察器，不生成生产表示，不推定最大bank仅取决于全局调色板大小'}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
