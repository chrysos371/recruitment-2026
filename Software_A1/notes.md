# 学习过程与踩坑记录 — Rational 有理数类

## 学习过程

### 阶段一：回顾 C++ 面向对象

写完 C++ 基础之后有段时间没碰了，这次重新过了以下知识点：

- [W3Schools C++ OOP 教程](https://www.w3schools.com/cpp/cpp_oop.asp)（题目推荐）
- 类的封装原则：数据成员 private，通过 public 接口访问
- 构造函数重载：默认构造、参数化构造、拷贝构造（本题没用显式拷贝，编译器默认生成够用）
- 运算符重载：成员函数 vs 友元函数的区别——`+` `-` `*` `/` 用成员函数（左操作数是 `*this`），`<<` 用友元（左操作数是 `ostream`）
- C++20 新特性：`<=>` 三路比较运算符，编译器自动生成其他比较运算符

### 阶段二：设计 Rational 类

核心设计决策：

1. **内部表示**：`int64_t num_, den_`，分母恒为正
2. **自动约分**：每次构造时调用 `gcd()` + `simplify()`
3. **防溢出**：使用 `int64_t`（相比普通 `int` 多一倍的取值范围），理想情况下用 `__int128` 做乘法中间值
4. **异常处理**：分母/除数为零时抛 `std::invalid_argument`

**为什么分母恒为正**：假设用户构造 `Rational(6, -9)`，如果不做规范化，输出 `6/-9` 可读性差。同时比较大小时的交叉乘法需要符号一致性——分母为正后，`a/b <=> c/d` 等价于 `a*d <=> c*b`。

### 阶段三：编译与测试

编译器环境：**VS 2022 MSVC 14.44.35207**，安装在 `D:\新建文件夹\`。

运行方式——由于 VS 不在标准路径 + 中文路径导致 vcvars64.bat 无法正常运行，手动设置了 INCLUDE / LIB / PATH 环境变量：

```powershell
$msvc = "D:\新建文件夹\VC\Tools\MSVC\14.44.35207"
$sdk = "D:\Windows Kits\10"
$sdkVer = "10.0.26100.0"
$env:INCLUDE = "$msvc\include;...;$sdk\Include\$sdkVer\ucrt;..."
$env:LIB = "$msvc\lib\x64;...;$sdk\Lib\$sdkVer\ucrt\x64;..."
$env:PATH = "$msvc\bin\Hostx64\x64;$env:PATH"
```

编译命令：
```
cl /EHsc /std:c++20 /utf-8 /Fe:rational_demo.exe rational.cpp main.cpp
```

main.cpp 中编写了 7 组测试用例，覆盖构造、四则运算、比较、类型转换、异常处理、边界大数、GCD 静态方法。

---

## 踩坑记录

### 坑 1：MSVC 不认 UTF-8 源文件中的中文

**现象**：
```
warning C4819: 该文件包含不能在当前代码页(936)中表示的字符
error C2511: "Rational::Rational(int64_t)":"Rational"中没有找到重载的成员函数
error C2001: 常量中有换行符
```

一堆语法错误看起来跟代码逻辑完全无关。

**原因**：Windows 中文系统下 MSVC 默认按 GBK（代码页 936）解析源文件。UTF-8 编码的中文注释在 GBK 解析下产生非法字节序列，导致编译器"看到"的代码跟实际文件不一样——构造函数声明被解析坏，后续所有对构造函数的调用都报找不到重载。

**解决**：加 `/utf-8` 编译标志：
```
cl /EHsc /std:c++20 /utf-8 /Fe:rational_demo.exe rational.cpp main.cpp
```

| 标志 | 效果 |
|------|------|
| 不加 | MSVC 默认 GBK 解析 → UTF-8 中文出错 |
| `/utf-8` | MSVC 按 UTF-8 解析 → 正确 |

### 坑 2：`auto` 返回类型的 `<=>` 不能跨翻译单元

**现象**：
```
error C3779: "Rational::operator <=>": 要使用将会返回"auto"的函数，必须首先定义此函数
```

**原因**：C++20 的三路比较运算符在头文件中声明为 `auto operator<=>(const Rational&) const;`，返回类型用 `auto` 推导。但实现写在 `rational.cpp` 中，main.cpp 编译时看不到函数体，也就无法推导返回类型。

**解决**：显式指定返回类型：
```cpp
// rational.hpp
std::strong_ordering operator<=>(const Rational& rhs) const;

// rational.cpp
std::strong_ordering Rational::operator<=>(const Rational& rhs) const {
    // ...
}
```

虽然 IDE 经常提示 `auto` 返回类型更简洁，但当声明和实现分离时必须写具体类型。

### 坑 3：`explicit` 构造函数与整数运算的摩擦

**背景**：单参数构造函数标记了 `explicit`：
```cpp
explicit Rational(std::int64_t n);  // 禁止隐式转换
```

这意味着不能写 `Rational r = 5;` 或 `r + 5`。

**解决**：整数运算时需要显式构造：
```cpp
Rational d(2, 3);
Rational e = d + Rational(1);   // 显式构造, 而非 d + 1
```

`explicit` 增加了打字量，但防止了 `Rational r = some_double_value` 这种隐蔽的 bug。对于有理数类这种数学类型，隐式转换可能掩盖精度损失问题。

### 坑 4：VS 2010 和 VS 2022 共存的混淆

排查编译器时先在 C 盘发现了 VS 2010 的 `cl.exe`，花了不少时间尝试让它跑——结果 vcvars32.bat 虽然能设置环境变量，cl.exe 却退出了码 53（DLL 不兼容 Win11）。后来用户提醒才在 `D:\新建文件夹\` 找到 VS 2022，cl.exe 完全正常。

**教训**：不要看到第一个编译器就认为是唯一/正确的那个，尤其是旧版本 VS 残留很容易误导排查方向。
