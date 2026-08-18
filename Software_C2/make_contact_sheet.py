"""
Software_C2 — 生成标注框缩略图总览 (用于全量误检排查)
======================================================
把所有 person / bike 框裁出来, 拼成带编号的网格图, 方便快速扫一遍找出误检框。

输出:
  contact_sheet/page_XX.png   — 缩略图网格 (每页 48 个框, 带全局编号)
  contact_sheet/mapping.csv   — 编号 → (split, 图片名, 框序号, class) 映射

用法: 扫 page_*.png, 把"框到无关东西"的编号记下来, 告诉删除脚本即可。
"""

import cv2
import numpy as np
import os
from pathlib import Path

BASE = Path(__file__).parent
SPLITS = [("train", BASE / "dataset/images/train", BASE / "dataset/labels/train"),
          ("val", BASE / "dataset/images/val", BASE / "dataset/labels/val")]

CELL = 140          # 缩略图边长
PAD = 8             # 缩略图间距
COLS = 6            # 每页列数
ROWS = 8            # 每页行数
PER_PAGE = COLS * ROWS

CLASS_NAMES = {0: "community", 1: "non-comm", 2: "bike"}
CLASS_COLORS = {0: (255, 120, 0), 1: (0, 0, 255), 2: (0, 200, 0)}


def read_img(path):
    return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)


def crop_box(img, cx, cy, w, h):
    ih, iw = img.shape[:2]
    x1 = max(0, int((cx - w / 2) * iw)); x2 = min(iw, int((cx + w / 2) * iw))
    y1 = max(0, int((cy - h / 2) * ih)); y2 = min(ih, int((cy + h / 2) * ih))
    crop = img[y1:y2, x1:x2]
    if crop.size == 0:
        return np.zeros((CELL, CELL, 3), np.uint8)
    # 等比缩放 + 白底填充
    ch, cw = crop.shape[:2]
    r = min(CELL / ch, CELL / cw)
    crop = cv2.resize(crop, (int(cw * r), int(ch * r)))
    canvas = np.full((CELL, CELL, 3), 240, np.uint8)
    y0 = (CELL - crop.shape[0]) // 2
    x0 = (CELL - crop.shape[1]) // 2
    canvas[y0:y0 + crop.shape[0], x0:x0 + crop.shape[1]] = crop
    return canvas


def main():
    out_dir = BASE / "contact_sheet"
    out_dir.mkdir(exist_ok=True)

    # 收集所有框, 分配全局编号
    records = []  # (global_idx, split, img_name, box_idx, cls, crop)
    for split, img_dir, lab_dir in SPLITS:
        for lf in sorted(lab_dir.glob("*.txt")):
            img = read_img(img_dir / (lf.stem + ".jpg"))
            if img is None:
                continue
            boxes = []
            for ln in open(lf, encoding='utf-8'):
                p = ln.strip().split()
                if len(p) >= 5:
                    boxes.append((int(p[0]), *map(float, p[1:5])))
            for bi, (cls, cx, cy, w, h) in enumerate(boxes):
                if cls in (0, 1, 2):
                    crop = crop_box(img, cx, cy, w, h)
                    records.append((len(records) + 1, split, lf.stem, bi, cls, crop))

    # 写映射 csv
    with open(out_dir / "mapping.csv", "w", encoding='utf-8') as f:
        f.write("idx,split,image,box_idx,class\n")
        for idx, split, name, bi, cls, _ in records:
            f.write(f"{idx},{split},{name},{bi},{cls}\n")

    # 生成分页网格图
    n_pages = (len(records) + PER_PAGE - 1) // PER_PAGE
    for page in range(n_pages):
        page_records = records[page * PER_PAGE:(page + 1) * PER_PAGE]
        canvas_w = COLS * (CELL + PAD) + PAD
        canvas_h = ROWS * (CELL + PAD) + PAD
        canvas = np.full((canvas_h, canvas_w, 3), 255, np.uint8)
        for i, (idx, split, name, bi, cls, crop) in enumerate(page_records):
            r, c = divmod(i, COLS)
            y = PAD + r * (CELL + PAD)
            x = PAD + c * (CELL + PAD)
            canvas[y:y + CELL, x:x + CELL] = crop
            cv2.rectangle(canvas, (x, y), (x + CELL, y + CELL),
                          CLASS_COLORS.get(cls, (0, 0, 0)), 2)
            label = f"#{idx} {CLASS_NAMES.get(cls, cls)}"
            cv2.putText(canvas, label, (x + 2, y + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        png = out_dir / f"page_{page + 1:02d}.png"
        # 中文路径: 用 imencode + 二进制写, 避免 cv2.imwrite 不支持中文
        ok, buf = cv2.imencode('.png', canvas)
        if ok:
            with open(str(png), 'wb') as fh:
                fh.write(buf.tobytes())

    print(f"共 {len(records)} 个框, 生成 {n_pages} 页缩略图")
    print(f"输出目录: {out_dir}/")
    print(f"映射文件: mapping.csv")


if __name__ == "__main__":
    main()
