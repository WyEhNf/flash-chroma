# 四级解析校准的统一入口证据

Agent：Codex；Operator：WyEhNf；仅本地研究，未PR或推送。

仅一条预声明的严格可分离Filmic家族四级链，四源不同但同家族，不代表通用三维LUT或官方数据；RGB欧氏码值距离非CIEDE2000，Threshold未知；不改默认、不加入默认68源扫描、不PR不推送。单调插值函数族已扩大，同字节不是同规范几何插值。不可行阶段必须保留，不能换源得到全零后倒填计划。

本轮没有进入完整模型映射或百图验收。固定原Filmic04/05/06/07串联：原17³、原33³、新17³解析整链误差均为0，原基线局部误差被后缀吞掉，预定严格改善触发失败。

三个CLI拟合及缓存核对成功；只有新17³四级各自都精确，不能据此把整链零误差计为新方法收益。全部12模型、解析结果和源码保留；实际完整指标CSV为空，不填解析值冒充测量。

环境与目的、源SHA、精确CLI命令及实际route在run/preparation和缓存manifest；原始stdout/stderr、源码快照在evidence.zip，模型在models.zip。大原表/输出流留本地，依冻结生成器和SHA可重建。

复现需使用本阶段measured-source.zip内实测源码与run中的计划，在新输出目录执行run_filmic_chain_calibrated.py prepare，只有full_eligible时accept。原Filmic链和等距控制链身份不同，禁止改旧计划后补验收。

Windows11 26200/Ryzen9 8945HX/Python3.12.14/NumPy1.26.4/Numba0.60.0，Numba4、OMP/BLAS/MKL1；GCC15.2 Release三原生后端各1线程。没有性能计时；RGB欧氏码值距离非CIEDE2000；官方阈值未知，历史已见照片非盲测；默认不改。
