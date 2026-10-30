# Velvia匹配算子归因精简归档

本归档保存同一m33权威Q16设计、完整cube均匀L2下四面体/三线性各一次近似LS诊断；不含新的全域流、百图、性能或官方验收结果。两类连续节点可能越出RGB8，不能当作可部署SLUT。

首先阅读[中文报告](report.md)；[冻结计划](plan.json)、[运行身份](run.json)、[全部指标](results.json)和[文件清单](manifest.json)提供来源及验证范围。measured-source.zip包含实际脚本、计划、Python依赖和原生组装源码。

matched-nodes.npz含两套float64节点及各自clip+half-up后的RGB8控制，并保存原grid/idx/frac；baseline.slut与baseline-grid.npy是已验收2dd参照；fixed-probes.npz是前阶段冻结的两组16384颜色和旧top16，没有重选样本。

复现使用仓库scripts/explain_velvia_matched_operators.py和experiments/velvia-matched-operators-v1.json，命令及环境见报告。需要按plan恢复各原路径，尤其同SHA的50MB原表和旧已验收流；大输入仍由既有数据来源提供。本轮使用的原生fullfit库必须匹配run.json指纹，未在归档里包含DLL或自动构建替代。缺少该库时不能把三线性单独结果冒充完整matched实验。

结果支持当前固定设计下四面体在一般探针上的优势，不能外推为所有ISP排名，也不能把它和不同目标的2dd比较写成matched改进率。报告明确残差代入理论式只是浮点诊断量，不是含舍入区间的全局证书。未提交、推送或创建PR。
