# 修订73二维布局与普通写组合原始档案

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Status：Failed（候选73），整体任务In Progress。完整RGB8逐字节通过；首次性能系列纯映射1/4线程均未达三倍，且单线程A/A控制失败，未采用、未重测、未执行独立确认。整体三倍目标尚未完成。

`manifest.json`按长度和SHA绑定110份原件。`audit.json`从原始数组独立复算1920内轮、四worker配对中位和控制门槛，结论为`accepted=false`。控制失败系列的比值只是原始观测，不能作为可靠优化成绩。`archive.py`仅归档与离线复算，不执行原生像素或性能；不要覆盖本目录重新归档。

- `skylake-tilexy-t0-linux-build-v1/`：编译身份、参数、源码ZIP、本机参考/候选库及中间文件压缩包。
- `skylake-tilexy-t0-linux-full-v1/`：24组完整RGB8 API配置、独立16M ID比对、有限/保护页/对齐/拒绝矩阵及两表资源；字节和哨兵零差。
- `skylake-tilexy-t0-static-v1/`：两像素对象汇编、原检查器及独立审计。tilexy热环378/188/53条指令无spill；独立检查补充完整寄存器名和ELF指令EVEX排除。
- `skylake-tilexy-t0-preflight-v1/`：策略生成器v1、`KeyError: confirmation_policy`失败回执和v2。v1已写validation但尚未写策略，原生调用0；v2核对原validation并修正为`confirmation`，之后才首次测量。
- `skylake-tilexy-t0-long-perf-v1/`：四进程全部原始数组、48次预热/批末SHA、空闲、实际线程绑定及两张16MiB表的前后精确VMA/全THP回执。
- `confirmation-decision.json`：绑定首次失败结果，跳过条件确认，新增确认原生调用0。

源码、冻结计划和脚本位置、环境、计时范围、复现命令与风险见[阶段说明](../../../docs/stages/2026-10-21-skylake-tilexy-t0.md)。固定模型可按计划从`report/data/skylake-palette-v1/fixed-models.zip`恢复；照片和大oracle流须按冻结SHA恢复。实际环境为Ryzen9 8945HX/Windows11宿主WSL2，未验证Skylake。两张表各16MiB；四级句柄44,823,884字节、单级272,883字节，为程序记账而非RSS。

本README、阶段说明及后补`remote-check.json`不在110份原件清单内。PR创建前的协作记录检查以该远端回执为准；74后备提案不包含在本阶段性能结论中。
