"""只派生79验收胶水；不生成可执行策略，不运行原生。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'scripts/bench_skylake_andn_split_long_linux.py'
target = ROOT/'scripts/bench_skylake_pair48_long_linux.py'
text = source.read_text(encoding='utf-8').replace('78', '79').replace('andn_split', 'pair48').replace('andn-split', 'pair48')
with target.open('x', encoding='utf-8') as stream:
    stream.write(text)
print('已派生验收胶水；全域及静态绑定完成前不生成79性能策略或执行')
