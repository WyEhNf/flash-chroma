"""默认架构/CPU检测合同；宿主严格用题定编译选项，非宿主宏仅作编译逻辑模拟。"""
from __future__ import annotations

import importlib.util
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('auto_detection_installer', ROOT / 'scripts/install_framework.py')
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)


@pytest.fixture(scope='module')
def standalone(tmp_path_factory):
    compiler = os.environ.get('CXX') or shutil.which('g++') or shutil.which('clang++')
    if not compiler:
        pytest.skip('未发现C++编译器')
    folder = tmp_path_factory.mktemp('framework-auto-detection')
    header, _ = INSTALL.amalgamate()

    def build(name, source, extra=()):
        target = folder / name
        target.mkdir()
        (target / 'flash_chroma_framework.hpp').write_text(header, encoding='utf-8')
        (target / 'main.cpp').write_text(source, encoding='utf-8')
        # 默认验收分支严格保持题定选项，不加-mavx2/-fopenmp或任何-D功能开关。
        command = [compiler, '-O2', '-std=c++17', *extra, '-o', 'lut3d', 'main.cpp']
        result = subprocess.run(command, cwd=target, capture_output=True, text=True, encoding='utf-8', errors='replace')
        assert result.returncode == 0, result.stdout + result.stderr
        executable = target / ('lut3d.exe' if os.name == 'nt' else 'lut3d')
        ran = subprocess.run([str(executable)], cwd=target, capture_output=True)
        assert ran.returncode == 0, f'默认检测合同退出码{ran.returncode}：{ran.stderr!r}'
        return target
    return build


def test_official_flags_default_header_matches_real_cpu_and_all_feature_combinations(standalone):
    source = '#define FC_TEST_FRAMEWORK_HPP "flash_chroma_framework.hpp"\n' + (
        ROOT / 'tests/framework_auto_detection_contract.cpp').read_text(encoding='utf-8')
    standalone('host-official-options', source)


def test_freestanding_without_embedded_macro_runs_existing_rom_contract(standalone):
    source = '#define FC_TEST_FRAMEWORK_HPP "flash_chroma_framework.hpp"\n' + (
        ROOT / 'tests/framework_embedded_cpp_contract.cpp').read_text(encoding='utf-8')
    standalone('freestanding-auto-rom', source, ('-ffreestanding', '-fno-exceptions', '-fno-rtti'))


@pytest.mark.parametrize('architecture', ['__arm__', '__aarch64__', '__riscv'])
def test_bare_architecture_macro_selection_without_manual_switch(standalone, architecture):
    # 先按真实宿主加载基础标准头，再仅模拟平台宏判断；不声称生成ARM/RISC-V机器码。
    source = r'''
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>
#undef __linux__
#undef __ANDROID__
#undef __APPLE__
#undef _WIN32
#undef __unix__
'''+f'#define {architecture} 1\n'+r'''
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma_framework.hpp"
static_assert(fc::is_embedded(), "裸架构缺省目标未识别");
static_assert(FLASH_CHROMA_ENABLE_AVX2 == 0 && FLASH_CHROMA_ENABLE_DIRECT == 0, "裸架构能力未裁剪");
int main() { return fc::RuntimeConfig{}.target == fc::Target::Embedded && fc::available_backends() == 1u ? 0 : 1; }
'''
    standalone('simulated-' + architecture.strip('_'), source)


def test_explicit_host_setting_remains_available_with_official_flags(standalone):
    source = r'''
#define FLASH_CHROMA_EMBEDDED 0
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma_framework.hpp"
static_assert(!fc::is_embedded(), "显式主机设置未保留");
int main() { return fc::RuntimeConfig{}.target == fc::Target::Desktop ? 0 : 1; }
'''
    # 指定host不意味着freestanding标准库突然提供string/vector等宿主设施。
    standalone('manual-host-setting', source)


@pytest.fixture(scope='module')
def original_contest_framework():
    framework = Path(os.environ.get('FLASH_CHROMA_TEST_FRAMEWORK', ROOT.parents[1] / '极速焕彩测试框架'))
    if not (framework / 'C++/main.cpp').is_file():
        pytest.skip('未提供赛方原main.cpp，跳过只读原文保留合同；无需CI持有原LUT/图片')
    return framework


def _function_text(source, name):
    # 屏蔽字符串和注释中的花括号，保留位置后独立提取完整函数原文。
    lexical = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/'
    masked = re.sub(lexical, lambda match: ' ' * len(match.group(0)), source, flags=re.DOTALL)
    start = re.search(rf'(?m)^(?:bool|double|void)\s+{re.escape(name)}\s*\(', masked)
    assert start, name
    opening = masked.index('{', start.start())
    level = 0
    for index in range(opening, len(masked)):
        if masked[index] == '{':
            level += 1
        elif masked[index] == '}':
            level -= 1
            if level == 0:
                return source[start.start():index + 1]
    raise AssertionError('原函数花括号未闭合：' + name)


def test_contest_generation_preserves_official_comments_reference_and_automatic_backend(original_contest_framework):
    original = (original_contest_framework / 'C++/main.cpp').read_text(encoding='utf-8-sig')
    generated = INSTALL.generate_contest_main(original)
    assert generated.startswith(original[:original.index('#include')])
    assert '//   g++ -O2 -std=c++17 -o lut3d main.cpp' in generated
    assert '//   ./lut3d <data_dir>' in generated
    for name in ('now_sec', 'image_load_bin', 'lut_read_3dl', 'lut_sparse_ref', 'apply_lut256',
                 'apply_3d_lut_ref', 'color_dalta_calc', 'print_time_now'):
        assert _function_text(original, name) == _function_text(generated, name), name
    assert 'options.backend = fc::Backend::Auto;' in generated
    assert 'fc::Backend::Avx2' not in generated
    assert not re.search(r'-(?:march\b|mavx\w*|fopenmp\b)', generated)
    assert not re.search(r'#\s*define\s+FLASH_CHROMA_(?:TARGET|EMBEDDED|ENABLE_)', generated)
    assert 'fc_arguments' not in generated and '--preference' not in generated


def test_contest_delivery_contains_exactly_cpp_and_hpp_without_mutating_original(original_contest_framework, tmp_path):
    original = original_contest_framework / 'C++/main.cpp'
    before = hashlib.sha256(original.read_bytes()).hexdigest()
    output = tmp_path / 'contest-delivery'
    result = INSTALL.install_contest(original_contest_framework, output)
    assert sorted(item.name for item in output.iterdir()) == ['flash_chroma_framework.hpp', 'main.cpp']
    assert result['build'] == 'g++ -O2 -std=c++17 -o lut3d main.cpp'
    assert result['run'] == './lut3d <data_dir>'
    assert result['original_main_sha256'] == before == hashlib.sha256(original.read_bytes()).hexdigest()
    header = (output / 'flash_chroma_framework.hpp').read_text(encoding='utf-8')
    assert not re.search(r'^\s*#\s*include\s*"', header, re.MULTILINE)
