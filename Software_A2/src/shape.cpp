/**
 * @file    shape.cpp
 * @brief   Shape 图形类体系 — 实现文件
 * @author  张杨亦航 (2524030231)
 * @date    2026-07-07
 */

#include "shape.hpp"

// ===================================================================
//  Circle
// ===================================================================

Circle::Circle(double radius) : r_(radius) {
    if (radius <= 0.0) {
        throw std::invalid_argument(
            "Circle: 半径必须大于零 (radius must be positive)");
    }
}

double Circle::area() const {
    return std::numbers::pi * r_ * r_;
}

double Circle::perimeter() const {
    return 2.0 * std::numbers::pi * r_;
}

// ===================================================================
//  Rectangle
// ===================================================================

Rectangle::Rectangle(double width, double height) : w_(width), h_(height) {
    if (width <= 0.0 || height <= 0.0) {
        throw std::invalid_argument(
            "Rectangle: 宽和高必须大于零 (width and height must be positive)");
    }
}

double Rectangle::area() const {
    return w_ * h_;
}

double Rectangle::perimeter() const {
    return 2.0 * (w_ + h_);
}

// ===================================================================
//  Triangle (海伦公式)
// ===================================================================

Triangle::Triangle(double a, double b, double c) : a_(a), b_(b), c_(c) {
    if (a <= 0.0 || b <= 0.0 || c <= 0.0) {
        throw std::invalid_argument(
            "Triangle: 边长必须大于零 (sides must be positive)");
    }
    // 三角不等式: 任意两边之和大于第三边
    if (a + b <= c || a + c <= b || b + c <= a) {
        throw std::invalid_argument(
            "Triangle: 不满足三角不等式 (triangle inequality violated)");
    }
}

double Triangle::area() const {
    // 海伦公式: s = (a+b+c)/2,  area = sqrt(s * (s-a) * (s-b) * (s-c))
    double s = (a_ + b_ + c_) / 2.0;
    return std::sqrt(s * (s - a_) * (s - b_) * (s - c_));
}

double Triangle::perimeter() const {
    return a_ + b_ + c_;
}
