"""将一个实验分通道NPZ模型用于RGB8图片；显式调用独立原生研究库。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'));sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
import numpy as np
from PIL import Image
from lutlab import channel_coordinates as cc, io
from channel_native import Library,digest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model',type=Path);parser.add_argument('--image',type=Path,required=True)
    parser.add_argument('--library',type=Path,required=True);parser.add_argument('--library-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--kernel',choices=['scalar','avx2'],default='avx2')
    parser.add_argument('--threads',type=int,default=4)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('输出目录已存在，不覆盖已有工作')
    with np.load(args.model,allow_pickle=False) as z:
        if str(z['format'])!='channel_coordinates_v1_experimental':raise ValueError('未知实验NPZ格式')
        model=cc.ChannelLut(z['grid'].copy(),z['nodes'].copy(),z['shared_idx'].copy(),z['channel_frac'].copy())
    cc.validate(model)
    with Image.open(args.image) as image:
        if image.mode!='RGB':raise ValueError('此入口要求RGB8图片，不能默默删除alpha或转换位深')
        pixels=np.asarray(image).copy()
    library=Library(args.library,args.library_sha256)
    args.output.mkdir(parents=True)
    # 这两个文件共同构成私有适配缓存；base单独不能表达分通道模型。
    base=args.output/'base-requires-sidecar.slut';side=args.output/'channel-frac.bin'
    io.save_sparse(base,io.SparseLut(model.grid,model.nodes,model.idx,model.channel_frac[0]))
    model.channel_frac.astype('<u4').tofile(side)
    with library.chain([base],[side]) as chain:
        chain.apply(pixels,kernel=args.kernel,threads=args.threads);memory=chain.model_bytes
    Image.fromarray(pixels,'RGB').save(args.output/'result.png')
    result={'model_sha256':digest(args.model),'input_image_sha256':digest(args.image),
        'library_sha256':library.sha256,'library_revision':library.revision,'capabilities':library.capabilities,
        'kernel':args.kernel,'requested_threads':args.threads,'m':model.m,'width':pixels.shape[1],'height':pixels.shape[0],
        'output_rgb_sha256':hashlib.sha256(pixels.tobytes()).hexdigest(),
        'model_accounting_bytes':memory,'sidecar_bytes':side.stat().st_size,'requires_channel_sidecar':True,
        'scope':'单级实验应用，非SLUTv1独立模型；无原表时不报告精度，没有性能计时或官方通过声明'}
    (args.output/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
