# header15／残差6／tag63：两项照片门槛失败

[两格式阶段说明](../../../docs/stages/2026-10-23-skylake-brick2-rgb-base.md)。新独立编码保持2³输入几何，以15bit基值头、八个6bit残差和bit63例外tag取代旧24bit RGB基值／八5bit残差。旧5bit原件及失败判定保持。

完整色域及100图离线重建零差；池2,035,136B位于旧跨度推导的2,033,344～2,036,608B界内并通过2MiB，但照片异常8包14.782206%、最差46.474202%，未过5%／20%，停止。没有候选原生或性能成绩。

`evidence.zip`保存五原件原字节，manifest绑定身份。`verify_archive.py`仅用标准库从ZIP核对结果和统计，不导入原分析、重建colorword/pool或再次解码。主表／池二进制没有保存，原件仅含其大小/SHA。

```powershell
python report/data/skylake-brick2-header15-profile-v1/verify_archive.py
```

本次`audit.json`还实际核对原件逐字节、六输入与100图分片SHA、prior3D身份和跨度相同，并从全部230palette重新推导signed min/span。仅ZIP核验不等于重读这些外部输入；复现额外检查需恢复协议输入及prior文件、选择新输出路径：

```powershell
python report/data/skylake-brick2-header15-profile-v1/verify_archive.py --repository . --compare-originals --rehash-inputs --output artifacts/skylake-brick2-header15-audit-reproduction.json
```

后补核验器首轮因跨度循环变量覆盖数学界dict而TypeError；初版源码/manifest和失败信息保存于`audit-preflight-failure.zip`。仅将局部变量改为span_limit后审计通过，原五件、编码、门槛及分析执行次数均未改变。
