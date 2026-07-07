# 学习过程与踩坑记录 — OpenCV 人脸模糊

## 学习过程

### 阶段一：OpenCV 基础

之前主要用 PyTorch 做深度学习，OpenCV 只在数据预处理时用到过 `cv2.imread()` 和 `cv2.resize()`。这次系统过了以下模块：

| 模块 | 核心函数 | 用途 |
|------|----------|------|
| I/O | `cv2.imread`, `cv2.imwrite` | 图像读写 |
| 色彩空间 | `cv2.cvtColor`, `cv2.COLOR_BGR2GRAY` | 转灰度（人脸检测只需要亮度信息） |
| 几何变换 | 数组切片 `img[y1:y2, x1:x2]` | 裁剪（NumPy 原生操作，比 PIL 快） |
| 像素运算 | `cv2.convertScaleAbs` | 对比度/亮度（饱和转换，值域 [0,255]） |
| 滤波 | `cv2.GaussianBlur` | 高斯模糊 |
| 目标检测 | `cv2.CascadeClassifier` + `detectMultiScale` | Haar 级联人脸检测 |

### 阶段二：理解 Haar Cascade

Haar Cascade 是 2001 年 Viola-Jones 提出的经典人脸检测算法：

1. **Haar 特征**：矩形区域亮度差（如眼窝比脸颊暗），用积分图加速计算
2. **AdaBoost 级联**：多个弱分类器串联，前面的快速排除非人脸，后面的精细确认
3. **多尺度检测**：`scaleFactor=1.1` 表示每次将图像缩小 10%，在不同尺度上重复检测

相比 YOLO 等深度学习方法，Haar Cascade 的优点是：
- 不需要 GPU
- 推理极快（毫秒级）
- 不需要训练，开箱即用

缺点是：
- 侧脸、遮挡、极端光照下容易漏检
- 假阳性较高（有时把非人脸误检为人脸）

### 阶段三：实现自动模糊管线

设计思路上分了两个脚本：

1. **`face_blur.py`**（图片模式）：
   - 加载 → 基础处理演示（裁剪/增强/高斯） → 人脸检测 → 模糊人脸 → 保存
   - 同时输出 6 张中间结果，方便写文档时对比

2. **`face_blur_camera.py`**（实时模式）：
   - 摄像头逐帧读取 → 人脸检测 → 实时模糊
   - 可交互调整模糊强度和检测框开关

---

## 踩坑记录

### 坑 1：OpenCV 的 BGR 色彩空间

**现象**：`cv2.imread()` 读进来的图像用 `matplotlib` 显示时颜色诡异——蓝色变红，红色变蓝。

**原因**：OpenCV 默认使用 **BGR** 通道顺序（历史原因：早期 Windows BMP 格式），而 `matplotlib` / PIL / 网页使用 **RGB** 顺序。

**解决**：
```python
# 方法 1: cv2 原生转换
rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

# 方法 2: NumPy 通道翻转
rgb = bgr[:, :, ::-1]
```

本题不涉及 matplotlib 显示所以没踩这个坑，但写文档截图时需要注意。

### 坑 2：`GaussianBlur` 的 kernel size 必须是奇数

**现象**：
```
cv2.error: OpenCV(4.x.x) ... : error: (-215:Assertion failed)
ksize.width > 0 && ksize.width % 2 == 1
```

**原因**：高斯核需要一个中心像素，所以宽高必须为正奇数。

**解决**：
```python
if ksize % 2 == 0:
    ksize += 1
```

### 坑 3：`detectMultiScale` 的 `minNeighbors` 调参

**默认 `minNeighbors=3`** 时检测到很多假阳性（背景纹理被误认为人脸）。

**调试过程**：逐级提高阈值——5 时假阳性显著减少，7 时开始漏掉稍偏的面孔。最终选择 **`minNeighbors=5`** 作为默认值，在精确率和召回率之间平衡。

经验总结：
- 正面清晰人脸 → `minNeighbors=5~7`
- 人群密集场景 → `minNeighbors=3~4`（避免漏检）
- 证件照/单人照 → `minNeighbors=6~8`（杜绝假阳性）

### 坑 4：`cv2.imwrite` 不支持中文路径 (Windows)

**现象**：脚本输出 `[SAVE]` 路径显示正确，但文件根本没写入磁盘——目录空空如也。`cv2.imwrite()` 返回 `False` 且不报异常。

**原因**：OpenCV 的 `cv2.imwrite()` 在 Windows 上内部调用的是非 Unicode API，中文路径编码后无法正确解析。

**解决**：用 `cv2.imencode()` + 二进制写入替代：
```python
# 错误写法 (中文路径下失败)
cv2.imwrite(path, img)

# 正确写法 (兼容中文路径)
ext = os.path.splitext(name)[1]
success, buf = cv2.imencode(ext, img)
if success:
    with open(path, "wb") as f:
        f.write(buf.tobytes())
```
这个问题在 Windows 中文用户名 (如 `C:\Users\张三\`) 或中文项目目录下必现。

### 坑 5：测试图像生成——Haar Cascade 不认纯色圆

**现象**：测试生成的图像（彩色渐变 + 纯色圆形）中 `detectMultiScale` 返回 0 个人脸。

**原因**：Haar Cascade 检测的是**灰度梯度特征**（明暗交替的矩形模式），需要一个类似"眼睛比额头暗、鼻子比脸颊亮"的纹理结构。纯色圆形没有这种特征。

**解决**：测试生成图只验证处理管线（加载/裁剪/增强/模糊）是否正常运作，人脸检测部分需要用真实人脸照片验证。题目本身也要求"识别图像中的人脸"，真实照片测试是必须的。

### 坑 6：`__file__` 相对路径导致 output 写到错误位置

**现象**：从其他目录运行 `python ..\Software_C1\src\face_blur.py` 时，输出文件没有出现在项目的 `Software_C1/output/`，而是跑到了用户目录下。

**原因**：
```python
# 错误写法
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
```
当脚本以相对路径运行时（`python face_blur.py`），`__file__` 是 `"face_blur.py"`，`os.path.dirname` 返回 `""`，最终路径变成 `"../output"`，解析到当前工作目录的上级。

**解决**：
```python
# 正确写法：先用 abspath 获取绝对路径
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "output"
)
```
`os.path.abspath(__file__)` 确保无论怎么运行都拿到脚本的绝对路径，后续 `dirname` 和 `join` 都正确。

---

## 运行环境

| 组件 | 版本 |
|------|------|
| Python | 3.14.0 |
| OpenCV | 4.13.0 |
| NumPy | (随 OpenCV 安装) |
| OS | Windows 11 |
