"""82执行前从80定点派生性能脚本；保留未执行初件，修正81传入的元数据误改。"""
import difflib
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'artifacts/skylake-input256-deferred-preflight-v1'
new=ROOT/'scripts/bench_skylake_input256_deferred_long_linux.py'
before=new.read_bytes()
(HERE/'unexecuted-benchmark-initial.py.txt').write_bytes(before)
source=(ROOT/'scripts/bench_skylake_andn_normal_long_linux.py').read_text(encoding='utf-8')
source=source.replace('冻结80对23','冻结82对23').replace("'candidate': 80","'candidate': 82")
source=source.replace('新候选80','新候选82').replace('仅新80对23','仅新82对23')
source=source.replace('andn_normal','input256_deferred').replace('andn-normal','input256-deferred')
assert "'comparison_inner_rounds': 1280" in source
new.write_text(source,encoding='utf-8')
patch=''.join(difflib.unified_diff(before.decode().splitlines(keepends=True),source.splitlines(keepends=True),fromfile='未执行初件',tofile='执行前修正'))
(HERE/'benchmark-preflight-correction.patch').write_text(patch,encoding='utf-8')
record={'purpose':__doc__,'initial_sha256':hashlib.sha256(before).hexdigest(),'corrected_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),
    'reason':'81胶水全字符串80→81误把报告常量1280改成1281并留下scope81；81本身静态失败未执行。82初件同样未执行；现在由80原稿只替换身份，实际循环/门槛/协议无改。',
    'candidate_library_loads':0,'pixel_calls':0,'performance_calls':0}
with (HERE/'benchmark-preflight-correction.json').open('x',encoding='utf-8') as stream:json.dump(record,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(record,ensure_ascii=False))
