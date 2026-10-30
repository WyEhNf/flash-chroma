# Flash Chroma 框架适配

在此目录执行 `.\run.ps1`，编译后直接运行原框架的四张样图；无需Python或OpenMP运行时。指定编译器可设置 `FLASH_CHROMA_CXX`。构建使用同一单线程O3，不用GPU/NPU。原C、C++模板和数据未修改。

```powershell
.\run.ps1 -GridSizes 17 -Mode auto
.\run.ps1 -GridSizes 33 -Mode sparse -Backend avx2
.\run.ps1 -GridSizes '17,25,33,33' -Mode sparse
```

auto只有在遍历原LUT全部256³节点、证明每个通道独立时，才采用每级768B精确曲线sidecar并组成查表；否则使用真实m³稀疏四面体。结构证明和拟合不读取图片。sparse显式关闭该结构分支，适合比较仅稀疏节点的方案；direct是额外内存较大的实验表示，不能把其磁盘或稀疏节点大小当作全部RAM。

输出分配仍在原apply计时区内，四LUT联合准备显式位于允许的不计时预处理区。参考查表、量化和平均RGB欧氏差公式保留。默认处理4张，`-Count 100`要求对应data/image/1.bin..100.bin完整存在；图片必须是1024×768连续RGB8，不能把PNG改名传入。

样例Test2/3/4相同，Test1是正式验收不会使用的线性表。样例最优不等于任意未知LUT最优；实际阈值与换分公式未提供，不宣称官方满分。资源行包含模型、sidecar、arena、对象和框架节点副本；sidecar是对象内子集，勿重复累加。
