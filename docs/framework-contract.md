# 新比赛框架的实际合同与独立核验

来源是用户提供的`极速焕彩测试框架/Readme.md`、`C/main.c`、`C++/main.cpp`及四表四图。原始文件保留，适配与验证在项目中独立实施。源码注释里的历史Python接口说明不代替实际执行的C/C++表达式。

## 适配必须保持的语义

- `lut_sparse`接收原文本行序的uint16三元组与m；`apply_3d_lut`接收图像和按顺序排列的四张稀疏表。模板调用m17，Readme允许四级m分别在17–33。
- 原图是无文件头、无行padding的1024×768 RGB8，文件必须为2359296B。C++严格检查长度；C版只检查已读取长度，不能把其接受额外尾字节当作正式允许。
- `lut_sparse_ref`中，规范化表为`T[R,G,B,C] = uint8(raw[((B*256+G)*256+R)*3+(2-C)] / 16)`：原索引最快轴与内部最快轴对换，输出通道倒序，再整数除16截断及uint8转换。不能按普通RGB8表读取或改成四舍五入。源码注释描述值域0–4080；独立审计读取uint16范围并记录是否符合该注释，忠实保留其uint8转换行为。
- 参考结果是四张256³表顺序整数查表，每级输出RGB8。评分观测为逐像素RGB欧氏距离再取图像均值，打印第二个Delta是候选对参考误差，不是CIE色差。
- 计时起止只包围`apply_3d_lut`，内部准备/分配均计入；原表读取、`lut_sparse`、图片读取、参考输出和色差计算不计入。预处理可优化，但只能依赖LUT和固定参数。
- Readme明确**禁止多线程并行、GPU和NPU**，且**压缩不利用图片信息**。单线程SIMD、由全LUT证明的结构捷径和融合四级遍历不违背这些已给出的规则；未知额外存储许可应单列，不能靠样图颜色做局部缓存获得资格。

## 样例与未给出的信息

四张.bin样图均齐全。Test1为线性调试表，Readme明确正式验收不用；Test2/3/4三个文件的SHA相同，因此不能沿用旧入口“四个不同SHA”的强制要求，也不能把本轮相同表样例当成四种不同正式变换的覆盖。

2026-10-29已实际完成独立严格解析：Test1原值范围0–4080，而Test2/3/4范围为0–4095，原框架0–4080注释与样例不一致。不能按该注释把后三表拒绝；整数除16均仍落入RGB8范围。Test1 SHA为`38874daab811418151454542ff442f524f3abc2dd5eebbe83164a8a343b5b891`，后三表SHA均为`a2afb212ab35705ab7c99c059baf343d2d1a162e66b7d3e8f15ed10196040c53`。

同次独立NumPy检查了每个不同LUT的全部16777216节点：Test1可按三个独立通道曲线表示；后三表不能，RGB通道独立假设分别失配14234733、13693348、13608048个节点。此结论只否定该种三曲线捷径，不否定其他由LUT证明的结构。规范化RGB8表SHA分别为`95eeb80877c99cdcb38755b9bb5ed29066bf70e870ea6eff9ee30285bd4cd5b7`与`12d34228110802a6e4fb6a3bb577557fabd28ed93ee258598f5f45ff6a8e932a`。回执位于本机`artifacts/framework-oracle-20261029/manifest.json`，准备日志为`artifacts/framework-oracle-prepare-20261029.log`；这些不是候选性能或正式精度成绩。

两份模板虽定义MAX_IMAGES=100，实际都循环1..4；失败/缺图会登记255哨兵后继续，最后仍可能返回0。适配验收必须单独检查处理数量、每图输出和失败记录。当前代码没有Threshold判断或总分计算。Readme仅说预计两个精度阈值，具体值、换分公式、最终硬件尚未提供。

验收说明指定MinGW GCC13.2.0，源码头注释建议-O2，`.vscode/tasks.json`却只有-g；性能对比必须披露并对齐实际编译参数。当前本机另有GCC15.2，不能替代13.2版本验收。C版本失败清理还可能释放尚未初始化的Lut3D指针，C++使用RAII无此问题。

## 独立检查入口

`scripts/framework_contract_check.py`只负责合同、身份、结构与像素核验，不执行计时。它用独立NumPy按行解析文本，检查恰256³行三整数，再按上面的表达式规范化；不调用候选parser、适配器或候选生成的参考输出。

```powershell
python scripts/framework_contract_check.py inspect --framework 'F:\Hackathon\极速焕彩测试框架' --output artifacts/framework-inspection.json
python scripts/framework_contract_check.py prepare --framework 'F:\Hackathon\极速焕彩测试框架' --output artifacts/framework-oracle
python scripts/framework_contract_check.py verify --oracle artifacts/framework-oracle/manifest.json --candidate-dir artifacts/candidate/outputs/fast --output artifacts/fast-oracle.json
```

prepare只按SHA去重解析相同表，写独立规范化RGB8密集参考及manifest；每个不同LUT检查全部16777216节点、50331648通道值，证明或否定通道独立结构，并记录全部失配数和真正曲线。该证明不观察图片。可附加`--cache <四个原序u16le缓存路径>`，逐值核对候选缓存与原始文本，不因SHA清单自洽就相信缓存轴序。

verify读取候选目录`image-1.bin`至`image-4.bin`，独立执行四级密集参考，记录逐图mean/RMS/max、不同像素数、输入/输出/参考SHA。提供`--threshold T`才判断未舍入mean严格小于T；未知T保留null，不推算官方分数。所有输出拒绝覆盖，输入与清单改变会报错。准备失败保留failure.json。

补充自有图片可给verify增加`--image-list <列表路径>`，不需要重新解析原表。列表每行一张bin，相对路径按列表所在目录解析；每张仍须恰为1024×768 RGB8，输出按列表顺序读取`image-1.bin`至`image-N.bin`。空列表、重复路径和错误长度拒绝。报告用`input_scope: supplemental_images`明确与默认`framework_samples`原四图区分，并记录列表SHA；即使提供100张也不自动成为官方测试集或正式验收。

契约单测为`python -m pytest tests/test_framework_contract.py -q`，覆盖输入轴/通道、整数截断与转换、内部节点破坏结构、缓存内容/长度、RGB距离定义及输出不覆盖。小型夹具不能代替实际四表完整结构证明；实际执行结果须以各次生成的回执为准。

本阶段在Windows 11 26200、Python3.12.14、NumPy1.26.4下实际通过11项定向测试，日志为`artifacts/framework-contract-tests-final.log`。上述完整源解析和结构证明也在同一环境实际运行，并将OMP/MKL/OpenBLAS线程环境设为1；未运行计时基准。

补充图片列表入口加入后，同一环境的14项定向测试通过，日志为`artifacts/framework-contract-image-list-tests-final.log`；新增覆盖列表相对路径/长度/重复项，以及实际verify调用选取补充输入并保持明确scope和严格阈值。该增量没有重新解析大表或执行性能测试。

## 适配器CMake合同与独立样例核验

`single_header/CMakeLists.txt`注册`framework_adapter_contract`和`framework_adapter_scalar_contract`两项CTest，分别验证运行时分派与强制禁AVX2构建，两者都明确禁止OpenMP。现有CI默认任务中的单头构建与CTest步骤会包含它们，不需要额外修改workflow。测试数据来自解析公式，不读取比赛图片或LUT；包含完整源域结构证明及未采样节点反例、uint16边界、混合网格、独立u64四面体、Scalar/AVX2、线程/预算/失败契约。

```powershell
cmake --build build-single-header --target fc_framework_adapter_contract fc_framework_adapter_scalar_contract
ctest --test-dir build-single-header --output-on-failure -R '^framework_.*_contract$' --no-tests=error
```

本机MinGW GCC15.2 Release/C++17已实际2/2通过，编译命令确认两个目标都没有-fopenmp且有`FLASH_CHROMA_ENABLE_OPENMP=0`。来源、二进制和日志SHA在`artifacts/framework-contract-cmake-verification.json`；该本机结果不能替代尚未执行的远端或GCC13.2验收。

对`framework-samples-matrix-20261029-v2`另完成独立NumPy复核：runner四图密集参考逐字节正确；FrameworkStep m17标量、UniformRounded m33 AVX2和RGB24的逐图mean/RMS/max与原3DL独立参考一致。同一uniform网格m17、m25、m33下的Scalar/AVX2/structure，以及m33两种后端RGB24，输出SHA均一致。FrameworkStep m17与UniformRounded m17是不同模型，不能只看m相同就要求相同输出。证据在`artifacts/framework-independent-20261029/summary.json`及各候选小JSON。

完整源域LS m33实验的sample/fitted四图输出也已独立核验，证据为`artifacts/framework-fit-independent-20261029/summary.json`。其最差单图mean从约2.05213降至1.84289，但图1和图3的均值变差；不得只凭最差均值改善就写成每图精度均提高。上述检查不计时，Threshold未给时不授予通过资格。

末层链拟合`chain-m33`的sample/fitted四图也通过同一独立参考核验，记录为`artifacts/framework-chain-fit-independent-20261029/summary.json`。拟合后均值依次为1.46896307067645、1.56972128273236、1.65108627257213、1.38285879944606，与C++驱动结果最大偏差约4.23e-12。最差均值约2.05213降至1.65109，但第3图约0.77817升至1.65109；完整色域的均值和平方误差门控不保证每张图片或每个像素改善。拟合固定前三层，以全部256³输入的原始四级参考作为末层目标，不读取图片；末层节点改动后清除原曲线证明资格，避免结构快捷路径绕过新节点。

新增`framework_fit_contract`和`framework_fit_numerics_contract`已进入同一CMake/CTest入口，本机GCC15.2 Release/C++17、OpenMP禁用下2/2通过。前者覆盖候选格式兼容、已知解CG和未测量报告为null；后者用3375个非均匀轴探针独立重建Q16几何并核对实际四级标量输出，再用3³显式设计矩阵核对稀疏正规矩阵乘法、二次型和坐标下降项，检查无数据支持节点的正则保持初值及整数边界。3³仅为矩阵夹具，没有作为比赛运行模型；该测试不新增完整域拟合或性能实验。来源/二进制/日志SHA和复现命令见`artifacts/framework-fit-cmake-verification.json`，两份测试源码为`tests/framework_fit_contract.cpp`、`tests/framework_fit_numerics_contract.cpp`。现有CI会包含这些目标，但远端尚未实际执行。

对`framework-photos-100-20261029/images.txt`的100张既有补充照片，已用同一原始3DL独立参考核对sample-direct、independent-direct、chain-direct全部输出，并逐图确认sample-sparse/direct的SHA完全一致。三候选mean与runner最大偏差小于5.67e-12，RMS/max完全一致。全图等权平均mean和最差单图mean分别为：sample 1.76587312583410 / 3.58835819772377，independent 1.69601426394885 / 3.32959157246395，chain 1.50036350634779 / 2.40318387403820。chain相对sample为94图改善、6图退化。回执为`artifacts/framework-photos-independent-20261029/summary.json`、`driver-comparison.json`与三个候选JSON；均明确`input_scope: supplemental_images`。这100张不是官方图，独立核验不计时，也不根据数量或结果宣称赛事阈值已通过。
