"""纯标准库逐原ID建立坐标色集/最小见证；不导入生产函数/NumPy/native。"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/p16-direct-axis-banks-v1'
N=1<<24
MISSING=(1<<32)-1


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify(frozen):
    for name,expected in frozen['source_sha256'].items():
        assert sha(ROOT/name)==expected,name
    for name,spec in frozen['inputs'].items():
        assert sha(spec['path'])==spec['sha256'] and Path(spec['path']).stat().st_size==spec['bytes'],name


def words(path):
    raw=Path(path).read_bytes();assert len(raw)%4==0
    return [v[0] for v in struct.iter_unpack('<I',raw)]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖轴bank独立重放')
    frozen=read(OUT/'frozen.json');verify(frozen);result=read(OUT/'results.json')
    assert result['passed'] and result['frozen_sha256']==sha(OUT/'frozen.json')
    for name,spec in result['artifacts'].items():
        assert sha(OUT/name)==spec['sha256'] and (OUT/name).stat().st_size==spec['bytes'],name
    whole=words(frozen['inputs']['whole-palette-u32.bin']['path'])
    colors=words(frozen['inputs']['active-palette-u32.bin']['path'])
    assert len(whole)==613 and len(colors)==344 and colors==sorted(set(colors))
    positions=[[{} for _ in range(256)] for _ in range(3)]
    counts=Counter();rows=0
    with Path(frozen['inputs']['physical-ids-u16-with-guard.bin']['path']).open('rb') as stream:
        for begin in range(0,N,65536):
            raw=stream.read(2*65536);assert len(raw)==2*65536
            for offset,entry in enumerate(struct.iter_unpack('<H',raw)):
                old_id=entry[0];assert old_id<len(whole);color=whole[old_id];code=begin+offset
                counts[color]+=1
                for axis in range(3):
                    coordinate=(code//(256**axis))%256
                    positions[axis][coordinate].setdefault(color,code)
                rows+=1
        assert stream.read()==bytes(4)
    assert rows==N and sorted(counts)==colors and [counts[c] for c in colors]==result['active_rgb_frequencies']
    assert words(OUT/'active-colors-u32.bin')==colors
    first=words(OUT/'first-input-u32.bin');assert len(first)==3*256*344
    p=0
    for axis in range(3):
        for coordinate in range(256):
            for color in colors:
                assert first[p]==positions[axis][coordinate].get(color,MISSING)
                p+=1
    records=[];coarse_all={}
    for axis,name in enumerate(('R','G','B')):
        for banks in (2,4,8,16,32,64,128,256):
            width=256//banks;coarse=[]
            for bank in range(banks):
                found={}
                for coordinate in range(bank*width,(bank+1)*width):
                    for color,code in positions[axis][coordinate].items():
                        found[color]=min(found.get(color,MISSING),code)
                coarse.append(found)
            numbers=[len(v) for v in coarse];failed=[i for i,n in enumerate(numbers) if n>256]
            first_bad=failed[0] if failed else None
            witness=[] if first_bad is None else [{'rgb32':color,'output_rgb':list(color.to_bytes(4,'little')[:3]),
                'minimum_physical_input':coarse[first_bad][color]} for color in sorted(coarse[first_bad])[:257]]
            records.append(dict(axis=name,axis_index=axis,bank_count=banks,coordinate_width=width,bank_color_counts=numbers,
                maximum_bank_colors=max(numbers),representable=not failed,first_overflow_bank=first_bad,overflow_257_colors=witness))
            coarse_all[(axis,banks)]=coarse
    assert records==result['configurations'] and len(records)==24
    valid=[r for r in records if r['representable']]
    selected=min(valid,key=lambda r:(r['bank_count'],r['axis_index'])) if valid else None
    assert selected==result['selected_configuration'];decoded=0
    if selected is None:
        assert result['stop']=='no_representable_configuration' and result['selected_table_and_palette_bytes'] is None
        assert not (OUT/'selected-ids-u8-with-guard.bin').exists() and not (OUT/'selected-palette-u32.bin').exists()
    else:
        palette=words(OUT/'selected-palette-u32.bin');assert len(palette)==selected['bank_count']*256
        coarse=coarse_all[(selected['axis_index'],selected['bank_count'])]
        for bank,found in enumerate(coarse):
            active=sorted(found)
            assert palette[bank*256:bank*256+len(active)]==active
            assert palette[bank*256+len(active):(bank+1)*256]==[0]*(256-len(active))
        with Path(frozen['inputs']['physical-ids-u16-with-guard.bin']['path']).open('rb') as original, (OUT/'selected-ids-u8-with-guard.bin').open('rb') as packed:
            for begin in range(0,N,65536):
                old=original.read(2*65536);new=packed.read(65536)
                assert len(old)==2*65536 and len(new)==65536
                for i,entry in enumerate(struct.iter_unpack('<H',old)):
                    code=begin+i;coordinate=(code//(256**selected['axis_index']))%256
                    bank=coordinate//selected['coordinate_width'];old_color=whole[entry[0]]
                    assert palette[bank*256+new[i]]==old_color
                    assert new[i]<len(coarse[bank]);decoded+=1
            assert packed.read()==bytes(4) and original.read()==bytes(4)
        assert decoded==N==result['selected_full_rgb_decode_entries']
        assert result['selected_table_and_palette_bytes']==N+4+len(palette)*4
    verify(frozen)
    value=dict(passed=True,frozen_sha256=sha(OUT/'frozen.json'),results_sha256=sha(OUT/'results.json'),
        script_sha256=sha(Path(__file__)),python=sys.version,byteorder=sys.byteorder,full_first_matrix_rows=3*256*344,
        independently_scanned_original_entries=rows,independently_decoded_selected_entries=decoded,
        aggregate_first_matrix_scan_entries=2*N,aggregate_selected_decode_entries=2*decoded,
        aggregate_total_original_table_entries=2*N+2*decoded,
        entry_count_scope='只计两路径矩阵扫描/可选解码的逻辑表项；不含身份SHA、序列化读取，非全部I/O',
        configurations=24,active_colors=len(colors),selected=selected,
        native_prepare_calls=0,native_apply_calls=0,performance_samples=0,
        scope='标准库完整矩阵/最小见证/24配置/确定选择/可选16M重放；不授native/速度/RSS收益')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'independent_pass':True,'configurations':24,'selected':None if selected is None else [selected['axis'],selected['bank_count']],
        'original_entries':rows,'selected_decoded':decoded},flush=True)


if __name__=='__main__':
    main()
