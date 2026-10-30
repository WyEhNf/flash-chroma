"""仅冻结本次唯一只读方案；不读取完整色域/照片数组，不执行统计。"""
import ast
import datetime
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


previous = json.loads((ROOT / "artifacts/skylake-r8-packed-profile-v1/analysis.json").read_text(encoding="utf-8"))
inputs = {name: {key: value[key] for key in ("path", "sha256", "bytes")} for name, value in previous["inputs"].items() if "bytes" in value}
generation = previous["inputs"]["cache_generation"]
inputs["cache_generation"] = dict(path=generation["path"], sha256=generation["sha256"], bytes=(ROOT / generation["path"]).stat().st_size)
paths = ["experiments/skylake-direct16-runtime/channel_avx2.cpp",
         "experiments/skylake-fused16-runtime/channel_avx2.cpp",
         "experiments/skylake-load16-runtime/channel_avx2.cpp",
         "experiments/skylake-paged32-runtime/channel_avx2.cpp",
         "experiments/skylake-pack5-runtime/channel_avx2.cpp",
         "experiments/skylake-compact-cache-runtime/channel_runtime.cpp",
         "experiments/skylake-domain-delta-runtime/channel_avx2.cpp",
         "docs/stages/2026-10-20-skylake-delta16.md",
         "docs/stages/2026-10-20-skylake-delta-cache.md",
         "docs/stages/2026-10-21-skylake-pack5.md"]
history = dict(direct_equivalent_found=False, scope="针对既有小源码与阶段文档，未发现相同8R/24bit合成基值/固定2+2+1差分/32B例外池机制；不声称所有历史提交均已形式验证",
               distinctions=["24/28/29分别为同一全局R8+DG4+DB4每色16bit编码的不同加载方法，不共享每8输入的局部基值。",
                 "26为64MiB逐色RGB32直表；不是本次16MiB块基值。",
                 "62为R连续8色的1B palette ID基数+8个5bit ID差；仍依赖palette。",
                 "早期delta16/delta-cache/domain-delta压缩插值坐标；compact-cache使用全局16bit输出编码；均不等同本方案。"],
               sources=[dict(path=path, sha256=sha(ROOT / path)) for path in paths])
save("history.json", history)
ast.parse((OUT / "analyze.py").read_text(encoding="utf-8"))
protocol = dict(purpose="只读编码筛查；固定一个方案，事前冻结，不运行原生/构建/性能",
    frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(OUT / "analyze.py"),
    history_sha256=sha(OUT / "history.json"), freeze_script_sha256=sha(__file__), inputs=inputs,
    previous_profile_identity=dict(path="artifacts/skylake-r8-packed-profile-v1/analysis.json", sha256=sha(ROOT / "artifacts/skylake-r8-packed-profile-v1/analysis.json")),
    expected_photo_output_sha256="f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528",
    encoding=dict(input_code="R | (G<<8) | (B<<16)", coarse="code>>3", fine="code&7", input_block_pixels=8,
      delta_bits=[2, 2, 1], base="baseR=min(R), baseDG=min(G-R), baseDB=min(B-R); baseRGB=(baseR,baseR+baseDG,baseR+baseDB)",
      normal_eligibility="baseRGB各通道0..255且非ffffff；dR,dDG在0..3，dDB在0..1；不近似",
      code5="dR | (dDG<<2) | (dDB<<4)", word="baseRGB24 | sum(code5[k] << (24+5*k))",
      normal_decode="baseRGB24 + (code5&3)*0x010101 + ((code5&12)<<6) + ((code5&16)<<12)",
      exception_word="低24位ffffff；高40位为按coarse升序的连续例外块序号",
      exception_pool="每例外块8个精确little-endian RGB32，共32字节；全白基值也走例外",
      main_table_bytes=1 << 24, main_table_cacheline="((code>>3)*8)>>6 == code>>6，与原16MiB ID表相同",
      source_order="已验cube[R,G,B,channel]转换为逻辑地址[B,G,R]；直接RGB，不使用221色ID重新编号"),
    gate=dict(exception_packet8_fraction_max=0.05, any_image_exception_packet8_fraction_max=0.20, exception_pool_bytes_max=2 << 20),
    correctness="全部16777216色和100图逐字节一致、完整输出SHA一致、索引逆映射与无进位检查均通过，才可通过离线门槛",
    attempt_policy=dict(maximum_analysis_executions=1, overwrite=False, automatic_retry=False,
      scan_bits=False, scan_block_size=False, scan_channel_order=False, failure_action="停止；保留原始失败与退出回执，不重新分配位数重扫"),
    windows="每图从像素0起连续8像素；不扫描偏移；任一图门槛同样按包含至少一个例外的8像素包",
    interpretation="目标仅省去正常像素ID到palette的依赖；不减少主表行集合，不预测吞吐；原生代价未知",
    future_constructor="任何将来候选必须由原模型构造，不读取gold或照片；本profile仅判断可行性",
    native_calls=0, performance_calls=0, compiler_calls=0)
save("protocol.json", protocol)
save("preparation.json", dict(protocol_sha256=sha(OUT / "protocol.json"), analyze_sha256=sha(OUT / "analyze.py"),
      history_sha256=sha(OUT / "history.json"), freeze_sha256=sha(__file__), ast_parse_passed=True,
      analysis_executions=0, native_calls=0, performance_calls=0, compiler_calls=0))
print(json.dumps(dict(protocol_sha256=sha(OUT / "protocol.json"), analyze_sha256=sha(OUT / "analyze.py")), ensure_ascii=False))
