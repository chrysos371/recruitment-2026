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
├── 自我介绍.pdf
└── README.md
```

## 环境

| 组件 | 版本/说明 |
|------|-----------|
| OS | Windows 11 |
| C++ 编译器 | VS 2022 MSVC 14.44 (D 盘), `/std:c++20 /utf-8` |
| C++ 一键编译 | `Software_A1/src/build.bat` (自动设置环境变量) |
| Python | 3.14.0 (D 盘), 主要包: numpy, opencv, torch, sklearn, ultralytics |
| GPU 训练 (E4) | AutoDL RTX 5090: `python cifar10_train.py --epochs 80` |
| E1 预训练权重 | `e1_1d_weights.npz` / `e1_2d_weights.npz` (已缓存, 评审秒出) |

## A1/A2 编译说明

VS 2022 装在非标准路径 (`D:\新建文件夹\`), 直接运行 `cl.exe` 会报错。
请在 `Software_A1/src/` 下**双击 `build.bat`** 一键编译 A1 和 A2。

## 进度

| 题目 | 状态 | 完成日期 |
|------|:----:|------|
| Base_A — Markdown | ✅ | 7/7 |
| Base_B — Git | ✅ | 7/7 |
| Base_C — Linux | ⏸️ 暂缓 | 等移动硬盘 |
| Base_D — 科学上网 | ✅ | 7/7 |
| Software_A1 — Rational 类 | ✅ | 7/7 |
| Software_A2 — Shape 体系 | ✅ | 7/7 |
| Software_C1 — OpenCV 人脸模糊 | ✅ | 7/7 |
| Software_C2 — YOLO 目标检测 | ⚠️ | 7/8 (待人工修正标注) |
| Software_C3 — 红绿灯检测 | ✅ | 7/8 |
| Software_E1 — BP 神经网络 | ✅ | 7/8 |
| Software_E2 — MLP vs CNN | ✅ | 7/8 |
| Software_E3 — Titanic Kaggle | ✅ | 7/8 |
| Software_E4 — VGG vs ResNet | ✅ | 7/8 (VGG 90.72%, ResNet 93.96%) |
