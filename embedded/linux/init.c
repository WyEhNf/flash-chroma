/* Linux 客户机的 PID 1；无需 shell、磁盘或网络即可运行共用契约。 */
#include <stdio.h>
#include <string.h>
#include <sys/reboot.h>
#include <sys/utsname.h>
#include <unistd.h>

int jshc_embedded_contract(void (*checkpoint)(void));
int main(void)
{
    struct utsname os;
    int result = 1;
    setbuf(stdout, NULL);
    if (getpid() == 1 && uname(&os) == 0 && strcmp(os.machine, "aarch64") == 0) {
        printf("客户机：%s %s，架构=%s，PID=1\n", os.sysname, os.release, os.machine);
        result = jshc_embedded_contract(NULL);
        printf("失败行=%d\n", result);
    }
    puts(result ? "FAIL: Linux Cortex-A53 LUT contract" : "PASS: Linux Cortex-A53 LUT contract");
    reboot(RB_POWER_OFF);
    return 1;
}
