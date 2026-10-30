# Flash Chroma 框架适配

在此目录执行 `.\run.ps1`，编译后直接运行原框架的四张样图；无需Python或OpenMP运行时。完整接入只需一个 `flash_chroma_framework.hpp` 和 `main.cpp`。指定编译器可设置 `FLASH_CHROMA_CXX`。构建使用同一单线程O3，静态链接GCC运行库，不用GPU/NPU。原C、C++模板和数据未修改。当前实测GCC15.2；题面指定的13.2尚未执行，不能混称。

```powershell
.\run.ps1 -GridSizes 17 -Mode auto
.\run.ps1 -GridSizes 33 -Mode sparse -Backend avx2
.\run.ps1 -GridSizes '17,25,33,33' -Mode sparse
.\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Backend auto
.\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Fit chain_ls
```

auto只有在遍历原LUT全部256³节点、证明每个通道独立时，才采用每级768B精确曲线sidecar并组成查表；否则使用真实m³稀疏四面体。结构证明和拟合不读取图片。sparse显式关闭该结构分支，适合比较仅稀疏节点的方案；direct是额外内存较大的实验表示，不能把其磁盘或稀疏节点大小当作全部RAM。

RGB24的AVX2执行核已补齐八路独立查表和64像素成块普通写出，保持同一LUT表、精度与内存需求。高级编译选项 `FLASH_CHROMA_RGB24_STREAMING=1` 可切流式写，`FLASH_CHROMA_RGB24_LEGACY=1` 用于旧gather回归；默认脚本使用普通写新核，不在图片之间重新测速选核。

默认sample采样；independent_ls用全色域分别拟合各级，chain_ls固定前三层并针对原四级完整输出拟合末层。固定参数：正则1e-5、CG最多160轮/相对残差1e-8、整数精化最多8轮。实际全色域整数mean及SSE双门控失败会保留原模型，不读取测试图片挑选节点。完整域改善不保证每张照片改善；未知阈值时保持三档显式选择。DirectRGB24与相同拟合的Sparse逐字节等价，约多用48MiB缓存；U8/U16容量不足会非零退出。

输出分配仍在原apply计时区内，四LUT联合准备显式位于允许的不计时预处理区。参考查表、量化和平均RGB欧氏差公式保留。默认处理4张，`-Count 100`要求对应data/image/1.bin..100.bin完整存在；图片必须是1024×768连续RGB8，不能把PNG改名传入。

样例Test2/3/4相同，Test1是正式验收不会使用的线性表。样例最优不等于任意未知LUT最优；实际阈值与换分公式未提供，不宣称官方满分。资源行包含模型、sidecar、arena、对象和框架节点副本；sidecar是对象内子集，勿重复累加。
