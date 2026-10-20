# 标准库服务器包恢复的唯一数据验证

[阶段说明](../../../docs/stages/2026-10-20-skylake-packet-restore.md)给出环境、命令、保护逻辑及未测范围。`restore-results.json`保存114个落盘文件、339633805字节的全部SHA和manifest身份；三个原流被复制，没有重新生成图像、模型或输出。

`command.json`与`source-and-command.zip`绑定一次实际命令、恢复脚本、交付元数据和归档程序。目标目录含空格；新目录内容与既有已验4/16包相同，不把数据恢复称为再次运行内核或Skylake通过。代码有格式/路径/覆盖拒绝条件，本轮没有另跑负例或性能。

`prior-head-ci.json`是对性能提交e155dc2的六项真实成功查询，后续提交须另查CI。实际Windows11 / Python3.12.14标准库，后端/编译器/线程不适用；不修改原包、公共默认或AGENTS.md。
