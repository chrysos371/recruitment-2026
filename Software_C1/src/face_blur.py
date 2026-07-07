"""
Software_C1 — OpenCV 基础图像处理 + 人脸自动模糊
==================================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

功能:
  1. 图像加载与基本信息查看
  2. 裁剪 (Crop)
  3. 对比度/亮度增强
  4. 高斯模糊 (Gaussian Blur)
  5. Haar Cascade 人脸检测 + 人脸区域自动模糊

用法:
  python face_blur.py [图片路径]
  默认使用 OpenCV 自带的示例图片或指定路径

依赖: opencv-python, numpy
"""

import cv2
import numpy as np
import sys
import os


# ================================================================
#  1. 加载图像
# ================================================================

def load_image(path: str) -> np.ndarray:
    """加载图像，文件不存在时使用 OpenCV 内置的 Lena 图 (仅作测试用)。"""
    if os.path.exists(path):
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"无法读取图像: {path}")
        print(f"[INFO] 已加载: {path}")
        return img
    else:
        # fallback: 生成一张测试用渐变图
        print(f"[WARN] 文件不存在: {path}, 生成测试图像代替")
        h, w = 480, 640
        img = np.zeros((h, w, 3), dtype=np.uint8)
        for i in range(h):
            color = int(255 * i / h)
            img[i, :] = (color, 100, 200 - color // 2)
        # 画几个模拟人脸位置 (纯色圆形)
        cv2.circle(img, (150, 180), 80, (0, 0, 255), -1)
        cv2.circle(img, (450, 180), 80, (0, 255, 0), -1)
        cv2.circle(img, (300, 350), 90, (255, 0, 0), -1)
        return img


def show_info(img: np.ndarray):
    """打印图像基本信息。"""
    h, w, c = img.shape
    print(f"[INFO] 尺寸: {w} x {h}, 通道数: {c}, dtype: {img.dtype}")
    print(f"[INFO] 像素值范围: [{img.min()}, {img.max()}]")


# ================================================================
#  2. 基础图像处理
# ================================================================

def demo_crop(img: np.ndarray) -> np.ndarray:
    """裁剪：取图像中心 50% 区域。"""
    h, w = img.shape[:2]
    x1, y1 = w // 4, h // 4
    x2, y2 = w * 3 // 4, h * 3 // 4
    cropped = img[y1:y2, x1:x2]
    print(f"[OP] 裁剪: 从 ({x1},{y1}) 到 ({x2},{y2}), 新尺寸 {cropped.shape[1]}x{cropped.shape[0]}")
    return cropped


def demo_brightness_contrast(img: np.ndarray,
                             alpha: float = 1.5,
                             beta: int = 30) -> np.ndarray:
    """
    对比度与亮度调整。
      dst = alpha * src + beta
      alpha > 1 → 对比度增强
      beta  > 0 → 亮度提升
    """
    result = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    print(f"[OP] 对比度/亮度: alpha={alpha}, beta={beta}")
    return result


def demo_gaussian_blur(img: np.ndarray, ksize: int = 15) -> np.ndarray:
    """高斯模糊 — 整张图模糊。"""
    # ksize 必须为正奇数
    if ksize % 2 == 0:
        ksize += 1
    result = cv2.GaussianBlur(img, (ksize, ksize), sigmaX=0)
    print(f"[OP] 高斯模糊: kernel_size=({ksize},{ksize})")
    return result


# ================================================================
#  3. 人脸检测 + 自动模糊
# ================================================================

# 加载 Haar Cascade 分类器 (OpenCV 内置)
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

if face_cascade.empty():
    print(f"[ERROR] 无法加载 Haar Cascade: {CASCADE_PATH}")
    sys.exit(1)


def detect_and_blur_faces(img: np.ndarray,
                          blur_strength: int = 31) -> np.ndarray:
    """
    检测人脸区域并用高斯模糊处理。

    参数:
      img            — 输入图像 (BGR)
      blur_strength  — 高斯核大小 (奇数, 越大越模糊)

    返回:
      处理后的图像, 人脸区域已被模糊
    """
    result = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 多尺度人脸检测
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,    # 每次缩小 10%
        minNeighbors=5,     # 至少 5 个相邻窗口确认
        minSize=(30, 30),   # 最小人脸尺寸
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    print(f"[DETECT] 检测到 {len(faces)} 个人脸")

    if blur_strength % 2 == 0:
        blur_strength += 1

    for i, (x, y, w, h) in enumerate(faces):
        # 提取人脸 ROI (Region of Interest)
        roi = result[y:y+h, x:x+w]

        # 对该区域做高斯模糊
        roi_blurred = cv2.GaussianBlur(roi, (blur_strength, blur_strength), sigmaX=0)

        # 写回原图
        result[y:y+h, x:x+w] = roi_blurred

        # 画检测框 (可选, 便于对比)
        cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)

        print(f"  Face #{i+1}: x={x}, y={y}, w={w}, h={h} → 已模糊 (kernel={blur_strength})")

    return result


# ================================================================
#  4. 结果保存
# ================================================================

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_result(img: np.ndarray, name: str):
    """保存图像到 output/ 目录。"""
    path = os.path.join(OUTPUT_DIR, name)
    cv2.imwrite(path, img)
    print(f"[SAVE] {path}")


# ================================================================
#  main
# ================================================================

def main():
    print("=" * 60)
    print("  Software_C1 — OpenCV 人脸模糊演示")
    print("  张杨亦航 (2524030231)")
    print("=" * 60)

    # 加载图像
    img_path = sys.argv[1] if len(sys.argv) > 1 else ""
    if not img_path:
        # 找不到文件就生成测试图
        img_path = "test_fallback"
    img = load_image(img_path)

    show_info(img)
    save_result(img, "01_original.jpg")

    # ---- 基础处理演示 ----
    print("\n--- 基础处理 ---")

    # 裁剪
    cropped = demo_crop(img)
    save_result(cropped, "02_cropped.jpg")

    # 对比度/亮度增强
    enhanced = demo_brightness_contrast(img, alpha=1.5, beta=20)
    save_result(enhanced, "03_enhanced.jpg")

    # 整图高斯模糊
    blurred_full = demo_gaussian_blur(img, ksize=15)
    save_result(blurred_full, "04_blurred_full.jpg")

    # ---- 人脸检测 + 模糊 (核心功能) ----
    print("\n--- 人脸检测 + 自动模糊 ---")

    result = detect_and_blur_faces(img, blur_strength=31)
    save_result(result, "05_face_blurred.jpg")

    # 对比: 更轻的模糊
    result_light = detect_and_blur_faces(img, blur_strength=11)
    save_result(result_light, "06_face_blurred_light.jpg")

    print(f"\n[DONE] 所有结果已保存到: {OUTPUT_DIR}")
    print("请查看 output/ 目录下的对比图片。")


if __name__ == "__main__":
    main()
