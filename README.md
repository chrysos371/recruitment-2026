# 智泽实验室 2026 年招新考核

> **选题**：软件类 · 计算机视觉 (C) + 机器学习 (E)

## 目录结构

```
├── Base_A/          # Markdown 使用
├── Base_B/          # Git 使用
├── Base_C/          # Linux 使用
├── Base_D/          # 科学上网与账户
├── Software_A1/     # 有理数类 Rational 设计 [简单]
├── Software_A2/     # Shape 图形类体系设计 [简单]
├── Software_C1/     # OpenCV 基础 + 人脸模糊 [简单]
├── Software_C2/     # YOLO 目标检测 [中等]
├── Software_C3/     # 红绿灯检测 [困难]
├── Software_E1/     # BP 神经网络手写实现 [简单]
├── Software_E2/     # 手写数字识别 MLP vs CNN [中等]
├── Software_E3/     # 泰坦尼克号生还预测 [中等]
├── Software_E4/     # VGG vs ResNet 对比复现 [困难]
├── 自我介绍.pdf     (待补充)
└── README.md
```

## 环境

| 组件 | 版本/说明 |
|------|-----------|
| OS | Windows 11 |
| WSL | Ubuntu 26.04 LTS (2026/08/11 安装) |
| C++ 编译器 | VS 2022 MSVC 14.44 (D 盘), `/std:c++20 /utf-8` |
| C++ 一键编译 | `Software_A1/src/build.bat` (自动设置环境变量) |
| Python | 3.14.0 (D 盘), 主要包: numpy, opencv, torch, sklearn, ultralytics |
| GPU 训练 (E4) | AutoDL RTX 5090: `python cifar10_train.py --epochs 80` |
| E1 预训练权重 | `e1_1d_weights.npz` / `e1_2d_weights.npz` (Python+NumPy 推理) |
| E1 C++ 推理 | `test.cpp` + `e1_1d_weights.h` / `e1_2d_weights.h` (预训练权重嵌入) |
| 代理 | Clash Verge + cokecloud.biz |

## A1/A2 编译说明

VS 2022 装在非标准路径 (`D:\新建文件夹\`), 直接运行 `cl.exe` 会报错。
请在 `Software_A1/src/` 下**双击 `build.bat`** 一键编译 A1 和 A2。

## 进度

| 题目 | 状态 | 完成日期 | 备注 |
|------|:----:|------|------|
| Base_A — Markdown | ✅ | 7/7 | |
| Base_B — Git | ✅ | 7/7 | |
| Base_C — Linux | ✅ | 8/19 | WSL2 Ubuntu 26.04 + demo.sh 实操 + 4 张截图 |
| Base_D — 科学上网 | ✅ | 7/7 | |
| Software_A1 — Rational 类 | ✅ | 7/7 | 已修复 INT64_MIN 溢出保护 |
| Software_A2 — Shape 体系 | ✅ | 7/7 | |
| Software_C1 — OpenCV 人脸模糊 | ✅ | 7/7 | 已修复中文路径 cv2.imread |
| Software_C2 — YOLO 目标检测 | ⚠️ | 7/8 | 代码已修复(中文路径+模型路径)；标注待人工修正 |
| Software_C3 — 红绿灯检测 | ✅ | 7/8 | 已修复 KeyError 'off' |
| Software_E1 — BP 神经网络 | ✅ | 7/8 | 已修复 C++ predict stubs+PyTorch bug；Python/C++ 双版本均可用 |
| Software_E2 — MLP vs CNN | ✅ | 7/8 | 已修复 top5_acc.py 模型加载兼容性 |
| Software_E3 — Titanic Kaggle | ✅ | 7/8 | 已修复 NaN/入口缺失/tuning |
| Software_E4 — VGG vs ResNet | ✅ | 7/8 | VGG 90.72%, ResNet 93.96% |

> **2026/08/11 代码审查修复**：修复 22 个文件共 25 项 bug（崩溃/中文路径/类型错误/溢出/CUDA/模型路径等），commit `d8c70ba`。

> **2026/08/19 截图补齐**：为 E1-E4/A1/A2/Base_B/Base_C 生成真实运行截图（拟合曲线/准确率/终端输出等），并起草 `自我介绍.pdf`。

> **待完成**：C2 标注修正、Base_A/Base_D 手动截图、自我介绍个人信息核验、打包提交
