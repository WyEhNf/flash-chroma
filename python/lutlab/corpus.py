"""Versioned, labelled RGB8 cases; bounded-memory, content-addressed full LUTs.

The catalog is the dataset definition, not a claim that cases were tested.
Materialisation and inspection produce separate immutable evidence. No images
are fetched, and generated samples are never labelled as natural photographs.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys
import time

import numpy as np

from . import io, luts
from .entry import _write_report

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = ("ccm", "gamma", "logistic", "filmic", "saturation", "hue", "split_tone",
    "coupled_warp", "separable_wave", "cross_product", "hard_clip", "axis_posterize",
    "quantize_early", "quantize_late", "coupled_steps", "oblique_threshold",
    "radial_threshold", "endpoint_face", "endpoint_edge", "narrow_gamut")
IMAGE_FAMILIES = ("uniform_noise", "correlated_noise", "neutral_ramp", "near_neutral",
    "shadow_gradient", "highlight_gradient", "primary_ramp", "hue_wheel", "skin_mixture",
    "sky_gradient", "foliage_gradient", "flat_colour", "checkerboard", "vertical_stripes",
    "impulse_pixels", "face_sweep", "edge_sweep", "near_endpoints", "quantizer_edges", "grid_planes")
SPLITS = ("development", "calibration", "holdout")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest_file(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def generator_fingerprint():
    package = Path(__file__).parent
    return {"schema": 1, "numpy": np.__version__, "files": {
        name: digest_file(package / name) for name in ("corpus.py", "luts.py", "io.py")}}


def op(operator, /, **parameters):
    return {"op": operator, "parameters": parameters}


def _stages(family, strength, seed):
    rng = np.random.default_rng(281000 + 997 * FAMILIES.index(family) + 71 * seed)
    s = strength + 1
    stages = []
    for k in range(4):
        if family == "ccm":
            matrix = np.eye(3) + rng.uniform(-.12*s, .12*s, (3, 3))
            matrix -= np.diag(matrix.sum(1) - 1)
            item = op("affine", matrix=np.rint(matrix*4096).astype(int).tolist(),
                bias=rng.integers(-3*s, 3*s+1, 3).tolist(), denominator=4096)
        elif family == "gamma":
            item = op("gamma", gamma=np.exp(rng.uniform(-.22*s, .22*s, 3)).tolist())
        elif family == "logistic":
            item = op("existing", name="tone", kwargs={"contrast": float(rng.uniform(.5, .8)*s),
                "pivot": float(rng.uniform(.32, .68)), "gamma": float(rng.uniform(.85, 1.15))})
        elif family == "filmic":
            item = op("existing", name="filmic", kwargs={"exposure": float((.5+.17*k+rng.uniform(0,.1))*s)})
        elif family == "saturation":
            item = op("existing", name="saturation", kwargs={"sat": float(1+rng.uniform(-.22, .35)*s), "vibrance": .12*s})
        elif family == "hue":
            item = op("existing", name="hue_local", kwargs={"center_deg": float(rng.uniform(-180, 180)),
                "width_deg": [40, 14, 3][strength], "shift_deg": float(rng.uniform(10, 25)*s), "sat_gain": 1+.15*s})
        elif family == "split_tone":
            item = op("existing", name="split_tone", kwargs={"shadow": rng.uniform(-.1, .1, 3).tolist(),
                "highlight": rng.uniform(-.1, .1, 3).tolist(), "amount": .5*s})
        elif family == "coupled_warp":
            item = op("existing", name="warp", kwargs={"amp": .012*s,
                "k_vecs": rng.uniform(-s, s, (3, 3)).tolist(), "phases": rng.uniform(0, 6.28, 3).tolist(),
                "dirs": rng.uniform(-1, 1, (3, 3)).tolist()})
        elif family == "separable_wave":
            item = op("wave", amplitude=8*s, frequency=rng.uniform(1, 2*s, 3).tolist(), phase=rng.uniform(0, 6.28, 3).tolist())
        elif family == "cross_product":
            item = op("cross_product", alpha=rng.uniform(.15*s, min(.31*s, .95), 3).tolist())
        elif family == "hard_clip":
            gains = rng.uniform(.9, 1.15, 3)*[1.2, 1.8, 3.][strength]
            item = op("affine", matrix=np.diag(np.rint(gains*4096)).astype(int).tolist(),
                bias=rng.integers(-30*s, 10, 3).tolist(), denominator=4096)
        elif family == "axis_posterize":
            item = op("quantize", levels=[[64, 24, 8][strength]+3*seed-k-j for j in range(3)])
        elif family in ("quantize_early", "quantize_late"):
            hue = op("existing", name="hue_local", kwargs={"center_deg": float(rng.uniform(80, 150)),
                "width_deg": [30, 12, 4][strength], "shift_deg": float(rng.uniform(8, 20)*s), "sat_gain": 1+.2*s})
            quant = op("quantize", levels=[[64, 24, 8][strength]]*3)
            tone = op("existing", name="tone", kwargs={"contrast": float(rng.uniform(.8, 1.2)+.15*s), "pivot": float(rng.uniform(.4, .6))})
            sat = op("existing", name="saturation", kwargs={"sat": float(1+rng.uniform(.1, .25)*s)})
            return [tone, quant, hue, sat] if family == "quantize_early" else [tone, hue, quant, sat]
        elif family == "coupled_steps":
            item = op("coupled_steps", bins=[6, 14, 36][strength], seed=int(rng.integers(1, 2**31)))
        elif family in ("oblique_threshold", "radial_threshold"):
            item = op(family, weights=rng.integers(1, 6, 3).tolist(), cut=float(rng.uniform(.35, .65)),
                center=rng.uniform(.3, .7, 3).tolist(), radius=float(rng.uniform(.22, .43)),
                low=rng.integers(0, 128, 3).tolist(), high=rng.integers(128, 256, 3).tolist(), amplitude=s/3)
        elif family.startswith("endpoint_"):
            item = op("endpoint", kind=family.removeprefix("endpoint_"), axis=k%3, side=k%2,
                width=[0, 1, 3][strength], amplitude=[1, 32, 160][strength], delta=rng.choice([-1, 1], 3).tolist())
        elif family == "narrow_gamut":
            weights = rng.uniform(.1, 1, (3, 3)); weights /= weights.sum(1, keepdims=True)
            item = op("narrow", matrix=weights.tolist(), low=rng.integers(16, 160, 3).tolist(), span=[96, 32, 8][strength])
        else:
            raise KeyError(family)
        stages.append(item)
    return stages


def _case(family, intensity, seed, split, stages, tags, expected=None):
    value = {"family": family, "intensity": intensity, "seed": seed, "split": split,
        "tags": sorted(set(tags)), "stages": stages, "expected": expected or {},
        "eligibility": "four_independent_RGB8_LUTs", "official": False}
    value["id"] = f"{family}-{intensity}-s{seed}-{hashlib.sha256(canonical(value)).hexdigest()[:8]}"
    return value


def catalog():
    cases = []
    separable = {"gamma", "logistic", "filmic", "separable_wave", "hard_clip", "axis_posterize"}
    discontinuous = {"axis_posterize", "quantize_early", "quantize_late", "coupled_steps", "oblique_threshold", "radial_threshold", "endpoint_face", "endpoint_edge"}
    for family in FAMILIES:
        tags = ["synthetic", "separable" if family in separable else "coupled",
            "discontinuous" if family in discontinuous else "smooth_before_RGB8_quantization"]
        if "quant" in family or family == "coupled_steps": tags += ["finite_palette", "node_budget_transition"]
        if family.startswith("endpoint_"): tags += ["boundary_impulse", "near_0_255"]
        if family == "cross_product": tags += ["multiaffine", "tri_vs_tetra"]
        if family == "narrow_gamut": tags += ["reachable_domain_collapse"]
        for strength, seed in itertools.product(range(3), range(3)):
            cases.append(_case(family, ("mild", "medium", "strong")[strength], seed, SPLITS[seed],
                _stages(family, strength, seed), tags))
    cases.append(_case("identity_roundtrip", "control", 0, "regression",
        [op("invert", mask=mask) for mask in (1, 2, 4, 7)], ["exact_identity_chain", "extreme_nodes", "separable"], {"composite": "identity"}))
    for seed in range(3):
        values = [[(17+seed*53+k*41+c*67)%256 for c in range(3)] for k in range(4)]
        cases.append(_case("constant", "control", seed, "regression", [op("constant", rgb=v) for v in values],
            ["degenerate", "constant_output", "separable"], {"composite_rgb": values[-1]}))
    permutations = list(itertools.permutations(range(3)))
    for seed in range(2):
        choices = [permutations[(seed+i+1)%6] for i in range(4)]
        cases.append(_case("permutations", "control", seed, "regression", [op("permute", axes=list(a)) for a in choices],
            ["axis_permutation", "separable", "exact_integer_control"]))
    for strength, amplitude in enumerate((1, 64, 255)):
        cases.append(_case("endpoint_corner", ("mild", "medium", "strong")[strength], 0, "regression",
            [op("endpoint", kind="corner", corner_mask=k+1, axis=k%3, side=k%2, width=0, amplitude=amplitude,
                delta=[1 if (k+c)%2 else -1 for c in range(3)]) for k in range(4)], ["coupled", "corner_impulse", "boundary_impulse"]))
    for levels in (16, 17, 18, 24, 32, 33, 34, 64):
        cases.append(_case("quantizer_budget", f"levels{levels}", 0, "regression",
            [op("gamma", gamma=[.91, 1.07, 1.13]), op("quantize", levels=[levels]*3),
             op("cross_product", alpha=[.17, .23, .29]), op("existing", name="saturation", kwargs={"sat": 1.2})],
            ["finite_palette", "separable_quantizer", "node_budget_transition", "discontinuous"],
            {"quantizer_stage": 2, "required_hold_knots_per_axis": levels+1}))
    cases.append(_case("hashed_random", "adversarial", 0, "regression",
        [op("hashed_random", seed=719+103*k) for k in range(4)], ["adversarial", "incompressible_control", "coupled", "discontinuous"],
        {"accuracy_pass_expected": False, "purpose": "representation limit, never excluded for failing accuracy"}))
    for name, denominator in (("integer_ties", 1), ("half_rounding", 2)):
        matrices = [[[1,1,0],[0,1,1],[1,0,1]], [[1,0,1],[1,1,0],[0,1,1]],
                    [[0,1,1],[1,0,1],[1,1,0]], [[1,1,0],[1,0,1],[0,1,1]]]
        cases.append(_case(name, "control", 0, "regression", [op("affine", matrix=m,
            bias=[-k, k, k%2], denominator=denominator) for k,m in enumerate(matrices)],
            ["coupled", "half_up_rounding", "equal_coordinates", "clipping"]))
    images = [{"id": f"{family}-i{intensity}-s{seed}", "family": family, "intensity": intensity,
        "seed": seed, "split": ("development", "calibration", "holdout", "holdout")[seed],
        "tags": ["synthetic", "RGB8", "1024x768", family], "natural_photo": False}
        for family, intensity, seed in itertools.product(IMAGE_FAMILIES, range(4), range(4))]
    assert len(cases) == 200 and len(images) == 320
    return {"schema": 1, "name": "problem16-corpus-v1", "generator": generator_fingerprint(), "cases": cases, "images": images,
        "split_policy": "all intensities of a generator seed remain in one split; exact chain bytes must differ across splits; primitives may be shared; controls are separate regression cases",
        "coverage_limits": ["synthetic only; no claim of natural photograph coverage", "RGB8 LUT output adapter only",
            "no finite corpus covers all 256^3 RGB8 transforms", "official data and Threshold unavailable"],
        "image_policy": "20 families x 4 intensities x 4 seeds; actual frame hashes define uniqueness",
        "benchmark_policy": "100 stratified frames, five per image family; four-stage timing separate from corpus generation"}


def evaluate_stage(stage, rgb):
    """Specified RGB8 -> RGB8 operator, independent of sparse model fitting."""
    name, p = stage["op"], stage["parameters"]
    x = np.asarray(rgb, dtype=np.uint8)
    if name == "invert":
        return x ^ np.asarray([255 if p["mask"] & (1<<c) else 0 for c in range(3)], np.uint8)
    if name == "constant": return np.broadcast_to(np.asarray(p["rgb"], np.uint8), x.shape).copy()
    if name == "permute": return x[..., p["axes"]].copy()
    if name == "affine":
        numerator = x.astype(np.int64) @ np.asarray(p["matrix"], np.int64).T
        d = p["denominator"]
        return np.clip((2*numerator+d)//(2*d)+np.asarray(p["bias"]), 0, 255).astype(np.uint8)
    if name == "quantize":
        n = np.asarray(p["levels"], np.int32)-1
        bins = (2*x.astype(np.int32)*n+255)//510
        return ((2*bins*255+n)//(2*n)).astype(np.uint8)
    if name == "hashed_random":
        values = x.astype(np.uint32)
        key = (values[...,0]<<16) | (values[...,1]<<8) | values[...,2]
        key ^= np.uint32(p["seed"]); key ^= key>>16; key *= np.uint32(0x7feb352d)
        key ^= key>>15; key *= np.uint32(0x846ca68b); key ^= key>>16
        return np.stack((key & 255, (key>>8)&255, (key>>16)&255), -1).astype(np.uint8)
    if name == "coupled_steps":
        rng = np.random.default_rng(p["seed"]); bins = p["bins"]
        axes = [np.r_[0, np.sort(rng.choice(np.arange(1,255), bins-1, replace=False))] for _ in range(3)]
        labels = rng.integers(0,256,(bins,bins,bins,3),dtype=np.uint8)
        indices = [np.searchsorted(axis, x[...,c], side="right")-1 for c,axis in enumerate(axes)]
        return labels[tuple(indices)]
    v = x.astype(np.float64)/255
    if name == "gamma": y = v ** np.asarray(p["gamma"])
    elif name == "existing": y = luts.OPS[p["name"]](v, **p["kwargs"])
    elif name == "wave": y = v + p["amplitude"]/255*np.sin(2*np.pi*v*np.asarray(p["frequency"])+p["phase"])
    elif name == "cross_product":
        a = np.asarray(p["alpha"]); y = (1-a)*v+a*np.roll(v,1,axis=-1)*np.roll(v,2,axis=-1)
    elif name in ("oblique_threshold", "radial_threshold"):
        mask = (v @ np.asarray(p["weights"]) >= p["cut"]*sum(p["weights"]) if name == "oblique_threshold"
            else np.sum((v-p["center"])**2,axis=-1) < p["radius"]**2)
        label = np.where(mask[...,None],p["high"],p["low"])/255
        y = (1-p["amplitude"])*v + p["amplitude"]*label
    elif name == "endpoint":
        axis = p["axis"]; selected = np.stack([x[..., (axis+c)%3] for c in range(3)], -1)
        extent = selected <= p["width"] if p["side"] == 0 else selected >= 255-p["width"]
        dimensions = {"face":1,"edge":2,"corner":3}[p["kind"]]
        mask = np.all(extent[...,:dimensions],axis=-1)
        if "corner_mask" in p:
            mask = np.all(np.stack([x[...,c]>=255-p["width"] if p["corner_mask"]&(1<<c)
                else x[...,c]<=p["width"] for c in range(3)],-1),axis=-1)
        y = v + mask[...,None]*p["amplitude"]/255*np.asarray(p["delta"])
    elif name == "narrow": y = (np.asarray(p["low"])+p["span"]*(v@np.asarray(p["matrix"]).T))/255
    else: raise ValueError(f"unknown corpus operator: {name}")
    if not np.all(np.isfinite(y)): raise ValueError("nonfinite generated LUT output")
    return np.clip(np.floor(y*255+.5),0,255).astype(np.uint8)


def _rgb_block(begin, end):
    r,g,b = np.ogrid[begin:end,:256,:256]
    return np.stack(np.broadcast_arrays(r,g,b),-1).astype(np.uint8)


def _publish_full(directory, recipe, producer, block=8):
    key = hashlib.sha256(canonical(recipe)).hexdigest()
    marker = directory / "recipes" / f"{key}.json"
    if marker.exists():
        old = json.loads(marker.read_text())
        path = directory / "objects" / f"{old['sha256']}.lut256"
        if path.stat().st_size != io.FULL_NBYTES: raise RuntimeError("cached full object truncated")
        return path, old
    temporary = directory / "objects" / f"pending-{key}.raw"
    mapped = np.memmap(temporary, mode="w+", dtype=np.uint8, shape=io.FULL_SHAPE)
    digest = hashlib.sha256()
    try:
        for begin in range(0,256,block):
            values = np.ascontiguousarray(producer(begin,min(begin+block,256)))
            if values.shape != (min(block,256-begin),256,256,3) or values.dtype != np.uint8:
                raise ValueError("generator produced a malformed RGB8 block")
            mapped[begin:begin+len(values)] = values; digest.update(values.tobytes())
        mapped.flush()
    finally: mapped._mmap.close()
    hexdigest = digest.hexdigest(); target = directory / "objects" / f"{hexdigest}.lut256"
    if target.exists():
        if digest_file(target) != hexdigest: raise RuntimeError("content-addressed object corrupt")
        temporary.unlink()
    else: temporary.replace(target)
    record = {"sha256":hexdigest,"bytes":io.FULL_NBYTES,"recipe_sha256":key}
    _write_report(marker,record)
    return target,record


def materialize_case(directory, case, generator):
    directory = Path(directory); folder = directory / "cases" / case["id"]
    folder.mkdir(parents=True,exist_ok=True)
    records, paths = [], []
    for k,stage in enumerate(case["stages"],1):
        path,record = _publish_full(directory,{"generator":generator,"stage":stage},
            lambda a,b: evaluate_stage(stage,_rgb_block(a,b)))
        destination = folder / f"lut{k}.lut256"
        if destination.exists():
            if not os.path.samefile(destination,path): raise RuntimeError("case link belongs to different source bytes")
        else: os.link(path,destination)
        records.append(record); paths.append(destination)
    if len({r["sha256"] for r in records}) != 4:
        raise RuntimeError(f"four distinct original LUTs required: {case['id']}")
    tables = [io.load_full(path,mmap=True) for path in paths]
    try:
        def composed(a,b):
            rgb = _rgb_block(a,b)
            for table in tables: rgb = io.apply_full(table,rgb)
            return rgb
        target, composite = _publish_full(directory,{"source_sha256":[r["sha256"] for r in records],"composition":"four exact integer lookups v1"},composed)
    finally:
        for table in tables: table._mmap.close()
    destination = folder / "composite.lut256"
    if not destination.exists(): os.link(target,destination)
    elif not os.path.samefile(target,destination): raise RuntimeError("composite points at different bytes")
    result = {"id":case["id"],"spec_sha256":hashlib.sha256(canonical(case)).hexdigest(),
        "stages":records,"composite":composite,"paths":[str(path.resolve()) for path in paths]}
    _write_report(folder/"manifest.json",result)
    return result


def image(spec):
    family,s,seed = spec["family"],spec["intensity"],spec["seed"]
    rng = np.random.default_rng(280000+997*IMAGE_FAMILIES.index(family)+71*seed)
    h,w = 768,1024; yy,xx = np.ogrid[:h,:w]
    u = np.broadcast_to(((xx+seed*37)%w)/(w-1),(h,w)); v = np.broadcast_to(((yy+seed*29)%h)/(h-1),(h,w))
    grey = np.repeat(u[...,None],3,axis=-1)*255
    if family == "uniform_noise": a = rng.integers(0,256,(h,w,3),dtype=np.uint8).astype(float)*[.25,.5,.75,1][s]+[0,24,40,0][s]
    elif family == "correlated_noise":
        base = rng.uniform(0,255,(h,w,1)); a = base+rng.normal(0,[1,4,16,64][s],(h,w,3))
    elif family in ("neutral_ramp","near_neutral"):
        a = grey + rng.normal(0,[0,.5,2,8][s] if family == "neutral_ramp" else [1,3,9,24][s],(h,w,3))
    elif family == "shadow_gradient": a = grey/255*[2,8,24,64][s] + rng.uniform(0,.4,(h,w,3))
    elif family == "highlight_gradient": a = 255-grey/255*[2,8,24,64][s]-rng.uniform(0,.4,(h,w,3))
    elif family == "primary_ramp":
        a = np.stack((u*255,v*[0,16,64,255][s],np.full_like(u,seed*19)),axis=-1)[...,list(itertools.permutations(range(3)))[seed]]
    elif family == "hue_wheel":
        hue=(u*6+seed*.17)%6; sat=[.05,.25,.65,1][s]; val=.03+.97*v
        rgb=np.clip(np.abs((hue[...,None]+np.array([0,4,2]))%6-3)-1,0,1)
        a=255*val[...,None]*(1-sat+sat*rgb)
    elif family in ("skin_mixture","sky_gradient","foliage_gradient"):
        base=np.array({"skin_mixture":[205,149,118],"sky_gradient":[80,145,220],"foliage_gradient":[62,128,45]}[family])
        a=base*(.2+.8*u[...,None]) + (v[...,None]-.5)*[2,8,24,64][s]+rng.normal(0,1+seed,(h,w,3))
    elif family == "flat_colour":
        base=rng.integers(12,240,3); a=np.broadcast_to(base*(s+1)/4,(h,w,3)).copy()
    elif family in ("checkerboard","vertical_stripes"):
        period=[1,2,8,64][s]; mask=((xx//period+(yy//period if family=="checkerboard" else seed))%2).astype(bool)
        a=np.where(mask[...,None],rng.integers(128,256,3),rng.integers(0,128,3))
        a=np.broadcast_to(a,(h,w,3)).copy()
    elif family == "impulse_pixels":
        a=np.broadcast_to(rng.integers(8,248,3),(h,w,3)).copy();flat=a.reshape(-1,3)
        count=[1,32,4096,65536][s]; chosen=rng.choice(h*w,count,replace=False);flat[chosen]=rng.integers(0,2,(count,3))*255
    elif family in ("face_sweep","edge_sweep","near_endpoints"):
        a=np.stack((u*255,v*255,((u+v)%1)*255),-1)
        low=[0,1,2,4][s]; chosen=(seed+s)%3;a[...,chosen]=low if (seed+s//3)%2==0 else 255-low
        if family=="edge_sweep": a[...,(chosen+1)%3]=255-low if seed%2==0 else low
        if family=="near_endpoints": a=np.where(rng.integers(0,2,(h,w,3)),255-low,low)+rng.integers(-s,s+1,(h,w,3))
    elif family == "quantizer_edges":
        levels=[16,24,32,64][s]; transitions=np.flatnonzero(np.diff((np.arange(256)*(levels-1)*2+255)//510))+1
        axis=np.clip((transitions[:,None]+np.arange(-2,3)).reshape(-1),0,255)
        a=np.stack((axis[(xx+seed*7)%len(axis)]+np.zeros_like(yy),axis[(yy+seed*3)%len(axis)]+np.zeros_like(xx),u*255),-1)
    elif family == "grid_planes":
        m=[17,18,25,33][s]; knots=np.rint(np.linspace(0,255,m)).astype(int)
        axis=np.clip((knots[:,None]+np.arange(-1,2)).reshape(-1),0,255)
        a=np.stack((axis[(xx+seed*7)%len(axis)]+np.zeros_like(yy),v*255,u*255),-1)
    else: raise ValueError(family)
    return np.ascontiguousarray(np.clip(np.floor(a+.5),0,255).astype(np.uint8))


def build_images(directory, definition):
    folder = Path(directory)/"images"; folder.mkdir(parents=True,exist_ok=True)
    records,seen = [],{}
    for spec in definition["images"]:
        array=image(spec); digest=hashlib.sha256(array.tobytes()).hexdigest()
        if digest in seen: raise RuntimeError(f"duplicate frame content: {spec['id']} and {seen[digest]}")
        seen[digest]=spec["id"]; path=folder/f"{spec['id']}.ppm"
        encoded=b"P6\n1024 768\n255\n"+array.tobytes()
        if path.exists() and digest_file(path)!=hashlib.sha256(encoded).hexdigest(): raise RuntimeError("image cache changed")
        if not path.exists(): path.write_bytes(encoded)
        keys=(array[...,0].astype(np.uint32)<<16)|(array[...,1].astype(np.uint32)<<8)|array[...,2]
        lo,hi=array.min(axis=-1),array.max(axis=-1)
        records.append({**spec,"path":str(path.resolve()),"rgb_sha256":digest,"sha256":hashlib.sha256(encoded).hexdigest(),"bytes":len(encoded),
            "features":{"unique_rgb":int(np.unique(keys).size),"channel_min":array.min(axis=(0,1)).tolist(),
                "channel_max":array.max(axis=(0,1)).tolist(),"near_neutral_pixels":int(np.count_nonzero(hi-lo<=2)),
                "boundary_pixels":int(np.count_nonzero((lo==0)|(hi==255))),"shadow_pixels":int(np.count_nonzero(hi<=16)),
                "highlight_pixels":int(np.count_nonzero(lo>=239))}})
    sets = {split:[r for r in records if r["split"]==split] for split in SPLITS}
    sets["all"] = records
    sets["benchmark100"] = [next(r for r in records if r["family"]==family and r["intensity"]==intensity and r["seed"]==seed)
        for family in IMAGE_FAMILIES for intensity,seed in ((0,0),(1,1),(2,2),(3,3),(3,2))]
    for name,selected in sets.items():
        (Path(directory)/f"{name}.txt").write_text("".join(r["path"]+"\n" for r in selected),encoding="utf-8")
    return {"records":records,"sets":{name:{"count":len(selected),"ids":[r["id"] for r in selected],
        "list_sha256":digest_file(Path(directory)/f"{name}.txt")} for name,selected in sets.items()}}


def build_probes(directory):
    folder=Path(directory)/"probes";folder.mkdir(parents=True,exist_ok=True)
    result={}
    def save(name, values, tags):
        values=np.unique(np.ascontiguousarray(values,dtype=np.uint8).reshape(-1,3),axis=0)
        path=folder/f"{name}.npy";np.save(path,values,allow_pickle=False)
        result[name]={"count":len(values),"sha256":digest_file(path),"tags":tags}
    mesh=np.indices((256,256),dtype=np.uint8).reshape(2,-1).T
    for label,levels in (("boundary",(0,255)),("near_boundary_1",(1,254)),("near_boundary_2",(2,253))):
        parts=[]
        for axis,value in itertools.product(range(3),levels):
            part=np.empty((256**2,3),np.uint8);part[:,axis]=value
            part[:,[c for c in range(3) if c!=axis]]=mesh;parts.append(part)
        save(label,np.concatenate(parts),["complete_six_planes","all_other_axis_coordinates"])
    save("corners",list(itertools.product((0,255),repeat=3)),["all_eight_corners"])
    save("neutrals",np.repeat(np.arange(256,dtype=np.uint8)[:,None],3,axis=1),["all_greys","three_fraction_ties"])
    rng=np.random.default_rng(2026101628)
    save("uniform_random",rng.integers(0,256,(262144,3),dtype=np.uint8),["uniform_RGB8","sampling_without_uniqueness_claim"])
    for m in range(17,34):
        axis=np.rint(np.linspace(0,255,m)).astype(np.uint8)
        save(f"grid_vertices_m{m}",np.stack(np.meshgrid(axis,axis,axis,indexing="ij"),-1),["integer_grid_vertices",f"m{m}"])
    if result["boundary"]["count"]!=256**3-254**3 or result["corners"]["count"]!=8:
        raise RuntimeError("independent boundary/cardinality oracle failed")
    _write_report(Path(directory)/"probes.json",result)
    return result


def inspect(directory, definition):
    """One complete integrity stage: unique objects hashed once, all chains checked."""
    directory=Path(directory); report={"objects":{},"cases":[],"images":[],"pass":False}
    for path in sorted((directory/"objects").glob("*.lut256")):
        digest=digest_file(path)
        if path.stem!=digest or path.stat().st_size!=io.FULL_NBYTES: raise RuntimeError("full object integrity failed")
        report["objects"][digest]=path.stat().st_size
    anchors=np.unique(np.r_[np.arange(256),0,1,2,127,128,253,254,255]).astype(np.uint8)
    rgb=np.stack((anchors,np.roll(anchors,71),np.roll(anchors,139)),-1)
    chain_splits={};composite_groups={}
    for case in definition["cases"]:
        folder=directory/"cases"/case["id"]; record=json.loads((folder/"manifest.json").read_text())
        if record["spec_sha256"]!=hashlib.sha256(canonical(case)).hexdigest(): raise RuntimeError("case definition mismatch")
        if len({r["sha256"] for r in record["stages"]})!=4: raise RuntimeError("duplicate original stages")
        chain=tuple(r["sha256"] for r in record["stages"])
        if chain in chain_splits and chain_splits[chain]!=case["split"]: raise RuntimeError("exact chain leakage across splits")
        chain_splits[chain]=case["split"]
        composite_groups.setdefault(record["composite"]["sha256"],[]).append(case["id"])
        for k,(stage,item) in enumerate(zip(case["stages"],record["stages"]),1):
            expected_recipe=hashlib.sha256(canonical({"generator":definition["generator"],"stage":stage})).hexdigest()
            if item["recipe_sha256"]!=expected_recipe or item["sha256"] not in report["objects"]:
                raise RuntimeError("source recipe or object missing")
            if not os.path.samefile(folder/f"lut{k}.lut256",directory/"objects"/f"{item['sha256']}.lut256"):
                raise RuntimeError("source link not bound to hashed object")
        if not os.path.samefile(folder/"composite.lut256",directory/"objects"/f"{record['composite']['sha256']}.lut256"):
            raise RuntimeError("composite link not bound to hashed object")
        tables=[io.load_full(folder/f"lut{k}.lut256",mmap=True) for k in range(1,5)]
        composite=io.load_full(folder/"composite.lut256",mmap=True)
        try:
            for k,table in enumerate(tables):
                if not np.array_equal(io.apply_full(table,rgb),evaluate_stage(case["stages"][k],rgb)): raise RuntimeError("source/axis-order anchor oracle failed")
            # Separate implementation from materialisation: start with the first
            # full LUT, not an explicit RGB input cube, then apply the other 3.
            for begin in range(0,256,8):
                exact=tables[0][begin:begin+8].copy()
                for table in tables[1:]: exact=table[exact[...,0],exact[...,1],exact[...,2]]
                if not np.array_equal(exact,composite[begin:begin+8]): raise RuntimeError("full integer composition failed")
                expected=case["expected"]
                if expected.get("composite")=="identity" and not np.array_equal(exact,_rgb_block(begin,begin+8)): raise RuntimeError("independent identity roundtrip oracle failed")
                if "composite_rgb" in expected and not np.all(exact==expected["composite_rgb"]): raise RuntimeError("constant oracle failed")
        finally:
            for table in [*tables,composite]:table._mmap.close()
        report["cases"].append({"id":case["id"],"colors":256**3,"composition_pass":True})
        if len(report["cases"])%10==0: print(f"[inspect] {len(report['cases'])}/{len(definition['cases'])} complete RGB cubes",flush=True)
    image_manifest=json.loads((directory/"images.json").read_text())
    if [r["id"] for r in image_manifest["records"]]!=[r["id"] for r in definition["images"]]: raise RuntimeError("image catalog mismatch")
    unique=set()
    for item in image_manifest["records"]:
        path=Path(item["path"])
        if digest_file(path)!=item["sha256"]: raise RuntimeError("frame hash mismatch")
        values=io.load_image(path)
        if values.shape!=(768,1024,3) or values.dtype!=np.uint8 or hashlib.sha256(values.tobytes()).hexdigest()!=item["rgb_sha256"]: raise RuntimeError("decoded frame differs")
        unique.add(item["rgb_sha256"]); report["images"].append(item["id"])
    if len(unique)!=320:raise RuntimeError("image content not unique")
    for name,item in image_manifest["sets"].items():
        listing=directory/f"{name}.txt"
        if digest_file(listing)!=item["list_sha256"] or len(listing.read_text().splitlines())!=item["count"]:
            raise RuntimeError("image set list differs")
    if image_manifest["sets"]["benchmark100"]["count"]!=100: raise RuntimeError("benchmark cardinality")
    probes=json.loads((directory/"probes.json").read_text())
    for name,item in probes.items():
        path=directory/"probes"/f"{name}.npy"
        if digest_file(path)!=item["sha256"] or np.load(path,allow_pickle=False).shape!=(item["count"],3):
            raise RuntimeError("probe integrity failed")
    report.update(pass_=True,verified_case_count=len(report["cases"]),verified_image_count=len(unique),
        unique_full_object_bytes=sum(report["objects"].values()),unique_chains=len(chain_splits),
        duplicate_composite_groups=[ids for ids in composite_groups.values() if len(ids)>1],probe_sets=probes)
    report["pass"]=report.pop("pass_")
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["catalog","build","inspect"])
    parser.add_argument("--catalog",type=Path,default=ROOT/"datasets/problem16-v1/catalog.json")
    parser.add_argument("--data",type=Path,default=ROOT/"data/corpus-v1")
    parser.add_argument("--report",type=Path,default=ROOT/"artifacts/r28-corpus/build.json")
    args=parser.parse_args(argv)
    if args.command=="catalog":
        definition=catalog()
        if args.catalog.exists() and json.loads(args.catalog.read_text())!=definition:raise RuntimeError("catalog is immutable; create a new version for extensions")
        _write_report(args.catalog,definition)
        print(json.dumps({"cases":len(definition["cases"]),"images":len(definition["images"]),"catalog":str(args.catalog)}));return 0
    definition=json.loads(args.catalog.read_text())
    if definition["generator"]!=generator_fingerprint():raise RuntimeError("catalog belongs to a different generator; preserve it and create a new version")
    args.data.mkdir(parents=True,exist_ok=True)
    for child in ("objects","recipes","cases"):(args.data/child).mkdir(exist_ok=True)
    if args.command=="inspect":
        result=inspect(args.data,definition);_write_report(args.report,result);return 0
    report={"catalog_sha256":digest_file(args.catalog),"generator":definition["generator"],"started_unix":time.time(),
        "cases":[],"complete":False,"official":False,"dataset_root":str(args.data.resolve())}
    image_manifest=build_images(args.data,definition);_write_report(args.data/"images.json",image_manifest)
    report["probe_sets"]=build_probes(args.data)
    report["image_sets"]=image_manifest["sets"];_write_report(args.report,report)
    print("[images] 320 unique labelled RGB8 frames, stratified benchmark100",flush=True)
    for case in definition["cases"]:
        value=materialize_case(args.data,case,definition["generator"]);report["cases"].append(value)
        _write_report(args.report,report)
        print(f"[build] {len(report['cases'])}/{len(definition['cases'])} {case['id']}",flush=True)
    result=inspect(args.data,definition)
    _write_report(args.data/"inspection.json",result)
    report.update(complete=result["pass"],finished_unix=time.time(),inspection_sha256=digest_file(args.data/"inspection.json"),
        unique_full_object_bytes=result["unique_full_object_bytes"],verified_images=result["verified_image_count"],
        coverage={"family":dict(Counter(c["family"] for c in definition["cases"])),"split":dict(Counter(c["split"] for c in definition["cases"])),
                  "intensity":dict(Counter(c["intensity"] for c in definition["cases"]))})
    if definition["generator"]!=generator_fingerprint() or digest_file(args.catalog)!=report["catalog_sha256"]:
        raise RuntimeError("generator or catalog changed during construction")
    _write_report(args.report,report)
    return 0


if __name__=="__main__":raise SystemExit(main())
