# 既有精度候选的比较图与边界

Agent：`/root`；Operator：本会话用户；状态：本阶段只导出指标图，不授新模型或速度资格。实际提交由本文件所属Git提交标识，不在正文制造循环SHA。

目标是把已完成的六个候选放在相同坐标下比较mean、p99和max，另提供RMS/CVaR完整表。脚本读取四份已经提交的质量JSON，共十二组群体指标；公共角色的重复值逐字段精确相同，未重新运行LUT、拟合或速度测试。图中方块373a的90%速度档来自此前独立同场证据，其它点不继承此资格。

结果见[图](../../report/data/p16-tail-frontier-plot-20261024/tail-frontier.png)、[精确数据](../../report/data/p16-tail-frontier-plot-20261024/data.md)和[机器数据](../../report/data/p16-tail-frontier-plot-20261024/data.json)。max41在全域mean/p99/max上优于373a；百图聚合p99持平、CVaR从4.32123800825升至4.35270417251，新宽表仍待速度测量。图不能替代逐图退化、首级忠实度或官方ΔE判分。100图均已见过。

执行环境为本机Windows11/x64、Python3.12.14及现有Matplotlib Agg；实际版本和Windows微软雅黑文件SHA保存在原始identity.json。该阶段无编译器、native图像调用、线程后端或测速样本。没有分发字体二进制，PNG/SVG已经渲染。首次布局中三个邻近点的标注相互重叠，原图与源保留；独立V2仅调整标注坐标、引导线及画布，十二组数值逐字一致，PNG目视确认无重叠裁切。曾有一条创建V2的PowerShell命令在解析阶段报错，未执行Python或写文件；后用独立准备器生成唯一V2。

复现依次运行`python scripts/plot_p16_tail_frontier.py`、`python scripts/prepare_p16_tail_frontier_layout_v2.py`、`python scripts/plot_p16_tail_frontier_v2.py`；每个新目录存在即拒绝覆盖。封存用`python scripts/archive_p16_tail_frontier_plot.py`，暂存和提交后分别用`python scripts/audit_p16_tail_frontier_plot_git.py index`及`head`检查实际Git对象、两个ZIP的CRC/全部成员SHA和十二组来源指标。

所有原始图、身份、数据及布局失败通过raw.zip保留，执行源及本说明在sources.zip。后续正式293/294速度协议是独立工作，不从图形位置推断速度、内存或可移植性。
