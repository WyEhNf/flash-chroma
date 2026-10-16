"""将已收集素材按明确声明的数值解释烘焙为RGB8完整LUT。"""
from io import StringIO
from pathlib import Path
import numpy as np
import tifffile
from . import study_kernels as kernels


def load_source(path, metadata):
    path = Path(path)
    n = metadata["grid_size"]
    grid = np.stack([np.linspace(0, 255, n)] * 3)
    policy = {"axis_order": "R,G,B", "input_interpretation": "RGB8归一化码值，不推断真实摄影色彩空间",
              "source_interpolation": "trilinear", "output_policy": "clip到0..255后floor(x+0.5)"}
    if metadata["format"] == "hald_tiff":
        image = tifffile.imread(path)
        nodes = image.reshape(n, n, n, 3).transpose(2, 1, 0, 3).astype(np.float64)
        policy["file_order"] = "R最快；Hald像素不经过ICC转换"
    elif metadata["format"] == "cube":
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        numeric = [line for line in lines if line.strip() and line.lstrip()[0] in "+-.0123456789"]
        nodes = np.loadtxt(StringIO("\n".join(numeric))).reshape(n, n, n, 3).transpose(2, 1, 0, 3) * 255
        low, high = np.asarray(metadata["domain_min"]), np.asarray(metadata["domain_max"])
        grid = low[:, None] * 255 + (high - low)[:, None] * grid
        policy["file_order"] = "R最快"
    elif metadata["format"] == "3dl":
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        axis = np.fromstring(lines[0], sep=" ")
        if np.max(np.abs(axis - np.linspace(0, 1023, n))) >= 2:
            raise ValueError("当前适配器只接受这批近恒等10bit输入shaper")
        nodes = np.loadtxt(StringIO("\n".join(lines[1:]))).reshape(n, n, n, 3)
        # 采用OCIO的偶数位深推断口径；本批最大码值落在12bit区间。
        maximum = nodes.max()
        bits = next(b for b in (8, 10, 12, 16) if maximum <= 2 ** (b + 1) - 1)
        nodes = nodes * (255 / (2 ** bits - 1))
        policy.update(file_order="B最快", inferred_output_bits=bits,
                      input_shaper="与OCIO相同，将误差小于2码值的轴视为恒等",
                      bitdepth_reference="https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/main/src/OpenColorIO/fileformats/FileFormat3DL.cpp")
    else:
        raise ValueError("不支持的原始素材格式")
    return np.ascontiguousarray(nodes.reshape(-1, 3)), grid, policy


def source_axes(grid):
    idx = np.empty((3, 256), np.int32)
    frac = np.empty((3, 256), np.float64)
    for a in range(3):
        x = np.clip(np.arange(256), grid[a, 0], grid[a, -1])
        idx[a] = np.clip(np.searchsorted(grid[a], x, side="right") - 1, 0, grid.shape[1] - 2)
        frac[a] = (x - grid[a, idx[a]]) / (grid[a, idx[a] + 1] - grid[a, idx[a]])
    return idx, frac


def bake_source(path, metadata):
    nodes, grid, policy = load_source(path, metadata)
    idx, frac = source_axes(grid)
    return kernels.expand_cube(nodes, idx, frac, grid.shape[1], 1).reshape(256, 256, 256, 3), policy
