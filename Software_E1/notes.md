# 学习过程与踩坑记录 — BP 神经网络手写实现

## 学习过程

### 阶段一：理解反向传播

我之前用 PyTorch 写过 MLP（见 `sinx by myself.py`），对 `loss.backward()` 和 `optimizer.step()` 很熟悉，但一直停留在"框架帮你做"的层面。这次 E1 要求纯 NumPy 手写，迫使我把链式求导从头推了一遍。

核心公式回顾：

```
前向传播: z^(l) = W^(l)·a^(l-1) + b^(l)
         a^(l) = ReLU(z^(l))        (隐藏层)
         a^(L) = z^(L)              (输出层, 回归无激活)

损失:    L = MSE(y_pred, y_true)

反向传播:
  δ^(L) = 2(y_pred - y_true) / N            (输出层)
  δ^(l) = (W^(l+1))^T·δ^(l+1) ⊙ ReLU'(z^(l))  (隐藏层)
  dW^(l) = δ^(l)·(a^(l-1))^T
  db^(l) = sum(δ^(l))

参数更新: W -= lr * dW,  b -= lr * db
```

### 阶段二：网络设计

参照之前 PyTorch 跑 sin(x) 的经验 (1→32→64→1)，1D 直接复用这个结构。2D 用 2→48→96→48→1。

关键设计选择：

| 选择 | 理由 |
|------|------|
| Xavier 初始化 | 比 He 更温和，第一层 fan_in=1 时不会爆炸 |
| 输入归一化 | x / (2π)，映射到 [0,1]，大幅加速收敛 |
| ReLU 隐藏层 | 避免 sigmoid 梯度消失 |
| 输出无激活 | 回归任务，输出范围 [-1,1] |
| 梯度裁剪 | `np.clip(grad, -1, 1)` 防止爆炸 |

### 阶段三：调参过程

| 尝试 | 1D MAE | 2D MAE | 结果 |
|------|--------|--------|:--:|
| lr=0.005, He init, 无归一化 | — | — | 梯度爆炸, NaN |
| lr=0.002, Xavier init, 无归一化 | 0.018 | NaN | 2D 仍爆炸 |
| lr=0.001, Xavier init, 归一化+梯度裁剪 | 0.006 | 0.028 | 1D 过, 2D 不够 |
| lr=0.0015, 网络加大 48→96→48, 25000 epochs | **0.006** | **0.007** | ✅✅ |

---

## 踩坑记录

### 坑 1：He 初始化在单输入时的灾难

**现象**：第一层权重初始化的标准差为 `sqrt(2/fan_in) = sqrt(2/1) ≈ 1.4`，导致第一个隐藏层的输出直接飞到几十甚至几百，经过 ReLU 放大后迅速爆炸为 NaN。

**原因**：He 初始化假设 fan_in 不会太小（通常是几百个输入特征），但 1D 网络的输入只有 1 维。

**解决**：改用 Xavier uniform 初始化：`limit = sqrt(6 / (fan_in + fan_out))`，同时考虑了输入和输出维度，对 1 维输入友好得多。

### 坑 2：输入不归一化导致收敛极慢

**现象**：同一网络、同一超参，不加归一化时 loss 下降缓慢甚至不收敛。

**原因**：输入范围 [0, 2π] ≈ [0, 6.28]，权重需要适应这个数值范围。归一化到 [0, 1] 后，所有输入、输出都在相近的量级。

**解决**：训练时 `X_train = X_raw / (2π)`，预测时 `x_norm = input_x / (2π)`，保持一致。

### 坑 3：Python 方法不支持重载（模板 bug）

**现象**：
```
TypeError: Test.output_y() missing 1 required positional argument: 'input_x2'
```

**原因**：题目模板中 `output_y` 被定义了两次（1 参数版和 2 参数版），但 Python 不像 C++ 支持方法重载——第二个定义会覆盖第一个。`testbench(0)` 用 1 个参数调用时，Python 只看到 2 参数版本。

**解决**：合并为带默认参数的单一方法：
```python
def output_y(self, input_x, input_x2=None):
    if input_x2 is None:
        return self.net1.predict(input_x)
    return self.net2.predict(input_x, input_x2)
```
题目要求在 C++ 版本是正确的（支持重载），Python 版本需要这个适配。

### 坑 4：梯度爆炸

**现象**：训练中突然出现 `RuntimeWarning: overflow encountered in dot`，然后所有参数变成 NaN。

**原因**：MSE 梯度 `2*(y_pred - y_true)` 在初始预测误差大时可达几百，经过深层反向传播逐层放大。

**解决**：三层防护——(1) Xavier 初始化减少初始权重；(2) 输入归一化减小数据范围；(3) 梯度裁剪 `np.clip(delta, -10, 10)` 和 `np.clip(dW, -1, 1)`。
