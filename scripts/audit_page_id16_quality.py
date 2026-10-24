"""离线独立核P4九模式质量、逐图、原始输入SHA与实测容量，不重运行。"""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan_path=ROOT/'experiments/page-id16-runtime-v1.json';plan=read(plan_path)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('冻结原始源/输入不一致')
    run=read(a.input/'run.json');quality=read(a.input/'quality/results.json');export=read(a.input/'rom/export.json');build=read(a.input/'build/build.json');labels={'core_out','c991_out','c991_in','c994_out','c994_in','avx1_out','avx1_in','avx4_out','avx4_in'}
    if not run['passed'] or [value['returncode'] for value in run['jobs']]!=[0,0,0] or not quality['passed'] or quality['plan_sha256']!=sha(plan_path) or export['plan_sha256']!=sha(plan_path) or build['plan_sha256']!=sha(plan_path):raise AssertionError('唯一执行/计划不同')
    if set(quality['full_hashes'])!=labels or set(quality['photo_hashes'])!=labels or set(quality['full_hashes'].values())!={plan['quality']['expected_full_sha256']} or set(quality['photo_hashes'].values())!={plan['quality']['expected_photos_sha256']}:raise AssertionError('九完整域/百图原身份不同')
    if len(quality['photos'])!=100 or [row['image'] for row in quality['photos']]!=list(range(100)) or any(set(row['modes'])!=labels or set(row['modes'].values())!={row['oracle_sha256']} for row in quality['photos']):raise AssertionError('100逐图u64不同')
    expected_finite=22*10*4+10
    if (quality['finite'],quality['io_rejections'],len(quality['rejected_formats']),quality['image_guards'],quality['rom_guards'],quality['unaligned_rom'])!=(expected_finite,113,21,18*10,4*9,8*9) or not quality['closed_models_zero'] or quality['per_image_heap_scratch']!=0:raise AssertionError('固定全部计数/生命周期不同')
    rom=a.input/'rom/page-id16.bin';actual=rom.stat().st_size;capacity=actual+quality['actual_model_bytes']
    if actual!=12633124 or actual!=quality['actual_rom_bytes'] or quality['actual_model_bytes']!=40 or capacity!=12633164 or quality['actual_capacity']!=capacity or quality['net_saving']!=16779328-capacity or export['output']['bytes']!=actual or sha(rom)!=quality['rom_sha256'] or sha(rom)!=export['output']['sha256']:raise AssertionError('实际文件/ABI/账本不同')
    for name,value in build['outputs'].items():
        path=a.input/'build'/name
        if path.stat().st_size!=value['bytes'] or sha(path)!=value['sha256']:raise AssertionError('构建原件不同：'+name)
    if sha(a.input/'build/jshc_page_id16.dll')!=quality['library_sha256'] or sha(a.input/'build/jshc_page_id16_c99.dll')!=quality['standalone_sha256']:raise AssertionError('质量计算对象不同')
    # 独立struct读取实际P4，按照原map编号只回放，不生成新分类。
    import struct
    logical=hashlib.sha256()
    with rom.open('rb') as stream:
        header=stream.read(1056);ids=struct.unpack('<4096H',stream.read(8192))
        if header[:32]!=b'P4ID'+struct.pack('<7I',1,12,230,1<<24,3082,0,0):raise AssertionError('实际P4头不同')
        for identifier in ids:
            if identifier>=3082:raise AssertionError('map越界')
            stream.seek(9248+4096*identifier);logical.update(stream.read(4096))
        stream.seek(-4,2)
        if stream.read(4)!=bytes(4):raise AssertionError('显式guard不同')
    if logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('独立全ID回放不同')
    result=dict(audit_passed=True,purpose=__doc__,plan_sha256=sha(plan_path),full_modes=9,photo_modes=9,images=100,finite=quality['finite'],io_rejections=quality['io_rejections'],format_rejections=len(quality['rejected_formats']),image_guards=quality['image_guards'],rom_guards=quality['rom_guards'],unaligned_rom=quality['unaligned_rom'],actual_file=actual,actual_model=40,actual_capacity=capacity,net_saving=16779328-capacity,logical_id_sha256=logical.hexdigest(),rom_sha256=sha(rom),library_sha256=quality['library_sha256'],scope='只离线重算/原件身份，不运行native/图片/WASM/吞吐，不提前授100..50速度档。')
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
