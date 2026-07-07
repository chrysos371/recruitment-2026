# Software_E1 — BP 神经网络算法实现

## 自我介绍

我是张杨亦航（学号 2524030231）。BP 神经网络是我在本次招新前就已经系统学习并动手实现过的内容。以下代码均来自我个人的练习项目，涵盖了从单神经元到多层 BP 网络、再到卷积神经网络的完整学习路径。

---

## 已有代码清单（均为本人此前编写）

| 文件 | 来源 | 内容 |
|------|------|------|
| `back_propagation_neural_network.py` | `cs-tutorials/Python/neural_network/` | **纯 NumPy 实现的 BP 框架**：DenseLayer + BPNN 类，支持任意层数、Sigmoid 激活、MSE 损失、梯度下降 |
| `two_hidden_layers_neural_network.py` | `cs-tutorials/Python/neural_network/` | **纯 NumPy 两层隐藏层实现**：手动推导链式求导，feedforward + back_propagation |
| `simple_neural_network.py` | `cs-tutorials/Python/neural_network/` | 单神经元前向/反向传播演示 |
| `convolution_neural_network.py` | `cs-tutorials/Python/neural_network/` | NumPy 手写 CNN 实现（卷积层 + 池化层 + 全连接） |
| `sinx by myself.py` | `PycharmProjects/PythonProject/` | PyTorch 拟合 sin(x)：1→32→64→1 MLP，ReLU + MSE + Adam，250 epochs |

### 核心实现：`back_propagation_neural_network.py`

这是我之前参照 [neuralnetworksanddeeplearning.com](http://neuralnetworksanddeeplearning.com/chap2.html) 和 Stephen Lee 的框架思路，用纯 NumPy 手写的 BP 神经网络。核心设计：

- **DenseLayer**：全连接层，封装了 weight/bias 初始化、前向传播 (`forward_propagation`)、反向传播 (`back_propagation`)、梯度计算 (`cal_gradient`)
- **BPNN**：网络容器，支持 `add_layer()` 逐层添加 → `build()` 自动初始化 → `train()` 训练
- **损失函数**：MSE，梯度为 `2*(y_pred - y_true)`
- **激活函数**：Sigmoid（可扩展为 linear）

```python
model = BPNN()
model.add_layer(DenseLayer(1))    # 输入层
model.add_layer(DenseLayer(32))   # 隐藏层 1
model.add_layer(DenseLayer(64))   # 隐藏层 2
model.add_layer(DenseLayer(1))    # 输出层
model.build()
model.train(xdata, ydata, train_round=5000, accuracy=0.01)
```

### sin(x) 拟合经验：`sinx by myself.py`

用 PyTorch 写过 sin(x) 的 MLP 拟合，三层全连接 (1→32→64→1)，250 轮训练收敛良好。虽然 E1 要求不用 PyTorch，但网络结构设计和训练经验可直接迁移到 NumPy 版本。

---

## E1 题目要求

- 手动实现多层感知机（MLP），不使用深度学习框架，仅借助 NumPy
- 训练网络拟合 sin(x)（一维输入）和 sin(x₁)·cos(x₂)（二维输入）
- 基于给定模板 `test.py`：填入 `NeuralNetwork1D` 和 `NeuralNetwork2D` 类
- 达标标准：`testbench(0)` 和 `testbench(1)` 的 MAE ≤ 0.01

---

## 实现方案

基于我之前写的 `back_propagation_neural_network.py` 的核心逻辑（DenseLayer 的前向传播 + 反向传播 + 梯度更新），填入 `test.py` 模板。基本思路：

1. **网络结构**：1D 用 `[1, 32, 64, 1]`，2D 用 `[2, 64, 128, 64, 1]`
2. **激活函数**：隐藏层用 ReLU（缓解梯度消失），输出层无激活（回归任务）
3. **损失**：MSE
4. **优化**：SGD + Momentum 或 Adam（用 NumPy 手写）
5. **训练**：批量梯度下降，epochs 足够多直到 MAE < 0.01

---

## 文件结构

```
Software_E1/
├── src/
│   ├── back_propagation_neural_network.py   # 我之前的纯 NumPy BP 框架
│   ├── two_hidden_layers_neural_network.py  # 我之前的双层隐藏层实现
│   ├── simple_neural_network.py             # 我之前的单神经元示例
│   ├── convolution_neural_network.py        # 我之前的 NumPy CNN
│   ├── sinx by myself.py                   # 我之前的 PyTorch sin(x) 拟合
│   └── test.py                              # 题目模板（待填入）
├── README.md
└── notes.md
```
