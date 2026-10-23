# 固定86节点的52项同方向组探针

Agent：`/root/tail`。Operator：本任务用户。状态：52项质量与独立审计完成，全部严格max49失败；按协议停止，不追加轮、不切默认。

原116个max50输入的gold全部是黑色，逐点节点分量±2放松盒下界均为22；单节点和一次八色贪心仍未降max。因此，本阶段另冻结一种跨整数平台的组探针：从原`max_first`（0ea0首级、904e/95cb/5b8后缀、143e完整流）出发，对固定86个物理节点同时施加相同RGB方向，26方向×步长1、2，共52项。每项都相对原模型，不能叠加，也不借用八色失败模型的预算。

实现以每个节点`clip[0,255]`后的真实新值减原值作为delta，保留未选顶点的原始acc贡献，其变动权重为零。不能用假定每个节点都移动同样幅度的简式替代截断。每项在已认证的完整70,571行正支撑并集上重算，外部16,706,645行整数直方图固定；同时断言支撑外`hist[50]==0`。固定逐点cap仍为`max(49,原d²)`，原完整域/60图mean、RMS、p99及最差1% CVaR八项预算不放松。

所有52项均构造真实首级节点模型、执行完整并集fresh uint64前向，并与紧凑acc更新逐字节比较，不只核对winner。另一个独立审计用八角解析权重及uint64累加重新计算全部52×70,571=3,669,692行，并从原始全域流/60图整数频数重建支撑外直方图，复核每项完整直方图、固定cap、八预算和选型。全部零差。

结果没有任何一项将完整域max²降到49，**即使只看max、尚不考虑mean预算，也没有成功项**。11项仍为50，其余41项分别增加至57、66、68、75、77、108或110；因此不能把整组共同移动看作无代价的平台跨越。全部52项均未同时通过严格49和保护门槛，预注册要求停止，没有继续加轮或改方向。

一个具体边界是组方向(0,+1,0)：全域mean从0.7990738071534367降到0.7990548093016683，p99仍为3，max²仍50，产生41个违反固定逐点cap的新点，max50计数从116增至157。该方向虽然有轻微mean收益，仍没有改善用户要求的最坏误差，不能升级。

有限17/33模型合同覆盖多节点共享角、部分固定角、占位0屏蔽、0/255与1/254截断边界、训练零频数，并对全部52项逐项核独立uint64前向。环境为共享Windows x86-64与项目Python3.12/NumPy环境，质量执行不包含正式性能。新完整四级、原生后端、百图、RSS与吞吐均未验收；未知许可的原分输出坐标研究表示保持原状。

协议为`experiments/p16-cinema-first-group-v1.json`，实现为`scripts/{check,run,audit,archive}_cinema_first_group.py`，复用已验证的`channel_first_joint.py`紧凑变动设计。完整方向记录和所有失败保留在`artifacts/cinema-first-group-v1`；[阶段归档](../../report/data/p16-cinema-first-group-20261024)保存17项冻结源、原始方向/直方图、合同及独立审计共六份原件，各文件及ZIP成员SHA均核对。没有候选进入当前最优序列。

```powershell
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/check_cinema_first_group.py --output artifacts/cinema-first-group-contract-v1.json
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/run_cinema_first_group.py --contract artifacts/cinema-first-group-contract-v1.json --output artifacts/cinema-first-group-v1
& 'F:/Hackathon/projects/16-lut-color/artifacts/error-study-py312/Scripts/python.exe' scripts/audit_cinema_first_group.py --study artifacts/cinema-first-group-v1 --output artifacts/cinema-first-group-independent-v1.json
```

该负例只约束52项固定同方向整组移动，不证明86节点各自不同方向的联合整数问题无解，也不把逐点放松下界22当作可实现的联合方案。
