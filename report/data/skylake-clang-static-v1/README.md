# 同源Clang对象级研究

静态信号不一致，未进入链接、像素、正确性或性能验收，不采用。[阶段说明](../../../docs/stages/2026-10-20-skylake-clang-static.md)列出目的、环境和限制。

`analysis.json`保留两者热循环计数、两项相反方向的MCA估计、停止决定及工具/输入身份；`qualification.json`记录实际编译命令、目标和返回码。原预处理搜索、编译stdout/stderr、完整汇编、热循环与MCA输出放入`diagnostics.zip`，对象和符号表放入`objects-and-symbols.zip`，输入源/头在`measured-source.zip`。

公共符号一致不等于已验证混编运行ABI，MCA模拟不是Skylake实测。没有新拟合、像素映射、benchmark或公共后端选项。`manifest.json`核对原始字节；日志含行尾空格时仍在ZIP内原样保存。
