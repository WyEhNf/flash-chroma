"""将同源 C99 核与 C++17 运行库、选择器生成为一个独立头文件。"""
from pathlib import Path
import argparse
import re

ROOT = Path(__file__).resolve().parents[1]


def rendered():
    core = (ROOT / 'include/flash_chroma_c.h').read_text(encoding='utf-8')
    core = core.replace('FLASH_CHROMA_C_H', 'FLASH_CHROMA_CPP_C_CORE_H')
    core = core.replace('FLASH_CHROMA_C_IMPLEMENTED', 'FLASH_CHROMA_CPP_C_CORE_IMPLEMENTED')
    core = re.sub(r'\bFC_C_([A-Z0-9_]+)', r'FC_CPP_CORE_\1', core)
    core = core.replace('FC_DETAIL_', 'FC_CPP_DETAIL_')
    core = re.sub(r'#ifdef __cplusplus\s+extern "C" \{\s+#endif', '', core)
    core = re.sub(r'#ifdef __cplusplus\s+\}\s+#endif', '', core)
    core = core.replace('四级 RGB8/Q16 单头 C99 运行库。',
                        '四级 RGB8/Q16 C++内部标量核心，与独立C99头共享数值语义。')
    cpp = (ROOT / 'src/flash_chroma_cpp.inc').read_text(encoding='utf-8')
    # 维护片段只在生成时展开，部署头不引用仓库私有文件。
    def fragment(match):
        return (ROOT / 'src' / match.group(1)).read_text(encoding='utf-8')
    cpp = re.sub(r'^// @include (flash_chroma_[a-z_]+\.inc)$', fragment, cpp, flags=re.MULTILINE)
    selection_path = ROOT / 'src/flash_chroma_selection.inc'
    selection = selection_path.read_text(encoding='utf-8') if selection_path.exists() else ''
    return '\n'.join([
        '/* 独立C++17单头；维护时由同源标量核心及src片段生成，部署不依赖.c/.h或生成脚本。 */',
        '#ifndef FLASH_CHROMA_HPP', '#define FLASH_CHROMA_HPP',
        '#if !defined(__cplusplus) || __cplusplus < 201703L',
        '#error "flash_chroma.hpp 要求 C++17"', '#endif',
        '#include <stddef.h>', '#include <stdint.h>',
        '#define FC_CPP_CORE_STATIC', '#define FC_CPP_CORE_IMPLEMENTATION',
        'namespace fc_core {', core, '}',
        '#undef FC_CPP_CORE_IMPLEMENTATION', '#undef FC_CPP_CORE_STATIC', '#undef FC_CPP_CORE_API',
        cpp, selection, '#endif', '',
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='只检查生成物是否为当前来源')
    args = parser.parse_args()
    path = ROOT / 'include/flash_chroma.hpp'
    content = rendered()
    if args.check:
        if not path.exists() or path.read_text(encoding='utf-8') != content:
            raise SystemExit('单头文件与维护源码不同步，请重新生成')
    else:
        path.write_text(content, encoding='utf-8', newline='\n')
    print('单头文件来源检查通过' if args.check else '单头文件已生成')


if __name__ == '__main__':
    main()
