#include <stdio.h>
#ifdef JSHC_EMBEDDED_PORTABLE_PARITY
#include "jshc_portable.h"
#endif
int jshc_embedded_contract(void (*checkpoint)(void));
int main(void)
{
    const int result = jshc_embedded_contract(NULL);
    printf("嵌入式契约测试：%s，失败行=%d\n", result ? "FAILED" : "PASS", result);
#ifdef JSHC_EMBEDDED_PORTABLE_PARITY
    printf("portable 两条路径与独立参考对照；单模型对象=%zu，链对象=%zu 字节\n",
           jshc_p_model_bytes(), jshc_p_chain_bytes());
#endif
    return result ? 1 : 0;
}
