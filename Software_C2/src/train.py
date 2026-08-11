"""
Software_C2 — YOLO 目标检测训练 (train.py)
=============================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

基于预标注数据训练 YOLOv8 目标检测模型。
3类: community_person / non_community_person / electric_bike

用法:
  python train.py
"""

from pathlib import Path
from ultralytics import YOLO


def main():
    print("=" * 60)
    print("  C2 YOLOv8 目标检测训练")
    print("  张杨亦航 (2524030231)")
    print("=" * 60)

    # 数据配置文件
    data_yaml = Path(__file__).parent.parent / "dataset.yaml"

    # 加载预训练模型 (nano, 轻量快速)
    print("\n[1] 加载 YOLOv8n 预训练权重...")
    model = YOLO("yolov8n.pt")

    # 训练
    print("\n[2] 开始训练...")
    results = model.train(
        data=str(data_yaml),
        epochs=100,
        imgsz=640,
        batch=16,
        name="c2_detection",
        exist_ok=True,
        # 数据增强 (小数据集必需)
        hsv_h=0.015,      # 色调
        hsv_s=0.7,        # 饱和度
        hsv_v=0.4,        # 明度
        degrees=10.0,     # 旋转
        translate=0.1,    # 平移
        scale=0.5,        # 缩放
        shear=2.0,        # 剪切
        perspective=0.0,  # 透视
        flipud=0.0,       # 上下翻转
        fliplr=0.5,       # 左右翻转
        mosaic=0.5,       # Mosaic 增强
        # 超参
        lr0=0.01,         # 初始学习率
        lrf=0.01,         # 最终学习率 (余弦衰减)
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        warmup_momentum=0.8,
        # 其他
        device="cpu",     # 当前用 CPU, GPU 改为 "cuda" 或 "0"
        workers=4,
        seed=42,
        verbose=True,
    )

    print("\n[3] 训练完成!")
    print(f"  最佳模型: runs/detect/{results.save_dir.name}/weights/best.pt")
    print(f"  训练日志: runs/detect/{results.save_dir.name}/results.csv")

    # 验证
    print("\n[4] 验证集评估...")
    metrics = model.val()
    print(f"  mAP@50:    {metrics.box.map50:.4f}")
    print(f"  mAP@50-95: {metrics.box.map:.4f}")


if __name__ == "__main__":
    main()
