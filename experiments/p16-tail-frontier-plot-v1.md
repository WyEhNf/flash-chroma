# 精度候选比较图：只消费已保存指标

Agent：`/root`。目的为解释既有精度权衡，不进行拟合、LUT调用、输出质量重测或性能采样。输入固定为四份已提交的精度JSON：current-full-quality的V2、max48-pareto、second-nodes的max_first及p99_first；按实际字段导出a399、373a、max_first、p99_first、max48、max41的全色域与百图mean/p99/max/CVaR。公共角色的重复值逐字段一致才画图，每份输入保存完整SHA。

使用当前Python 3.12环境中的Matplotlib Agg和Windows微软雅黑，固定画两张群体面板：横轴mean、纵轴max、颜色p99。每个标记附实际模型名及max平方；不以全域聚合图代替逐图代价或速度资格。数据另外写JSON与Markdown，图内明确100图均已见、RGB代理并非官方ΔE、max41仍无新速度资格。373a仅标注历史同场90%速度档，不能移用到其它模型或本次图导出。

运行前先写输入身份及绘图环境收据；唯一新输出目录，存在即拒绝覆盖，首错误STOP。运行后核输入SHA未变、固定6角色×2群体全部有限数及样本数量、p99≤max；完整绘制PNG和SVG后查看PNG确认文字无裁切。无native图像调用、无测速、无新精度结论。
