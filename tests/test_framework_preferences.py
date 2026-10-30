"""赛事偏好入口合同：临时目录仅携带一个hpp，不读取LUT或图片、不执行计时。"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('preference_installer', ROOT / 'scripts/install_framework.py')
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)


def test_preference_amalgamation_is_one_self_contained_header():
    header, identities = INSTALL.amalgamate()
    assert 'framework/preference_selection.hpp' in identities
    assert not re.search(r'^\s*#\s*include\s*"', header, re.MULTILINE)
    for relative, expected in identities.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected


@pytest.fixture(scope='module')
def argument_probe(tmp_path_factory):
    # 不复制仓库include目录；编译通过才能证明聚合后的部署头没有隐藏本地依赖。
    compiler = os.environ.get('CXX') or shutil.which('g++') or shutil.which('clang++')
    if not compiler:
        pytest.skip('未发现C++编译器，跳过原生参数入口合同')
    folder = tmp_path_factory.mktemp('preference-single-header')
    header, _ = INSTALL.amalgamate()
    (folder / 'flash_chroma_framework.hpp').write_text(header, encoding='utf-8')
    source = r'''
#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "flash_chroma_framework.hpp"
#include <cstdio>
#include <filesystem>
#include <memory>
'''+INSTALL.GLOBALS+r'''
int main(int argc, char** argv) {
    try {
        fc_arguments(argc, argv);
        const auto weights = fc_use_preference ? fc_parse_preference(fc_preference_spec) : fc::Preference{};
        std::printf("{\"enabled\":%s,\"weights\":[%.17g,%.17g,%.17g],"
                    "\"runtime\":%zu,\"workspace\":%zu,\"mean\":%.17g,\"pixel\":%.17g,"
                    "\"time\":%.17g,\"reps\":%u,\"unstable\":%s,\"threads\":%u,"
                    "\"sizes\":[%u,%u,%u,%u]}\n",
                    fc_use_preference ? "true" : "false", weights.accuracy, weights.speed, weights.compactness,
                    fc_max_runtime_bytes, fc_max_workspace_bytes, fc_max_mean_error, fc_max_pixel_error,
                    fc_max_ms_per_mp, fc_calibration_reps, fc_allow_unstable_time ? "true" : "false",
                    fc_options.threads, fc_sizes[0], fc_sizes[1], fc_sizes[2], fc_sizes[3]);
        return 0;
    } catch (const std::exception& error) { std::fprintf(stderr, "%s\n", error.what()); return 2; }
}
'''
    cpp = folder / 'argument_probe.cpp'
    cpp.write_text(source, encoding='utf-8')
    executable = folder / ('argument_probe.exe' if os.name == 'nt' else 'argument_probe')
    command = [compiler, '-std=c++17', '-O0', '-Wall', '-Wextra', '-Wpedantic', str(cpp), '-o', str(executable)]
    built = subprocess.run(command, cwd=folder, capture_output=True, text=True, encoding='utf-8', errors='replace')
    assert built.returncode == 0, built.stdout + built.stderr

    def run(*arguments):
        # 路径有意不存在：解析既不访问图片，也不为测试创建稠密参考表。
        return subprocess.run([str(executable), 'nonexistent-lut-only-input', *arguments], cwd=folder,
                              capture_output=True, text=True, encoding='utf-8', errors='replace')
    return run


def test_cli_continuous_preferences_and_hard_budgets_reach_actual_globals(argument_probe):
    actual = argument_probe('--preference', '0.123456789,0.876543210,0.000000001',
                            '--max-runtime-mib', '12.5', '--max-workspace-mib', '0.25',
                            '--max-mean-error', '1.125', '--max-pixel-error', '8.5', '--max-ms-per-mp', '2.75',
                            '--calibration-reps', '7', '--allow-unstable-time',
                            '--candidate-sizes', '17;17,25,33,31;33', '--candidate-modes', 'sparse,direct_rgb24')
    assert actual.returncode == 0, actual.stderr
    result = json.loads(actual.stdout)
    assert result['enabled'] and result['weights'] == [0.123456789, 0.876543210, 0.000000001]
    assert result['runtime'] == 13107200 and result['workspace'] == 262144
    assert (result['mean'], result['pixel'], result['time']) == (1.125, 8.5, 2.75)
    assert result['reps'] == 7 and result['unstable'] and result['threads'] == 1


def test_cli_legacy_positions_still_work_without_preference(argument_probe):
    actual = argument_probe('17,25,33,31', 'sparse', 'scalar', 'framework', '4', 'sample')
    assert actual.returncode == 0, actual.stderr
    result = json.loads(actual.stdout)
    assert not result['enabled'] and result['sizes'] == [17, 25, 33, 31] and result['threads'] == 1


def test_cli_history_is_explicit_and_works_with_preference(argument_probe):
    actual = argument_probe('33', 'direct_rgb24', 'auto', 'framework', '4', 'history',
                            '--preference', '1,0,0', '--candidate-sizes', '33;17,25,33,33')
    assert actual.returncode == 0, actual.stderr
    assert json.loads(actual.stdout)['enabled']


def test_cli_selection_report_preserves_existing_file_and_does_not_create_during_parse(argument_probe, tmp_path):
    report = tmp_path / 'existing-report.json'
    report.write_text('已有证据不得覆盖\n', encoding='utf-8')
    actual = argument_probe('--preference', '1,0,0', '--selection-report', str(report))
    assert actual.returncode == 2 and report.read_text(encoding='utf-8') == '已有证据不得覆盖\n'
    new_report = tmp_path / 'new-report.json'
    actual = argument_probe('--preference', '1,0,0', '--selection-report', str(new_report))
    assert actual.returncode == 0, actual.stderr
    assert not new_report.exists()
    actual = argument_probe('--selection-report', str(new_report))
    assert actual.returncode == 2 and not new_report.exists()


@pytest.mark.parametrize('weights', [
    '0,0,0', 'nan,0,1', 'inf,0,1', '-0.1,0,1', '1.00001,0,0', '1,0', '1,0,0,0',
    '1,,0', '1,0,', '1, 0,0', '0.1suffix,0.2,0.3',
])
def test_cli_rejects_invalid_weights_before_any_source_read(argument_probe, weights):
    actual = argument_probe('--preference', weights)
    assert actual.returncode == 2 and actual.stderr and not actual.stdout


@pytest.mark.parametrize('options', [
    ('--max-runtime-mib', '1'),
    ('--preference', '1,0,0', '--preference', '0,1,0'),
    ('--preference', '1,0,0', '--unknown', '1'),
    ('--preference', '1,0,0', '--max-mean-error'),
    ('--preference', '1,0,0', '--max-mean-error', 'nan'),
    ('--preference', '1,0,0', '--max-pixel-error', 'inf'),
    ('--preference', '1,0,0', '--max-ms-per-mp', '-1'),
    ('--preference', '1,0,0', '--max-runtime-mib', '1e100'),
    ('--preference', '1,0,0', '--max-workspace-mib', '-0.5'),
    ('--preference', '1,0,0', '--candidate-sizes', '16;33'),
    ('--preference', '1,0,0', '--candidate-sizes', '17;25,33'),
    ('--preference', '1,0,0', '--candidate-sizes', '17;'),
    ('--preference', '1,0,0', '--candidate-modes', 'sparse,gpu'),
    ('--preference', '1,0,0', '--calibration-reps', '2'),
    ('--preference', '1,0,0', '--calibration-reps', '4'),
    ('--preference', '1,0,0', '--calibration-reps', '33'),
    ('--preference', '1,0,0', '--image-list', 'photos.txt'),
])
def test_cli_rejects_invalid_budget_protocol_or_image_selection_input(argument_probe, options):
    actual = argument_probe(*options)
    assert actual.returncode == 2 and actual.stderr and not actual.stdout
