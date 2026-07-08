# 学习过程与踩坑记录 — VGG vs ResNet

## 学习过程

### 阶段一：理解 VGG 的设计哲学

VGG（Visual Geometry Group, Oxford 2014）的核心思想简单到极致：**全部用 3×3 小卷积 + 逐步增通道数 + 逐层 MaxPool**。

为什么堆 3×3 就够了：两个 3×3 的感受野 = 一个 5×5，三个 3×3 = 一个 7×7，但参数少得多（2×3×3=18 vs 5×5=25）。

CIFAR-10 适配的关键改动：
- 输入 32×32（不是 224×224），经过 5 次 pooling 后 → 1×1
- 所以 flatten 后只有 512 维（不是 25088 维）
- FC 层从 25088→4096→4096→1000 大幅缩小为 512→512→10

### 阶段二：理解 ResNet 的残差学习

ResNet（Microsoft 2015）解决的核心问题：**网络太深反而表现更差（退化问题）**。

残差块的核心公式：`output = F(x) + x`（skip connection）

直觉解释：
- 如果深层学不到更好的特征，残差连接让网络至少能"原样传递"浅层特征
- 梯度通过 skip connection 直通底层，解决梯度消失
- 实际效果：152 层的 ResNet 比 16 层的 VGG 训练更快、效果更好

CIFAR-10 适配：
- 首层 7×7 卷积 → 改为 3×3（32×32 不需要那么大的感受野）
- stride 2→1（保留空间信息）
- 去掉首层 MaxPool

### 阶段三：训练策略

VGG 和 ResNet 在 CIFAR-10 上的训练配置有微妙区别：

| 方面 | VGG-16 | ResNet-18 |
|------|--------|-----------|
| 初始 LR | 0.01 | 0.05 |
| 原因 | FC 层多，大 LR 容易震荡 | 有 BN，可以用更大 LR |

---

## 踩坑记录

### 坑 1：VGG-16 直接复制 ImageNet 版 FC 层会 OOM

**现象**：原版 VGG-16 的 `Linear(25088, 4096)` 在 CIFAR-10 上也造成了巨大的参数浪费。

**原因**：ImageNet 输入 224×224 → 5 次 pooling → 7×7×512 = 25088。但 CIFAR-10 输入 32×32 → 5 次 pooling → 1×1×512 = **512**。

**解决**：根据 CIFAR-10 的实际特征图尺寸调整 FC 层为 512→512→10。参数从 138M 降到 ~14.7M，显存从 >3GB 降到 ~1GB。

### 坑 2：CIFAR-10 ResNet 不能直接套用 ImageNet 的 7×7 卷积

**现象**：ResNet-18 在 CIFAR-10 上首轮准确率只有 10%（= 随机猜测），loss 不下降。

**原因**：ImageNet 版的 ResNet 首层是 7×7 stride=2，在 32×32 的图上非常粗暴——第一个卷积后只剩 13×13，丢失了大量信息。

**解决**：改为 3×3 stride=1，去掉紧跟的 MaxPool。这样第一个卷积后保持 32×32 的空间分辨率。这是 CIFAR-10 ResNet 的标准做法。

### 坑 3：CPU 训练 VGG-16 的绝望速度

**实测**：CPU 上一个 epoch 约 180 秒，80 epochs = 4 小时（仅 VGG）。加上 ResNet 总共 ~6-7 小时。

**解决**：上 AutoDL 租 RTX 3090。GPU 上一个 epoch ~6 秒，80 epochs + 切换模型总共 1-2 小时。

### 坑 4：VGG-16 初始化不当导致前几轮 loss 极大

**现象**：前几个 epoch 的 loss 在 2.3 左右（= ln(10)，随机猜测的 CE loss），但 acc 不涨。

**原因**：Kaiming 初始化的默认 `fan_in` 模式对 VGG 的某些层不够好，`fan_out` 对连续 conv 层更稳定。

**解决**：统一用 `kaiming_normal_(mode='fan_out', nonlinearity='relu')`，BN 初始化为 weight=1, bias=0。
