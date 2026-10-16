# R43：无文件系统的 C99 ROM 部署

新增 `python -m lutlab.portable_export`，把四张具有已验证独立来源清单的 Q16 四面体模型导出为 `const uint8_t` C99 数组、头文件、准备函数和来源侧车文件。目标设备不需要 Python、模型文件读取或堆分配；主机侧的导出工具仍需要现有 Python 环境。没有重新拟合、合并四张表或改变节点／轴表字节。

## 主机导出与目标调用

```powershell
$env:PYTHONPATH = 'python'
python -m lutlab.portable_export --models stage1.slut stage2.slut stage3.slut stage4.slut --output firmware-model --prefix flash_chroma
```

四个路径必须按源链顺序传入，同目录的 `manifest.json` 必须通过现有缓存合同核验，声明四个不同的原始 LUT 内容哈希及 `interpolation_basis=tetra_q16`。`tri_float` 或缺失插值依据的模型会被拒绝。已有输出目录不会被覆盖，输入在导出期间改变也会拒绝发布。

生成的 `flash_chroma.c/.h` 与现有 `portable/src/jshc_portable.c` 一起编译，包含路径加入 `portable/include` 和导出目录。固件集成示意：

```c
#include "flash_chroma.h"

static jshc_p_model models[JSHC_P_STAGES];
static jshc_p_chain chain;

/* 初始化一次，之后模型与准备对象均保持有效、不可变。 */
jshc_p_status initialize_model(void) {
    return flash_chroma_prepare(models, &chain, 0);
}

/* row 指向调用者的 1024 像素 RGB8 行，原地执行全部四级。 */
jshc_p_status process_row(uint8_t row[3072]) {
    return jshc_p_apply_rgb8(&chain, row, 3072, 3072,
                          row, 3072, 3072, 1024, 1);
}
```

完整图像可以由主机／设备按行送入这个点对点算子，不要求内核持有完整帧。图像容器解码、DMA、线程、错误处理和输入格式约束继续由调用者负责。生成的准备函数可能在报错前初始化部分准备对象，不承诺整个工作区原子回滚；原始 ROM 数组始终只读。

`portable-model.json` 保留源链、四模型、原始拟合清单、生成文件和运行时源代码的 SHA256。`model-source-manifest.json` 原样保存拟合清单。这些侧车文件用于主机审计，不需要在设备上解析。仅有裸 SLUT 文件不能推断插值类型或独立拟合来源，因此导出器不会跳过清单检查。

## 一次集中验收的实际结果

成功结果为 `artifacts/r43-rom-export/stage.json`。同一个未修改的 C99 核心与导出的常量数组实际编译为 Windows 原生程序。先从已编译常量数组导出字节，四张表逐一与原模型 SHA256 相同；随后两组模型各执行一次完整 256³ 输入颜色，输出 SHA256 与 R35 冻结原生输出一致。

| 模型 | 序列化 ROM 数组负载 | 原始 RGB 节点负载 | 实际四级路径 | 完整色域结果 |
| --- | ---: | ---: | --- | --- |
| 新 17 箱／m17 | 75,196 B | 58,956 B | 节点、曲线、曲线、曲线 | 与冻结输出相同 |
| 新压力／m33 | 448,252 B | 431,244 B | 曲线、曲线、节点、通用四面体 | 与冻结输出相同 |

Windows 64 位实际准备对象共 12,560 B。若调用者只保留一条 1024 像素的原地行缓冲，二者相加为 15,632 B；这只描述模型工作区加像素行，不含栈、链接器元数据、驱动或其他应用内存，也不是实际峰值 RAM。目标 ABI 的尺寸应使用公开查询函数或 `sizeof`，不能直接复制主机数字。ROM 负载不含指针／长度表、代码、对齐填充和链接器开销。

最大 m33 生成源还实际通过 Clang 的四个 freestanding 目标编译：AArch64 小端、AArch64 大端、Cortex-M4 Thumb 和 RV32IM。对象文件与 LLVM 头部／节信息均保留。这是目标编译证据；本轮没有执行这些 ARM/RISC-V 对象，也不新增实体移动端耗时或功耗结论。此前 R31 的 AArch64 大小端模拟运行是另一份独立证据。

一个真实三线性训练模型被导出器拒绝，未创建输出目录。这避免把相同 SLUT 容器中的三线性节点误送给四面体 C99 后端。

## 修复与复用范围

首次阶段已通过两组编译字节核对和完整色域执行，随后因本机没有 `llvm-readelf` 而停止。原失败报告和驱动保留为 `failed-first-stage.json`、`failed-first-driver.py`。修复使用本机实际可用的 `llvm-readobj`；恢复先验证旧模型、生成文件、执行文件、源码及两份完整色域凭据，随后只完成目标编译和元数据检查。恢复阶段新增像素执行为 0，整个阶段共执行两个完整色域，没有重复通过的像素测试。

[可核验归档](../report/data/r43/README.md)。这一步补齐 ROM 打包与实际消费模型的工程链路，不代表全部 7,917 项策略矩阵或官方验收已经完成。
