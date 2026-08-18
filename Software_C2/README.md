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
  - 区分 community vs non_community (59 → 61 框)
  - 删除误检框 205 个 (框到树/路牌/车辆部件等)
  - 部分补充漏检 (受预标注偏好限制, 仍存在漏标)
    ↓
最终标注 325 框 → YOLOv8 微调训练
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

### 2. 人工修正标注（已完成）

用本地标注工具 `annotate_tool.py` 完成（替代 makesense.ai）：

```bash
python annotate_tool.py    # 左键切换 0↔1, 右键删框, n/p 翻页, q 退出
```

修正要点:
- 所有 person 默认标为 class 0 (community_person)
- 根据参考图（`reference/` 目录），红框内为非社区人员 → 改为 class 1
- 确认电动车标注是否准确
- 删除模型误检的框
- 补充模型漏检的目标（受预标注偏好限制，仍存在漏标）

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

## 数据标注的偏差与局限性（诚实说明）

本数据集采用「YOLOv8n 预标注 + 人工修正」的流程，存在以下固有偏差：

### 1. 漏标（召回缺口）

预标注模型（YOLOv8n COCO）存在检测偏好，对遮挡、小目标、密集人群、特殊姿态等场景容易漏检。人工修正主要以「删除误检 + 改类别」为主，难以逐图系统性补全所有漏检目标。因此**数据集中仍有部分真实目标未被标注**，这会直接限制模型召回率的上限。

### 2. 误检（精度偏差）

预标注共生成 530 框，人工清理后剩余 325 框（删除 205 个误检框，多为框到树木、路牌、车辆部件等非目标物）。清理后仍可能残留少量误检框。

### 3. 类别标注的主观性

「社区人员（穿制服）」与「非社区人员（便装）」的边界是主观判断，以下情况容易标错：
- 穿深色/单色便装的居民 vs 深色制服 → 易误判为社区人员
- 制服被遮挡或半脱 → 易误判为非社区人员

### 4. 单人标注，无一致性校验

整个数据集由单人完成标注，缺少多人交叉标注（inter-annotator agreement），标注的一致性与稳定性无法量化。工业级数据通常需要 2-3 人交叉标注 + 仲裁。

### 5. 预标注偏差传递

使用 COCO 预训练模型做预标注，其「person / motorcycle」的检测偏好（对尺寸、姿态、遮挡的敏感度）会传递到最终数据集的框质量上。

> 上述偏差意味着：本模型的 mAP 指标反映的是「在这个有偏差的数据集上」的表现；实际部署到新的社区监控场景时，召回率可能进一步下降。

---

## 文件结构

```
Software_C2/
├── people_electrocar_*.jpg      # 原始图片 (68张)
├── reference/                   # 标注参考图
├── dataset.yaml                 # YOLO 数据集配置
├── dataset/
│   ├── images/train|val/        # 训练/验证图片
│   └── labels/train|val/        # YOLO 格式标注 (已人工修正)
├── annotate_tool.py             # 本地标注修正工具
├── make_contact_sheet.py        # 生成标注框缩略图总览
├── delete_boxes.py              # 批量删除误检框
├── src/
│   ├── auto_annotate.py         # 自动预标注脚本
│   ├── train.py                 # 训练脚本
│   └── infer.py                 # 推理/可视化脚本
├── runs/                        # 训练输出 (best.pt + 日志)
├── output/                      # 推理结果图片
├── README.md
└── notes.md
```
