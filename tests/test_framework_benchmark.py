"""受控比较的实际输入身份契约；只用小型固定字节，不执行性能测试。"""
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import benchmark_framework as benchmark


@pytest.mark.parametrize(('payload', 'expected'), [
    (b'', 'cbf29ce484222325'), (b'a', 'af63dc4c8601ec8c'), (b'hello', 'a430d84680aabd0b'),
])
def test_fnv_golden_values(tmp_path, payload, expected):
    path = tmp_path / 'pixels.bin'
    path.write_bytes(payload)
    assert benchmark.fnv1a64_file(path) == expected


def test_executed_input_identity_requires_pixels_order_count_and_shape():
    records = [{'index': 1, 'fnv1a64': 'first'}, {'index': 2, 'fnv1a64': 'second'}]
    result = {'width': 5, 'height': 7, 'image_count': 2,
              'images': [{'index': 1, 'input_fnv1a64': 'first'}, {'index': 2, 'input_fnv1a64': 'second'}]}
    assert benchmark.executed_input_identity(result, records, 5, 7)
    assert not benchmark.executed_input_identity(result, records, 7, 5)
    assert not benchmark.executed_input_identity({**result, 'image_count': 1}, records, 5, 7)
    assert not benchmark.executed_input_identity({**result, 'images': result['images'][::-1]}, records, 5, 7)
    assert not benchmark.executed_input_identity({**result, 'images': [result['images'][0]] * 2}, records, 5, 7)
    assert not benchmark.executed_input_identity({**result, 'images': []}, records, 5, 7)
    assert not benchmark.executed_input_identity(None, records, 5, 7)
