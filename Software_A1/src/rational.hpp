/**
 * @file    rational.hpp
 * @brief   Rational 有理数类 — 头文件
 * @author  张杨亦航 (2524030231)
 * @date    2026-07-07
 *
 * 河海大学智泽实验室 2026 招新考核 — Software_A1
 *
 * 设计要点:
 *   - 使用 int64_t 作为内部存储类型, 乘法运算时中间值提升为 __int128 防溢出
 *   - 分母恒为正, 符号统一由分子携带
 *   - 构造时自动约分 (GCD 化简)
 *   - 运算符重载: +, -, *, /, ==, !=, <, >, <=, >=, <<
 *   - 构造函数重载体现封装性: 默认构造 / 单参数 / 双参数
 */

#ifndef RATIONAL_HPP
#define RATIONAL_HPP

#include <cstdint>
#include <compare>
#include <iostream>
#include <stdexcept>
#include <string>

class Rational {
public:
    // ======================== 构造函数 ========================
    /// @brief 默认构造, 值为 0/1
    Rational();

    /// @brief 从整数构造 (分母 = 1)
    /// @param n 整数值
    explicit Rational(std::int64_t n);

    /// @brief 从分子分母构造, 自动约分化简
    /// @param num 分子
    /// @param den 分母 (不能为 0)
    /// @throws std::invalid_argument 分母为零时抛出
    Rational(std::int64_t num, std::int64_t den);

    // ======================== 访问器 ========================
    /// @brief 获取分子 (已约分)
    std::int64_t numerator() const noexcept { return num_; }

    /// @brief 获取分母 (恒为正)
    std::int64_t denominator() const noexcept { return den_; }

    // ======================== 运算符重载 ========================
    // ---- 四则运算 ----
    Rational operator+(const Rational& rhs) const;
    Rational operator-(const Rational& rhs) const;
    Rational operator*(const Rational& rhs) const;
    Rational operator/(const Rational& rhs) const;

    // 复合赋值
    Rational& operator+=(const Rational& rhs);
    Rational& operator-=(const Rational& rhs);
    Rational& operator*=(const Rational& rhs);
    Rational& operator/=(const Rational& rhs);

    // ---- 比较运算符 (C++20 三路比较) ----
    std::strong_ordering operator<=>(const Rational& rhs) const;
    bool operator==(const Rational& rhs) const = default;

    // ---- 一元运算符 ----
    Rational operator+() const;   // 正号
    Rational operator-() const;   // 负号

    // ---- 类型转换 ----
    /// @brief 转换为 double (近似值, 便于打印和比较)
    explicit operator double() const;

    // ---- 流输出 ----
    friend std::ostream& operator<<(std::ostream& os, const Rational& r);

    // ======================== 工具方法 ========================
    /// @brief 判断是否为整数 (分母 == 1)
    bool is_integer() const noexcept { return den_ == 1; }

    /// @brief 计算最大公约数 (辗转相除法, 静态方法)
    static std::int64_t gcd(std::int64_t a, std::int64_t b);

private:
    /// @brief 约分化简 (同时确保分母为正)
    void simplify();

    std::int64_t num_;   // 分子
    std::int64_t den_;   // 分母 (恒为正)
};

#endif // RATIONAL_HPP
