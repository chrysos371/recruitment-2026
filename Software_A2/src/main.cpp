/**
 * @file    main.cpp
 * @brief   Shape 图形类体系 — 多态演示与测试
 * @author  张杨亦航 (2524030231)
 * @date    2026-07-07
 *
 * 编译方法 (VS 2022 MSVC):
 *   cl /EHsc /std:c++20 /utf-8 /Fe:shape_demo.exe shape.cpp main.cpp
 *
 * 河海大学智泽实验室 2026 招新考核 — Software_A2
 */

#include "shape.hpp"
#include <algorithm>
#include <iostream>
#include <iomanip>
#include <vector>
#include <memory>
#include <string>
#include <cmath>

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
}

// 浮点数比较
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
    //  1. 各派生类基本功能
    // ================================================================
    print_header("1. 各派生类面积 & 周长验证");

    Circle    c(5.0);                  // 半径 5
    Rectangle r(4.0, 6.0);            // 宽 4, 高 6
    Triangle  t(3.0, 4.0, 5.0);      // 3-4-5 直角三角形

    // circle: area = π*25 ≈ 78.5398, perimeter = 10π ≈ 31.4159
    check_double("Circle area (r=5)",      c.area(),      25.0 * std::numbers::pi);
    check_double("Circle perimeter (r=5)", c.perimeter(), 10.0 * std::numbers::pi);

    // rectangle: area = 24, perimeter = 20
    check_double("Rectangle area (4x6)",   r.area(),      24.0);
    check_double("Rectangle perimeter",    r.perimeter(), 20.0);

    // triangle 3-4-5: area = 6, perimeter = 12
    check_double("Triangle area (3-4-5)",  t.area(),      6.0);
    check_double("Triangle perimeter",     t.perimeter(), 12.0);

    // ================================================================
    //  2. 多态 — 动态绑定演示
    // ================================================================
    print_header("2. 多态 — 基类指针动态绑定");

    // 用基类指针数组管理不同派生类对象
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Circle>(3.0));
    shapes.push_back(std::make_unique<Rectangle>(5.0, 7.0));
    shapes.push_back(std::make_unique<Triangle>(6.0, 8.0, 10.0));

    std::cout << "通过基类指针调用虚函数 (运行时多态):\n\n";

    for (const auto& s : shapes) {
        std::cout << "  Shape* → " << s->name() << '\n';
        std::cout << "    面积:     " << s->area() << '\n';
        std::cout << "    周长:     " << s->perimeter() << "\n\n";
    }

    // 验证运行时类型正确
    check_double("Circle(3.0) area",     shapes[0]->area(), 9.0 * std::numbers::pi);
    check_double("Rectangle(5x7) area",  shapes[1]->area(), 35.0);
    // 6-8-10 三角形: s=12, area=√(12*6*4*2)=√576=24
    check_double("Triangle(6-8-10) area", shapes[2]->area(), 24.0);

    // ================================================================
    //  3. 模板方法模式 — print_info()
    // ================================================================
    print_header("3. 非虚接口 print_info() — 模板方法模式");

    std::cout << "基类 Shape::print_info() 内部调用虚函数 area()/perimeter()/name():\n\n";

    for (const auto& s : shapes) {
        s->print_info();
        std::cout << '\n';
    }

    // ================================================================
    //  4. 引用也能多态
    // ================================================================
    print_header("4. 基类引用同样支持多态");

    auto print_area = [](const Shape& s) {
        std::cout << s.name() << " 的面积 = " << s.area() << '\n';
    };

    Circle    c2(2.5);
    Rectangle r2(3.0, 4.0);
    Triangle  t2(5.0, 5.0, 6.0);  // 等腰三角形

    print_area(c2);
    print_area(r2);
    print_area(t2);

    // ================================================================
    //  5. 三角形特别测试
    // ================================================================
    print_header("5. 三角形专项测试");

    // 等边三角形: 边长 2, s=3, area=√(3*1*1*1)=√3≈1.73205
    Triangle equilateral(2.0, 2.0, 2.0);
    check_double("等边三角形(2,2,2) area", equilateral.area(), std::sqrt(3.0));
    check_double("等边三角形(2,2,2) peri", equilateral.perimeter(), 6.0);

    // 非法三角形: 三角不等式不成立
    bool caught = false;
    try {
        Triangle bad(1.0, 2.0, 5.0);
    } catch (const std::invalid_argument& e) {
        caught = true;
        std::cout << "1-2-5 三角形异常: " << e.what() << '\n';
    }
    check<std::string>("1-2-5 应抛异常", caught ? "true" : "false", "true");

    // 非法半径
    caught = false;
    try {
        Circle bad(-1.0);
    } catch (const std::invalid_argument& e) {
        caught = true;
        std::cout << "负半径异常: " << e.what() << '\n';
    }
    check<std::string>("负半径应抛异常", caught ? "true" : "false", "true");

    // ================================================================
    //  6. 面积排序 — 多态的实际应用
    // ================================================================
    print_header("6. 多态应用 — 按面积排序");

    std::vector<std::unique_ptr<Shape>> sorted;
    sorted.push_back(std::make_unique<Circle>(1.0));           // π ≈ 3.14
    sorted.push_back(std::make_unique<Triangle>(3.0, 4.0, 5.0)); // 6
    sorted.push_back(std::make_unique<Rectangle>(2.0, 3.0));   // 6
    sorted.push_back(std::make_unique<Circle>(2.0));           // 4π ≈ 12.57

    std::sort(sorted.begin(), sorted.end(),
              [](const auto& a, const auto& b) {
                  return a->area() < b->area();
              });

    std::cout << "按面积升序:\n";
    for (const auto& s : sorted) {
        std::cout << "  " << s->name() << ": area = " << s->area() << '\n';
    }

    // ================================================================
    //  7. Shape 不可直接实例化
    // ================================================================
    print_header("7. 抽象基类不可实例化");

    std::cout << "Shape 是抽象类 (含纯虚函数), 无法直接创建对象.\n";
    std::cout << "编译器会阻止: Shape s; // error: cannot declare variable 's'\n";

    // ================================================================
    //  结果
    // ================================================================
    print_header("全部测试完成");
    std::cout << "\nShape 图形类体系功能验证完毕。\n"
              << "覆盖: Circle / Rectangle / Triangle 的面积周长计算、\n"
              << "      多态动态绑定、基类非虚接口、异常处理、排序应用。\n";

    return 0;
}
