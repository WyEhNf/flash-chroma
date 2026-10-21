# G低字节布局只读筛查

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Task：完整RGB8精度不降、通用AVX2、相对23至少三倍吞吐；Status：Failed（布局筛查）/ Draft，整体In Progress。基于Draft [PR73](https://github.com/WyEhNf/flash-chroma/pull/73)头`886e733b5168e2ea7d8ed17583eabbb23ef8ef2e`，模型、运行时和精度证据未改。

本阶段只统计一个未发现直接重复的布局：`G | R<<8 | B<<16`，与当前`R | G<<8 | B<<16`交换低两字节。先前66通道差、73局部bit交换和47双PEXT并非同一映射。拟议原生输入变换需要增加旋转/地址依赖，各个尾部/前缀/回退也须同变；本次未实现原生，不引用未读取完整Intel PDF作为已验证指令吞吐。

首次扫描前冻结唯一G低布局、64像素窗口、同一100张1024×768照片及门槛：全局G/R行集合比≤0.80且任一图≤1.05，失败停止、不扫其他轴顺序或重跑。协议SHA`62e0695236d1035fadbd6e5c33e437f57efa523106e18a816bdd859619e4fb6e`。独立只读复核确认uint32位交换自逆/范围、2MiB页编号、窗口及比例口径正确后才执行一次。

实际环境Windows11 / Anaconda Python3.13.12 / NumPy2.4.6，本机Ryzen9 8945HX；这是离线地址集合统计，不是Linux或Skylake执行。输入总SHA及100个逐图SHA均核对。全部16,777,216个输入索引的置换自逆、16MiB范围及2MiB页编号变化均零差；这只是索引数学检查，不是重新执行RGB8映射精度。

| 项目 | 结果 |
| --- | ---: |
| 64像素窗口数 | 1,228,800 |
| 当前R低平均不同64B表行 | 49.415258789 |
| G低平均不同64B表行 | 50.636512858 |
| 全局G/R比 | **1.024714109** |
| 最差单图G/R比 | **1.205545265** |

两个门槛均失败，停止该路线。原R低总行60,721,470及完整65桶直方图与既有记录完全一致；全部逐图/直方图原件、stdout/stderr及退出状态保留，未新增原生表、拟合、像素调用或性能测试。固定最低轴后，另两个高字节互换只重命名64B行，逐窗口行集合基数不变，因此不重复扫描G低的另一个高轴顺序；该等价仅适用于此集合指标，不代表真实cache set冲突、miss或性能等价。

记录是地址集合，不测量cache miss、跨窗口替换、带宽、线程竞争或吞吐，不能直接外推实际Skylake。旧R/B统计来自另一个Python/NumPy环境，只对其整数总量和直方图复现，不把解释器时间跨环境比较。归档复算只读聚合，不重新扫描输入。

复现使用SHA匹配的大流与manifest，新目录执行一次：

```powershell
python artifacts/skylake-g-low-profile-v1/analyze.py
python report/data/skylake-g-low-profile-v1/archive.py
```

[原件及复算](../../report/data/skylake-g-low-profile-v1/README.md)。完整RGB8和首次长批次仍以PR73证据为准：79单线程通过、四线程未通过三倍，总体目标未完成。

结果SHA`43a10810b484a3c2a7f06b4be47e41578a2c65ab8d12203c6a6de08dccdcd0f7`。6份原件清单、11份暂存档案blob与磁盘原字节、Python语法及空白检查通过，均为Windows只读交付检查，不新增扫描。操作前fetch GitHub，完整读取67份PR正文与前66份比较仅新增73，其余相同；73完整评论/review/行内线程均空，issue updated检索无新增。main b19c5a0及已验修复仍包含；issue7保留已修复状态、issue8接口/预算/实板待办继续跟踪。Discussion接口仍不可读取，缺口保留，不合并或关闭事项。
