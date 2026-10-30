# 修订81：单YMM输入因热区spill停止

[阶段说明](../../../docs/stages/2026-10-21-skylake-input256.md)。新组合每8像素一次32B输入、四ID先行和既有预排NT输出；单线程及分离保留79两个pair48对象。输入机制已有34先例，没有将它称为首创。

唯一构建后，两份独立静态检查均定位64像素区段`0x4c9`的32B栈写入及`0x6e9`读回，按冻结门槛停止；32区段无栈，8/4输入折叠内存VPERMD、索引零扩展、四ID和图像先读后写成立。初版root分类把spill误计图像store，原件保留；v2分类修正后唯一失败仍是no_stack，候选与对象不变。

`manifest.json`绑定34份原件，包括生成器/差分、完整构建命令/库/源码ZIP/中间对象ZIP、两份root结果和独立逐节对象审计。`audit.json`核对72项冻结源码与构建ZIP；后补本文、摘要和交付审计自身不列入原件清单。候选加载、完整RGB8、有限/guard/align、性能及确认均未执行，像素/性能调用0；verify和bench胶水仅派生，未经运行。不能用旧版本完整域或性能代替新版本验证。

实际构建/主静态环境Ryzen9 8945HX、Windows11宿主WSL2 Ubuntu Linux6.18.33.2、GCC15.2、Python3.14.4标准库；独立反汇编环境及解析器SHA见其原件。通用AVX2、Skylake调优，仅两个保留pair TU带BMI1。归档/交付核对为Windows11/Anaconda Python3.13.12标准库。不是真实Skylake或缺BMI硬件实测，没有任何本轮性能结论。

复现应在新checkout按阶段说明恢复固定大流/模型及静态脚本支持，使用新构建目录；原件不得覆盖，已有results目录不得直接运行写入型checker。`skylake-input256-preflight-v1/root-archive_input256_static.py`和`root-audit_input256_delivery.py`保存实际核对程序，使用前还原到其原`artifacts/`路径。

远端69份完整PR正文与前68份比较仅新增75；75完整意见刷新为空，issue无新增。Discussion接口仍不可读取，保留缺口，不执行合并或关闭。整体三倍、真实Skylake和官方许可/预算/Threshold仍未完成。
