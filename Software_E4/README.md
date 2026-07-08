# Software_E4 — VGG-16 vs ResNet-18 对比复现

## 自我介绍

我是张杨亦航（学号 2524030231）。这是本次招新考核的最后一题，也是分值最高的一题（5 分）。要求在 CIFAR-10 上从零实现 VGG-16 和 ResNet-18，严禁调用 torchvision.models 等预封装模型。

两个经典 CNN 架构代表了深度学习发展的两个里程碑——VGG（2014）用"堆深度"证明更深更好，ResNet（2015）用残差连接解决了"太深反而退化"的问题。

本地 Python 3.14 的 CUDA wheel 不可用，训练在 AutoDL 云 GPU 上完成。

---

## 模型架构

### VGG-16（纯手写）

```
Conv3-64 → Conv3-64 → MaxPool   (32→16)
Conv3-128 → Conv3-128 → MaxPool (16→8)
Conv3-256 → Conv3-256 → Conv3-256 → MaxPool (8→4)
Conv3-512 → Conv3-512 → Conv3-512 → MaxPool (4→2)
Conv3-512 → Conv3-512 → Conv3-512 → MaxPool (2→1)
FC 512→512→10 (+Dropout)
```

- **CIFAR-10 适配**: FC 层从原版 25088→4096→4096→1000 缩小为 512→512→10
- **BatchNorm**: 加速收敛
- **参数量**: ~14.7M

### ResNet-18（纯手写）

```
Conv3-64 (stride=1, 无 MaxPool)
→ 2× BasicBlock(64, 64)
→ 2× BasicBlock(64, 128, stride=2)
→ 2× BasicBlock(128, 256, stride=2)
→ 2× BasicBlock(256, 512, stride=2)
→ AdaptiveAvgPool → FC(512→10)
```

- **CIFAR-10 适配**: 首个卷积 7×7→3×3, stride 2→1, 去掉首层 MaxPool
- **残差连接**: 输入直接加到卷积输出, 解决梯度消失
- **参数量**: ~11.2M

---

## 训练配置

| 参数 | VGG-16 | ResNet-18 |
|------|:------:|:---------:|
| 优化器 | SGD(momentum=0.9, wd=5e-4) | 同左 |
| 学习率 | 0.01 | 0.05 |
| LR 调度 | CosineAnnealing (80 epochs) | 同左 |
| Batch | 128 | 128 |
| 数据增强 | RandomCrop + HorizontalFlip + Normalize | 同左 |

---

## 使用方法

### 方案 A：AutoDL 云 GPU（推荐）

**1. 注册 & 开机**
- 打开 [AutoDL.com](https://www.autodl.com/)，注册充值
- 租一台 **RTX 3090**（约 ¥2/小时）
- 镜像选 **PyTorch 2.x + CUDA 12.x** 预配镜像
- 开机，进入 JupyterLab / 终端

**2. 在终端中依次执行：**
```bash
# 克隆仓库
git clone git@github.com:chrysos371/recruitment-2026.git
cd recruitment-2026/Software_E4

# 安装依赖 (镜像已预装 PyTorch, 只需补 torchvision)
pip install torchvision -q

# 快速验证管线 (3 epochs, 约 2 分钟)
python cifar10_train.py --quick

# 完整训练 (80 epochs, 约 1-2 小时)
python cifar10_train.py --epochs 80
```

**3. 下载结果**
训练完成后，`output/` 目录下有：
- `VGG-16_best.pth` / `ResNet-18_best.pth`（模型权重）
- 终端输出中有对比结果表 → 截图保存

用 AutoDL 的文件管理功能下载权重到本地。

### 方案 B：本地 CPU（慢，仅验证）

```bash
cd Software_E4
python cifar10_train.py --quick   # 3 epochs, ~30-40 分钟
```

---

## 文件结构

```
Software_E4/
├── cifar10_train.py       # 完整训练代码 (VGG + ResNet 手写实现)
├── data/                  # CIFAR-10 数据集 (自动下载)
├── output/                # 训练产物 (权重)
├── README.md
└── notes.md
```
