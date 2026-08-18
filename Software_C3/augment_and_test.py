"""
Software_C3 — 干扰数据集构建 + 鲁棒性验证
============================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

题目要求: 借助数据增强构建受干扰数据集, 验证算法在
  阳光反光 / 夜晚灯光 / 红色车尾灯 / 绿色广告牌 / 摄像头抖动
  以及"熄灭"状态下的鲁棒性。

本脚本对全部 40 张原始图各生成 6 类增强(5 干扰 + 1 熄灭),
再对增强图跑检测, 统计状态在干扰前后是否保持一致(鲁棒率)。

用法:
  python augment_and_test.py            # 生成全部增强图并检测
  python augment_and_test.py --limit 5  # 只处理前 5 张(快速演示)
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path

import traffic_light_detector as tld


# ================================================================
#  数据增强函数 (每类返回增强后的 BGR 图)
# ================================================================

def read_img(path):
    return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)


def save_img(img, path):
    ext = os.path.splitext(path)[1] or '.jpg'
    ok, buf = cv2.imencode(ext, img)
    if ok:
        with open(str(path), 'wb') as f:
            f.write(buf.tobytes())


def aug_glare(img, rng):
    """阳光反光: 叠加多个高斯亮斑 (高亮度低饱和度, 类似镜面反光)。"""
    out = img.astype(np.float32)
    h, w = out.shape[:2]
    for _ in range(4):
        cx, cy = rng.integers(0, w), rng.integers(0, h)
        r = int(rng.integers(40, 120))
        spot = np.zeros((h, w, 3), np.float32)
        cv2.circle(spot, (cx, cy), r, (255, 255, 255), -1)
        spot = cv2.GaussianBlur(spot, (0, 0), r / 3)
        out = cv2.addWeighted(out, 1.0, spot, rng.uniform(0.35, 0.55), 0)
    return np.clip(out, 0, 255).astype(np.uint8)


def aug_night(img, rng):
    """夜晚灯光干扰: 整体压暗 + 叠加多个高亮小光点(路灯/霓虹)。"""
    out = cv2.convertScaleAbs(img, alpha=0.35, beta=-20)
    h, w = out.shape[:2]
    for _ in range(6):
        cx, cy = rng.integers(0, w), rng.integers(0, h)
        r = int(rng.integers(2, 8))
        color = (255, 255, 255) if rng.random() > 0.5 else (255, 255, 200)
        cv2.circle(out, (cx, cy), r, color, -1)
    return out


def aug_taillight(img, rng):
    """红色车尾灯误检: 在图像底部区域叠加红色圆形光斑。"""
    out = img.copy()
    h, w = out.shape[:2]
    for _ in range(3):
        cx = int(rng.integers(w // 6, w * 5 // 6))
        cy = int(rng.integers(h * 7 // 10, h - 10))
        r = int(rng.integers(10, 25))
        # 红色光斑 (BGR: 0,0,255) + 高斯晕影
        spot = np.zeros_like(out)
        cv2.circle(spot, (cx, cy), r, (0, 0, 220), -1)
        spot = cv2.GaussianBlur(spot, (0, 0), r / 2)
        out = cv2.addWeighted(out, 1.0, spot, 0.9, 0)
    return out


def aug_billboard(img, rng):
    """绿色广告牌误检: 在画面中上部叠加大面积绿色矩形。"""
    out = img.copy()
    h, w = out.shape[:2]
    bw = int(w * rng.uniform(0.3, 0.5))
    bh = int(bw * rng.uniform(0.6, 0.8))
    x = int(rng.integers(0, max(1, w - bw)))
    y = int(rng.integers(0, max(1, h // 2 - bh)))
    # 绿色矩形 (BGR: 0,160,0)
    cv2.rectangle(out, (x, y), (x + bw, y + bh), (0, 160, 0), -1)
    return out


def aug_blur(img, rng):
    """摄像头抖动: 运动模糊 (水平方向 + 轻微垂直)。"""
    k = 15
    kernel = np.zeros((k, k), np.float32)
    kernel[k // 2, :] = 1.0 / k          # 水平运动
    kernel[:, k // 2] += 0.4 / k         # 加一点垂直分量
    kernel /= kernel.sum()
    return cv2.filter2D(img, -1, kernel)


def aug_off(img, rng):
    """熄灭: 将高饱和高亮区域(灯)的亮度压到阈值以下, 模拟灯灭, 场景不变。"""
    out = img.copy()
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    lamp = (S > 100) & (V > 80)
    V = V.astype(np.float32)
    V[lamp] *= 0.12   # 压到 10-30, 远低于任何颜色阈值 → 判为 off
    hsv[:, :, 2] = np.clip(V, 0, 255).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


AUGMENTATIONS = [
    ("glare",     aug_glare,     "阳光反光"),
    ("night",     aug_night,     "夜晚灯光"),
    ("taillight", aug_taillight, "红色车尾灯"),
    ("billboard", aug_billboard, "绿色广告牌"),
    ("blur",      aug_blur,      "摄像头抖动"),
    ("off",       aug_off,       "熄灭"),
]


# ================================================================
#  主程序
# ================================================================

def main():
    limit = None
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])

    base = Path(__file__).parent
    disturbed_dir = base / "disturbed"
    out_dir = disturbed_dir / "output"
    disturbed_dir.mkdir(exist_ok=True)
    out_dir.mkdir(exist_ok=True)

    images = sorted([base / f for f in os.listdir(base)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    if limit:
        images = images[:limit]

    rng = np.random.default_rng(42)

    # 统计: 每类增强下, 状态与"原图状态"一致的比例 (鲁棒率)
    stability = {name: {"same": 0, "total": 0} for name, _, _ in AUGMENTATIONS}
    state_dist = {name: {} for name, _, _ in AUGMENTATIONS}

    print("=" * 62)
    print("  Software_C3 — 干扰数据集构建 + 鲁棒性验证")
    print("  张杨亦航 (2524030231)")
    print("=" * 62)
    print(f"  处理 {len(images)} 张原始图 × {len(AUGMENTATIONS)} 类增强\n")

    for img_path in images:
        img = read_img(img_path)
        if img is None:
            continue
        clean_state = tld.detect_lights(img_path)["state"]

        for name, func, label in AUGMENTATIONS:
            aug_img = func(img, rng)
            aug_path = disturbed_dir / f"{name}_{img_path.name}"
            save_img(aug_img, aug_path)

            # 直接对增强图数组做检测 (避免再读盘 + 中文路径)
            res = tld.detect_lights_array(aug_img)
            state = res["state"]

            stability[name]["total"] += 1
            if state == clean_state:
                stability[name]["same"] += 1

            state_dist[name][state] = state_dist[name].get(state, 0) + 1

            # 保存标注结果
            annotated = tld.draw_result(aug_img, res)
            save_img(annotated, out_dir / f"detected_{name}_{img_path.name}")

    # ---------- 汇总 ----------
    print(f"\n{'='*62}")
    print(f"  鲁棒性汇总 (状态在干扰前后保持一致的比例)")
    print(f"{'='*62}")
    print(f"  {'干扰类型':<12} {'一致':>6} {'总数':>6} {'鲁棒率':>8}   状态分布")
    print(f"  {'-'*56}")
    for name, _, label in AUGMENTATIONS:
        st = stability[name]
        rate = st["same"] / st["total"] if st["total"] else 0
        dist = " ".join(f"{k}:{v}" for k, v in sorted(state_dist[name].items()))
        print(f"  {label:<12} {st['same']:>6} {st['total']:>6} {rate:>7.1%}   {dist}")

    print(f"\n  增强图目录: {disturbed_dir}/")
    print(f"  检测结果目录: {out_dir}/")
    print(f"{'='*62}")


if __name__ == "__main__":
    main()
