"""冻结单一相邻字节异或布局；只准备，不执行统计。"""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'artifacts/skylake-xor-chroma-profile-v1'
HERE.mkdir(exist_ok=False)
prior = ROOT/'report/data/skylake-g-low-profile-v1/raw/analyze.py'
source = prior.read_text(encoding='utf-8')
start = source.index('def swap16(')
end = source.index('\ndef ', start+4)
source = source[:start]+'''def swap16(code):
    # 数学索引h=[R,G xor R,B xor G]，最高位限定为零。
    return (code ^ (code << 8)) & np.uint32(0xffffff)

def inverse(code):
    return (code ^ (code << 8) ^ (code << 16)) & np.uint32(0xffffff)

'''+source[end:]
source = source.replace('swap16(permuted)!=code','inverse(permuted)!=code')
source = source.replace('    assert inverse_errors==range_errors==page_errors==0','    assert inverse_errors==range_errors==0')
source = source.replace('G低','相邻字节异或').replace('G_low','xor_chroma').replace('G_over_R','xor_over_R')
source = source.replace("'2MiB页编号", "'2MiB页编号")
source = source.replace("'16M输入索引自逆/范围证明不是执行全部RGB8映射精度，模型和运行时未改'", "'16M索引正逆/范围证明不是RGB8映射验证；页编号改变，模型与运行时未改'")
source = source.replace("'只试固定相邻字节异或/R中/B高，不选择最佳参数；另一高轴顺序仅重命名行，无需重复'", "'只试R,G xor R,B xor G，不扫描轴、移位或其他可逆变换'")
source = source.replace('停止相邻字节异或路线，不构造原生或扫其他轴顺序', '停止该异或布局，不构造原生或扫描变种')
(HERE/'analyze.py').write_bytes(source.encode('utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
protocol = {
    'purpose':'首次统计前冻结单一h=R|((G xor R)<<8)|((B xor G)<<16)布局，使用100图连续64像素窗口，不重测择优',
    'frozen_utc':datetime.now(timezone.utc).isoformat(),
    'script_sha256':sha(HERE/'analyze.py'),
    'parent_script_sha256':sha(prior),
    'generator_sha256':sha(Path(__file__)),
    'gate':{'mean_lines_ratio_max':0.80,'any_image_lines_ratio_max':1.05},
    'layout':'h=(code xor (code<<8))&0xffffff; inverse=(h xor (h<<8) xor (h<<16))&0xffffff',
    'prior_art':'41为code xor code>>10；60/61/66/67为字节模减；此布局改为逐字节xor，未声称业内首创',
    'hypothesis':'若通道共同变化使异或布局的短窗口行集合显著减少，则支持一次原生研究；两条向量移位/xor仍有成本，行集合不代表miss或吞吐',
    'source_only_shape':'未来输入先展开[R,G,B,B]，再vpslld8及vpxor生成[R,G xor R,B xor G,0]；最高字节B xor B为零',
    'window_pixels':64,'maximum_analysis_executions':1,
    'native_calls':0,'performance_calls':0,'compiler_calls':0,
    'on_fail':'保存并停止，不实现原生、不换轴/移位/变种重扫；不修改旧任何失败判定',
    'input_binding':'analyze.py SPECS中的照片、manifest及原R/B统计路径和SHA全部保留',
    'limits':'离线索引可逆不替代运行时完整精度；改变2MiB页号；不是Skylake性能'
}
(HERE/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'script_sha256':sha(HERE/'analyze.py'),'protocol_sha256':sha(HERE/'protocol.json')},ensure_ascii=False))
