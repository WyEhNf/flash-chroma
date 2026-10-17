# portable 与 embedded 的共同数值合同

两套库保留各自接口，公共部分以同一份序列化模型和独立 u64 oracle 为准，不以函数名相似推断等价。关联 [Issue #8](https://github.com/WyEhNf/flash-chroma/issues/8)。

| 范围 | 公共约束或明确差异 |
| --- | --- |
| 公共模型范围 | SLUT v1、m=17..33、四级独立 RGB8/Q16 四面体映射；每级加 32768 后右移 16 位，再进入下一级 |
| 权威坐标 | 使用文件中的 idx/frac，65536 是合法端点；不从 f32 网格重建权重 |
| 所有权 | 模型字节由调用者持有，只读借用；模型、准备对象在最后一次执行前保持有效且不可变 |
| embedded 额外能力 | m=2..256，0..4 级，连续原地 RGB 像素块；无曲线缓存，初始化失败使视图失效 |
| portable 额外约束/能力 | 固定四级、m=17..33；二维步长、容量及重叠检查；初始化失败保持旧对象；可选结构证明与曲线缓存 |
| 资源 | embedded 视图在 32/64 位 ABI 为 16/32 字节；portable 的三条 256 项 u32 曲线缓存为每模型 3072 字节，另加对象字段、链对象及栈，不能把无堆分配写成零 RAM |

共同正确性夹具复用 `embedded/tests/contract.c`：四张不同网格 m17/18/25/33、非均匀轴、非对齐模型与像素、0..257 长度、哨兵、真实触发的曲线/常量捷径；portable 默认与强制通用两种路径、embedded 都与独立 u64 oracle 比较。两套接口的专属失败语义继续单独验证，不强行统一。

根目录同时启用 portable 和 embedded 时，默认打开 `JSHC_EMBEDDED_PORTABLE_PARITY`。独立 embedded 构建默认关闭此选项，保持可独立构建；需要整个仓库中的 portable 源码时显式打开：

```bash
cmake -S embedded -B build-embedded-parity -DJSHC_EMBEDDED_PORTABLE_PARITY=ON
cmake --build build-embedded-parity --parallel 2
ctest --test-dir build-embedded-parity --output-on-failure
```

三个 QEMU 工作流已接入该选项。是否已执行成功，以对应提交的 CI 日志为准；不能把修改 workflow 当成通过。RTOS 日志报告栈剩余字数、portable 模型/链对象实际字节；链接 map 和 `.su` 文件用于复核该目标 ABI 的资源。测试用双链对象、全量模型夹具的 BSS 不等于生产最小开销。

宿主 `embedded_desktop_parity` 还在完整 RGB 色域上比较桌面标量、embedded、portable C99 与可用的结构化 AVX2。上述结果只证明所测模型的数值兼容，不能证明实板速度、功耗、BSP 存储或实时截止期。接口合并与调用者迁移仍需维护者确定，不删除任何现有 API。
