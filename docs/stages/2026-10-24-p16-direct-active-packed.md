# max41实际命中颜色与精确9位表示：离线可表示性通过

Agent：Codex `/root`；Operator：本会话用户。三个方向仍保持独立分支；本阶段属于精度分支的表示研究，未改变数学模型、默认实现或任何速度资格。

## 结果与适用范围

对已通过完整质量检查的293/max41，只prepare一次、只读导出完整R最快物理uint16表。16,777,216个输入实际命中344种RGB32颜色；整个后缀缓存的613色中，269色未被原始RGB8完整域命中。以RGB32升序重编号后，9位索引可精确表示全部输入，无采样、删色、近似或照片参与。

紧密表载荷18,874,368B，加4B owned zero guard和344×4B palette，合计18,875,748B。原uint16表及613色palette合计33,556,888B。这个差值仅比较两份表的载荷与palette；它不是一个已实现native模型的容量差，更不是进程峰值差。293原生模型实际常驻35,673,508B保持原值。

有限合同覆盖9/10位、四种模式和43种长度，共344例。真实16M表由生产向量打包/解码核过；另一个纯stdlib审计器独立使用逐位地址、4字节整数窗口、struct原ID与Counter，完整复核全部16M ID和RGB值。独立审计不导入NumPy或native模块。两条路径通过只说明离线表示正确，不能继承为新native的内存安全、跨平台或速度证明。

## 实际调用、成本与失败记录

唯一native调用是293/max41 prepare一次；native apply为0，正式性能调用为0。没有读取gold、照片或新拟合参数。历史质量资料仅绑定其冻结身份，重新核验本次实际使用的13项输入；已有217源质量谱系也纳入223源冻结。独立审计检查同一223源/13输入及全部有限与真实表。

普查同时保留原生32MiB表、32MiB导出副本、32MiB重编号ID数组、约18MiB紧密表及Python/频数/分块暂态。若未来native需先生成宽表再压缩，prepare时间与峰值必须实测；不能把离线表当作免费预处理。

首次V1冻结在查找293构建目录中的四个GCC依赖副本时触发FileNotFoundError；尚未创建V1输出目录，未进入有限合同、prepare或apply。失败原脚本/计划与基于实际工具输出的STOP记录保留。机械V2只将依赖身份目录改为实际E:/mingw64/bin，并使用独立V2输出与自身份；没有修改已执行V1源码。V2冻结SHA为`ba77cb94813346b1906f696c30637933be7b62d738221331d725af34142268d4`，结果SHA为`728165235480fb336ef39ec4ce6ffb801c33d59a3c19676c62aa063ba249dc7e`。

旧289固定10位实现有有效低于50%的速度负例，仍然拒绝。本次9位可表示性不恢复它的资格。新实现若继续，须先固定一版native算法，再分别完成guard/完整域/百图、三分母冷热速度与fresh无图RSS；任意有效速度低于50%依旧拒绝。

## 原件与复核

计划为`experiments/p16-direct-active-packed-plan-v1.md`，机械说明为`p16-direct-active-packed-mechanical-v2.md`；V1/V2脚本和独立审计均保留原字节。`artifacts/p16-direct-active-packed-v2`保留冻结、有限、结果、四份实际二进制表及独立核。发布归档仅封存这些已产生证据，不调用模型或计时；ZIP按CRC与每成员SHA回读，Git index/HEAD按实际对象核原字节。

实际环境为Windows11 x64、Ryzen9 8945HX、Python3.12.14、NumPy1.26.4、psutil5.9；native生产物仍为原GCC15.2编译的293 DLL，SHA `f70f0e6ac98c753c15496e23fe1c2684dec04b6c0cdec47539d83e6df67c51a5`，本阶段未重新编译。普查在NumPy/native导入前设置0x55进程允许集、OMP4/THREAD_LIMIT4/DYNAMIC FALSE/PASSIVE和BLAS1，不是逐线程绑定或锁频。纯stdlib独立审计不需要native后端。

复现应使用全新输出目录和冻结原输入：依次运行`python scripts/census_direct_active_packed_v2.py freeze`、`python scripts/census_direct_active_packed_v2.py run`和`python scripts/audit_direct_active_packed.py`。已有结果目录不可覆盖；复核已交付原件可运行`python scripts/audit_p16_direct_active_packed_git.py head`，其目的仅为Git/ZIP数据完整性，不重新普查、prepare或计时。具体入口参数与单版源一同封存，不能在已有正式目录补采。
