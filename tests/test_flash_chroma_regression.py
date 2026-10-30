"""验证基准不会把上一轮输出当作下一轮正确性证据。"""
from pathlib import Path
from types import SimpleNamespace
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import bench_flash_chroma_regression as regression


def experiment(tmp_path):
    frames = np.arange(36, dtype=np.uint8).reshape(2, 2, 3, 3)
    expected = regression.modern.sha(frames)
    value = regression.Experiment(SimpleNamespace(output=tmp_path), frames, {}, {'test': expected}, {}, {})
    value.progress['active_case'] = {'scope': 'hot_apply', 'profile': 'test', 'threads': 1, 'pair': 'old_fixed'}
    np.copyto(value.target, frames)
    value.check_output({}, 'test')
    return value, frames


def test_reset_changes_every_previously_correct_byte(tmp_path):
    value, truth = experiment(tmp_path)
    value.reset_output('test')
    assert np.all(value.target != truth)
    np.copyto(value.target, truth)
    value.check_output({}, 'test')


@pytest.mark.parametrize('missed', [1, 36])
def test_rejects_missed_tail_and_noop_after_correct_previous_call(tmp_path, missed):
    value, truth = experiment(tmp_path)
    value.reset_output('test')
    value.target.reshape(-1)[:-missed] = truth.reshape(-1)[:-missed]
    with pytest.raises(RuntimeError, match='百图输出SHA不一致'):
        value.check_output({}, 'test')
