"""只给通过全域及逐图50%精度的两个7bit候选导出真实P16B ROM。"""
from __future__ import annotations
import argparse
from pathlib import Path
import json
import struct
import numpy as np
from profile_palette_bitpack import sha, save

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    profile=json.loads((args.profile/'results.json').read_text(encoding='utf-8'))
    assert sha(args.rom)=='146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5'
    ids=np.frombuffer(args.rom.read_bytes(),np.uint8,offset=1056)
    rows=[]
    for name in ['weighted_ward_centroid7','maximin_original_color7']:
        row=next(row for row in profile['results'] if row['name']==name)
        assert row['minimum_retention']>=.5 and row['bits']==7
        model=np.load(args.profile/(name+'.npz'))
        palette,mapping=model['palette'],model['mapping']
        assert len(palette)<=128 and mapping.shape==(256,) and np.max(mapping)<len(palette)
        words=np.zeros(len(ids)//8,np.uint64)
        mapped=mapping[ids].reshape(-1,8)
        for field in range(8):
            words |= mapped[:,field].astype(np.uint64) << (7*field)
        payload=words.astype('<u8').view(np.uint8).reshape(-1,8)[:,:7].copy().reshape(-1)
        padded=np.pad(payload,(0,4))
        for start in range(0,len(ids),65536):
            bit=np.arange(start,start+65536,dtype=np.uint32)*7
            values=(padded[bit>>3].astype(np.uint32)|(padded[(bit>>3)+1].astype(np.uint32)<<8))>>(bit&7)
            np.testing.assert_array_equal((values&127).astype(np.uint8),mapping[ids[start:start+65536]])
        rgb32=np.zeros((256,4),np.uint8);rgb32[:len(palette),:3]=palette
        header=b'P16B'+struct.pack('<7I',1,7,len(palette),len(payload),0,0,0)+rgb32.tobytes()
        path=args.output/(name+'.bin');path.write_bytes(header+padded.tobytes())
        rows.append(dict(name=name,bytes=path.stat().st_size,sha256=sha(path),profile_minimum_retention=row['minimum_retention'],
                         full_id_reconstruction_mismatches=0,profile_model_sha256=sha(args.profile/(name+'.npz'))))
    save(args.output/'export.json',dict(purpose=__doc__,script_sha256=sha(__file__),profile_results_sha256=sha(args.profile/'results.json'),
        original_rom_sha256=sha(args.rom),models=rows,scope='真实7bit文件与完整ID独立重建；不是native映射或性能/RSS'))
    print(json.dumps(rows,ensure_ascii=False))


if __name__=='__main__':main()
