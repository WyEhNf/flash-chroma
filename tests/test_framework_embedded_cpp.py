"""同一聚合hpp的主机/嵌入式/可移植编译与依赖裁剪合同，不执行性能测量。"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('embedded_cpp_installer', ROOT / 'scripts/install_framework.py')
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)


@pytest.fixture(scope='module')
def isolated_compile(tmp_path_factory):
    compiler = os.environ.get('CXX') or shutil.which('g++') or shutil.which('clang++')
    if not compiler:
        pytest.skip('未发现GCC/Clang C++编译器，跳过原生单hpp合同')
    folder = tmp_path_factory.mktemp('framework-embedded-cpp')
    header, identities = INSTALL.amalgamate()
    assert 'framework/preference_selection.hpp' in identities
    assert not re.search(r'^\s*#\s*include\s*"', header, re.MULTILINE)
    # 项目本身不声明C ABI；标准库展开后的libc声明不属于项目交付接口。
    assert not re.search(r'extern\s+"C"', header)

    def build(name, source, definitions=(), *, freestanding=False, preprocess=False, syntax_only=False):
        target = folder / name
        target.mkdir()
        (target / 'flash_chroma_framework.hpp').write_text(header, encoding='utf-8')
        cpp = target / 'contract.cpp'
        cpp.write_text(source, encoding='utf-8')
        assert sorted(item.suffix for item in target.iterdir()) == ['.cpp', '.hpp']
        command = [compiler, '-std=c++17', '-Os', '-Wall', '-Wextra', '-Wpedantic']
        command += [f'-D{definition}' for definition in definitions]
        if freestanding:
            command += ['-ffreestanding', '-fno-exceptions', '-fno-rtti']
        executable = target / ('contract.exe' if os.name == 'nt' else 'contract')
        if preprocess:
            command += ['-E', '-P']
        elif syntax_only:
            command += ['-fsyntax-only']
        else:
            command += ['-o', str(executable)]
        command.append(str(cpp))
        result = subprocess.run(command, cwd=target, capture_output=True, text=True, encoding='utf-8', errors='replace')
        return result, executable
    return build


def test_same_single_header_default_host_keeps_preferences(isolated_compile):
    source = r'''
#define FLASH_CHROMA_IMPLEMENTATION
#define FLASH_CHROMA_ENABLE_OPENMP 0
#include "flash_chroma_framework.hpp"
#include "flash_chroma_framework.hpp"
static_assert(!fc::is_embedded(), "缺省主机模式被嵌入式别名改变");
int main() {
    const fc_framework::PreferenceOptions options;
    return fc_framework::preference_detail::validate(options).empty() ? 0 : 1;
}
'''
    result, executable = isolated_compile('host', source)
    assert result.returncode == 0, result.stdout + result.stderr
    ran = subprocess.run([str(executable)], capture_output=True)
    assert ran.returncode == 0, ran.stderr


def test_embedded_single_header_executes_caller_rom_and_buffers_without_host_flags(isolated_compile):
    source = '#define FC_TEST_FRAMEWORK_HPP "flash_chroma_framework.hpp"\n' + (
        ROOT / 'tests/framework_embedded_cpp_contract.cpp').read_text(encoding='utf-8')
    result, executable = isolated_compile('embedded-runtime', source, ('FLASH_CHROMA_EMBEDDED=1',), freestanding=True)
    assert result.returncode == 0, result.stdout + result.stderr
    ran = subprocess.run([str(executable)], capture_output=True)
    assert ran.returncode == 0, f'嵌入式解析输出合同失败：退出码{ran.returncode}，{ran.stderr!r}'
    assert not ran.stdout and not ran.stderr


@pytest.mark.parametrize(('name', 'definitions'), [
    ('embedded', ('FLASH_CHROMA_EMBEDDED=1',)),
    ('portable', ('FLASH_CHROMA_TARGET=4',)),
])
def test_embedded_and_portable_preprocessing_prunes_host_dependencies(isolated_compile, name, definitions):
    source = '#define FLASH_CHROMA_IMPLEMENTATION\n#include "flash_chroma_framework.hpp"\n'
    result, _ = isolated_compile(f'{name}-preprocessed', source, definitions, freestanding=True, preprocess=True)
    assert result.returncode == 0, result.stderr
    for pattern in (r'namespace\s+fc_framework\b', r'\bPreferenceOptions\b', r'\bfit_chain_last\b',
                    r'\bclass\s+vector\b', r'\bclass\s+basic_fstream\b', r'\bclass\s+basic_ifstream\b',
                    r'\b__m256i\b', r'\bomp_get_num_threads\b'):
        assert not re.search(pattern, result.stdout), f'{name}预处理残留宿主依赖：{pattern}'
    assert re.search(r'\bclass\s+Runtime\b', result.stdout)
    assert 'SelectionStatus select(' in result.stdout


def test_portable_explicit_target_stays_cpp_only_and_scalar(isolated_compile):
    source = r'''
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma_framework.hpp"
static_assert(!fc::is_embedded(), "portable不应冒充embedded目标");
static_assert(FLASH_CHROMA_ENABLE_DIRECT == 0 && FLASH_CHROMA_ENABLE_AVX2 == 0, "portable未裁剪能力");
int main() { return fc::compiled_capabilities() == 1u && fc::RuntimeConfig{}.target == fc::Target::Portable ? 0 : 1; }
'''
    result, executable = isolated_compile('portable-runtime', source, ('FLASH_CHROMA_TARGET=4',), freestanding=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert subprocess.run([str(executable)], capture_output=True).returncode == 0


@pytest.mark.parametrize('definitions', [
    ('FLASH_CHROMA_EMBEDDED=2',),
    ('FLASH_CHROMA_EMBEDDED=1', 'FLASH_CHROMA_TARGET=1'),
    ('FLASH_CHROMA_EMBEDDED=0', 'FLASH_CHROMA_TARGET=3'),
    ('FLASH_CHROMA_EMBEDDED=1', 'FLASH_CHROMA_ENABLE_DIRECT=1'),
    ('FLASH_CHROMA_EMBEDDED=1', 'FLASH_CHROMA_ENABLE_AVX2=1'),
    ('FLASH_CHROMA_EMBEDDED=1', 'FLASH_CHROMA_ENABLE_OPENMP=1'),
    ('FLASH_CHROMA_EMBEDDED=1', 'FLASH_CHROMA_ENABLE_PREPARE_CACHE=1'),
])
def test_conflicting_or_reenabled_embedded_capabilities_fail_at_compile_time(isolated_compile, definitions):
    source = '#include "flash_chroma_framework.hpp"\nint main() { return 0; }\n'
    label = '-'.join(definitions).replace('=', '-')
    result, _ = isolated_compile(label, source, definitions, syntax_only=True)
    assert result.returncode != 0 and '#error' in result.stderr


def test_aggregate_does_not_expose_global_c_delivery_api(isolated_compile):
    source = '#include "flash_chroma_framework.hpp"\nfc_model model;\nint main() { return 0; }\n'
    result, _ = isolated_compile('no-global-c-api', source, ('FLASH_CHROMA_EMBEDDED=1',), syntax_only=True)
    assert result.returncode != 0 and 'fc_model' in result.stderr
