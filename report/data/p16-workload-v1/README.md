# 92原字节证据

本目录保留固定2^26像素阈值的新92同旧87配对，不覆盖91无条件构造的失败。全部4worker、320热/80冷记录、1760实际末组输出SHA与8个RSS进程保留；A/A失效全留，没有补测或调整阈值。ordinary首次总墙钟五N均有效并过90档；有效热最劣只到80档；a399冷N1及多热场控制失效，所以all-scene≥50尚未证明。N100 standalone prepare最劣11.4943%低于50，不能称prepare提速。

raw-evidence.zip含所有原始JSON（含partial快照）、完整质量及合成输入、预检；execution-sources.zip保存执行原字节，identity逐项区分父HEAD blob的CRLF/LF/新源。build-files.zip保存实际构建依赖、flags/link/rsp及日志；models.zip为两条固定模型/侧表去重集合。不打包DLL、照片或完整目标LUT；DLL SHA和源身份已固定，可重建，不冒称工具链产物逐bit必同。

离线复算：python scripts/audit_p16_workload.py report/data/p16-workload-v1/raw-evidence.zip。它不加载DLL或重测。已提交归档及冻结源需另按manifest/identity逐Git blob SHA核验。
