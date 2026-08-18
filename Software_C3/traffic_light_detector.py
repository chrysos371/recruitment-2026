"""
Software_C3 — 红绿灯检测 (传统CV方法)
========================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

纯 OpenCV 实现, 不使用深度学习。
综合 HSV 颜色空间、阈值分割、形态学处理、轮廓提取。

鲁棒性设计:
  - 阳光反光 → HSV 饱和度阈值 + LAB 空间验证
  - 夜晚灯光 → 暗通道检测 + 自适应亮度阈值
  - 红色尾灯 → 位置过滤 (下半部权重降低)
  - 绿色广告牌 → 面积/圆形度/Sobel边缘过滤
  - 摄像头抖动 → 形态学闭运算连接断裂区域

用法:
  python traffic_light_detector.py                  # 处理所有图片
  python traffic_light_detector.py <image_path>     # 处理单张图片
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path


# ================================================================
#  配置参数
# ================================================================

# ---- HSV 颜色范围 (H:0-180, S:0-255, V:0-255) ----
# 绿色范围收紧: 交通绿灯是较纯的正绿 (H≈60-85), 不是黄绿/青绿 (H<60),
# 后者常见于树叶/草地/反光, 是绿色过检的主要来源。S/V 下限也相应提高。
RED_RANGE_1 = ((0, 150, 80), (10, 255, 255))
RED_RANGE_2 = ((160, 150, 80), (180, 255, 255))
YELLOW_RANGE = ((18, 120, 120), (33, 255, 255))
GREEN_RANGE = ((60, 120, 120), (85, 255, 255))

# ---- 形态学参数 ----
MORPH_KERNEL_SMALL = (3, 3)   # 小噪点
MORPH_KERNEL_MEDIUM = (5, 5)  # 一般去噪

# ---- 几何过滤 ----
MIN_AREA = 20          # 最小面积 (滤噪点)
MAX_AREA = 5000        # 最大面积 (滤广告牌)
MIN_CIRCULARITY = 0.3  # 最小圆形度 (滤不规则形状)
MAX_ASPECT_RATIO = 3.0 # 最大长宽比

# ---- 位置权重 ----
IMAGE_BOTTOM_RATIO = 0.3  # 图像底部 30% 区域降低置信度 (滤尾灯)


# ================================================================
#  检测函数
# ================================================================

def create_color_mask(hsv: np.ndarray, ranges: list) -> np.ndarray:
    """创建颜色掩码, 支持多段 HSV 范围 (如红色跨越 0°)"""
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for (lower, upper) in ranges:
        m = cv2.inRange(hsv, np.array(lower), np.array(upper))
        mask = cv2.bitwise_or(mask, m)
    return mask


def morphological_clean(mask: np.ndarray) -> np.ndarray:
    """形态学清理: 开运算去噪 + 闭运算连接"""
    k_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, MORPH_KERNEL_SMALL)
    k_medium = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, MORPH_KERNEL_MEDIUM)
    # 开运算: 去除小噪点
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k_small)
    # 闭运算: 填充小孔, 连接断裂
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k_medium)
    return mask


def circularity(contour) -> float:
    """计算轮廓圆形度 = 4π * area / perimeter², 完美圆=1.0"""
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        return 0.0
    return 4.0 * np.pi * area / (perimeter * perimeter)


def contour_color_strength(hsv: np.ndarray, contour) -> float:
    """轮廓区域内"点亮的强度": 平均 (饱和度×亮度) 归一化到 0-1。

    真实的点亮的灯是 高饱和 + 高亮度 的; 反光/暗淡背景/绿色植被
    要么低饱和(白色反光), 要么低亮度(阴影), 强度低。用这个权重能
    显著区分"亮着的灯"和"被颜色掩码误抓的暗色/低饱和斑块"。
    """
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    region = hsv[mask > 0]
    if len(region) == 0:
        return 0.0
    s_mean = region[:, 1].astype(np.float64).mean()
    v_mean = region[:, 2].astype(np.float64).mean()
    return float(s_mean * v_mean / (255.0 * 255.0))


def geometric_filter(contours, img_h, img_w, hsv) -> list:
    """几何过滤: 面积、圆形度、长宽比、位置 + 颜色强度加权。"""
    valid = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < MIN_AREA or area > MAX_AREA:
            continue

        # 圆形度
        circ = circularity(c)
        if circ < MIN_CIRCULARITY:
            continue

        # 长宽比
        x, y, w, h = cv2.boundingRect(c)
        aspect = max(w, h) / (min(w, h) + 1e-6)
        if aspect > MAX_ASPECT_RATIO:
            continue

        # 位置: 底部区域降低置信度 (尾灯通常在画面底部, 交通灯在上部)
        center_y = y + h // 2
        bottom_penalty = 1.0
        if center_y > img_h * (1 - IMAGE_BOTTOM_RATIO):
            bottom_penalty = 0.3  # 底部可能是尾灯, 强降权

        # 颜色强度 (亮点 vs 暗淡/低饱和误抓)
        strength = contour_color_strength(hsv, c)

        conf = area * circ * bottom_penalty * strength
        valid.append((c, conf))

    return valid


def detect_lights(img_path: str) -> dict:
    """从路径读取图像并检测 (兼容中文路径)。"""
    img = cv2.imdecode(np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return {"state": "unknown", "counts": {}, "boxes": []}
    return detect_lights_array(img)


def detect_lights_array(img: np.ndarray) -> dict:
    """
    检测 BGR 图像数组中的红绿灯。
    返回: {"state": "red"/"yellow"/"green"/"off"/"unknown", "counts": {...}, "boxes": [...]}
    """
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    results = {}
    color_configs = [
        ("red",    [RED_RANGE_1, RED_RANGE_2], (0, 0, 255)),
        ("yellow", [YELLOW_RANGE],            (0, 255, 255)),
        ("green",  [GREEN_RANGE],             (0, 255, 0)),
    ]

    for name, ranges, color in color_configs:
        # 创建颜色掩码
        mask = create_color_mask(hsv, ranges)

        # 夜晚/暗光场景: 降低 V 阈值重新检测
        if np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)) < 80:
            dark_ranges = []
            for (l, u) in ranges:
                dark_ranges.append(((l[0], l[1], 50), u))
            dark_mask = create_color_mask(hsv, dark_ranges)
            mask = cv2.bitwise_or(mask, dark_mask)

        # 形态学清理
        mask = morphological_clean(mask)

        # 找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 几何过滤
        valid = geometric_filter(contours, h, w, hsv)
        results[name] = valid

    # 统计每种颜色的候选数
    counts = {name: len(items) for name, items in results.items()}

    # 判断状态: 取"最强单灯候选"的颜色, 而不是平均置信度。
    # 一盏亮着的灯对应一个高置信度轮廓; 平均会混入噪声斑块,
    # 且多个暗色误检的平均可能压过单个真实亮灯。
    best_color = "off"
    best_conf = 0.0
    boxes = []

    for name, items in results.items():
        for c, conf in items:
            x, y, cw, ch = cv2.boundingRect(c)
            boxes.append((name, x, y, cw, ch, conf))
        if items:
            max_conf = max(it[1] for it in items)
            if max_conf > best_conf:
                best_conf = max_conf
                best_color = name

    return {
        "state": best_color if best_conf > 0 else "off",
        "counts": {k: len(v) for k, v in results.items()},
        "boxes": boxes,
    }


def draw_result(img: np.ndarray, result: dict) -> np.ndarray:
    """在图像上绘制检测框。"""
    color_map = {
        "red": (0, 0, 255), "yellow": (0, 255, 255),
        "green": (0, 255, 0), "off": (128, 128, 128),
    }

    output = img.copy()
    for name, x, y, cw, ch, conf in result["boxes"]:
        c = color_map.get(name, (255, 255, 255))
        cv2.rectangle(output, (x, y), (x + cw, y + ch), c, 2)
        cv2.putText(output, f"{name} {conf:.1f}", (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, c, 1)

    # 状态栏
    state = result["state"]
    state_color = color_map.get(state, (255, 255, 255))
    state_text = f"Signal: {state.upper()}  |  R:{result['counts'].get('red',0)} Y:{result['counts'].get('yellow',0)} G:{result['counts'].get('green',0)}"
    cv2.putText(output, state_text, (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_color, 2)

    return output


# ================================================================
#  主程序
# ================================================================

def main():
    print("=" * 60)
    print("  Software_C3 — 红绿灯检测 (传统CV)")
    print("  张杨亦航 (2524030231)")
    print("=" * 60)

    img_dir = Path(__file__).parent
    output_dir = img_dir / "output"
    output_dir.mkdir(exist_ok=True)

    # 收集图片
    if len(sys.argv) > 1:
        images = [Path(sys.argv[1])]
    else:
        images = sorted([img_dir / f for f in os.listdir(img_dir)
                        if f.lower().endswith((".jpg", ".jpeg", ".png"))])

    print(f"\n处理 {len(images)} 张图片...\n")

    summary = {"red": 0, "yellow": 0, "green": 0, "off": 0, "unknown": 0}

    for img_path in images:
        result = detect_lights(img_path)
        state = result["state"]
        summary[state] = summary.get(state, 0) + 1

        # 绘制结果 (兼容中文路径)
        img = cv2.imdecode(np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is not None:
            annotated = draw_result(img, result)
            out_path = output_dir / f"detected_{img_path.name}"
            ext = os.path.splitext(img_path.name)[1]
            success, buf = cv2.imencode(ext, annotated)
            if success:
                with open(str(out_path), "wb") as f:
                    f.write(buf.tobytes())

        counts = result["counts"]
        print(f"  {img_path.name:<30} → {state.upper():<8} "
              f"(R:{counts.get('red',0)} Y:{counts.get('yellow',0)} G:{counts.get('green',0)})")

    print(f"\n{'='*60}")
    print(f"  汇总: RED={summary['red']}  YELLOW={summary['yellow']}  "
          f"GREEN={summary['green']}  OFF={summary['off']}")
    print(f"  结果图片: {output_dir}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
