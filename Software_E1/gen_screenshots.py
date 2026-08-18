"""
Software_E1 — 生成运行截图 (BP 神经网络)
=========================================
加载预训练权重, 绘制 1D sin(x) 与 2D sin(x1)cos(x2) 拟合对比图。
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from test import NeuralNetwork1D, NeuralNetwork2D, Test

os.makedirs('output', exist_ok=True)

# ---------- 1D: sin(x) ----------
net1 = NeuralNetwork1D()
xs = np.linspace(0, 2 * math.pi, 500)
preds = np.array([net1.predict(x) for x in xs])
true = np.sin(xs)
mae1 = float(np.mean(np.abs(preds - true)))

plt.figure(figsize=(8, 5))
plt.plot(xs, true, 'b-', lw=2, label='ground truth  sin(x)')
plt.plot(xs, preds, 'r--', lw=2, label='NN prediction')
plt.xlabel('x')
plt.ylabel('y')
plt.title(f'BP Network 1D: fit sin(x)   (MAE = {mae1:.5f})')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('output/e1_1d_fit.png', dpi=130)
plt.close()

# ---------- 2D: sin(x1)·cos(x2) ----------
net2 = NeuralNetwork2D()
n = 60
x1 = np.linspace(0, 2 * math.pi, n)
x2 = np.linspace(0, 2 * math.pi, n)
X1, X2 = np.meshgrid(x1, x2)
Z_true = np.sin(X1) * np.cos(X2)
Z_pred = np.zeros_like(Z_true)
for i in range(n):
    for j in range(n):
        Z_pred[j, i] = net2.predict(X1[j, i], X2[j, i])
mae2 = float(np.mean(np.abs(Z_pred - Z_true)))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
im0 = axes[0].imshow(Z_true, cmap='viridis', origin='lower',
                     extent=[0, 2 * math.pi, 0, 2 * math.pi])
axes[0].set_title('ground truth  sin(x1)·cos(x2)')
axes[0].set_xlabel('x1'); axes[0].set_ylabel('x2')
im1 = axes[1].imshow(Z_pred, cmap='viridis', origin='lower',
                     extent=[0, 2 * math.pi, 0, 2 * math.pi])
axes[1].set_title(f'NN prediction   (MAE = {mae2:.5f})')
axes[1].set_xlabel('x1'); axes[1].set_ylabel('x2')
fig.colorbar(im1, ax=axes, fraction=0.046)
plt.tight_layout()
plt.savefig('output/e1_2d_fit.png', dpi=130)
plt.close()

# ---------- 打印官方 testbench 结果 ----------
print('=' * 60)
print('  Software_E1 testbench (官方评估)')
print('=' * 60)
t = Test()
t.testbench(0)   # 1D sin(x)
t.testbench(1)   # 2D sin(x1)cos(x2)
print()
print(f'[图] 1D MAE = {mae1:.5f}   -> output/e1_1d_fit.png')
print(f'[图] 2D MAE = {mae2:.5f}   -> output/e1_2d_fit.png')
print('完成。')
