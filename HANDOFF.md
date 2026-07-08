# 交接文档 — 智泽实验室 2026 招新

> 把这个文件内容复制给新会话的 Claude，即可无缝继续。

---

## 你是谁

张杨亦航，学号 2524030231，GitHub chrysos371，河海大学 2026 智泽实验室招新考核。

选题：**软件类 + 计算机视觉(C) + 机器学习(E)**，共 14 题，21 分（远超 9 分门槛）。

---

## 当前状态 (2026-07-08 22:00)

### 已完成 (13/14)

| 题目 | 状态 | 完成日 | 备注 |
|------|:--:|------|------|
| Base_A Markdown | ✅ | 7/7 | |
| Base_B Git | ✅ | 7/7 | 含 --no-ff 分支演示 |
| Base_C Linux | ⏸️ | | 等移动硬盘里的 Ubuntu 镜像 |
| Base_D 科学上网 | ✅ | 7/7 | Clash Verge + cokecloud.biz |
| Software_A1 Rational C++ | ✅ | 7/7 | VS 2022 MSVC 编译通过 |
| Software_A2 Shape C++ | ✅ | 7/7 | 多态演示 |
| Software_C1 OpenCV 人脸模糊 | ✅ | 7/7 | Haar Cascade + 中文路径修复 |
| Software_C2 YOLO 目标检测 | ⚠️ | 7/8 | 代码完成，**标注待修正** |
| Software_C3 红绿灯检测 | ✅ | 7/8 | HSV+形态学+轮廓 |
| Software_E1 BP 神经网络 | ✅ | 7/8 | MAE 0.006/0.007，预训练权重已缓存 |
| Software_E2 MNIST MLP vs CNN | ✅ | 7/8 | MLP 98.64%, CNN 99.48% |
| Software_E3 Titanic Kaggle | ✅ | 7/8 | LR 80.45% vs RF 79.89% |
| Software_E4 VGG vs ResNet | ✅ | 7/8 | VGG 90.72%, ResNet 93.96% (AutoDL RTX 5090) |

### 关键待办（需你手动）

| 任务 | 预计时间 | 说明 |
|------|:--:|------|
| **C2 标注修正** | 15 分钟 | 用 makesense.ai 打开 `Software_C2/dataset/images/train/`，把非社区人员 class 0→1 |
| **截图** | 30 分钟 | 每题截几张运行结果 |
| **自我介绍.pdf** | 10 分钟 | 根目录必须放 |
| **Base_C Linux** | ? | 等你移动硬盘 |
| **关 AutoDL！** | 1 分钟 | 去 autodl.com 关机，否则一直扣费 |

---

## 环境速查

| 组件 | 位置/版本 |
|------|-----------|
| Python | 3.14.0 @ `D:\python\` |
| C++ 编译器 | VS 2022 MSVC 14.44 @ `D:\新建文件夹\` |
| C++ 一键编译 | 双击 `Software_A1/src/build.bat` |
| OpenCV | 4.13.0（注意中文路径用 imencode） |
| PyTorch | 2.12.1 CPU（Python 3.14 无官方 CUDA wheel） |
| 代理 | Clash Verge + cokecloud.biz |
| SSH Key | `~/.ssh/github_chrysos371` (ED25519) |
| 仓库 | git@github.com:chrysos371/recruitment-2026.git |

### 关键环境坑

- **中文路径**：项目路径含"智泽实验室招新"，`cv2.imread` 不支持，必须用 `np.fromfile + cv2.imdecode`
- **MSVC 不在 PATH**：`D:\新建文件夹\` 非标准路径，需手动设 INCLUDE/LIB/PATH，或用 build.bat
- **Python 3.14 CUDA**：需 nightly build，普通 `pip install torch --index-url cu124` 找不到 wheel
- **E1 test.py**：`output_y` 用默认参数合并了 C++ 的两个重载版本（Python 不支持方法重载）

---

## 如果新会话要继续

把这段粘贴给新 Claude：

> 我在做河海大学智泽实验室 2026 招新考核，选题软件类+C+E。项目在 C:\Users\31633\Desktop\智泽实验室招新\，GitHub 仓库 chrysos371/recruitment-2026。请先读 HANDOFF.md，然后告诉我当前状态和建议下一步。

---

## 项目结构

```
智泽实验室招新/
├── README.md              # 根 README (进度表+环境说明)
├── HANDOFF.md             # 本文件
├── .gitignore             # 62 行，已配好
├── .gitattributes         # LFS 追踪 mnist_x.txt
├── Base_A/                # Markdown
├── Base_B/                # Git
├── Base_C/                # (空，暂缓)
├── Base_D/                # 科学上网
├── Software_A1/           # Rational C++
├── Software_A2/           # Shape C++
├── Software_C1/           # OpenCV 人脸模糊
├── Software_C2/           # YOLO 目标检测
│   ├── dataset/           # 预标注数据 (class 1 全为 0!)
│   └── reference/         # 标注参考图
├── Software_C3/           # 红绿灯检测
├── Software_E1/           # BP 神经网络
│   ├── e1_1d_weights.npz  # 预训练权重
│   └── e1_2d_weights.npz  # 预训练权重
├── Software_E2/           # MNIST MLP vs CNN
├── Software_E3/           # Titanic
└── Software_E4/           # VGG vs ResNet
    └── output/            # 权重 (VGG-16_best.pth, ResNet-18_best.pth)
```

---

## 提交要求速览

- 截止：**8 月 20 日前后**
- 格式：`学号_姓名.zip` = `2524030231_张杨亦航.zip`
- 提交：百度网盘（永久有效）+ 邮件 yuanzhechn@163.com
- 所有文档 Markdown
- 每题需：README.md + notes.md + 截图 + 源代码
- 根目录需：`自我介绍.pdf`
