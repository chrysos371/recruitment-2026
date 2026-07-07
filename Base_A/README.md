# Base_A — Markdown 使用

## 自我介绍

我是张杨亦航（学号 2524030231），计算机/AI 方向在读。选择软件方向参加智泽实验室招新，是因为我对计算机视觉和机器学习的落地场景有强烈兴趣——从 YOLO 做实时检测到 ResNet 的残差连接思想，这些技术正在重塑机器人感知的边界。

我目前的开发环境是一台 Windows 11 笔记本，配 AMD Ryzen 9 8940HX + RTX 5070 Laptop GPU（16GB 显存），本地跑中规模模型没问题。日常用 PyCharm 2025.3.3 作为主力 IDE，配合 Git Bash 做版本管理，Python 3.14 装在 D 盘，用 Conda 25.11 管理虚拟环境。这套配置足以支撑本次考核从 C++ 面向对象到 YOLO 目标检测的全部开发任务。

从 Markdown 开始看似简单，但**文档能力决定一个工程师的输出质量**。我的规划是：在 14 道题的全过程中，用一套统一的文档规范写 Markdown，让每道题的思路、实现、踩坑都清晰可追溯。这既是给自己看的"知识存档"，也是给评审看的"能力证明"。

后续方向规划：短期目标是通过本次考核进入智泽实验室，参与实际的机器人视觉项目；中期希望在目标检测（YOLO 系列）和模型轻量化方向深入，结合实验室的 ROS + 嵌入式平台积累工程经验。

---

## Markdown 语法速查

> 以下内容既是学习笔记，也是后续所有文档的格式参考。

### 1. 标题

```markdown
# 一级标题（每道题只用一次）
## 二级标题（章节）
### 三级标题（小节，最深到此为止，不嵌套四层）
```

### 2. 文本样式

| 效果 | 语法 | 使用场景 |
|------|------|----------|
| **粗体** | `**粗体**` | 强调关键结论 |
| *斜体* | `*斜体*` | 术语、文件名 |
| ~~删除线~~ | `~~删除线~~` | 废弃方案 |
| `行内代码` | `` `行内代码` `` | 变量名、命令 |

### 3. 列表

无序列表用 `-`，有序列表用 `1.`。子列表缩进两个空格：

```markdown
- Python 依赖
  - numpy（矩阵运算）
  - opencv-python（图像处理）
  - torch >= 2.0（深度学习）

1. 加载数据集
2. 定义模型结构
3. 训练并记录 loss
```

### 4. 代码块

始终注明语言，确保 PyCharm 和 GitHub 都能正确高亮：

````markdown
```python
import torch
import numpy as np
```
```cpp
#include <iostream>
```
```bash
cd project && python train.py
```
````

### 5. 表格

对齐方式：`|:--` 左对齐，`--:|` 右对齐，`|:--:|` 居中。

```markdown
| 模型 | 参数量 | Test Acc | 训练时间 |
|:-----|:------:|----------|---------:|
| MLP  | 118K  | 97.3%    | 2min     |
| CNN  | 93K   | 99.1%    | 8min     |
```

### 6. 图片

截图统一放 `screenshots/` 子目录，相对路径引用：

```markdown
![训练 loss 曲线](screenshots/loss_curve.png)
```

### 7. 链接

```markdown
[Ultralytics YOLO 文档](https://docs.ultralytics.com/zh/)
```

### 8. 引用

```markdown
> YOLO 的核心思想是将目标检测转化为回归问题，一次前向传播即可输出边界框和类别概率。
```

### 9. 任务列表

```markdown
- [x] 数据预处理
- [x] 模型训练
- [ ] 结果分析
- [ ] 文档编写
```

### 10. 数学公式（LaTeX）

PyCharm 自带 Markdown 预览（右侧分屏实时渲染），支持 LaTeX 公式。但 GitHub 原生不支持渲染，需要时用 [CodeCogs](https://latex.codecogs.com/) 生成公式图片嵌入。

```markdown
反向传播的核心链式法则：

$$
\frac{\partial L}{\partial w_{ij}} = \delta_j \cdot a_i
$$

行内公式：Softmax 函数 $p_i = \frac{e^{z_i}}{\sum_j e^{z_j}}$
```

### 11. HTML5 嵌入

Markdown 原生支持内嵌 HTML 标签，以下是考核中会用到的几种：

**折叠面板** (`<details>` / `<summary>`) — 长日志或大段输出折叠起来，保持文档清爽:

```markdown
<details>
<summary>点击展开：完整训练日志 (120 行)</summary>

```
Epoch 1/50: loss=0.4523, acc=0.8234
Epoch 2/50: loss=0.3214, acc=0.8712
...
```

</details>
```

实际效果:

<details>
<summary>点击展开：完整训练日志 (120 行)</summary>

```
Epoch 1/50: loss=0.4523, acc=0.8234
Epoch 2/50: loss=0.3214, acc=0.8712
...
```

</details>

**键盘按键** (`<kbd>`) — 用于快捷键文档:

```markdown
按 <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> 打开命令面板
```

实际效果: 按 <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> 打开命令面板

**文本居中** (`<div align="center">`) — 图片或表格居中:

```markdown
<div align="center">
  <img src="screenshots/result.png" width="400"/>
  <p><em>图: 处理前后的对比效果</em></p>
</div>
```

**补充说明:**
- GitHub 对 HTML 标签有安全白名单，`<script>` 和 `<iframe>` 会被过滤
- `<details>` 是 GitHub Flavored Markdown 最常用的 HTML 特性，适合隐藏大段日志
- PyCharm 预览窗也支持大部分 HTML 嵌入

---

## 我的编辑环境

| 工具 | 版本/配置 | 用途 |
|------|-----------|------|
| **PyCharm** | 2025.3.3 | 主力 IDE，自带 Markdown 实时预览 + Python/C++ 支持 |
| **Git Bash** | 2.53.0 | 版本控制 + 运行 shell 命令 |
| **Python** | 3.14.0 (D:\python\) | 所有 Python 题目的运行时 |
| **Conda** | 25.11.1 | 虚拟环境隔离 |
| **GitHub** | [chrysos371/recruitment-2026](https://github.com/chrysos371/recruitment-2026) | 代码托管 |

---

## 本套文档规范（后续 13 题统一采用）

```
Problem_X/
├── README.md           # 自我介绍 + 实现方案 + 使用方法 + 结果
├── notes.md            # 学习过程 + 踩坑记录 + 截图
└── screenshots/        # PNG 截图
```

**约束：代码块必注语言、表格对齐、标题最多三级、截图统一路径、换行符用 LF。**
