# 第二批压力图片与耦合回放

由 `python -m lutlab hackextend build` 构造，定义与来源哈希见[数据说明](../../datasets/problem16-hack-v2/README.md)。

- `stress.txt`：21 张 1024×768 RGB8 合成 PPM。
- `images/`：七个分布各三种同像素多重集布局。
- `replay/coupled-wave-p64/`：四张 m17 模型、固定探针、源真值和独立整数 oracle 输出。

没有使用外部图片素材，不替换自然照片或历史 benchmark100。运行时一致性和对完整源表的近似误差分开记录。
