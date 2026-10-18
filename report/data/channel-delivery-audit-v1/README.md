# 本轮研究档案交付静态检查

目的仅为交付完整性：检查本轮channel-*、velvia-channel-*、Cinema新增阶段及Emerald的manifest文件SHA/字节数，使用`git cat-file --batch`读取暂存区实际blob，与原字节比较；另检查相关文档中的本地相对链接。

一次检查通过：260个清单项/manifest的Git blob均与原字节一致，189个本地文档链接有效。完整路径、SHA、字节数、检查时Git索引树和环境在`results.json`。`measured-source.zip`保存此次脚本与相关文档快照；`remote-refresh.json`仅记录末次只读远端同步/PR检索结果，不代表执行了PR或merge操作。

环境Windows11 26200 x64、CPython3.12.14标准库及Git，具体版本见回执。编译器、数值后端、线程、映射和性能不适用；0拟合、0像素映射、0原生调用、0性能测试。静态通过不新增精度/速度结论，也不声称全仓CI通过。

复现：`artifacts/error-study-py312/Scripts/python.exe scripts/audit_precision_delivery.py --output report/data/channel-delivery-audit-v1`。需先暂存待检查档案，既有输出不覆盖；新检查使用新目录。原始measurement源码可与普通Git文本换行不同，应使用各阶段冻结ZIP重放。
