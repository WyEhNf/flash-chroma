# 独立OpenMP逐TID控制可行性：只用于后续基准方法

旧0x55只限制进程可用CPU，不保证每个OpenMP线程固定。已静态核实本机GCC15.2的libgomp-1.dll导入GetProcessAffinityMask，而gomp_init_affinity/gomp_init_thread_affinity入口均仅ret。不能靠GOMP_CPU_AFFINITY环境字符串声称已绑核。本实验不追溯改变任何旧有效失败或A/A失效的结论，也不混入已冻结95/C7BK性能。

独立Windows helper与现有DLL动态链接同一libgomp，在4线程team中按omp_tid把各自OS线程固定至0/2/4/6，记录GetCurrentThreadId、GetThreadGroupAffinity前后Mask/Group、SetThreadAffinityMask返回旧Mask及CPU端点。只影响该新测试进程；拒绝非单组或进程Mask不为0x55的环境。保留restore并要求同一omp_tid/OS TID，防止恢复错线程。不修改原模型/运行时或旧DLL。

当前只有静态源，不构建/调用。质量阶段需先冻结helper/driver/本协议和实际GCC/libgomp身份，在独立进程核加载libgomp唯一实例/路径/SHA。先snapshot，再pin，调用冻结87/94构造和实际四线程apply后再次snapshot；同team的OS TID及每线程单核Mask必须始终一致，输出仍对既有oracle零差，再restore核原Mask。失败保留，无速度或频率因果结论。4线程pool预热及绑定有真实成本；未来若用于cold生命周期，必须计入端到端边界或明确它是实验环境设置，不能把成本隐藏在已有库初始化前。

Microsoft原文：[SetThreadAffinityMask](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadaffinitymask)返回先前Mask、0为失败且需属于进程Mask；[GetThreadGroupAffinity](https://learn.microsoft.com/en-us/windows/win32/api/processtopologyapi/nf-processtopologyapi-getthreadgroupaffinity)获取真实线程组/Mask。GCC源码[configure.tgt](https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-15.2.0/libgomp/configure.tgt)和通用[affinity.c](https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-15.2.0/libgomp/affinity.c)仅作源码背景；当前DLL实物证据与源码推断分开。此helper不保证改善速度、A/A或目标Intel表现，不是生产接口/移植完成。
