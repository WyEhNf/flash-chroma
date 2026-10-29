"""从官方框架与 PR95 固定提交生成本地测试接入，不修改官方原件。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ROOT = REPO.parents[1]
OUT = REPO / 'artifacts/official-pr95-20261029'
SHA = 'fb7e195215f14df9f635394d75cde0e0e69c82c9'
OUT.mkdir(parents=True, exist_ok=True)
for m in (17, 33): (OUT / f'm{m}').mkdir(exist_ok=True)
for name in ('flash_chroma.hpp', 'flash_chroma_c.h'):
    (OUT / name).write_bytes(subprocess.check_output(['git', 'show', f'{SHA}:include/{name}'], cwd=REPO))
source = (ROOT / 'test/C++/main.cpp').read_text(encoding='utf-8-sig')
adapter = (HERE / 'adapter.inc').read_text(encoding='utf-8')
needle = '// Port of sparse_lut().'
assert source.count(needle) == 1
source = source.replace(needle, adapter + '\n' + needle)
old = '''    // add your code here
    return true;'''
assert source.count(old) == 1
source = source.replace(old, '    return bridge_sparse(lut256, lut_size, out);')
old = '''    // add your code here
    out = img;

    return true;'''
assert source.count(old) == 1
source = source.replace(old, '    return bridge_apply(img, out);')
source = source.replace('int main(int argc, char** argv)', 'int official_main(int argc, char** argv)')
source = source.replace('if (!lut_sparse(luts_raw[i], 17,  lut17[i]))', 'if (!lut_sparse(luts_raw[i], bridge_m(),  lut17[i]))')
source = source.replace('out = std::move(tmp1);', 'out = std::move(tmp1);\n    bridge_save(out.data, "reference-" + std::to_string(++bridge_ref_counter) + ".bin");')
prefix = '''#define FLASH_CHROMA_ENABLE_OPENMP 0
#define FLASH_CHROMA_IMPLEMENTATION
#include "flash_chroma.hpp"
#define FC_C_STATIC
#define FC_C_IMPLEMENTATION
#include "flash_chroma_c.h"
#include <algorithm>
#include <memory>
#include <stdexcept>
'''
(OUT / 'official_adapter.cpp').write_text(prefix + source + '\n' + (HERE / 'runner.inc').read_text(encoding='utf-8'), encoding='utf-8')
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024), b''): h.update(block)
    return h.hexdigest()
inputs = sorted(p for p in (ROOT/'test').rglob('*') if p.is_file())
record = {'pr':95, 'source_commit':SHA, 'official_root':str(ROOT/'test'),
          'files':[{'path':str(p.relative_to(ROOT)), 'bytes':p.stat().st_size, 'sha256':digest(p)} for p in inputs],
          'runtime_headers':{n:digest(OUT/n) for n in ('flash_chroma.hpp','flash_chroma_c.h')},
          'generated_sha256':digest(OUT/'official_adapter.cpp'), 'python':sys.version}
(OUT/'input-manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT), 'files':len(inputs)},ensure_ascii=False))
