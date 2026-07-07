/**
 * @file    rational.cpp
 * @brief   Rational 有理数类 — 实现文件
 * @author  张杨亦航 (2524030231)
 * @date    2026-07-07
 */

#include "rational.hpp"
#include <cstdlib>   // std::abs
#include <numeric>   // std::gcd (C++17 后备)
#include <sstream>

// ===================================================================
//  构造函数
// ===================================================================

Rational::Rational() : num_(0), den_(1) {}

Rational::Rational(std::int64_t n) : num_(n), den_(1) {
    // 整数不需要约分
}

Rational::Rational(std::int64_t num, std::int64_t den) : num_(num), den_(den) {
    if (den == 0) {
        throw std::invalid_argument(
            "Rational: 分母不能为零 (denominator cannot be zero)");
    }
    simplify();
}

// ===================================================================
//  GCD — 辗转相除法 (Euclidean algorithm)
// ===================================================================

std::int64_t Rational::gcd(std::int64_t a, std::int64_t b) {
    // 处理负数: 取绝对值
    a = std::abs(a);
    b = std::abs(b);
    while (b != 0) {
        std::int64_t t = b;
        b = a % b;
        a = t;
    }
    return a;
}

// ===================================================================
//  约分化简
// ===================================================================

void Rational::simplify() {
    // 分母必须为正, 符号移到分子
    if (den_ < 0) {
        num_ = -num_;
        den_ = -den_;
    }

    // 分子为 0 时, 分母归一化为 1
    if (num_ == 0) {
        den_ = 1;
        return;
    }

    std::int64_t g = gcd(num_, den_);
    num_ /= g;
    den_ /= g;
}

// ===================================================================
//  四则运算
//
//  溢出分析: 两个 int64_t 相乘的结果可能超出 int64_t 范围。
//  GCC/Clang 下可用 __int128 做中间类型防止溢出;
//  MSVC 不支持 __int128, 但本题为教学演示级别, 常规分数运算
//  (分子分母均在 ±10⁹ 范围内) 的中间值远未触及 int64_t 上限。
//  生产环境建议换用 Boost.Multiprecision::cpp_int。
// ===================================================================

Rational Rational::operator+(const Rational& rhs) const {
    // a/b + c/d = (a*d + c*b) / (b*d)
    std::int64_t new_num = num_ * rhs.den_ + rhs.num_ * den_;
    std::int64_t new_den = den_ * rhs.den_;
    return Rational(new_num, new_den);  // 构造时自动约分
}

Rational Rational::operator-(const Rational& rhs) const {
    // a/b - c/d = (a*d - c*b) / (b*d)
    std::int64_t new_num = num_ * rhs.den_ - rhs.num_ * den_;
    std::int64_t new_den = den_ * rhs.den_;
    return Rational(new_num, new_den);
}

Rational Rational::operator*(const Rational& rhs) const {
    // a/b * c/d = (a*c) / (b*d)
    std::int64_t new_num = num_ * rhs.num_;
    std::int64_t new_den = den_ * rhs.den_;
    return Rational(new_num, new_den);
}

Rational Rational::operator/(const Rational& rhs) const {
    // a/b / c/d = (a*d) / (b*c)
    if (rhs.num_ == 0) {
        throw std::invalid_argument("Rational: 不能除以零 (division by zero)");
    }
    std::int64_t new_num = num_ * rhs.den_;
    std::int64_t new_den = den_ * rhs.num_;
    return Rational(new_num, new_den);
}

// ---- 复合赋值 ----

Rational& Rational::operator+=(const Rational& rhs) {
    *this = *this + rhs;
    return *this;
}

Rational& Rational::operator-=(const Rational& rhs) {
    *this = *this - rhs;
    return *this;
}

Rational& Rational::operator*=(const Rational& rhs) {
    *this = *this * rhs;
    return *this;
}

Rational& Rational::operator/=(const Rational& rhs) {
    *this = *this / rhs;
    return *this;
}

// ===================================================================
//  比较运算符
// ===================================================================

std::strong_ordering Rational::operator<=>(const Rational& rhs) const {
    // a/b <=> c/d  等价于  a*d <=> c*b  (b, d 均为正)
    std::int64_t lhs_cross = num_ * rhs.den_;
    std::int64_t rhs_cross = rhs.num_ * den_;
    return lhs_cross <=> rhs_cross;
}

// ===================================================================
//  一元运算符
// ===================================================================

Rational Rational::operator+() const {
    return *this;
}

Rational Rational::operator-() const {
    return Rational(-num_, den_);
}

// ===================================================================
//  类型转换
// ===================================================================

Rational::operator double() const {
    return static_cast<double>(num_) / static_cast<double>(den_);
}

// ===================================================================
//  流输出
// ===================================================================

std::ostream& operator<<(std::ostream& os, const Rational& r) {
    if (r.den_ == 1) {
        // 整数: 直接输出分子
        os << r.num_;
    } else {
        // 分数: "分子/分母"
        os << r.num_ << '/' << r.den_;
    }
    return os;
}
