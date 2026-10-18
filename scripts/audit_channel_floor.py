"""只用标准库从原始整数矩复核新几何的盒下界，不调用数值库或映射器。"""
from __future__ import annotations
import argparse
import ast
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def array(archive, name):
    """仅解析本证据所用的C顺序整数NPY，不import numpy。"""
    data = archive.read(name+'.npy')
    if data[:6] != b'\x93NUMPY': raise ValueError('不是NPY')
    major = data[6]
    if major == 1: length, start = struct.unpack_from('<H', data, 8)[0], 10
    elif major in (2, 3): length, start = struct.unpack_from('<I', data, 8)[0], 12
    else: raise ValueError('未支持NPY版本')
    header = ast.literal_eval(data[start:start+length].decode('utf-8').strip())
    formats = {'|u1': 'B', '<u4': 'I', '<i4': 'i', '<u8': 'Q', '<i8': 'q'}
    if header['fortran_order'] or header['descr'] not in formats: raise ValueError('证据数组类型/顺序不符')
    code = '<'+formats[header['descr']]; payload = data[start+length:]
    count = 1
    for dim in header['shape']: count *= dim
    if len(payload) != count*struct.calcsize(code): raise ValueError('数组字节数不符')
    return header['shape'], [row[0] for row in struct.iter_unpack(code, payload)]


def evaluate(diagonal, upper, rhs, target_sum, z, m):
    """独立逐边对称矩乘；所有量为Python任意精度整数。"""
    hz = [d*v for d, v in zip(diagonal, z)]
    offsets = [1, m, m+1, m*m, m*m+1, m*m+m, m*m+m+1]
    for i in range(len(diagonal)):
        for slot, offset in enumerate(offsets):
            value = upper[7*i+slot]
            if value:
                j = i+offset
                if j >= len(diagonal): raise ValueError('矩边越界')
                hz[i] += value*z[j]; hz[j] += value*z[i]
    quadratic = sum(x*y for x, y in zip(z, hz))
    dot = sum(x*y for x, y in zip(z, rhs))
    objective = quadratic-2*(1 << 36)*dot+target_sum*(1 << 72)
    gradient = [a-b*(1 << 36) for a, b in zip(hz, rhs)]
    linear = 2*sum(g*((0 if g >= 0 else 255)*(1 << 20)-v) for g, v in zip(gradient, z))
    return Fraction(objective, 1 << 96), Fraction(objective+linear, 1 << 96)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); folder = args.input.resolve()
    if args.output.exists(): raise ValueError('不覆盖审计')
    result = json.loads((folder/'results.json').read_text('utf-8'))
    run = json.loads((folder/'run.json').read_text('utf-8'))
    for name, digest in result['artifact_sha256'].items():
        if sha(folder/name) != digest: raise ValueError('原证据SHA不符')
    model = ROOT/run['plan']['inputs']['model']['path']
    if sha(model) != run['plan']['inputs']['model']['sha256']: raise ValueError('新几何模型SHA不符')
    with zipfile.ZipFile(model) as z:
        shape, model_nodes = array(z, 'nodes'); assert shape == (33, 33, 33, 3)
        _, shared_idx = array(z, 'shared_idx'); _, all_frac = array(z, 'channel_frac')
    with zipfile.ZipFile(folder/'continuous-evidence-nodes.npz') as z:
        shape, evidence = array(z, 'zint_q20'); assert shape == (33**3, 3)
    lower, clipped, current = Fraction(0), Fraction(0), Fraction(0)
    records = []
    for channel in range(3):
        with zipfile.ZipFile(folder/f'raw-moments-c{channel}.npz') as z:
            _, diagonal = array(z, 'diagonal'); _, upper = array(z, 'upper')
            _, all_rhs = array(z, 'rhs'); _, meta = array(z, 'metadata')
            _, idx = array(z, 'idx'); _, frac = array(z, 'frac')
        assert idx == shared_idx and frac == all_frac[channel*768:(channel+1)*768]
        assert len(diagonal) == 33**3 and sum(diagonal)+2*sum(upper) == (1 << 24)*(1 << 32)
        assert meta[0] == 1 << 24 and meta[2:4] == [32, 1] and 1 <= meta[1] <= 4
        rhs = all_rhs[channel::3]; zint = evidence[channel::3]
        _, bound = evaluate(diagonal, upper, rhs, meta[4+channel], zint, 33)
        clipped_cost, _ = evaluate(diagonal, upper, rhs, meta[4+channel], [max(0, min(255*(1 << 20), v)) for v in zint], 33)
        current_cost, _ = evaluate(diagonal, upper, rhs, meta[4+channel], [v*(1 << 20) for v in model_nodes[channel::3]], 33)
        expected = result['channels'][channel]['box_first_order_unrounded_mse_lower_exact']
        assert bound == Fraction(int(expected['numerator']), int(expected['denominator']))
        lower += bound; clipped += clipped_cost; current += current_cost
        records.append({'channel': channel, 'integer_matrix_values': len(diagonal)+len(upper)+len(all_rhs),
                        'bound_numerator': str(bound.numerator), 'bound_denominator': str(bound.denominator)})
    for name, actual in [('box_first_order_uniform_mse_lower_exact', lower),
                         ('clipped_q20_feasible_continuous_mse_upper_exact', clipped),
                         ('current_rgb8_nodes_unrounded_uniform_mse_exact', current)]:
        expected = result[name]; assert actual == Fraction(int(expected['numerator']), int(expected['denominator']))
    # sqrt(L)-sqrt(3/4)>a，转换成两项全有理的严格比较。
    a = Fraction(123, 250); gap = lower-Fraction(3, 4)-a*a
    assert gap > 0 and gap*gap > 3*a*a and lower > Fraction(3, 4)
    output = {'pass': True, 'purpose': __doc__, 'implementation': 'CPython标准库；未导入NumPy/SciPy/项目数值模块',
              'input_results_sha256': sha(folder/'results.json'), 'model_sha256': sha(model),
              'script_sha256': sha(Path(__file__)), 'channels': records,
              'box_mse_lower_exact': [str(lower.numerator), str(lower.denominator)],
              'strict_rgb8_rms_lower_exact': [a.numerator, a.denominator],
              'clipped_continuous_and_current_mse_match': True,
              'native_assemblies': 0, 'solver_calls': 0, 'pixel_mapping_calls': 0,
              'scope': '从保存整数矩独立复核凸性盒下界和RMS推论；依赖同SHA原生完整矩组装的既有来源证据，不新增性能/照片/部署模型结论'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
