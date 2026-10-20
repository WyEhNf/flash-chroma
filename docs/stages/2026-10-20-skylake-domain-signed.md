# 获证快路径的正负斜率与四种网格补验

Agent：Codex；Operator：WyEhNf；Task：补齐当前m33完整验收之外的有限快路径覆盖；Status：Completed（有限整数，不含新性能）。

最终复核发现：此前m17/18/25合成缓存样例主要走原回退，新无检查路径的完整域验收集中于当前m33模型。本轮只增加一个确定性有限合同，验证不同网格、正负边斜率、三通道有效坐标不同时，候选真正获证并启用新路径；不修改原生源码或重测性能。

测试前在run回执固定seed=2026102022、首级m=17/18/25/33、共享节点灰值120..128、坐标幂1/1.1/0.9、8192个随机探针加8角点和3个固定边界点。每轴节点边同时含正负值；第一层三通道输出必须确实有差异，后三共享随机模型须产生非恒定输出，否则拒绝，未扫描seed。

Windows11 26200 / Ryzen9 8945HX / Python3.12.14/NumPy1.26.4，沿用原MinGW GCC15.2 Release AVX2二进制4/16；源/库SHA与原计划一致。两库×标量1/AVX2请求1/4×字节偏移0/1×4网格，共48次比较，每次8203像素，覆盖4096块和向量尾部；全部与独立uint64整数oracle逐字节相同，前后哨兵保持，模型持久容量相等。四个模型均明确获证且fast_path_enabled=1，没有以回退通过替代新路径验证。

```powershell
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/verify_skylake_domain_signed.py --plan experiments/skylake-domain-isolated-v1.json --build artifacts/skylake-domain-isolated-build-v1 --output artifacts/skylake-domain-signed-contract-v1
```

复现须新输出名称，并按原构建源码ZIP恢复精确字节。[结果、生成器、模型与侧表](../../report/data/skylake-domain-signed-contract-v1/README.md)保留固定seed、依赖/源/库身份及每例实际证书。探针由该版本NumPy和冻结生成器恢复；不宣称保存了未导出的原探针字节。

这是独立内核短输入，不替换100图或1024×768比赛图契约。它不是四个新模型的完整256³精度验收，也不证明任意网格/LUT或Skylake成绩；原20项候选、11项测速/9项静态停止、7.07%/5.10%本机结果保持。没有新拟合、性能、公共默认或AGENTS.md变更。
