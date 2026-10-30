# 从当前145个max48输入重选首级节点的必要证书

Agent：`/root/tail`。Operator：本任务用户。状态：唯一完整热点提取、整数盒/双链验证及独立审计完成；145点均未被单点必要条件阻断，无新模型、CP、拟合或性能。

此前只改变95分量的窄域，外部固定误差已使max平方至少48、p99至少为现值，继续在该子空间内搜索无法改善尾部。本阶段从已完整验收的741e55f见证重新提取当前全部max48输入，扩大变量选择，先判断首级±2是否有被单点下界阻断的情况。

固定首级NPZ SHA `741e55f55c674384543511dc20b98ecd7d6a1ed4c1b9bb17406cabd7cc86bea0`，同85b0侧表和904e/95cb/5b8后缀；完整输出流SHA `de4a98d5f3b3d430e349e83146d211296a4e6b3e2a9664a5806b321384a3c3f9`，gold SHA `ec79ca618022293b2d2f5c832f1a8647c88e4994ce820664310e09c0f4bf5690`。source/plan执行前冻结SHA `56c44cd3fb9ed74bf217cbf7a27ff42899ee9ac49e83ffdd4c26c9164d69a132`，含23源与12输入。

完整16,777,216流逐块重新提取，恰145个输入误差平方48，其他输入均不大于48；其数量与已认证直方图一致。按这些点真实Q16四角正权取122物理节点的全部RGB，共366分量，另用八角正权核节点集合一致。全部变量相对741e55f取±2并clip到0/255，其他节点、坐标、轴和后缀固定。没有沿旧116点或95分量删选，也未使用照片择优。

复用原17³/33³有限通用盒合同并核执行源码SHA，当前145点的两个整体端点再用独立uint64逐点核验。标量四角acc包含固定角贡献，完整枚举每点首级RGB整数AABB，最多125状态，总查询17,565，小于冻结上限145×125=18,125。

每个查询都以0ced预计算完整后缀和实际后三级uint64、Numba两条整数链逐字节交叉，全部零差；145个基线点也通过首级uint64/Numba及完整三层后缀对de4a流/gold身份。没有把数学包围盒误作新实际节点模型。

| 局部最小误差平方 | 热点数 |
| --- | ---: |
| 0 | 142 |
| 1 | 1 |
| 3 | 1 |
| 6 | 1 |

总计7,837条状态误差平方≤47，每点至少18条；没有一点局部最小值大于47。因此本模型、所选122节点±2盒和固定后缀没有被单点必要条件否定。不同输入仍共享节点，一个点的argmin可以与另一个点冲突；此结果不证明存在同时满足全部点的共享赋值，更未检查其他受影响输入的安全性或平均精度。

误差是三个整数RGB差的平方和。平方模8只可能0/1/4，三个平方之和不能模8为7，所以误差平方47本身不可能出现。目标≤47实际等价于≤46；协议仍保留原目标值，其数学口径不变。

独立只读审计用145个互异点各自真实误差48和已认证完整直方图计数145确认点集完整；整数重算全部权重、clip、acc上下界、盒体积、查询误差和argmin，全部通过。双链与端点数值由唯一主证书执行，审计不再次全域扫描，不追加搜索。

环境为Windows x86-64、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4/Numba0.60.0，BLAS1、OMP/Numba上限4。质量共享主机，没有正式性能或RSS测量，未用AVX512。阶段结束明确释放CPU。

主要文件是`experiments/p16-cinema-max48-first-box-v1.json`、`scripts/certify_cinema_max48_first_box.py`及独立audit；原件在`report/data/p16-cinema-max48-first-box-20261024`。这里没有改变任何旧精度预算、旧minL1失败或max48公共基线质量资格。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/certify_cinema_max48_first_box.py --frozen artifacts/cinema-max48-first-box-frozen-v1.json --output artifacts/cinema-max48-first-box-v1
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_max48_first_box.py --stage artifacts/cinema-max48-first-box-v1 --output artifacts/cinema-max48-first-box-independent-v1.json
```

后续必须完整构造这122节点的正支撑，核所有可能新增的坏点及公共基线预算；本证书不能代替该步骤，也不提供速度50%或整体升级结论。
