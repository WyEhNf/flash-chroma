# 2³输入块两种RGB差分编码的离线筛查

Agent：Codex /root、/root/base_delta_delivery；Operator：WyEhNf；Task：完整RGB8精度不降、通用AVX2、相对23至少三倍吞吐；Status：Failed（两格式资源/照片筛查）/ 待Draft交付。基于[PR80](https://github.com/WyEhNf/flash-chroma/pull/80)头`472a9a18fbfb69ae01d879b331fd384e071b91a5`。**两格式都未进入原生实现或性能测试，没有新增提速成绩。**

## 两种固定编码与判定

两者都用`coarse=(R>>1)|((G>>1)<<7)|((B>>1)<<14)`、`fine=(R&1)|((G&1)<<1)|((B&1)<<2)`，主表16MiB。按Bc分片，粗序[Bc,Gc,Rc]、细序[Bf,Gf,Rf]。正常基值均取baseR=min(R)、baseDG=min(G−R)、baseDB=min(B−R)，合成RGB三个通道须0..255且非ffffff；例外池每块八个精确RGB32，共32B。不使用旧2³-ID3bit的8MiB行比0.836作门槛，也不重评其失败。

旧格式在低24bit放baseRGB，高40bit放八个2+2+1差分，ffffff作例外哨兵。新独立格式把baseRGB精确表示为baseR8、DG_offset4、DB_offset3，共15bit，释放位置以放八个3+2+1的6bit残差，位移15+6k占bit15..62，bit63作例外tag，低63bit为池序号。全局min/span必须从全部原230palette求得：DG [-11,0]、DB [-6,0]，span11/6满足15/7上限，不能截断。解码以int32恢复DG/DB和真实RGB，先检查<0或>255，再转byte，不使用负数unsigned移位。

两套源码/协议分别冻结并唯一执行：5bit格式为2026-10-23 05:01 UTC，新header15格式为05:13 UTC。新格式改变基值表示和例外标记，不是在旧5bit结果上改门槛重跑；旧源、协议、结果和归档原字节保持。

| 项目与固定门槛 | 旧RGB24／八5bit | 新header15／八6bit／tag63 |
| --- | ---: | ---: |
| 全16,777,216色及100图离线重建 | 全部零差 | 全部零差 |
| 例外池≤2MiB | 5,728,896B，失败 | 2,035,136B，通过 |
| 总例外8像素包≤5% | 33.826314%，失败 | 14.782206%，失败 |
| 任一图≤20% | 72.789510%，索引98 div2k-0899 | 46.474202%，索引88 div2k-0885 |
| 完整域例外块 | 179,028 | 63,598 |
| 单图超20%数 | 84 | 16 |
| 整体筛查 | 失败，停止 | 失败，停止 |

新格式事前容量依据只来自旧3D跨度：Rspan>7为102块、DGspan>3为0、DBspan>1为63,542，原合成基值越界/白原因均0。因此并集63,542～63,644块，池2,033,344～2,036,608B；实际2,035,136B落在该界内。该数学界不预测照片率或周期。新格式两项照片门槛仍失败，按协议停止，不扫描位宽、几何或放宽门槛。

## 验证、证据与范围

原始离线正确性按R=0..255、每片完整G/B笛卡尔积寻址解码，对照cube像素/字节和完整SHA；100图用cube直接RGB索引对照。两者全域与照片的正逆映射、逐通道真实范围检查均零差。这是固定输出的离线编码重建，**不是候选原生完整域验证**，也没有重新拟合。

[旧5bit归档](../../report/data/skylake-brick2-rgb-base-profile-v1/README.md)与[新header15归档](../../report/data/skylake-brick2-header15-profile-v1/README.md)分别以ZIP保存五原件，manifest绑定源码/协议/启动/结果/退出。两个独立标准库审计均通过指定五件逐字节、六输入完整SHA及100图分片；重新加总128原因位图、三组511项跨度及阈值尾部、100图包直方图/总数/最差和gate。新审计还重哈希prior3D、确认两格式跨度相同，并从230palette独立推导min/span与池界。

**主表和pool二进制没有保存，只保大小/SHA；审计未独立重建colorword/pool或重跑色域/照片解码。** 单独ZIP核验仅证明归档身份及统计，附带重读输入/prior的复现命令见两README。新核验器首轮变量名冲突失败已留原件于audit-preflight-failure.zip，仅改局部变量名后通过；没有改分析数据或重复原profile。

实际分析环境为Windows11 10.0.26200、AMD64 Family25 Model97 Stepping2、Anaconda Python3.13.12、NumPy2.4.6、小端；归档审计为同Windows/Python标准库。两格式新增运行时、编译、候选/驱动C ABI、性能、模型执行/拟合均为0，没有实际Skylake或缓存行收益结论。

相关一手工作仅作后续设计参考：[Base-Delta-Immediate](https://www.cs.cmu.edu/~gpekhime/Papers/pact12_pekhimenko.pdf)利用缓存行内低动态范围的基值/差分，[SIMD整数压缩解码](https://arxiv.org/abs/1209.2137)研究成批数组的向量化。前者是硬件缓存机制，后者不等同本次随机逐色访问；未移用其性能数字或声称本格式为首创。

操作前fetch GitHub，完整74份PR正文对前73份逐字比较，仅新增80，其余不变；80全文、comment/review/行内均读且意见为空，updated issue无新。前阶段的issue7/8完整记录与main b19c5a0、337a3dd/876e15b8/397cc367祖先修复保留，公共代码未改；7绑定修复不混作8接口/预算/实板完成。Discussion当前连接器不可刷新，保留缺口，不合并或关闭。阶段按中文工作分支/提交/Draft PR交付，实际提交以PR头为准；整体同版单/四线程三倍与官方许可/预算/Threshold继续待办。
