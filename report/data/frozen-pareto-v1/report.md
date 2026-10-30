# 已冻结研究候选的完整验收

新候选进一步降低mean与全色域p99，但照片max从38.052595升到39.051248，未全面支配当前2dd模型。保留两版研究对照，默认模型未升级，未创建PR。

|版本|范围|mean|RMS|p99|最大误差|CVaR1%|
|---|---|---:|---:|---:|---:|---:|
|PR32/34|cube|0.981682|1.879181|7.000000|51.000000|11.524906|
|PR32/34|photos|1.033849|1.383880|7.141428|46.043458|4.797097|
|joint-grid-v2|cube|0.941689|1.686610|7.000000|41.012193|10.117563|
|joint-grid-v2|photos|0.926384|1.250491|6.082763|38.052595|4.473176|
|rounded-fullphotos-sweep1|cube|0.896904|1.653683|6.403124|41.012193|10.002951|
|rounded-fullphotos-sweep1|photos|0.905408|1.241471|6.082763|39.051248|4.471328|

照片p99栏为最差逐图p99，CVaR为平均逐图CVaR；RGB欧氏码值距离，不是CIEDE2000。100图均为历史已见数据，官方Threshold未知。

原拟合阶段因为照片mean未达额外3%而未入围，原记录不变。该候选的选择指标全部非退化，且全色域样本mean/p99降幅明显，因此单独冻结为研究验收，不等于修改原升级门槛。完整验收实际发现照片max退化，完整失败项photos.max及原严格门禁false如实保存。

相对2dd逐图变化：mean 94好/6差，RMS79好/21差，p99为11好/80平/9差，max38好/37平/25差，CVaR51好/49差。不能把聚合改善说成逐图支配。

独立整数oracle、C++标量、AVX2完整256³输出SHA均为a00581fe37b99854446940d3587b9f68a182b99ea52b09fcb31d2f1d0edca877，零字节差异。Windows11/Ryzen9 8945HX/Python3.12.14/Numba4线程，BLAS/MKL/OMP=1；原生GCC15.2 Release两后端各单线程，程序SHA ba088c682bb2b0e2e4634b23b35e662c52d87d38806d05827b876f08c8697f3a。不比较运行时性能。

复现命令：`artifacts/error-study-py312/Scripts/python.exe scripts/validate_frozen_pareto.py --output artifacts/frozen-pareto-replay --executable build-engineering-alignment/jshc.exe`；需恢复同SHA父模型/原表/照片及父结果。measured-source.zip为实际验收源码，run.json绑定依赖、输入和环境。模型112063字节，容量/权威轴表与2dd相同。

本阶段只完成单级Velvia；Cinema四级末级实验已另冻计划，尚未执行，不将这里的结果写成四级比赛成绩。
