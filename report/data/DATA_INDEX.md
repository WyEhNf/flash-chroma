# 报告数据索引

由 `scripts/build_typst_data.py` 从 Git `f73b8dd81a360521098ee985d68bcb3b548ccb19` 和独立日志 `32f23355ab678e0696725ac871762a5be7a0ce57` 生成。
包含 43 次运行、24 个当前候选、696 条逐图结果；原始日志按字节归档，生成器不修改 `logs/`。

| 文件 | SHA-256 |
| --- | --- |
| `run_records_exact.tar.gz` | `c2508b7102ab4b3bb00fb7bbea07f25ae551648f99fbe83abf32d25115d7af31` |
| `manifests_exact.tar.gz` | `cbdee2b59eb94eed019176cb5ab468eefa35aab01e050c7b1c4b64f63d9e2417` |
| `experiments_exact.tar.gz` | `df057ccd32cdaa03d02e4cb83d080eb0762c375f5c8a1904678901aabea519e2` |
| `ledger.csv` | `b59d7371f880db75780b5ffe6404823b31e8f968954112b1ad775737196884ba` |
| `image_results.csv` | `b11c2dd1f295264ae64d1b785ce6bcadf8d53a338f39e3ef12a1d46b89b9f636` |
| `cube_hotspots.csv` | `338714396d4adbcb4cdfc0168b987179c9fdcc010d9fbb2d2ee90e69651d8b88` |

原始图像和完整 LUT 约 1.8 GiB，保留在被 Git 忽略的 `data/`；本归档只保存清单和实验记录。
`run_records_exact.tar.gz` 包含运行目录中的 JSON、stdout、测试日志和代码差异；路径及字节不变。
