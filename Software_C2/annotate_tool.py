"""
Software_C2 — 本地标注修正工具 (无需 makesense.ai)
=====================================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

用法: 在 Software_C2/ 目录下运行
  python annotate_tool.py

操作:
  鼠标左键点击某个框  →  在 社区人员(0) 与 非社区人员(1) 之间切换
  鼠标右键点击某个框  →  删除该框 (误检/框到无关东西)
  n / →               →  保存并跳到下一张
  p / ←               →  保存并回到上一张
  s                   →  保存当前标注
  q / Esc             →  保存并退出

框颜色:
  蓝色  = class 0 社区人员(穿制服/在岗)
  红色  = class 1 非社区人员(普通行人/访客)
  绿色  = class 2 电动车 (点击不切换)
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path

CLASS_NAMES = {0: "community", 1: "non-comm", 2: "bike"}
CLASS_COLORS = {0: (255, 120, 0), 1: (0, 0, 255), 2: (0, 200, 0)}  # BGR

BASE = Path(__file__).parent
IMG_DIRS = [BASE / "dataset" / "images" / "train",
            BASE / "dataset" / "images" / "val"]
LAB_DIRS = [BASE / "dataset" / "labels" / "train",
            BASE / "dataset" / "labels" / "val"]

# ---- 全局状态 ----
images = []     # [(img_path, lab_path)]
idx = 0
img = None
disp = None
boxes = []      # [[cls, cx, cy, w, h], ...]
scale = 1.0
pad = (0, 0)


def read_img(path):
    return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)


def load_labels(path):
    boxes = []
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                p = line.strip().split()
                if len(p) >= 5:
                    boxes.append([int(p[0])] + [float(x) for x in p[1:5]])
    return boxes


def save_labels(path, boxes):
    with open(path, 'w', encoding='utf-8') as f:
        for cls, cx, cy, w, h in boxes:
            f.write(f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")


def load_image(i):
    global img, disp, boxes, scale, pad
    img_path, lab_path = images[i]
    img = read_img(img_path)
    if img is None:
        print(f"[警告] 无法读取 {img_path.name}")
        return
    boxes = load_labels(lab_path)
    # 缩放显示 (最长边 <= 900)
    h, w = img.shape[:2]
    scale = 900.0 / max(h, w)
    scale = min(1.0, scale)
    disp = cv2.resize(img, (int(w * scale), int(h * scale)))
    pad = (0, 0)


def redraw():
    global disp
    if img is None:
        return
    d = img.copy()
    h, w = d.shape[:2]
    for i, (cls, cx, cy, bw, bh) in enumerate(boxes):
        x1 = int((cx - bw / 2) * w); y1 = int((cy - bh / 2) * h)
        x2 = int((cx + bw / 2) * w); y2 = int((cy + bh / 2) * h)
        c = CLASS_COLORS.get(cls, (255, 255, 255))
        cv2.rectangle(d, (x1, y1), (x2, y2), c, 2)
        cv2.putText(d, f"{i}:{CLASS_NAMES.get(cls, cls)}", (x1, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, c, 1)
    counts = {}
    for b in boxes:
        counts[b[0]] = counts.get(b[0], 0) + 1
    name = os.path.basename(images[idx][0])
    info = f"{name}  [{idx+1}/{len(images)}]  " + \
           " | ".join(f"c{k}:{v}" for k, v in sorted(counts.items()))
    cv2.putText(d, info, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
    cv2.putText(d, info, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    disp = cv2.resize(d, (int(w * scale), int(h * scale)))


def on_mouse(event, x, y, flags, param):
    global boxes
    if img is None:
        return
    if event not in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN):
        return
    h, w = img.shape[:2]
    nx, ny = x / (w * scale), y / (h * scale)
    for i in range(len(boxes) - 1, -1, -1):
        cls, cx, cy, bw, bh = boxes[i]
        if abs(nx - cx) <= bw / 2 and abs(ny - cy) <= bh / 2:
            if event == cv2.EVENT_RBUTTONDOWN:
                del boxes[i]
                print(f"  删除框 {i} ({CLASS_NAMES.get(cls, cls)})")
            elif cls in (0, 1):
                boxes[i][0] = 1 - cls
                print(f"  框 {i}: {CLASS_NAMES[cls]} -> {CLASS_NAMES[1-cls]}")
            else:
                print(f"  框 {i}: 电动车, 不切换")
            break
    redraw()


def save_current():
    if images and boxes is not None:
        save_labels(images[idx][1], boxes)


def main():
    global idx
    # 收集所有图片
    for img_dir, lab_dir in zip(IMG_DIRS, LAB_DIRS):
        if not img_dir.exists():
            continue
        for img_path in sorted(img_dir.glob("*.jpg")):
            lab_path = lab_dir / (img_path.stem + ".txt")
            images.append((img_path, lab_path))
    if not images:
        print("未找到图片, 请确认 dataset/images/ 目录存在。")
        return

    print("=" * 55)
    print("  Software_C2 本地标注工具")
    print(f"  共 {len(images)} 张图 | 点击框切换 0(社区)↔1(非社区)")
    print("  n=下一张  p=上一张  s=保存  q=退出")
    print("=" * 55)

    cv2.namedWindow("annotate", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("annotate", on_mouse)
    load_image(0)
    redraw()

    while True:
        cv2.imshow("annotate", disp)
        key = cv2.waitKey(0) & 0xFF
        if key in (ord('q'), 27):        # q 或 Esc
            save_current()
            break
        elif key in (ord('n'), 83, 255):  # n 或 右箭头
            save_current()
            idx = min(idx + 1, len(images) - 1)
            load_image(idx); redraw()
        elif key in (ord('p'), 81):       # p 或 左箭头
            save_current()
            idx = max(idx - 1, 0)
            load_image(idx); redraw()
        elif key == ord('s'):
            save_current()
            print(f"  已保存 {os.path.basename(images[idx][1])}")

    cv2.destroyAllWindows()
    print("已退出。当前标注已保存。")


if __name__ == "__main__":
    main()
