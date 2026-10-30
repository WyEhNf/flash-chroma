/* 默认目标与CPU/OS门控合同：模拟特性组合不冒充旧CPU实机测试。
 * 本文件不设置部署或指令集宏；官方-O2/-std=c++17参数即可编译。
 */
#ifndef FC_TEST_FRAMEWORK_HPP
#define FC_TEST_FRAMEWORK_HPP "flash_chroma.hpp"
#endif
#define FLASH_CHROMA_IMPLEMENTATION
#include FC_TEST_FRAMEWORK_HPP

#define CHECK(value) do { if (!(value)) return __LINE__; } while (false)

int main() {
    constexpr unsigned required = (1u << 26) | (1u << 27) | (1u << 28);
    // 独立列举六项必要条件，覆盖64种组合及每种组合的无关位噪声。
    for (unsigned combination = 0; combination < 64; ++combination) {
        unsigned leaf1 = 0, xcr0 = 0, leaf7 = 0;
        if (combination & 1) leaf1 |= 1u << 26;
        if (combination & 2) leaf1 |= 1u << 27;
        if (combination & 4) leaf1 |= 1u << 28;
        if (combination & 8) xcr0 |= 2;
        if (combination & 16) xcr0 |= 4;
        if (combination & 32) leaf7 |= 1u << 5;
        const bool expected = combination == 63;
        CHECK(fc::detail::avx2_state_supported(leaf1, xcr0, leaf7) == expected);
        CHECK(fc::detail::avx2_state_supported(leaf1 | ~required, xcr0 | ~6u, leaf7 | ~(1u << 5)) == expected);
    }
    static_assert(!fc::detail::avx2_state_supported(required, 2, 1u << 5), "OS未启YMM不能使用AVX2");
    static_assert(!fc::detail::avx2_state_supported(required, 4, 1u << 5), "OS未启XMM不能使用AVX2");
    static_assert(!fc::detail::avx2_state_supported(required, 6, 0), "有AVX但无AVX2的旧CPU必须回退");
    static_assert(!fc::detail::avx2_state_supported(required & ~(1u << 26), 6, 1u << 5), "XSAVE缺失不能执行xgetbv门控路径");

    fc::RuntimeConfig config;
#if defined(__STDC_HOSTED__) && __STDC_HOSTED__ == 0
    CHECK(fc::is_embedded() && config.target == fc::Target::Embedded);
#elif defined(__ANDROID__)
    CHECK(!fc::is_embedded() && config.target == fc::Target::Mobile);
#else
    CHECK(!fc::is_embedded() && config.target == fc::Target::Desktop);
#endif
    CHECK(config.backend == fc::Backend::Auto && config.threads == 1);
    CHECK((fc::available_backends() & ~fc::compiled_capabilities()) == 0);

    // 独立读取本机寄存器，实际执行xgetbv前也先保护三项必要条件。
    // 这里验证当前机器的真实分派；老CPU/禁YMM场景由上方纯函数组合验证。
    bool native_avx2 = false;
#if FLASH_CHROMA_ENABLE_AVX2
    unsigned a = 0, b = 0, c = 0, d = 0;
    if (__get_cpuid(1, &a, &b, &c, &d) && (c & required) == required) {
        unsigned low = 0, high = 0;
        __asm__ volatile("xgetbv" : "=a"(low), "=d"(high) : "c"(0));
        if ((low & 6u) == 6u && __get_cpuid_count(7, 0, &a, &b, &c, &d)) native_avx2 = (b & (1u << 5)) != 0;
    }
#endif
    CHECK(bool(fc::available_backends() & 2u) == native_avx2);
    fc::Backend selected = fc::Backend::Auto;
    CHECK(fc::detail::resolve(config, &selected) == fc::Status::Ok);
    CHECK(selected == (native_avx2 ? fc::Backend::Avx2 : fc::Backend::Scalar));
    config.backend = fc::Backend::Scalar;
    CHECK(fc::detail::resolve(config, &selected) == fc::Status::Ok && selected == fc::Backend::Scalar);
    config.backend = fc::Backend::Avx2;
    CHECK(fc::detail::resolve(config, &selected) == (native_avx2 ? fc::Status::Ok : fc::Status::Unsupported));
    return 0;
}
