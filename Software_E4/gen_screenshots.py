"""
Software_E4 — 生成运行截图 (VGG-16 vs ResNet-18)
================================================
加载已训练权重, 统计参数量, 绘制 VGG vs ResNet 对比图。
准确率为 AutoDL RTX 5090 训练记录 (README 文档), 参数量为实时计算。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from cifar10_train import VGG16, ResNet18

os.makedirs('output', exist_ok=True)

# ---------- 加载权重 ----------
vgg = VGG16(num_classes=10)
resnet = ResNet18(num_classes=10)
vgg.load_state_dict(torch.load('output/VGG-16_best.pth', map_location='cpu'))
resnet.load_state_dict(torch.load('output/ResNet-18_best.pth', map_location='cpu'))

vgg_params = sum(p.numel() for p in vgg.parameters())
resnet_params = sum(p.numel() for p in resnet.parameters())

# 训练记录 (README/notes 文档, AutoDL RTX 5090 完整训练)
vgg_acc = 0.9072
resnet_acc = 0.9396

print('=' * 60)
print('  Software_E4 — VGG-16 vs ResNet-18 对比')
print('=' * 60)
print(f'  VGG-16    参数量: {vgg_params:,}')
print(f'  ResNet-18 参数量: {resnet_params:,}')
print(f'  VGG-16    测试准确率: {vgg_acc:.4f}  (训练记录)')
print(f'  ResNet-18 测试准确率: {resnet_acc:.4f}  (训练记录)')

# ---------- 图1: 参数量对比 ----------
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].bar(['VGG-16', 'ResNet-18'], [vgg_params, resnet_params],
            color=['#4C72B0', '#55A868'], width=0.5)
for i, v in enumerate([vgg_params, resnet_params]):
    axes[0].text(i, v + vgg_params * 0.02, f'{v/1e6:.1f}M',
                 ha='center', fontweight='bold')
axes[0].set_ylabel('Parameters')
axes[0].set_title('Model Size (parameters)')

axes[1].bar(['VGG-16', 'ResNet-18'], [vgg_acc, resnet_acc],
            color=['#4C72B0', '#55A868'], width=0.5)
for i, v in enumerate([vgg_acc, resnet_acc]):
    axes[1].text(i, v + 0.01, f'{v:.4f}', ha='center', fontweight='bold')
axes[1].set_ylim(0, 1)
axes[1].set_ylabel('Test Accuracy (CIFAR-10)')
axes[1].set_title('Accuracy (AutoDL RTX 5090, 80 epochs)')

plt.tight_layout()
plt.savefig('output/e4_vgg_resnet_comparison.png', dpi=130)
plt.close()

print(f'[图] VGG vs ResNet 对比 -> output/e4_vgg_resnet_comparison.png')
print('完成。')
