"""解析Hald身份/通道置换对照，独立检验轴序、端点与分数插值。"""
from pathlib import Path
import runpy
from PIL import Image


def test_rational_hald_mapping_matches_analytic_identity_and_channel_permutation():
    interpolate = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/audit_hald_reference.py"))["interpolate"]
    for permutation in ((0,1,2),(1,2,0)):
        image = Image.new("RGB",(8,8))
        image.putdata([tuple((r*85,g*85,b*85)[c] for c in permutation) for b in range(4) for g in range(4) for r in range(4)])
        for rgb in ([0,0,0],[255,255,255],[127,128,64],[1,254,85],[255,0,170]):
            assert interpolate(image,4,rgb) == [rgb[c] for c in permutation]
