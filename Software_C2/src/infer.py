"""
Software_C2 — YOLO 推理/可视化 (infer.py)
===========================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

对图片或视频进行推理, 绘制检测框并保存结果。

用法:
  python infer.py                      # 对数据集图片推理
  python infer.py <image_path>         # 对单张图片推理
"""

import os, sys
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO


CLASS_NAMES = {
    0: "community_person",
    1: "non_community_person",
    2: "electric_bike",
}

COLORS = {
    0: (0, 255, 0),    # 社区人员: 绿色
    1: (0, 0, 255),    # 非社区人员: 红色
    2: (255, 0, 0),    # 电动车: 蓝色
}


def imread_cn(path):
    """兼容中文路径的图片读取 (cv2.imread 不支持中文路径)"""
    data = np.fromfile(str(path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imwrite_cn(path, img):
    """兼容中文路径的图片写入 (cv2.imwrite 不支持中文路径)"""
    ext = os.path.splitext(str(path))[1]
    success, buf = cv2.imencode(ext, img)
    if success:
        with open(str(path), "wb") as f:
            f.write(buf.tobytes())
    return success


def find_best_model():
    """自动查找最新训练的 best.pt 模型"""
    runs_dir = Path(__file__).parent.parent / "runs" / "detect"
    if not runs_dir.exists():
        return None
    # 按修改时间排序, 找最新的 best.pt
    candidates = sorted(runs_dir.glob("*/weights/best.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def draw_boxes(img, results):
    """在图像上绘制检测框。"""
    if results[0].boxes is None:
        return img

    boxes = results[0].boxes
    for i in range(len(boxes)):
        cls_id = int(boxes.cls[i].item())
        conf = float(boxes.conf[i].item())
        x1, y1, x2, y2 = map(int, boxes.xyxy[i].tolist())

        color = COLORS.get(cls_id, (255, 255, 255))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

        label = f"{CLASS_NAMES.get(cls_id, '?')} {conf:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_bg_y1 = max(y1 - th - 4, 0)
        cv2.rectangle(img, (x1, label_bg_y1), (x1 + tw, y1), color, -1)
        cv2.putText(img, label, (x1, y1 - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return img


def main():
    print("=" * 60)
    print("  C2 YOLO 推理/可视化")
    print("=" * 60)

    # 加载模型 (自动查找最新训练结果)
    model_path = find_best_model()
    if model_path is None:
        # 回退到 c2_verify
        model_path = Path(__file__).parent.parent / "runs" / "detect" / "c2_verify" / "weights" / "best.pt"
    if not model_path.exists():
        print(f"[ERROR] 模型不存在: {model_path}")
        print("请先运行 train.py 训练模型")
        sys.exit(1)

    print(f"[INFO] 使用模型: {model_path}")
    model = YOLO(str(model_path))

    # 输出目录
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    # 推理
    if len(sys.argv) > 1:
        # 单张图片
        img_path = sys.argv[1]
        results = model(img_path)
        img = imread_cn(img_path)
        if img is None:
            print(f"[ERROR] 无法读取图片: {img_path}")
            sys.exit(1)
        img = draw_boxes(img, results)
        out_path = output_dir / ("infer_" + Path(img_path).name)
        imwrite_cn(out_path, img)
        print(f"  结果: {out_path}")
    else:
        # 数据集图片
        img_dir = Path(__file__).parent.parent
        count = 0
        for f in sorted(os.listdir(img_dir)):
            if f.lower().endswith((".jpg", ".png", ".jpeg")):
                img_path = img_dir / f
                results = model(str(img_path))
                img = imread_cn(img_path)
                if img is None:
                    continue
                img = draw_boxes(img, results)
                out_path = output_dir / ("infer_" + f)
                imwrite_cn(out_path, img)
                count += 1
        print(f"  推理完成: {count} 张图片 → {output_dir}")


if __name__ == "__main__":
    main()
