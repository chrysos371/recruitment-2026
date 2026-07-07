# Software_C1 — OpenCV 基础图像处理 + 人脸自动模糊

## 自我介绍

我是张杨亦航（学号 2524030231）。这道题是计算机视觉方向的第一题——从基础 OpenCV 操作入手，逐步过渡到 Haar Cascade 人脸检测和自动模糊。这个"检测→处理→回写原图"的思路其实贯穿后面的 C2（YOLO 目标检测）和 C3（红绿灯检测），只是后两者用深度学习替代了 Haar 级联分类器。

本地有 RTX 5070（8GB 显存），但 C1 用 CPU 就够——Haar Cascade 是传统视觉方法，不依赖 GPU。

---

## 功能概述

| 功能 | 说明 |
|------|------|
| 图像加载 | `cv2.imread()` + 尺寸/通道/dtype 信息 |
| 裁剪 | ROI 区域提取，取图像中心 50% |
| 对比度/亮度 | `cv2.convertScaleAbs()`, `dst = α·src + β` |
| 高斯模糊 | `cv2.GaussianBlur()`, 可调 kernel size |
| **人脸检测 + 模糊** | Haar Cascade → 提取 ROI → 高斯模糊 → 写回原图 |

### 人脸检测流程

```
原图 (BGR)
  ↓ cv2.cvtColor(..., COLOR_BGR2GRAY)
灰度图
  ↓ face_cascade.detectMultiScale(...)
人脸坐标列表 [(x, y, w, h), ...]
  ↓ 对每个人脸:
  提取 ROI → cv2.GaussianBlur(roi, ksize) → 写回原图
  ↓
输出: 人脸模糊后的图像
```

---

## 使用方法

### 安装依赖

```bash
pip install opencv-python numpy
```

### 图片模式

```bash
cd Software_C1/src
python face_blur.py [图片路径]
```

不传路径则生成测试图像（渐变背景 + 色块，用于验证处理管线）。

### 实时摄像头模式

```bash
python face_blur_camera.py
```

| 按键 | 功能 |
|------|------|
| `q` | 退出 |
| `+` / `-` | 调整模糊强度 |
| `b` | 切换检测框显示 |

### 输出文件

```
Software_C1/output/
├── 01_original.jpg          # 原始图像
├── 02_cropped.jpg           # 裁剪后 (中心 50%)
├── 03_enhanced.jpg          # 对比度/亮度增强
├── 04_blurred_full.jpg      # 全图高斯模糊
├── 05_face_blurred.jpg      # 人脸模糊 (强, kernel=31)
└── 06_face_blurred_light.jpg # 人脸模糊 (轻, kernel=11)
```

---

## 技术要点

### Haar Cascade 人脸检测

```python
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,      # 图像金字塔缩放比例
    minNeighbors=5,        # 相邻矩形数阈值 (越高假阳性越少)
    minSize=(30, 30),      # 最小检测窗口
    flags=cv2.CASCADE_SCALE_IMAGE
)
```

**参数调优经验：**

| 参数 | 调大效果 | 调小效果 |
|------|----------|----------|
| `scaleFactor` | 检测更快，但可能漏小脸 | 更精细，但更慢 |
| `minNeighbors` | 假阳性少，但可能漏遮挡脸 | 召回率高，但误检增多 |
| `minSize` | 忽略小尺寸噪点 | 能检测远处小脸 |

### 高斯模糊

```python
blurred = cv2.GaussianBlur(roi, (ksize, ksize), sigmaX=0)
```

- `ksize`: 核大小，必须为正奇数。越大越模糊，人脸越难辨识
- `sigmaX=0`: 让 OpenCV 根据核大小自动计算 sigma

### 对比度/亮度公式

```
dst(x,y) = α · src(x,y) + β
```

- `α > 1`: 对比度增强（暗的更暗，亮的更亮）
- `β > 0`: 亮度提升（整体偏亮）

---

## 文件结构

```
Software_C1/
├── src/
│   ├── face_blur.py           # 图片人脸模糊 (主脚本)
│   └── face_blur_camera.py    # 实时摄像头人脸模糊
├── output/                    # 生成的处理结果
├── README.md                  # 本文件
└── notes.md                   # 学习过程与踩坑记录
```

---

## 与后续题目的关联

- **C2 (YOLO 检测)**: 同样遵循"检测→提取 ROI→处理"的流程，但检测器从 Haar Cascade 升级为 YOLO 深度学习模型
- **C3 (红绿灯检测)**: 进一步涉及颜色空间转换、形态学处理、轮廓提取等传统 CV 方法
