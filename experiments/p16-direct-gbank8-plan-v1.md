# 当前宽palette模型的输入G分bank、完整8bit ID：静态单版普查

Agent：`/root`；Operator：16题用户；Status：仅静态，99正式性能窗口内不执行普查、AST、构建或hash统计。属于精度分支的精确运行时，不合并内存分支。

## 动机与与历史方案的区别

全局palette603/703/604阻断旧8bit直接表。287/288的32MiB u16、289的packed10及291的热点miss回算已有速度失败/不完整资格。完整RGB24表是另一条独立备选，本提案不能根据其未来成绩改参数。

固定选择输入G的完整8bit值作256个bank，每bank保留完整8bit ID，输入表仍16MiB，不压7bit或跨字节解码。bank palette固定256×256×4=262144B。输入码R|(G<<8)|(B<<16)中`code&0xff00`直接给palette bank基址，最终palette索引为`(code&0xff00)|id`；不需要由B再移位。这个地址表达的简单性是预先选择G的原因，不是性能结论。原内存分支512个RGB空间bank的7bit方案不等价本方案，且其有效低50%结果保持。

仅测试这一个G256划分，不扫描R/B或bank数量。如果任一必需宽模型的任一bank超过256种真实输出RGB，停止该模型的本版实施，保存超界bank/颜色见证，不能事后改分区并称原门通过。三个宽模型可以各自有明确通过/失败；不能删除失败模型后称三个全过。

## 先做纯模型可表示性普查

对象固定max_first、p99_first、max48及新max41首解，综合best234色只作未来旧8bit优先控制。max41在任何本普查数值执行前加入，不根据bank结果选入。消费已冻结模型和288纯模型直接表解码，不读gold、照片、训练权重或oracleRGB来选bank/ID。全部16777216输入的输出RGB来自原整数首级与suffix缓存；按G=0..255汇总256个不同色集合，严格RGB升序为ID，255为普通有效ID，没有sentinel。检查每个bank实际最大ID和全部映射回放，保存完整逐bank色数/摘要与最大bank见证。

普查本身不构建新生产DLL，不拟合或跑性能，不能用其精确回放冒充native质量。先冻结新协议、脚本、旧DLL与模型/已有physical表SHA，唯一执行；首次身份或回放错误STOP、不覆盖重采。

## 通过后的实现门另批

若单个模型256bank全≤256，才另冻结实现。常驻应包括完整16777216B ID数组与显式4B guard、固定262144B palette、固定uint16[256]长度表512B、实际Model诊断和旧fallback，不能只报16MiB。bank填满256项，未用palette项0；合法ID255必须独立覆盖。实际值与原四级变换完全相同，guard不放宽外部RGB读写。

后续pure-model prepare可按固定G bank分别枚举R/B的65536输入，最多4worker，每个worker只用本bankRGB临时数组；不得先建64MiB RGB32常驻中转后隐去峰。每bank按固定升序去重并填固定palette，再将ID写到Rfast物理表的唯一G位置；不同G线程不写同一字节，但并行存储/false sharing代价仍需实测。旧≤255全局palette保持旧路径优先，宽模型启用只靠完整证明。

pixel核复用87/288实际ILP、BMI/ANDN与stream框架，增加bank基址合并并移除u16解码，不引入AVX512或跨noinline的256bit返回。可能因262KiB palette工作集或额外地址依赖失败，未实现前不宣称改善。

完整native/16M/实际whole4T/100逐图、有限和NOACCESS合同须另立冻结阶段；再另冻结正式速度。主分母固定87a399、87综合best及本版wrapper综合best，不能用较慢288或291救线。四fresh、AA、所有原轮与输出SHA、100/90/80/70/60/50各门保持；任一有效必需场景<50拒绝，AA无效不授档。所有投影、真实容量、prepare峰、RSS、cold/hot均分列。

本分bank构造包含256次排序，故尤其不能只测hot。正式协议必须包含create→首个完整100图Out4的两阶段各5个新句柄、镜像角色顺序及相同AA，三个主分母全过50%才授该端到端资格。独立prepare耗时披露，OS文件cache暖而非磁盘冷；稳态门和创建起的整批门分别报告，前者不替代后者。
