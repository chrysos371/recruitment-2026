# Software_A2 — Shape 图形类体系 (C++)

## 自我介绍

我是张杨亦航（学号 2524030231）。A1 练了运算符重载和封装，A2 练的是 C++ 面向对象最核心的特性——**多态 (polymorphism)**。抽象基类 + 虚函数 + 动态绑定这条链，是设计模式（策略、工厂、模板方法等）的基础。

编译环境同 A1：VS 2022 MSVC 14.44.35207，C++20 标准。

---

## 类层次设计

```
Shape (抽象基类)
├── 纯虚函数: area(), perimeter(), name()
├── 非虚接口: print_info()          ← 模板方法模式
│
├── Circle    — 面积: πr²,     周长: 2πr
├── Rectangle — 面积: w×h,     周长: 2(w+h)
└── Triangle  — 面积: 海伦公式, 周长: a+b+c
```

### 为什么这样设计

| 设计点 | 说明 |
|--------|------|
| **纯虚函数** | `area()` / `perimeter()` / `name()` 三个都是纯虚，确保派生类必须实现 |
| **虚析构函数** | `virtual ~Shape() = default`，通过基类指针 delete 对象时正确调用派生类析构 |
| **非虚接口 `print_info()`** | 模板方法模式——基类定义调用骨架，派生类只填充具体步骤 |
| **参数校验** | 构造时检查：半径/边长 > 0，三角形满足三角不等式 |

### 动态绑定原理

```
Shape* ptr = new Circle(5.0);
ptr->area();   // 运行时通过 vtable 查找到 Circle::area()
               // 编译期只知道 ptr 是 Shape*，不知道具体类型
```

虚函数表 (vtable) 是实现多态的关键——每个含虚函数的类有一张函数指针表，派生类覆盖的表项指向自己的实现。

---

## 使用方法

### 编译

```powershell
# VS 2022 MSVC
cl /EHsc /std:c++20 /utf-8 /Fe:shape_demo.exe shape.cpp main.cpp
```

### 运行

```
.\shape_demo.exe
```

### 代码使用示例

```cpp
// 多态: 基类指针统一管理不同类型
std::vector<std::unique_ptr<Shape>> shapes;
shapes.push_back(std::make_unique<Circle>(3.0));
shapes.push_back(std::make_unique<Rectangle>(5.0, 7.0));
shapes.push_back(std::make_unique<Triangle>(6.0, 8.0, 10.0));

for (const auto& s : shapes) {
    s->print_info();   // 运行时自动调用正确的派生类方法
}

// 按面积排序——多态的实际应用
std::sort(shapes.begin(), shapes.end(),
          [](const auto& a, const auto& b) { return a->area() < b->area(); });
```

---

## 文件结构

```
Software_A2/
├── src/
│   ├── shape.hpp     # 抽象基类 + 三个派生类声明
│   ├── shape.cpp     # 面积/周长实现
│   └── main.cpp      # 7 组演示测试
├── README.md         # 本文件
└── notes.md          # 学习过程与踩坑记录
```

---

## 技术要点

| 特性 | 实现 |
|------|------|
| 抽象基类 | 纯虚函数 `= 0`，不可直接实例化 |
| 虚析构 | `virtual ~Shape() = default` |
| 多态 | 基类指针/引用调用派生类虚函数 |
| 模板方法 | `print_info()` 非虚接口 |
| 内存管理 | `std::unique_ptr<Shape>` RAII |
| 海伦公式 | `s = (a+b+c)/2`, `area = √(s(s-a)(s-b)(s-c))` |
| 参数校验 | 负数边长 → `std::invalid_argument`，三角不等式检查 |
