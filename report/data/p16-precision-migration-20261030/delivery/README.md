# Flash Chroma 框架适配

在此目录执行 `.\run.ps1`，编译后直接运行原框架的四张样图；无需Python或OpenMP运行时。完整接入只需一个 `flash_chroma_framework.hpp` 和 `main.cpp`。指定编译器可设置 `FLASH_CHROMA_CXX`。构建使用同一单线程O3，静态链接GCC运行库，不用GPU/NPU。原C、C++模板和数据未修改。当前实测GCC15.2；题面指定的13.2尚未执行，不能混称。

```powershell
.\run.ps1 -GridSizes 17 -Mode auto
.\run.ps1 -GridSizes 33 -Mode sparse -Backend avx2
.\run.ps1 -GridSizes '17,25,33,33' -Mode sparse
.\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Backend auto
.\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Grid framework -Fit chain_ls
.\run.ps1 -GridSizes 33 -Mode direct_rgb24 -Grid framework -Fit history
.\run.ps1 -Preference '0.6,0.3,0.1' -Grid framework -Fit chain_ls -SelectionReport 'selection.json'
.\run.ps1 -Preference '0.2,0,0.8' -Grid framework -Fit chain_ls -MaxRuntimeMiB 2 -SelectionReport 'compact.json'
```

auto只有在遍历原LUT全部256³节点、证明每个通道独立时，才采用每级768B精确曲线sidecar并组成查表；否则使用真实m³稀疏四面体。结构证明和拟合不读取图片。sparse显式关闭该结构分支，适合比较仅稀疏节点的方案；direct是额外内存较大的实验表示，不能把其磁盘或稀疏节点大小当作全部RAM。

`-Preference 'A,B,C'` 为连续精度/速度/紧凑偏好，各权重在0..1且不能全零，不要求和为1。它启用独立自动选型路径：在首次打开图片之前，为当前四表生成候选，以完整256³ RGB域核对原表误差、实际后端与Scalar输出，再用固定合成输入校准速度，调用hpp中的fc::select。候选默认m17/25/33各配Sparse/RGB24，`-CandidateSizes '17;25;33;17,25,33,33'`与`-CandidateModes 'sparse,direct_rgb24'`可收窄或扩展。Grid/Fit/Backend仍生效，GridSizes/Mode由候选列表替代；不传Preference时完全沿用手动模式。未知表首次准备和全域校验可能耗时，整批图片映射期间不重新选型。

预算含义须按实际范围使用：MaxMeanError是均匀完整RGB域mean，MaxPixelError是完整域max；前者不保证正式每张图mean达标，后者提供任意图片mean的保守上界。MaxMsPerMP是固定合成输入fresh输出分配+apply的毫秒/百万像素，不是正式照片TimeCost。MaxRuntimeMiB是所选计划的自有容量记账（含模型/arena/对象/包装副本及shared管理估算），不是RSS、分配器精确开销或准备峰值；MaxWorkspaceMiB限制所选运行工作区，原四张uint16源表和候选/校准暂态另计。速度权重为0且无时间预算时跳过计时；需要速度时每个候选独立检查前后A/A，失败默认剔除。AllowUnstableTime必须显式给出，结果标为provisional，不能据此宣称稳定性能。

SelectionReport必须为新路径，成功或无可行候选均保存选择JSON；没有合格候选时非零退出，不悄悄放松预算。报告绑定本次源表、模型、实际后端、全部候选拒绝原因、完整域误差和合成计时原样本；不读旧Cinema目录、不读测试照片训练或选择。最终重新准备后再次核对所选执行计划和资源，随后固定用于整批图片。直接运行EXE也支持同样的追加长选项，无需改代码或重编译，例如：

```powershell
.\main_flash_chroma.exe '..\data' 33 auto auto framework 4 chain_ls --preference '0.6,0.3,0.1' --candidate-sizes '17;33' --selection-report 'selection-exe.json'
```

RGB24的AVX2执行核已补齐八路独立查表和64像素成块普通写出，保持同一LUT表、精度与内存需求。高级编译选项 `FLASH_CHROMA_RGB24_STREAMING=1` 可切流式写，`FLASH_CHROMA_RGB24_LEGACY=1` 用于旧gather回归；默认脚本使用普通写新核，不在图片之间重新测速选核。

默认sample采样；independent_ls用全色域分别拟合各级，chain_ls固定前三层并针对原四级完整输出拟合末层。固定参数：正则1e-5、CG最多160轮/相对残差1e-8、整数精化最多8轮。实际全色域整数mean及SSE双门控失败会保留原模型，不读取测试图片挑选节点。完整域改善不保证每张照片改善。DirectRGB24与相同拟合的Sparse逐字节等价，约多用48MiB缓存；U8/U16容量不足会非零退出。

history为显式历史精度候选档：在chain_ls固定锚点上尝试曲率/DP/误差网格、精确单调坐标、匹配三线性、box-QP/IRLS/尾部加权、四级真实整数RGB联合搜索及共享/分输出坐标，最后作minimax/p99/CVaR搜索和有限整数箱穷举。每次接受均核对原四LUT完整域mean/SSE/max/p99/CVaR，使用Q24均值和尾部证书；不会据照片修改模型。默认每级32节点、12坐标、1扫、DP24×24探针、2轮IRLS，准备可能耗时数分钟。输出HistoryReport或PreferenceReport包含各步接受/拒绝、质量与参数。混合容量可通过GridSizes或Preference的CandidateSizes指定；更细开关和双loss通过hpp中的precision::Options设置。混合三线性Sparse使用Scalar，RGB24可用AVX2，U8/U16不支持该组合。历史照片频数及Cinema成品不导入，新增分输出坐标按实际字节计入模型RAM。

输出分配仍在原apply计时区内，四LUT联合准备显式位于允许的不计时预处理区。参考查表、量化和平均RGB欧氏差公式保留。默认处理4张，`-Count 100`要求对应data/image/1.bin..100.bin完整存在；图片必须是1024×768连续RGB8，不能把PNG改名传入。

样例Test2/3/4相同，Test1是正式验收不会使用的线性表。样例最优不等于任意未知LUT最优；实际阈值与换分公式未提供，不宣称官方满分。资源行包含模型、sidecar、arena、对象和框架节点副本；sidecar是对象内子集，勿重复累加。
