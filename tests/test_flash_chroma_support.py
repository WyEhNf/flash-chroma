"""宿主FFI拒绝不连续或只读输出，防止绕过原生容量契约。"""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import flash_chroma_support as support


def test_reject_read_only_destination():
    source = np.zeros((4,3), np.uint8)
    target = np.frombuffer(bytes(12), dtype=np.uint8)
    with pytest.raises(ValueError, match='可写'):
        support.check_arrays(source,target)


def test_reject_negative_stride_and_wrong_dtype():
    source = np.zeros((4,3),np.uint8)
    for a,b in ((source[::-1],source.copy()),(source,source[::-1]),
                (source.astype(np.uint16),source.copy())):
        with pytest.raises(ValueError, match='uint8'):
            support.check_arrays(a,b)


def test_model_requires_explicit_interpolation_basis():
    with pytest.raises(ValueError, match='tetra_q16'):
        support.Model({'models':[], 'sidecars':[]}, Path('.'))


def test_config_invalid_zero_thread_and_block():
    for key in ('threads','block_pixels'):
        config=support.configuration()
        config[key]=0
        with pytest.raises(ValueError):
            support.config_struct(config)
