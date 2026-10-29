"""独立框架oracle的轴序、截断、全域结构证明及像素误差合同。"""
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import framework_contract_check as check


def test_axis_channel_and_integer_truncation():
    raw = np.arange(2 ** 3 * 3, dtype=np.int32).reshape(-1, 3) * 17 + 7
    actual = check.normalize_reference(raw, 2)
    expected = np.empty((2, 2, 2, 3), dtype=np.uint8)
    for r in range(2):
        for g in range(2):
            for b in range(2):
                for c in range(3):
                    expected[r, g, b, c] = raw[b * 4 + g * 2 + r, 2 - c] // 16
    assert np.array_equal(actual, expected)


def test_reference_preserves_framework_uint8_cast_without_clipping():
    raw = np.array([[4095, 4096, 65535]], dtype=np.int32)
    assert check.normalize_reference(raw, 1).tolist() == [[[[255, 0, 255]]]]


@pytest.mark.parametrize('bad', [-1, 65536])
def test_source_range_rejected(bad):
    with pytest.raises(ValueError, match='范围'):
        check.normalize_reference(np.array([[bad, 0, 0]], dtype=np.int32), 1)


def test_parse_requires_three_columns_and_exact_rows(tmp_path):
    path = tmp_path / 'small.3DL'
    path.write_text('0 1 2 3\n4 5\n', encoding='utf-8')
    with pytest.raises(ValueError): check.parse_source(path, 1)
    path.write_text('0 1 2\n3 4 5\n', encoding='utf-8')
    with pytest.raises(ValueError, match='shape'): check.parse_source(path, 1)
    path.write_text('15 16 17\n', encoding='utf-8')
    assert check.parse_source(path, 1).tolist() == [[15, 16, 17]]


def test_parse_does_not_truncate_decimal_tokens(tmp_path):
    path = tmp_path / 'decimal.3DL'
    path.write_text('0.5 16 17\n', encoding='utf-8')
    with pytest.raises((ValueError, DeprecationWarning)):
        check.parse_source(path, 1)


def test_separability_checks_non_sampled_interior():
    r, g, b = np.indices((4, 4, 4), dtype=np.uint8)
    dense = np.stack((r * 3, 19 - g, b * 11), axis=-1)
    proof = check.separability_proof(dense)
    assert proof['separable'] and proof['checked_nodes'] == 64
    dense[2, 2, 2, 0] += 1
    rejected = check.separability_proof(dense)
    assert not rejected['separable'] and rejected['mismatches_by_channel'] == [1, 0, 0]
    assert rejected['curves_rgb'] is None


def test_cache_checks_every_value_and_exact_length(tmp_path):
    path = tmp_path / 'raw.u16'
    source = np.arange(24, dtype=np.int32).reshape(8, 3)
    source.astype('<u2').tofile(path)
    assert check.check_cache(path, source)['values_equal_to_original']
    changed = source.astype('<u2'); changed[-1, -1] += 1; changed.tofile(path)
    with pytest.raises(ValueError, match='不一致'): check.check_cache(path, source)
    path.write_bytes(b'')
    with pytest.raises(ValueError, match='字节'): check.check_cache(path, source)


def test_mean_distance_is_not_per_channel_or_rms():
    expected = np.array([[[0, 0, 0], [0, 0, 0]]], dtype=np.uint8)
    actual = np.array([[[3, 4, 0], [0, 0, 0]]], dtype=np.uint8)
    value = check.metrics(expected, actual)
    assert value['mean_rgb_distance'] == 2.5
    assert value['max_rgb_distance'] == 5
    assert value['rms_rgb_distance'] == pytest.approx(np.sqrt(12.5))
    assert value['different_pixels'] == 1 and not value['byte_equal']


def test_extreme_rgb_difference_does_not_overflow_int16():
    expected = np.zeros((1, 1, 3), dtype=np.uint8)
    actual = np.full((1, 1, 3), 255, dtype=np.uint8)
    assert check.metrics(expected, actual)['max_rgb_distance'] == pytest.approx(np.sqrt(3 * 255 ** 2))


def test_output_receipts_are_not_overwritten(tmp_path):
    path = tmp_path / 'receipt.json'
    check.save_new(path, {'passed': True})
    original = path.read_bytes()
    with pytest.raises(FileExistsError): check.save_new(path, {'passed': False})
    assert path.read_bytes() == original


def test_supplemental_list_paths_resolve_from_list_directory(tmp_path, monkeypatch):
    folder = tmp_path / 'images'; folder.mkdir()
    image = folder / 'a.bin'; image.write_bytes(bytes(np.prod(check.IMAGE_SHAPE)))
    listing = folder / 'list.txt'; listing.write_text('a.bin\n', encoding='utf-8')
    elsewhere = tmp_path / 'unrelated'; elsewhere.mkdir(); monkeypatch.chdir(elsewhere)
    images, identity = check.load_image_list(listing)
    assert images[0]['path'] == str(image.resolve())
    assert images[0]['index'] == 1 and images[0]['shape'] == list(check.IMAGE_SHAPE)
    assert identity['sha256'] == check.digest(listing)
    assert check.image_scope(listing) == 'supplemental_images'
    assert check.image_scope(None) == 'framework_samples'


def test_supplemental_list_rejects_wrong_size_empty_and_duplicate(tmp_path):
    image = tmp_path / 'a.bin'; image.write_bytes(b'\0')
    listing = tmp_path / 'list.txt'; listing.write_text('a.bin\n', encoding='utf-8')
    with pytest.raises(ValueError, match='1024×768'): check.load_image_list(listing)
    listing.write_text('\n', encoding='utf-8')
    with pytest.raises(ValueError, match='不能为空'): check.load_image_list(listing)
    image.write_bytes(bytes(np.prod(check.IMAGE_SHAPE)))
    listing.write_text('a.bin\n./a.bin\n', encoding='utf-8')
    with pytest.raises(ValueError, match='重复路径'): check.load_image_list(listing)


def test_verify_reports_actual_default_or_supplemental_input_scope(tmp_path, monkeypatch):
    monkeypatch.setattr(check, 'SIDE', 2)
    monkeypatch.setattr(check, 'IMAGE_SHAPE', (1, 2, 3))
    dense = tmp_path / 'dense.rgb8lut'; dense.write_bytes(bytes(24))
    original = tmp_path / 'original.bin'; original.write_bytes(bytes(6))
    supplemental = tmp_path / 'supplemental.bin'; supplemental.write_bytes(bytes([1]) * 6)
    listing = tmp_path / 'images.txt'; listing.write_text('supplemental.bin\n', encoding='utf-8')
    oracle = tmp_path / 'manifest.json'
    check.save_new(oracle, {'schema': check.SCHEMA, 'unique': {'table': {'dense': {'path': dense.name, 'sha256': check.digest(dense)}}},
                          'stages': [{'normalized_key': 'table'}] * 4,
                          'contract': {'files': [], 'luts': [], 'images': [dict(check.record(original), index=1)]}})
    candidate = tmp_path / 'candidate'; candidate.mkdir(); (candidate / 'image-1.bin').write_bytes(bytes(6))
    first = check.verify(oracle, candidate)
    second = check.verify(oracle, candidate, threshold=0, image_list=listing)
    assert first['input_scope'] == 'framework_samples' and first['image_list'] is None
    assert second['input_scope'] == 'supplemental_images' and second['image_list']['sha256'] == check.digest(listing)
    assert first['records'][0]['input_sha256'] == check.digest(original)
    assert second['records'][0]['input_sha256'] == check.digest(supplemental)
    assert first['all_byte_equal'] and second['all_byte_equal']
    assert second['all_image_mean_pass'] is False and not second['official_score_available']
