"""Independent arithmetic and split controls for the extended corpus."""
from fractions import Fraction
import math

import numpy as np

from lutlab import corpus


def test_corpus_integer_oracles_and_chunk_invariance():
    values=np.stack(np.meshgrid([0,1,2,127,128,254,255], [0,1,127,255], [0,128,255], indexing="ij"),-1).astype(np.uint8)
    affine=corpus.op("affine",matrix=[[1,-1,2],[2,1,-2],[-1,3,1]],bias=[-1,0,1],denominator=2)
    actual=corpus.evaluate_stage(affine,values).reshape(-1,3)
    expected=[]
    for rgb in values.reshape(-1,3):
        expected.append([min(255,max(0,math.floor(sum(int(x)*a for x,a in zip(rgb,row))/2+.5)+bias))
            for row,bias in zip(affine["parameters"]["matrix"],[-1,0,1])])
    assert np.array_equal(actual,np.asarray(expected,np.uint8))
    x=np.repeat(np.arange(256,dtype=np.uint8)[:,None],3,axis=1)
    for levels in (16,17,18,24,32,33,34,64):
        stage=corpus.op("quantize",levels=[levels]*3)
        y=corpus.evaluate_stage(stage,x)
        expected=[math.floor(Fraction(math.floor(Fraction(int(v)*(levels-1),255)+Fraction(1,2))*255,levels-1)+Fraction(1,2)) for v in x[:,0]]
        assert np.array_equal(y[:,0],expected)
        assert len(set(y[:,0]))==levels
        assert len({0,255,*list(np.flatnonzero(np.any(y[1:]!=y[:-1],axis=1))+1)})==levels+1
    stage=corpus.op("coupled_steps",bins=14,seed=2026101628)
    whole=corpus.evaluate_stage(stage,corpus._rgb_block(0,2))
    pieces=np.concatenate([corpus.evaluate_stage(stage,corpus._rgb_block(r,r+1)) for r in range(2)])
    assert np.array_equal(whole,pieces)


def test_catalog_split_and_budget_labels():
    definition=corpus.catalog()
    assert len({case["id"] for case in definition["cases"]})==200
    assert len(definition["images"])==320
    for seed,split in enumerate(corpus.SPLITS):
        rows=[case for case in definition["cases"] if case["split"]==split]
        assert len(rows)==60 and {c["seed"] for c in rows}=={seed}
    assert sum(case["split"]=="regression" for case in definition["cases"])==20
    assert {c["expected"]["required_hold_knots_per_axis"] for c in definition["cases"] if c["family"]=="quantizer_budget"}=={17,18,19,25,33,34,35,65}
    for family in corpus.FAMILIES:
        chains=[corpus.canonical(c["stages"]) for c in definition["cases"] if c["family"]==family]
        assert len(set(chains))==9
