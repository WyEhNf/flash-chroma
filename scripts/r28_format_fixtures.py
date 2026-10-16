"""Labelled invalid-format inputs, kept separate from valid accuracy cases.

This creates fixtures and expectations only. A manifest is not a test pass;
native parser and future embedded-C gates must record their own executions.
"""
from __future__ import annotations

import json
from pathlib import Path
import struct
import sys
import zlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
import numpy as np
from PIL import Image
from lutlab import corpus,io
from lutlab.entry import _write_report


def main():
    folder=ROOT/"data/corpus-v1/invalid";folder.mkdir(parents=True,exist_ok=True)
    m=17;grid=io.uniform_grid(m);axis=np.rint(grid).astype(np.uint8)
    nodes=np.stack(np.meshgrid(*axis,indexing="ij"),-1)
    valid=folder/"valid-control.slut";io.save_sparse(valid,io.SparseLut(grid,nodes));payload=valid.read_bytes()
    records=[]
    def save(name,data,tags,target,expected):
        path=folder/name;path.write_bytes(data)
        records.append({"id":path.stem,"path":str(path.resolve()),"sha256":corpus.digest_file(path),"bytes":len(data),
            "tags":tags,"target":target,"expected":expected,"execution_status":"not_executed"})
    def mutate(name,offset,data,tags):
        altered=bytearray(payload);altered[offset:offset+len(data)]=data
        save(name,altered,tags,"sparse_loader","reject")
    mutate("bad-magic.slut",0,b"FAIL",["header"])
    mutate("bad-version.slut",4,struct.pack("<I",2),["header","version"])
    mutate("nonzero-reserved.slut",12,struct.pack("<I",1),["header","reserved"])
    mutate("big-endian-size.slut",8,struct.pack(">I",m),["endianness","overflow_guard"])
    mutate("zero-grid-size.slut",8,struct.pack("<I",0),["invalid_grid_size","allocation_guard"])
    mutate("huge-grid-size.slut",8,struct.pack("<I",2**32-1),["invalid_grid_size","allocation_guard"])
    mutate("idx-out-of-range.slut",16+12*m,bytes([m-1]),["axis_bounds"])
    mutate("fraction-out-of-range.slut",16+12*m+768,struct.pack("<I",io.ONE+1),["Q16_bounds"])
    # Grid metadata is validated by Python. Some native versions treat it as
    # metadata only: the execution gate must expose the different behaviour.
    altered=bytearray(payload);altered[16:20]=struct.pack("<f",float("nan"))
    save("nan-grid.slut",altered,["nonfinite_grid","cross_layer_consistency"],"Python_sparse_loader","reject; native direct-loader behaviour must be measured separately")
    altered=bytearray(payload);altered[16:20]=struct.pack("<f",float("inf"))
    save("infinite-grid.slut",altered,["nonfinite_grid","cross_layer_consistency"],"Python_sparse_loader","reject; native direct-loader behaviour must be measured separately")
    altered=bytearray(payload);altered[20:24]=altered[16:20]
    save("duplicate-grid.slut",altered,["nonincreasing_grid","cross_layer_consistency"],"Python_sparse_loader","reject; native direct-loader behaviour must be measured separately")
    for name,count in (("truncated-header.slut",11),("truncated-grid.slut",40),("truncated-nodes.slut",len(payload)-1)):
        save(name,payload[:count],["truncation"],"sparse_loader","reject")
    save("trailing-byte.slut",payload+b"\0",["trailing_data"],"sparse_loader","reject")
    for m in (16,34):
        path=folder/f"competition-m{m}.slut";io.save_sparse(path,io.SparseLut(io.uniform_grid(m),np.zeros((m,m,m,3),np.uint8)))
        save(path.name,path.read_bytes(),["competition_m_bound"],"competition_loader","reject in competition mode; generic loader permits")
    for name,mode,size in (("rgba.png","RGBA",(1024,768)),("greyscale.png","L",(1024,768)),
            ("palette.png","P",(1024,768)),("wrong-width.png","RGB",(1023,768)),("wrong-height.png","RGB",(1024,767))):
        path=folder/name;Image.new(mode,size).save(path)
        save(name,path.read_bytes(),["image_contract",mode],"native_competition_image_decoder",
            "policy-sensitive: indexed PNG may decode to RGB8; compare container and decoded-channel policies" if mode=="P" else "reject")
    def chunk(kind,data):return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data))
    header=struct.pack(">IIBBBBB",1024,768,16,2,0,0,0)
    rows=(b"\0"+b"\x12\x34\xab\xcd\xff\xff"*1024)*768
    png=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",header)+chunk(b"IDAT",zlib.compress(rows))+chunk(b"IEND",b"")
    save("rgb16.png",png,["image_contract","source_bit_depth","Pillow_implicit_downcast"],"native_competition_image_decoder","reject")
    save("truncated.png",png[:41],["truncated_image"],"native_image_decoder","reject")
    save("empty-image.png",b"",["empty_input"],"native_image_decoder","reject")
    for width,height in ((0,768),(1024,0)):
        header=struct.pack(">IIBBBBB",width,height,8,2,0,0,0)
        data=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",header)+chunk(b"IDAT",zlib.compress(b""))+chunk(b"IEND",b"")
        save(f"zero-{width}x{height}.png",data,["zero_dimension"],"native_image_decoder","reject")
    for name,size in (("empty.lut256",0),("short-by-one.lut256",io.FULL_NBYTES-1),("long-by-one.lut256",io.FULL_NBYTES+1)):
        path=folder/name
        with path.open("wb") as stream:stream.truncate(size)
        records.append({"id":path.stem,"path":str(path.resolve()),"sha256":corpus.digest_file(path),"bytes":size,
            "tags":["full_LUT_size","truncation_or_trailing"],"target":"full_LUT_loader","expected":"reject","execution_status":"not_executed"})
    result={"schema":1,"records":records,"count":len(records),"status":"fixtures_constructed_not_executed",
        "source_sha256":corpus.digest_file(__file__),"valid_control_sha256":corpus.digest_file(valid),
        "excluded_from_accuracy_and_champion_counts":True,"official":False}
    _write_report(ROOT/"datasets/problem16-v1/invalid-formats.json",result)
    print(json.dumps({"invalid_fixtures":len(records),"status":result["status"]}))


if __name__=="__main__":main()
