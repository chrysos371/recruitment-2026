# Software_C2 — YOLO 目标检测（社区人员/非社区人员/电动车）

## 自我介绍

我是张杨亦航（学号 2524030231）。这道题从数据标注到模型训练走通了完整的 YOLO 目标检测流程——先用 YOLOv8n 预训练模型（COCO）自动生成初始标注框，再人工修正类别标签，最后微调训练。相比从零画框，预标注节省了大量时间。

当前 PyTorch 为 CPU 版本（Python 3.14 CUDA wheel 需 nightly build），训练在 CPU 上进行。68 张图数据量小，YOLOv8n 参数量仅 3.2M，CPU 可承受。

---

## 方案设计

### 类别定义

| ID | 类别 | 说明 |
|:--:|------|------|
| 0 | community_person | 社区人员（穿制服/在岗） |
| 1 | non_community_person | 非社区人员（普通行人/访客） |
| 2 | electric_bike | 电动车 |

### 自动预标注 → 人工修正

```
原始图片 (68张)
    ↓ YOLOv8n COCO 预训练模型
自动检测: person(COCO 0) → community_person(0)
          motorcycle(COCO 3) → electric_bike(2)
    ↓ 生成 530 个预标注框
人工修正:
  - 区分 community vs non_community
  - 补充漏检 / 删除误检
    ↓
最终标注 → YOLOv8 微调训练
```

### 训练策略

- **模型**: YOLOv8n (nano, 3.2M 参数) — 小数据集避免过拟合
- **预训练权重**: COCO 预训练 → 迁移学习
- **数据增强**: HSV 扰动、旋转、平移、缩放、Mosaic
- **超参**: lr=0.01, epochs=100, batch=16
- **评估**: mAP@50, mAP@50-95

---

## 使用方法

### 1. 自动预标注（已完成）

```bash
cd Software_C2/src
python auto_annotate.py
```

输出: `dataset/images/train/` (68 图) + `dataset/labels/train/` (530 框)

### 2. 人工修正标注（需手动完成）

推荐工具: [makesense.ai](https://www.makesense.ai/)（网页端，免安装）

修正要点:
- 所有 person 默认标为 class 0 (community_person)
- 根据参考图（`reference/` 目录），红框内为非社区人员 → 改为 class 1
- 确认电动车标注是否准确
- 补充模型漏检的目标
- 删除模型误检的框

### 3. 训练

```bash
python train.py
```

### 4. 推理

```bash
python infer.py                  # 对所有图片推理
python infer.py <image_path>     # 对单张图片推理
```

---

## 文件结构

```
Software_C2/
├── people_electrocar_*.jpg      # 原始图片 (68张)
├── reference/                   # 标注参考图
├── dataset.yaml                 # YOLO 数据集配置
├── dataset/
│   ├── images/train/            # 训练图片
│   └── labels/train/            # YOLO 格式标注 (待人工修正)
├── src/
│   ├── auto_annotate.py         # 自动预标注脚本
│   ├── train.py                 # 训练脚本
│   └── infer.py                 # 推理/可视化脚本
├── runs/                        # 训练输出 (best.pt + 日志)
├── output/                      # 推理结果图片
├── README.md
└── notes.md
```
