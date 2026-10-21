"""从已验78检查器派生79输入成对加载检查；冻结后才编译，不运行原生。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'artifacts/skylake-pair48-static-v1'
HERE.mkdir(exist_ok=False)
old = (ROOT/'artifacts/skylake-andn-split-static-v1/inspect-v2.py').read_text(encoding='utf-8')
new = old.replace('修订78', '修订79').replace('skylake-andn-split', 'skylake-pair48').replace('jshc_skylake_andn_split', 'jshc_skylake_pair48')
new = new.replace("width = len(masks) if role == 'linear' else len(andn)", "width = len(masks) if role == 'linear' else len(andn)*2")
new = new.replace("or raw[2] & 0x80:", "or not raw[2] & 0x80:")
new = new.replace("re.fullmatch(r'%(?:e[a-z]{2}|r(?:[89]|1[0-5])d)', parts[1])", "re.fullmatch(r'%r[a-z0-9]+', parts[1])")
new = new.replace("re.fullmatch(r'%(?:e[a-z]{2}|r(?:[89]|1[0-5])d)', parts[2])", "re.fullmatch(r'%r[a-z0-9]+', parts[2])")
new = new.replace("len(left) != 32", "len(left) != 16")
new = new.replace("x['mnemonic']=='mov' and x['operands'].startswith('$0xff000000,')", "x['mnemonic'] in ('mov','movabs') and x['operands'].startswith('$0xffff000000000000,')")
new = new.replace("x['mnemonic'] == 'mov' and x['operands'] == '$0xff000000,'+reg", "x['mnemonic'] in ('mov','movabs') and x['operands'] == '$0xffff000000000000,'+reg")
new = new.replace('0xff000000', '0xffff000000000000')
new = new.replace("o['mnemonic']=='mov' and parts[0]=='$0xffff000000000000'", "o['mnemonic'] in ('mov','movabs') and parts[0]=='$0xffff000000000000'")
new = new.replace("fewer_instructions=row['instructions'] < reference['instructions'],", "paired_input_loads=row['andn_count']*2 == row['width'],")
new = new.replace("row['andn_count'] == row['width']", "row['andn_count']*2 == row['width']")
new = new.replace("fewer_instructions='指令数未减少'", "paired_input_loads='输入加载数不符合每两像素一次'")
new = new.replace("results-v2.json", "results.json")
start = new.index("    result['initial_script_sha256']")
end = new.index("    save_new(HERE/'results.json'", start)
new = new[:start]+new[end:]
(HERE/'inspect.py').write_text(new, encoding='utf-8')
source = ROOT/'scripts/verify_skylake_andn_split_linux.py'
verify = source.read_text(encoding='utf-8').replace('78ANDN分入口', '79双像素ANDN输入').replace('andn_split', 'pair48')
(ROOT/'scripts/verify_skylake_pair48_linux.py').write_text(verify, encoding='utf-8')
print('检查器初稿生成；尚未冻结或编译，需进一步核对64位掩码活跃期及拆位证明')
