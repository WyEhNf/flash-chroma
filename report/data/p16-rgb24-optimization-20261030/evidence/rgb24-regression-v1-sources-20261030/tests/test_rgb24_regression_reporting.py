"""RGB24报告的范围隔离与实际图片身份契约；不运行计时或拟合。"""
import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('rgb24_report', Path(__file__).resolve().parents[1] / 'scripts/bench_rgb24_regression.py')
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def test_scopes_and_warmup_are_not_mixed():
    runs = []
    for scope, baseline, candidate in [('hot', 10, 5), ('allocated', 20, 16)]:
        for kernel, cost in [('legacy', baseline), ('cached', candidate)]:
            runs.append({'scope': scope, 'phase': 'comparison', 'kernel': kernel, 'verified': True,
                         'batch_ms': cost, 'image_ms': [cost / 2, cost / 2]})
            runs.append({'scope': scope, 'phase': 'warmup', 'kernel': kernel, 'verified': True,
                         'batch_ms': 9999, 'image_ms': [9999]})
    summaries, speedups = REPORT.summarize_native({'screen': False, 'runs': runs})
    assert len(summaries) == 4
    assert [row['baseline_over_candidate'] for row in speedups] == [2, 1.25]


def test_actual_image_order_identity_and_complete_outputs_are_required():
    images = [{'path': 'image-1.bin', 'fnv1a64': 'abc'}]
    value = {'images': [{'index': 1, 'path': 'image-1.bin', 'bytes': REPORT.IMAGE_BYTES, 'input_fnv1a64': 'abc'}],
             'runs': [{'verified': True, 'image_ms': [1], 'batch_ms': 1}]}
    assert REPORT.validate_native(value, images)
    value['images'][0]['input_fnv1a64'] = 'def'
    assert not REPORT.validate_native(value, images)
    value['images'][0]['input_fnv1a64'] = 'abc'
    value['runs'][0]['verified'] = False
    assert not REPORT.validate_native(value, images)
    value['runs'][0]['verified'] = True
    value['runs'][0]['image_ms'] = []
    assert not REPORT.validate_native(value, images)
