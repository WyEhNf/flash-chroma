# 测量档案原字节交付修正

Agent：Codex；Operator：WyEhNf；状态：本地交付静态修正完成，不PR、不推送。

数值实验没有变化。交付检查发现本轮8个研究档案共111个文件中，53个文件的Git提交对象被换行归一化，与测量时记录SHA的原文件字节不同。新增`.gitattributes`规则，将channel-*、velvia-channel-*以及本轮Emerald档案按原字节保存，并重新暂存这些文件。忽略行尾后，既有档案没有任何内容差异；原source ZIP及所有数值结果未改写。

Windows11 26200 x64、PowerShell7、CPython3.13.12标准库、Git2.51.0。测试目的仅为交付字节完整性：以`git cat-file --batch`读取全部111个暂存blob，与测量文件逐字节比较，修正后0差异；`git diff --cached --ignore-space-at-eol --stat`对既有档案无变化，`git diff --cached --check`通过。编译器/数值后端、线程和性能不适用，未重跑拟合、像素或性能测试。

[原始前后回执和111项SHA](../../report/data/channel-archive-bytes-v1/README.md)可复核。这项修正仅保证已列档案的Git字节，不把源码换行相同或历史ZIP所有源码与当前checkout相同作为结论；历史实验仍应使用其冻结源码ZIP。后续同类新档案沿该原字节规则保存。

后续Cinema档案使用`cinema-channel-*`命名，原规则没有覆盖，21个清单文件有14个提交blob发生同类换行转换。现为该明确前缀追加原字节规则，并只重新暂存这一新目录；没有重写数值、阈值、模型或历史测量来源。新增[Cinema交付回执](../../report/data/channel-archive-bytes-v1/cinema-extension.json)记录修正前后SHA，21个清单项和manifest本身的暂存对象均与工作区原字节相同。检查环境、目的及不涉及数值测试的范围与上文相同。
