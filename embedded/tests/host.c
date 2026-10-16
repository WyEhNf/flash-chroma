#include <stdio.h>
int jshc_embedded_contract(void (*checkpoint)(void));
int main(void)
{
    const int result = jshc_embedded_contract(NULL);
    printf("嵌入式契约测试：%s，失败行=%d\n", result ? "FAILED" : "PASS", result);
    return result ? 1 : 0;
}
