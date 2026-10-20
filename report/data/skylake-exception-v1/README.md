# 修订23对22：精确例外池的原始证据

[阶段报告](../../../docs/stages/2026-10-20-skylake-exception.md)给出完整原理、结果、失败和复现。唯一80轮中，本机1/4线程apply吞吐再提高70.91%/70.90%，copy+apply提高62.40%/54.32%，完整输出相同；新增约1.08MB。Skylake实机与官方许可未验收。

- `performance/worker0..3.json`保存四进程全部80轮、实际CPU/库/依赖及逐轮输出SHA。`audit/results.json`是独立标准库复算，没有新计时。
- `packed-contract`独立重建16M颜色、2M主词和全部269708个池词，包含1320次混合/尾部/偏移比较及14条拒绝；`base/cache/domain/signed/fallback-contract`分别保存通用、缓存、证书、正负斜率和大调色板补验。
- `full`为Windows完整域/100图，`linux-full`为WSL/AMD的12组完整域及528次有限比较；不是Skylake性能。
- `windows-build`、`linux-build`含构建日志/参数/源ZIP/二进制和对象；`static`含新完整函数反汇编。`reference22-object-proof.json`证明本轮参考运行时与AVX2对象就是旧22字节，另有Linux原回退对象证明。
- `failed-packed-contract-v1`保留导入函数被局部数组遮蔽造成的验证器失败，validation-v2与成功packed-v2另存；C++和唯一性能没有修改或重跑。
- `construction-and-validation-generators.zip`与`archive.py`保存生成和归档过程。`input-reuse.json`引用旧22小模型包/大流SHA，目录不含三个大流，不声称完整独立运行包。
- `remote-check.json`和`remote-snapshot.zip`保存39个PR及相关全部协作记录；剔除API临时克隆元数据字段，正文/评论不改。`manifest.json`覆盖100份原始文件，不自包含，也不含后补说明/审计。

原始源字节与SHA由`archive-audit.json`核对：12份源快照、714项成员，全部通过。提交或移机前从测量ZIP恢复旧依赖，避免Git换行归一化改变冻结身份。Linux标准库入口不需要NumPy；Windows性能脚本需要NumPy/Pillow/psutil。移机应新建构建/验证/策略和输出目录，不改旧回执。

```sh
python3 -I -S scripts/audit_skylake_exception_archive.py --archive report/data/skylake-exception-v1 --output artifacts/exception-archive-audit-new.json
```
