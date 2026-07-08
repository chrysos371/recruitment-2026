"""
Software_E2 — Top-1 到 Top-5 准确率 (top5_acc.py)
====================================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

Top-k 准确率含义:
  Top-1 准确率 = 模型最有可能的预测 == 真实标签 的比例 (即常规准确率)
  Top-5 准确率 = 真实标签出现在模型预测的前 5 个类别中的比例

  对于 MNIST (10 类), Top-5 准确率几乎总是接近 100%,
  因为模型很少把正确答案排到第 6 名之后。

  在 ImageNet (1000 类) 等大规模分类任务中, Top-5 更有意义 ——
  即使第一名预测错误, 模型可能已经"理解"了图像内容 (如把"豹"预测为"猎豹"),
  Top-5 能更公平地衡量模型的语义理解能力。
"""

import torch
import os

from utils import load_mnist, split_data, get_dataloaders, topk_accuracy

# 导入模型定义 (与 main.py / cnn.py 一致)
from main import MLP
from cnn import CNN


def main():
    os.makedirs("model", exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[DEVICE] {device}")

    # ---------- 加载数据 ----------
    X, y = load_mnist("mnist_x.txt", "mnist_y.txt")
    X_train, X_test, y_train, y_test = split_data(X, y)
    _, test_loader = get_dataloaders(X_train, X_test, y_train, y_test, batch_size=128)

    # ---------- MLP Top-k ----------
    print("\n" + "=" * 60)
    print("  MLP Top-1 ~ Top-5 准确率")
    print("=" * 60)

    mlp = MLP(hidden_sizes=(512, 256, 128), dropout=0.3).to(device)
    mlp.load_state_dict(torch.load("model/mlp.pth", map_location=device, weights_only=True))

    topk_mlp = topk_accuracy(mlp, test_loader, device, k=5)
    for k, acc in topk_mlp.items():
        print(f"  Top-{k}: {acc:.4f} ({acc*100:.2f}%)")

    # ---------- CNN Top-k ----------
    print("\n" + "=" * 60)
    print("  CNN Top-1 ~ Top-5 准确率")
    print("=" * 60)

    cnn = CNN().to(device)
    cnn.load_state_dict(torch.load("model/cnn.pth", map_location=device, weights_only=True))

    topk_cnn = topk_accuracy(cnn, test_loader, device, k=5)
    for k, acc in topk_cnn.items():
        print(f"  Top-{k}: {acc:.4f} ({acc*100:.2f}%)")

    # ---------- 对比 ----------
    print("\n" + "=" * 60)
    print("  MLP vs CNN Top-k 对比")
    print("=" * 60)
    print(f"{'k':>6}  {'MLP':>10}  {'CNN':>10}")
    print("-" * 30)
    for k in range(1, 6):
        print(f"{'Top-'+str(k):>6}  {topk_mlp[k]:.4f}     {topk_cnn[k]:.4f}")


if __name__ == "__main__":
    main()
