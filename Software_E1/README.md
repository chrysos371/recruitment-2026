# Software_E1 — BP 神经网络算法实现

## 自我介绍

我是张杨亦航（学号 2524030231）。BP 神经网络是我在本次招新前自学 PyTorch 时系统练习过的内容。以下代码全部来自我个人的 PyCharmProjects，是我在初学深度学习时一步步跟着教程手敲的——从全连接网络到 CNN、RNN，覆盖了前向传播、反向传播、梯度下降等核心概念。

---

## 本人此前编写的神经网络代码

所有文件来源：`C:\Users\31633\PycharmProjects\PythonProject\`

| 文件 | 内容 | 框架 |
|------|------|:--:|
| `sinx by myself.py` | 用 MLP 拟合 sin(x)：1→32→64→1，ReLU + MSE + Adam，250 epochs | PyTorch |
| `neaul network.py` | 手机价格预测：全连接网络 (input→128→256→4)，SGD 优化，包含数据加载/训练/测试 | PyTorch |
| `convolution neural network.py` | CIFAR-10 图像分类：Conv→Pool→Conv→Pool→FC，200 epochs，支持 GPU 训练 | PyTorch |
| `recurrent neural network.py` | 周杰伦歌词生成：Embedding + RNN + Linear，jieba 分词 | PyTorch |
| `iris classification.py` | 鸢尾花分类：经典入门案例 | PyTorch |

### 关于 `back_propagation_neural_network.py` 的说明

此前从 `cs-tutorials/` 目录复制过来的 BP 代码（`back_propagation_neural_network.py` 等）是我 **fork 的他人仓库**，不是我自己的原创代码。已从本项目中移除，只保留我本人手写的代码。

---

## E1 题目要求

- 手动实现多层感知机（MLP），不使用深度学习框架，仅借助 NumPy
- 训练网络拟合 **sin(x)**（一维输入）和 **sin(x₁)·cos(x₂)**（二维输入）
- 基于给定模板 `test.py` 填入 `NeuralNetwork1D` 和 `NeuralNetwork2D` 类
- `Test.testbench(0)` 和 `Test.testbench(1)` 的 **MAE ≤ 0.01**

---

## 实现思路

我之前用 PyTorch 写过 sin(x) 拟合（见 `sinx by myself.py`），对网络结构 (1→32→64→1) 和训练超参（Adam lr=0.001, 250 epochs）有实际经验。

E1 要求纯 NumPy 手写，需要把 PyTorch 那套（自动求导 + optimizer.step()）替换为手动实现：
1. 前向传播：矩阵乘法 + ReLU/Sigmoid
2. 反向传播：链式求导，手动计算每层梯度
3. 参数更新：SGD 或手写 Adam

---

## 文件结构

```
Software_E1/
├── src/
│   ├── sinx by myself.py                   # 我之前写的 PyTorch sin(x) 拟合
│   ├── neaul network.py                    # 我之前写的手机价格预测 NN
│   ├── convolution neural network.py       # 我之前写的 CIFAR-10 CNN
│   ├── recurrent neural network.py         # 我之前写的 RNN 歌词生成
│   ├── iris classification.py              # 我之前写的鸢尾花分类
├── test.py                                 # E1 完整实现 (NeuralNetwork1D / 2D / Test)
├── test.cpp                                # C++ 版本 (含预训练权重头文件)
├── e1_1d_weights.npz                       # 1D 预训练权重
├── e1_2d_weights.npz                       # 2D 预训练权重
├── e1_1d_weights.h                         # 1D 权重 C 头文件
├── e1_2d_weights.h                         # 2D 权重 C 头文件
├── export_weights.py                       # 权重导出脚本
├── README.md
└── notes.md
```
