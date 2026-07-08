# 学习过程与踩坑记录 — MNIST MLP vs CNN

## 学习过程

### 阶段一：数据加载

MNIST 是经典的 28×28 灰度手写数字数据集。题目提供的是 txt 格式（每行 784 个像素值 + 1 个标签），和常见的 idx 二进制格式不同。

```
mnist_x.txt: 70000 行 × 784 列 (像素值 0-255)
mnist_y.txt: 70000 行 × 1 列  (标签 0-9)
```

用 `np.loadtxt` 一次性读入内存（122MB → float32 ≈ 224MB），然后归一化到 [0, 1]。标准划分：前 60000 训练，后 10000 测试。

### 阶段二：MLP 设计与调参

MLP 结构思路——参考 E1 的 sin(x) 拟合经验，网络太浅拟合不好，太深容易过拟合：

- 输入 784 → 展平 → 多个全连接 → ReLU + Dropout → 输出 10

调了 5 组参数，每组训练后记录：

| 参数 | 尝试值 | 最佳 |
|------|--------|:--:|
| 隐藏层结构 | (128,), (256,128), (512,256,128) | (512,256,128) |
| batch_size | 64, 128 | 64 |
| learning_rate | 0.001, 0.003 | 0.001 |
| dropout | 0.0, 0.2, 0.3 | 0.3 |
| epochs | 15, 30 | 30 |

结论：**加深网络 + Dropout 正则化**收益最大，batch_size 和 lr 在合理范围内影响较小。

### 阶段三：CNN 设计与对比

CNN 结构：Conv(1→32, 3×3) → MaxPool(2) → Conv(32→64, 3×3) → MaxPool(2) → FC(64×5×5→128) → FC(128→10)

关键对比发现：

1. **参数量**：CNN 225K < MLP 670K。卷积层的参数共享大幅减少了参数数量
2. **准确率**：CNN 99.48% > MLP 98.64%。卷积天然抓住了图像的局部空间结构
3. **训练速度**：MLP 每 epoch ~1s，CNN ~12.6s（CPU）。CNN 卷积操作计算量更大，但 GPU 上差距会缩小

---

## 踩坑记录

### 坑 1：Python 3.14 + PyTorch CUDA = 找不到 wheel

**现象**：标准 `pip install torch --index-url cu124` 报 `No matching distribution found`。

**原因**：Python 3.14 是 2025 年 10 月发布的，PyTorch 稳定版的 CUDA wheel 尚未支持。只有 nightly build 有 cp314 的 CUDA wheel，但下载 2.8GB 太慢。

**解决**：直接用 CPU 版跑。MNIST 数据量小（28×28 灰度图），CPU 训练 CNN 也就 3 分钟 15 个 epoch，完全够用。E4 的 CIFAR-10 会需要 GPU，到时候再装 nightly CUDA 或者用 AutoDL。

### 坑 2：`np.loadtxt` 静默慢

**现象**：第一次加载 122MB 的 mnist_x.txt 时等了很久。

**原因**：`np.loadtxt` 是纯 Python 实现的逐行解析，70000 行 × 784 列 = 5488 万个数字，解析开销大。

**后续改进方向**（未在本题中实现——当前加载约 15 秒，可接受）：
- `np.fromfile` + `reshape` 对于二进制格式极快
- `pandas.read_csv` 支持多线程
- 或保存为 `.npy` 格式供后续快速加载

### 坑 3：GBK 编码导致 emoji 报错

**现象**：`UnicodeEncodeError: 'gbk' codec can't encode character '✅'`

**原因**：Windows 中文终端默认 GBK 编码，emoji（✅）在 GBK 中无对应字符。与 C1 的 `cv2.imwrite` 中文路径问题类似——Windows + 中文环境 + UTF-8 = 编码冲突。

**解决**：把 emoji 换成纯 ASCII 标记 `[BEST]`。简单但有效。长期方案是在脚本开头加 `sys.stdout.reconfigure(encoding='utf-8')`。

### 坑 4：CPU 训练时 `device` 的标注

E2 的代码在 CPU 上运行，但完整保留了 `device` 变量和 `.to(device)` 调用——这样以后换 GPU 只需改一行。在 README 和注释中明确标注了当前使用 CPU 的原因（Python 3.14 CUDA wheel 不可用），避免评审时误解为"不知道用 GPU"。
