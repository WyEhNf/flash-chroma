# WSL内存预算与真实工作流恢复

Agent：Codex `/root`、`/root/red_workflow`；Operator：WyEhNf。基于GUI阶段 `57e935cea832aeef0147c99673e64cf8e11cb564`，分支 `codex/wsl-memory-budget-20261023`，目标为Draft #84头分支。本阶段降低本机CPU工作流的WSL占用，保留既有解码、模型、262144像素分块、四线程内核和全部精度核对。

## 已应用的配置与复现

当前使用1GB内存、4个逻辑核、F盘2GB交换文件，保留Mirrored网络，关闭WSLg与嵌套虚拟化，VM空闲超时设为30000ms。`gpuSupport=false`已写入配置，但`/dev/dxg`仍存在，**没有证明GPU设备已被完全禁用**；本工作流显式使用官方CPU解码。显式设置`autoMemoryReclaim=dropCache`，它已经是当前微软文档中的默认值，不能把这一行单独算作新增优化。

```powershell
# 默认只预览；应用时检查本机GUI无活动任务，备份原始配置并关闭WSL。
.\artifacts\camera-raw-env-v1\Scripts\python.exe -X utf8 scripts/configure_wsl_memory.py
.\artifacts\camera-raw-env-v1\Scripts\python.exe -X utf8 scripts/configure_wsl_memory.py --apply --memory 1GB

# 需要本机已恢复的素材/工具及运行中的GUI；每次使用新的输出目录。
.\artifacts\camera-raw-env-v1\Scripts\python.exe -X utf8 gui/measure_wsl_memory.py --output artifacts/wsl-memory-repro-1
```

[配置脚本](../../scripts/configure_wsl_memory.py)只合并目标键，保留其他节和设置，拒绝重复目标节/键；备份及配置回执在`artifacts/wsl-memory-budget-v1/`。需要回滚时，在确认WSL任务已结束后关闭WSL，将所需备份的原始字节复制回`%USERPROFILE%/.wslconfig`，再启动。原C盘交换文件未删除；没有修改Windows分页设置或关闭其他应用。此配置不适合需要WSLg、嵌套虚拟机或更多核心的其他工作，恢复备份即可撤销。

[内存测量入口](../../gui/measure_wsl_memory.py)用独立Linux标准库进程每秒记录MemAvailable、缓存、交换和主要进程RSS高水位；Windows端通过真实GUI API发起任务。采样器本身会使WSL保持运行，包含在本次预算内。后台系统服务保持原状，没有停止更新/网络服务。没有在每个任务后清空全局缓存。

## 实际结果

环境：Windows11 26200.9711、Ryzen9 8945HX；WSL2.7.10 / Ubuntu / Linux6.18.33.2，4个来宾CPU，1GB内存、2GB交换。Windows Python3.13.12；Linux Python3.14.4 / NumPy2.4.6 / OCIO2.6.0 / OpenEXR3.5.2。使用原修订78 AVX2普通路径4线程、标量核对1线程，CPU解码版本和模型身份沿用#83。没有构建或修改内核/模型。

| 检查 | 结果与范围 |
| --- | --- |
| 基线及2GB/4核探针 | 缓存回收后，Linux估算不可回收占用由约769MiB变为397MiB；Windows vmmemWSL工作集样本约1577MiB→977MiB。这是配置/缓存状态探针，主机其他应用未冻结，不作为严格配对性能试验 |
| 1GB真实运行 | ARRI 2880×1620、RED 6144×3160、BRAW 6144×3456各新跑首帧，全分辨率官方CPU解码→Log→四级链，全部完成 |
| 精度与完整性 | 三家×SDR/HDR×reference16/runtime8共12路逐文件SHA与原首帧相等；所有处理像素native/scalar逐字节一致。未重定义已有float32参考画质误差 |
| 内存采样 | 50次、间隔1秒；`MemTotal−MemAvailable`采样峰值792739840字节（756.0MiB），交换使用峰值1429504字节（1.36MiB）。这是来宾估算占用，**不是Windows vmmem工作集，也不是连续峰值保证** |
| 进程高水位样本 | python3约360.5MiB，REDline约156.3MiB，BRAW解码器约323.8MiB；不同阶段的RSS不能相加，也不是PSS，短命进程可能未被采到 |
| GUI集成 | 原18种PNG和5项接口检查通过；本次启动窗口取消实际发布PID的worker后`kill -0`确认其已退出；新导入BRAW的总52帧/首帧结果绑定及目录重载通过，共25项 |
| 空闲释放 | 最后采样后约92秒检查：无vmmemWSL进程、无运行发行版，Windows GUI健康接口仍ready。没有测定精确停止时刻，不能把30000ms配置当作实测耗时 |

成功任务：ARRI `20261023-201626-10263d`、RED `20261023-201639-f6949d`、导入BRAW `20261023-201656-b0a9c7`、启动窗口取消 `20261023-201638-5982ba`。GUI旧WSL失败提示已被新成功任务更新，现有预览继续可用。集成脚本核对的四份视频回执来自前序ARRI导出 `20261023-181626-fa5881`，**本阶段没有新编码视频**。

第一次2GB配置的ARRI探针 `20261023-201344-2baf16`失败：Windows ART的EXR压缩器报告无法分配约2.4MB缓冲，虽然工具返回0并留下文件，但后续读取拒绝不完整EXR，任务明确失败。该次Linux采样峰值约459MiB，没有进入完整映射；失败记录保留。随后降低至1GB才取得上述三家成功结果，不能用首次失败冒充通过。

## 边界与协作记录

1GB配置只完成三家首帧验收，未在此预算下重跑完整52帧、长时间泄漏或吞吐试验。当前F盘余量不足GUI完整52帧约40GiB的事前空间预估，完整任务仍会拒绝；原54帧结果完整保留。CPU/交换限制可能影响性能，不能把低内存通过推断为更快或新的三倍/Skylake验收。

主机仍存在Windows提交空间紧张和分页盘近满问题。该阶段证明本机本轮工作流可以在1GB预算内完成，不证明此前MCE内核崩溃的唯一根因已定位或任何输入均不会OOM。旧`pipeline.py run()`整帧路径仍可能占用多份6K数组；当前GUI继续使用既有分块实现，没有切回旧入口。没有以缩图、降精度、跳过标量或减少样本来规避验收。

配置含义依据[微软WSL配置文档](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)。[公开回执及文本证据](../../report/data/wsl-memory-budget-v1/summary.json)保留成功、失败、采样与源身份；RAW、EXR、RGB、视频、交换文件和厂商二进制不上传。

操作前fetch并读取#84完整正文、全部comment/review/审查线程，无新增意见；WSL主题检索命中的8份PR正文与已读历史快照核对，新增#84单独全文读取。issue7/8全文及全部评论已刷新；337a3dd、876e15b8、397cc367实际祖先修复保留，7绑定修复不变，8接口/预算/实板未决事项继续保持。Discussion接口刷新缺口继续记录；本阶段保持Draft，不合并或关闭事项。阶段提交与PR实际身份见交付PR正文。
