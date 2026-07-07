/**
 * @file    main.cpp
 * @brief   Rational 有理数类 — 功能演示与测试
 * @author  张杨亦航 (2524030231)
 * @date    2026-07-07
 *
 * 编译方法 (VS 2022 MSVC):
 *   cl /EHsc /std:c++20 /Fe:rational_demo.exe rational.cpp main.cpp
 *
 * 河海大学智泽实验室 2026 招新考核 — Software_A1
 */

#include "rational.hpp"
#include <iostream>
#include <iomanip>
#include <cassert>
#include <string>

// ===================================================================
//  辅助打印
// ===================================================================

void print_header(const std::string& title) {
    std::cout << "\n"
              << std::string(60, '=') << '\n'
              << "  " << title << '\n'
              << std::string(60, '=') << '\n';
}

template<typename T>
void check(const std::string& label, const T& actual, const T& expected) {
    bool ok = (actual == expected);
    std::cout << (ok ? "[PASS] " : "[FAIL] ")
              << std::left << std::setw(40) << label
              << "  got: " << actual
              << "  expected: " << expected << '\n';
    if (!ok) {
        std::cerr << "  *** TEST FAILED! ***\n";
    }
}

// 浮点数比较 (允许误差)
void check_double(const std::string& label, double actual, double expected, double eps = 1e-9) {
    bool ok = std::abs(actual - expected) < eps;
    std::cout << (ok ? "[PASS] " : "[FAIL] ")
              << std::left << std::setw(40) << label
              << "  got: " << actual
              << "  expected: " << expected << '\n';
}

// ===================================================================
//  main
// ===================================================================

int main() {
    // ================================================================
    //  1. 构造函数 & 封装性
    // ================================================================
    print_header("1. 构造函数演示");

    Rational r0;                      // 默认构造: 0/1
    Rational r1(3);                   // 整数构造: 3/1
    Rational r2(1, 2);               // 分数构造: 1/2
    Rational r3(-4, 8);              // 自动化简: -1/2
    Rational r4(6, -9);              // 分母为负 → 符号移分子: -2/3
    Rational r5(0, 5);               // 分子为 0 → 归一化: 0/1

    std::cout << "默认构造 r0        = " << r0 << '\n';
    std::cout << "整数构造 r1(3)     = " << r1 << '\n';
    std::cout << "分数构造 r2(1,2)   = " << r2 << '\n';
    std::cout << "自动化简 r3(-4,8)  = " << r3 << '\n';
    std::cout << "分母负号 r4(6,-9)  = " << r4 << '\n';
    std::cout << "分子为 0 r5(0,5)   = " << r5 << '\n';

    // 验证访问器
    check<std::int64_t>("r3 分子应为 -1", r3.numerator(), -1);
    check<std::int64_t>("r3 分母应为 2",  r3.denominator(), 2);
    check<std::int64_t>("r4 分子应为 -2", r4.numerator(), -2);
    check<std::int64_t>("r4 分母应为 3",  r4.denominator(), 3);

    // 验证整数判断
    check<std::string>("r1 应为整数", r1.is_integer() ? "true" : "false", "true");
    check<std::string>("r2 非整数",   r2.is_integer() ? "true" : "false", "false");

    // 验证分母恒为正
    check<std::int64_t>("r1 分母 = 1", r1.denominator(), 1);

    // ================================================================
    //  2. 四则运算
    // ================================================================
    print_header("2. 四则运算演示");

    Rational a(1, 2);
    Rational b(1, 3);

    std::cout << "a = " << a << ",  b = " << b << "\n\n";

    Rational sum = a + b;          // 1/2 + 1/3 = 5/6
    Rational diff = a - b;         // 1/2 - 1/3 = 1/6
    Rational prod = a * b;         // 1/2 * 1/3 = 1/6
    Rational quot = a / b;         // 1/2 ÷ 1/3 = 3/2

    std::cout << "a + b = " << sum  << "  (期望: 5/6)\n";
    std::cout << "a - b = " << diff << "  (期望: 1/6)\n";
    std::cout << "a * b = " << prod << "  (期望: 1/6)\n";
    std::cout << "a / b = " << quot << "  (期望: 3/2)\n";

    check<std::string>("a + b == 5/6",  (sum  == Rational(5, 6))  ? "true" : "false", "true");
    check<std::string>("a - b == 1/6",  (diff == Rational(1, 6))  ? "true" : "false", "true");
    check<std::string>("a * b == 1/6",  (prod == Rational(1, 6))  ? "true" : "false", "true");
    check<std::string>("a / b == 3/2",  (quot == Rational(3, 2))  ? "true" : "false", "true");

    // 复合赋值
    Rational c(3, 4);
    c += Rational(1, 4);
    std::cout << "\n3/4 += 1/4 → " << c << '\n';
    check<std::string>("c == 1", (c == Rational(1)) ? "true" : "false", "true");

    // 整数参与运算
    Rational d(2, 3);
    Rational e = d + Rational(1);    // 2/3 + 1 = 5/3
    std::cout << "2/3 + 1 = " << e << '\n';
    check<std::string>("2/3 + 1 == 5/3", (e == Rational(5, 3)) ? "true" : "false", "true");

    // ================================================================
    //  3. 比较运算符
    // ================================================================
    print_header("3. 比较运算符演示");

    Rational p(2, 3);
    Rational q(3, 4);   // 2/3 < 3/4 (8/12 < 9/12)

    std::cout << "p = " << p << " (= " << static_cast<double>(p) << ")\n";
    std::cout << "q = " << q << " (= " << static_cast<double>(q) << ")\n\n";

    std::cout << std::boolalpha;
    std::cout << "p <  q  → " << (p <  q) << "  (期望: true)\n";
    std::cout << "p >  q  → " << (p >  q) << "  (期望: false)\n";
    std::cout << "p <= q  → " << (p <= q) << "  (期望: true)\n";
    std::cout << "p >= q  → " << (p >= q) << "  (期望: false)\n";
    std::cout << "p == q  → " << (p == q) << "  (期望: false)\n";
    std::cout << "p != q  → " << (p != q) << "  (期望: true)\n";

    check<std::string>("p < q",  (p < q)  ? "true" : "false", "true");
    check<std::string>("p != q", (p != q) ? "true" : "false", "true");

    // ================================================================
    //  4. 类型转换
    // ================================================================
    print_header("4. double 类型转换");

    Rational f(1, 3);
    double dval = static_cast<double>(f);
    std::cout << "1/3 ≈ " << dval << '\n';
    check_double("static_cast<double>(1/3)", dval, 1.0 / 3.0);

    // ================================================================
    //  5. 异常处理 — 分母为零
    // ================================================================
    print_header("5. 异常处理 — 分母为零");

    bool caught = false;
    try {
        Rational bad(1, 0);  // 应抛出异常
        std::cout << "bad = " << bad << " (不应执行到这里)\n";
    } catch (const std::invalid_argument& e) {
        caught = true;
        std::cout << "捕获异常: " << e.what() << '\n';
    }
    check<std::string>("分母为 0 应抛出异常", caught ? "true" : "false", "true");

    // 除零异常
    caught = false;
    try {
        Rational x(1, 2);
        Rational y(0, 1);
        Rational z = x / y;  // 应抛出异常
        std::cout << "z = " << z << " (不应执行到这里)\n";
    } catch (const std::invalid_argument& e) {
        caught = true;
        std::cout << "捕获异常: " << e.what() << '\n';
    }
    check<std::string>("除以 0 应抛出异常", caught ? "true" : "false", "true");

    // ================================================================
    //  6. 边界 & 大数运算
    // ================================================================
    print_header("6. 边界与大数运算");

    // 大数运算
    Rational big1(123456789, 987654321);
    Rational big2(987654321, 123456789);
    std::cout << "big1 = " << big1 << '\n';
    std::cout << "big2 = " << big2 << '\n';
    std::cout << "big1 * big2 = " << (big1 * big2) << " (= 1, 分子分母互逆相乘后约分)\n";

    // 负数运算
    Rational neg1(-1, 3);
    Rational neg2(1, -3);
    std::cout << "\n-1/3 = " << neg1 << "   1/(-3) = " << neg2 << "  (两者相等)\n";
    check<std::string>("-1/3 == 1/(-3)", (neg1 == neg2) ? "true" : "false", "true");

    std::cout << "+a = " << +neg1 << '\n';
    std::cout << "-a = " << -neg1 << '\n';

    // ================================================================
    //  7. GCD 静态方法
    // ================================================================
    print_header("7. GCD 静态方法");

    check<std::int64_t>("gcd(12, 18)", Rational::gcd(12, 18), 6);
    check<std::int64_t>("gcd(7, 13)",  Rational::gcd(7, 13),  1);
    check<std::int64_t>("gcd(-8, 12)", Rational::gcd(-8, 12), 4);
    check<std::int64_t>("gcd(0, 5)",   Rational::gcd(0, 5),   5);

    // ================================================================
    //  结果
    // ================================================================
    print_header("全部测试完成");
    std::cout << "\nRational 有理数类功能验证完毕。\n"
              << "所有构造函数、运算符重载、异常处理均已覆盖。\n";

    return 0;
}
