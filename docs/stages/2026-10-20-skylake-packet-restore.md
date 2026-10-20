# 用小包和旧数据恢复同一份服务器输入

Agent：Codex；Operator：WyEhNf；Task：补齐服务器包恢复入口与字节证据；Status：Completed（数据恢复，不含新增数值或性能）。

4/16完整传输ZIP约188MB，本地已保存；版本化小包省略三个大流，原先需要手工拼接。本轮增加标准库入口`scripts/restore_skylake_server_packet.py`：核对小包及manifest身份，检查成员和规范相对路径，将三个已知大小/哈希的数据流复制到新目录，最后逐文件核对落盘字节。拒绝覆盖已有输出或回执；失败保留新目录，不自动重试。路径/格式拒绝逻辑来自代码审阅，本轮没有另跑一组负例测试。

实际Windows11 26200 / Python3.12.14标准库，后端、线程和编译器不适用。目的仅为数据完整性；没有模型加载、图像解码、像素映射、拟合、构建或性能调用。

唯一有效恢复命令为：

```powershell
artifacts/error-study-py312/Scripts/python.exe -X utf8 scripts/restore_skylake_server_packet.py --archive report/data/skylake-domain-server-v2 --data-root artifacts/skylake-layout-server-v2 --output "artifacts/skylake-domain-server-restored v1"
```

在新环境中使用Python3.11+即可；`--data-root`须已有清单所需的原三个流，缺少数据时此脚本不会下载或生成替代数据。复现应使用新的输出名称。

实际恢复114个清单文件、339633805字节，另核对manifest；三个大流原样复制。恢复后的manifest SHA仍为`74649bd457527a55295d03bf3335041aa388cf1b4e090fd36b600eb4321e84b2`，与之前WSL完整验收的包相同。[全部文件回执及源码](../../report/data/skylake-packet-restore-v1/README.md)保存精确身份；输入/输出目录包含空格，恢复本身已执行，但没有重新构建或运行恢复目录中的内核。

恢复目录已经包含标准服务器入口及必要原字节输入。其后可按包内`SERVER_DOMAIN_README.md`独立构建/验收；正式性能仍需真实Skylake，显式`--measure`才进行四场景160组百图。当前只完成文件身份核对，不能给尚未运行的Skylake补发通过。

原生候选计数仍为20项、11项测速/9项静态停止，修订16的7.07%/5.10%仍限原Windows/AMD比较。原性能提交`e155dc2`的六项CI已查询为成功，但不提前称本次后续提交CI通过。原服务器包、性能数据、公共默认和AGENTS.md保持。
