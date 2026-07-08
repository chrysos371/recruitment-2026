"""
Software_C2 — YOLO 自动预标注 (auto_annotate.py)
====================================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

用 YOLOv8n (COCO预训练) 自动检测图片中的人和摩托车,
生成 YOLO 格式标注文件, 人工只需修正标签类别即可。

COCO 类别映射:
  person(0) → community_person(0)       [人工判断: 社区/非社区]
  motorcycle(3) → electric_bike(2)       [人工确认: 是否为电动车]

用法:
  python auto_annotate.py
"""

import os, shutil
from pathlib import Path
import cv2
from ultralytics import YOLO


# ================================================================
#  配置
# ================================================================

# 原始图片目录
IMAGE_DIR = Path(__file__).parent.parent  # Software_C2/
# 数据集目录
DATASET_DIR = IMAGE_DIR / "dataset"
TRAIN_IMG = DATASET_DIR / "images" / "train"
TRAIN_LBL = DATASET_DIR / "labels" / "train"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

# COCO → 我们的类别映射
# COCO: person=0, motorcycle=3
# 我们: community_person=0, non_community_person=1, electric_bike=2
COCO_TO_OURS = {
    0: 0,   # person → community_person (默认, 人工修正为非社区)
    3: 2,   # motorcycle → electric_bike
}

CONFIDENCE_THRESHOLD = 0.3  # 预标注置信度阈值 (偏低以提高召回)


# ================================================================
#  主逻辑
# ================================================================

def main():
    print("=" * 60)
    print("  C2 YOLO 自动预标注")
    print("  张杨亦航 (2524030231)")
    print("=" * 60)

    # 加载预训练 YOLOv8 nano
    print("\n[1] 加载 YOLOv8n (COCO 预训练)...")
    model = YOLO("yolov8n.pt")

    # 收集图片
    images = sorted([
        f for f in os.listdir(IMAGE_DIR)
        if Path(f).suffix.lower() in IMAGE_EXTENSIONS
    ])
    print(f"[2] 找到 {len(images)} 张图片")

    # 复制图片到 dataset + 生成预标注
    TRAIN_IMG.mkdir(parents=True, exist_ok=True)
    TRAIN_LBL.mkdir(parents=True, exist_ok=True)

    total_boxes = 0
    for fname in images:
        src = IMAGE_DIR / fname
        dst_img = TRAIN_IMG / fname
        dst_lbl = TRAIN_LBL / (Path(fname).stem + ".txt")

        # 复制图片
        shutil.copy2(src, dst_img)

        # 读取尺寸
        img = cv2.imread(str(src))
        h, w = img.shape[:2]

        # 推理
        results = model(src, verbose=False)

        # 提取检测结果并转换
        lines = []
        if results[0].boxes is not None:
            boxes = results[0].boxes
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                conf = float(boxes.conf[i].item())

                if cls_id not in COCO_TO_OURS or conf < CONFIDENCE_THRESHOLD:
                    continue

                our_cls = COCO_TO_OURS[cls_id]
                # YOLO 格式: x_center, y_center, width, height (归一化)
                x, y, bw, bh = boxes.xywhn[i].tolist()
                lines.append(f"{our_cls} {x:.6f} {y:.6f} {bw:.6f} {bh:.6f}")

        # 写入标注文件
        with open(dst_lbl, "w") as f:
            f.write("\n".join(lines))

        total_boxes += len(lines)
        if len(lines) > 0:
            print(f"  {fname}: {len(lines)} 个预标注框")

    print(f"\n[3] 完成! 共 {total_boxes} 个预标注框")
    print(f"  图片 → {TRAIN_IMG}")
    print(f"  标注 → {TRAIN_LBL}")
    print(f"\n[下一步] 人工修正:")
    print(f"  1. community_person (class 0) → 判断是否为非社区人员, 改为 class 1")
    print(f"  2. electric_bike (class 2) → 确认是否为电动车, 删除误检")
    print(f"  3. 补充未检测到的目标")
    print(f"  4. 推荐工具: makesense.ai (网页,免安装) 或 LabelImg")


if __name__ == "__main__":
    main()
