"""从291验收框架机械生成292独立质量入口；本脚本不执行模型或像素。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('唯一胶水标记失配：' + old)
    return text.replace(old, new, 1)


def main():
    source = ROOT / 'scripts/check_direct_sentinel_native_v2.py'
    target = ROOT / 'scripts/check_direct_rgb24_native.py'
    mt_target = ROOT / 'scripts/check_direct_rgb24_full_mt.py'
    if target.exists() or mt_target.exists():
        raise FileExistsError('不覆盖292质量入口')
    text = source.read_text(encoding='utf-8')
    text = text.replace('p16-direct-sentinel-v2-build', 'p16-direct-rgb24-build')
    text = text.replace('p16-direct-sentinel-v2-quality', 'p16-direct-rgb24-quality')
    text = text.replace('p16-direct-sentinel-v2-contracts', 'p16-direct-rgb24-contracts')
    text = text.replace('check_direct_sentinel_contracts_v2.py', 'check_direct_rgb24_contracts.py')
    text = text.replace('libjshc_direct_sentinel_v2.dll', 'libjshc_direct_rgb24.dll')
    text = text.replace('p16_cc_get_direct_sentinel_info', 'p16_cc_get_direct_rgb24_info')
    text = text.replace('p16_cc_copy_sentinel_palette', 'p16_cc_copy_rgb24_palette')
    text = text.replace('libraries[\'new\'].revision==291', 'libraries[\'new\'].revision==292')
    text = text.replace('p16_direct_sentinel_quality_v2', 'p16_direct_rgb24_quality_v1')
    text = text.replace('290真实四链', '292真实四链').replace('哨兵96B诊断不符', 'RGB24的96B诊断不符')
    text = text.replace('全16M物理ID与独立Counter/288精确值核验', '完整48MiB物理RGB24逐字节与288解码精确值核验')
    text = once(text, "'id_identity':[]", "'physical_rgb_identity':[]")
    start = text.index("            if name not in ('old_best','87_old_best'):")
    end = text.index("        save(OUT/'tables.json',result)", start)
    text = text[:start] + PHYSICAL + text[end:]
    text = once(text, "elif name=='256':assert state['enabled'] and state['palette_size']==256 and state['whole_cache_colors']==256 and direct['format']==17",
                "elif name=='256':assert state['enabled'] and state['palette_size']==0 and state['id_bytes']==3 and direct['format']==18")
    text = once(text, "elif name=='overflow':assert not state['enabled'] and state['reason']==3 and state['whole_cache_colors']>65536",
                "elif name=='overflow':assert state['enabled'] and state['format']==18 and state['palette_size']==0")
    text = text.replace("'sentinel':state", "'rgb24':state")
    text = once(text, "for handle,out,count in [(None,pointer,256),(chain.handle,None,256),(chain.handle,pointer,255),(chain.handle,pointer,257)]:",
                "for handle,out,count in [(None,pointer,0),(chain.handle,None,1),(chain.handle,pointer,1),(chain.handle,pointer,2)]:")
    # 原source闭包新增本生成器和292计划，所有身份仍在任何新像素执行前冻结。
    text = once(text, "paths.update((ROOT/'python/lutlab').rglob('*.py'))",
                "paths.update((ROOT/'python/lutlab').rglob('*.py'))\n    paths.update([ROOT/'scripts/prepare_direct_rgb24_quality.py',ROOT/'experiments/p16-direct-rgb24-plan-v1.md'])")
    target.write_text(text, encoding='utf-8', newline='\n')
    mt = (ROOT / 'scripts/check_direct_sentinel_full_mt_v3.py').read_text(encoding='utf-8')
    mt = mt.replace('from check_direct_sentinel_native_v2 import', 'from check_direct_rgb24_native import')
    mt = mt.replace('p16-direct-sentinel-v2-full-mt-frozen-v2', 'p16-direct-rgb24-full-mt-frozen-v1')
    mt = mt.replace('p16-direct-sentinel-v2-full-mt-v2', 'p16-direct-rgb24-full-mt-v1')
    mt_target.write_text(mt, encoding='utf-8', newline='\n')
    print('292独立质量入口已生成；尚未冻结或运行真实模型。')


PHYSICAL = '''            if name not in ('old_best','87_old_best'):
                assert state['enabled'] and state['format']==18 and state['id_bytes']==3 and state['guard_bytes']==4
                assert state['palette_size']==0 and state['palette_capacity_bytes']==0 and state['guaranteed_alignment']==1
                raw=direct_table(chain).view(np.uint8)
                assert raw.size==3*2**24+4 and np.all(raw[-4:]==0)
                rgb_values=raw[:-4].reshape(-1,3)
                spec=frozen['roles'][name]
                with libraries['old288'].chain(spec['models'],spec['sidecars']) as old:
                    old_raw=direct_table(old).view(np.uint16);old_palette=palette(old,False)
                    assert old_raw.size==2**24+2 and np.all(old_raw[-2:]==0)
                    for start in range(0,2**24,65536):
                        values=old_palette[old_raw[start:start+65536]]
                        wanted=np.column_stack((values&255,(values>>8)&255,(values>>16)&255)).astype(np.uint8)
                        np.testing.assert_array_equal(rgb_values[start:start+65536],wanted)
                result['physical_rgb_identity'].append({'model':name,'raw_sha256':hashlib.sha256(raw.tobytes()).hexdigest(),
                    'full_physical_entries':2**24,'bytes_per_value':3,'guard_bytes':4,'guard_zero':True,'legacy288_values_equal':True})
                del raw,rgb_values,old_raw,old_palette
            else:assert direct_info(chain)['enabled'] and direct_info(chain)['format']==9
'''


if __name__ == '__main__':
    main()
