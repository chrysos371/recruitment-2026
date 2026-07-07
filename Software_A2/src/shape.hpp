/**
 * @file    shape.hpp
 * @brief   Shape 图形类体系 — 头文件
 * @author  张杨亦航 (2524030231)
 * @date    2026-07-07
 *
 * 河海大学智泽实验室 2026 招新考核 — Software_A2
 *
 * 类层次:
 *   Shape (抽象基类, 含纯虚函数)
 *   ├── Circle    (圆形)
 *   ├── Rectangle (矩形)
 *   └── Triangle  (三角形)
 *
 * 设计要点:
 *   - Shape 为抽象基类, 至少包含一个纯虚函数 (area / perimeter / name)
 *   - 派生类各自实现面积与周长计算
 *   - 通过基类指针/引用展现动态绑定 (多态)
 *   - 使用 const 成员函数保证接口安全性
 */

#ifndef SHAPE_HPP
#define SHAPE_HPP

#include <cmath>
#include <string>
#include <iostream>
#include <numbers>    // C++20 std::numbers::pi
#include <stdexcept>

// ===================================================================
//  Shape — 抽象基类
// ===================================================================
class Shape {
public:
    virtual ~Shape() = default;

    /// @brief 计算面积
    virtual double area() const = 0;

    /// @brief 计算周长
    virtual double perimeter() const = 0;

    /// @brief 返回形状名称
    virtual std::string name() const = 0;

    /// @brief 非虚接口: 统一打印形状信息 (模板方法模式)
    void print_info() const {
        std::cout << "[" << name() << "]\n"
                  << "  面积 (area)      = " << area() << '\n'
                  << "  周长 (perimeter)  = " << perimeter() << '\n';
    }
};

// ===================================================================
//  Circle — 圆形
// ===================================================================
class Circle : public Shape {
public:
    /// @brief 构造函数
    /// @param radius 半径 (必须 > 0)
    explicit Circle(double radius);

    double area()      const override;
    double perimeter() const override;
    std::string name() const override { return "Circle"; }

    double radius() const { return r_; }

private:
    double r_;
};

// ===================================================================
//  Rectangle — 矩形
// ===================================================================
class Rectangle : public Shape {
public:
    /// @brief 构造函数
    /// @param width  宽度 (必须 > 0)
    /// @param height 高度 (必须 > 0)
    Rectangle(double width, double height);

    double area()      const override;
    double perimeter() const override;
    std::string name() const override { return "Rectangle"; }

    double width()  const { return w_; }
    double height() const { return h_; }

private:
    double w_, h_;
};

// ===================================================================
//  Triangle — 三角形 (海伦公式)
// ===================================================================
class Triangle : public Shape {
public:
    /// @brief 构造函数
    /// @param a 边长 a (必须 > 0, 且满足三角不等式)
    /// @param b 边长 b
    /// @param c 边长 c
    Triangle(double a, double b, double c);

    double area()      const override;
    double perimeter() const override;
    std::string name() const override { return "Triangle"; }

    double side_a() const { return a_; }
    double side_b() const { return b_; }
    double side_c() const { return c_; }

private:
    double a_, b_, c_;
};

#endif // SHAPE_HPP
