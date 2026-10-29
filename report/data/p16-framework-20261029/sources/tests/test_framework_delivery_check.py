"""只测试解析/归因契约；不运行赛事可执行程序。"""
import importlib.util
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'scripts/check_framework_delivery.py'
SPEC = importlib.util.spec_from_file_location('framework_delivery_check', MODULE)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def test_original_output_units_order_and_both_deltas():
    text = ('Start Time: now\n'
            'Img: ../data/image/1.bin TimeCost: 0.003535, Delta: 22.000000 2.052127\n'
            'Img: C:\\data\\image\\2.bin TimeCost: 0.001978, Delta: 10.500000 0.778171\n')
    rows = CHECK.parse_output(text, 2)
    assert rows[0]['time_ms'] == 3.535
    assert rows[0]['reference_delta'] == 22
    assert rows[0]['candidate_delta'] == 2.052127
    assert rows[1]['image'] == 2


@pytest.mark.parametrize('text,count', [
    ('', 1),
    ('Img: image/2.bin TimeCost: 0.1, Delta: 1 2', 1),
    ('Img: image/1.bin TimeCost: nan, Delta: 1 2', 1),
    ('Img: image/1.bin TimeCost: 0.1, Delta: 1 inf', 1),
    ('Img: image/1.bin TimeCost: -0.1, Delta: 1 2', 1),
    ('Img: image/1.bin TimeCost: 0.1, Delta: 1', 1),
])
def test_partial_invalid_or_nonfinite_output_is_rejected(text, count):
    with pytest.raises(ValueError):
        CHECK.parse_output(text, count)


def test_config_is_a_single_safe_component():
    assert CHECK.parse_config('fast,33,direct_rgb24,avx2,uniform,sample')['m'] == 33
    assert CHECK.parse_config('ls,33,sparse,auto,uniform,independent_ls')['fit'] == 'independent_ls'
    for invalid in ('../escape,33,sparse,auto,uniform,sample',
                    'bad,16,sparse,auto,uniform,sample',
                    'bad,33,sparse,auto,uniform,unknown'):
        with pytest.raises(ValueError):
            CHECK.parse_config(invalid)


def test_delta_drift_is_not_hidden_by_median():
    config = CHECK.parse_config('fast,33,sparse,auto,uniform,sample')
    runs = [{'config': 'fast', 'passed': True, 'batch_ms': 1,
             'images': [{'time_ms': 1, 'candidate_delta': delta, 'reference_delta': 9}]}
            for delta in (2, 3)]
    summary = CHECK.summarize_config(config, runs, 2, 1)
    assert summary['complete']
    assert not summary['delta_consistent']


def test_thread_count_does_not_imply_cpu_parallelism():
    history = {1: {'id': 1, 'max_total_cpu_seconds': 10},
               2: {'id': 2, 'max_total_cpu_seconds': 0},
               3: {'id': 3, 'max_total_cpu_seconds': 0.015625}}
    report = CHECK.summarize_threads(history)
    assert report['observed_distinct_thread_count'] == 3
    assert report['threads_with_observed_cpu'] == 2
    assert report['additional_threads_with_observed_cpu'] == 1
    assert report['dominant_cpu_thread_id'] == 1
