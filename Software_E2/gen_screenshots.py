"""
Software_E2 — 生成运行截图 (MNIST MLP vs CNN)
=============================================
加载已训练权重, 在测试集上评估并绘制对比图 + 预测样例网格。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils import load_mnist, split_data, get_dataloaders, evaluate
from main import MLP
from cnn import CNN

os.makedirs('output', exist_ok=True)
device = torch.device('cpu')

# ---------- 数据 ----------
X, y = load_mnist('mnist_x.txt', 'mnist_y.txt')
X_train, X_test, y_train, y_test = split_data(X, y)

# ---------- 加载模型 ----------
mlp = MLP(hidden_sizes=(512, 256, 128), dropout=0.3).to(device)
mlp.load_state_dict(torch.load('model/mlp.pth', map_location=device))
cnn = CNN().to(device)
cnn.load_state_dict(torch.load('model/cnn.pth', map_location=device))

_, test_loader = get_dataloaders(X_train, X_test, y_train, y_test, batch_size=256)

mlp_acc = evaluate(mlp, test_loader, device)
cnn_acc = evaluate(cnn, test_loader, device)

print('=' * 60)
print('  Software_E2 — MNIST MLP vs CNN (测试集)')
print('=' * 60)
print(f'  MLP 准确率: {mlp_acc:.4f}')
print(f'  CNN 准确率: {cnn_acc:.4f}')

# ---------- 图1: 准确率对比 ----------
plt.figure(figsize=(7, 5))
names = ['MLP\n(3 hidden layers)', 'CNN\n(2 conv + 2 fc)']
vals = [mlp_acc, cnn_acc]
bars = plt.bar(names, vals, color=['#4C72B0', '#C44E52'], width=0.5)
for b, v in zip(bars, vals):
    plt.text(b.get_x() + b.get_width() / 2, v + 0.005, f'{v:.4f}',
             ha='center', fontweight='bold')
plt.ylim(0, 1)
plt.ylabel('Test Accuracy')
plt.title('MNIST: MLP vs CNN')
plt.tight_layout()
plt.savefig('output/e2_accuracy_comparison.png', dpi=130)
plt.close()

# ---------- 图2: 预测样例 ----------
mlp.eval(); cnn.eval()
n_cols, n_rows = 8, 3
idx = np.arange(60000, 60000 + n_cols * n_rows)
X_sample = torch.from_numpy(X_test[:n_cols * n_rows]).to(device)
y_sample = y_test[:n_cols * n_rows]

with torch.no_grad():
    pred_mlp = mlp(X_sample).argmax(1).cpu().numpy()
    pred_cnn = cnn(X_sample).argmax(1).cpu().numpy()

fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 1.3, n_rows * 1.6))
for i, ax in enumerate(axes.flat):
    ax.imshow(X_test[i].reshape(28, 28), cmap='gray')
    ok_mlp = (pred_mlp[i] == y_sample[i])
    ok_cnn = (pred_cnn[i] == y_sample[i])
    color_mlp = 'green' if ok_mlp else 'red'
    color_cnn = 'green' if ok_cnn else 'red'
    ax.set_title(f'T{y_sample[i]} M{pred_mlp[i]} C{pred_cnn[i]}',
                 fontsize=9, color='black')
    ax.axis('off')
fig.suptitle('Sample predictions  (T=true, M=MLP, C=CNN)', fontsize=12)
plt.tight_layout()
plt.savefig('output/e2_sample_predictions.png', dpi=130)
plt.close()

print(f'[图] 准确率对比 -> output/e2_accuracy_comparison.png')
print(f'[图] 预测样例   -> output/e2_sample_predictions.png')
print('完成。')
