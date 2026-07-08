"""
Software_E2 — MNIST 数据加载与评估工具
========================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


def load_mnist(x_path: str, y_path: str):
    """
    从文本文件加载 MNIST 数据。
    mnist_x.txt: 每行 784 个像素值 (0-255)
    mnist_y.txt: 每行 1 个标签 (0-9)
    返回: (X, y) 均为 numpy 数组
    """
    X = np.loadtxt(x_path, dtype=np.float32)
    y = np.loadtxt(y_path, dtype=np.int64)

    # 归一化到 [0, 1]
    X /= 255.0

    print(f"[DATA] X shape: {X.shape}, y shape: {y.shape}")
    print(f"[DATA] 标签范围: [{y.min()}, {y.max()}], 像素范围: [{X.min():.2f}, {X.max():.2f}]")
    return X, y


def split_data(X, y, train_ratio=0.857):
    """
    划分训练集和测试集。
    MNIST 标准: 前 60000 训练, 后 10000 测试。
    train_ratio = 60000/70000 ≈ 0.857
    """
    split = int(len(X) * train_ratio)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    print(f"[DATA] Train: {len(X_train)}, Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test


class MNISTDataset(Dataset):
    """PyTorch Dataset 封装"""
    def __init__(self, X, y):
        self.X = torch.from_numpy(X)
        self.y = torch.from_numpy(y)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def get_dataloaders(X_train, X_test, y_train, y_test, batch_size=64):
    """创建训练和测试 DataLoader"""
    train_ds = MNISTDataset(X_train, y_train)
    test_ds = MNISTDataset(X_test, y_test)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader


def evaluate(model, loader, device):
    """计算模型在 loader 上的准确率"""
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            outputs = model(x)
            _, predicted = torch.max(outputs, 1)
            total += y.size(0)
            correct += (predicted == y).sum().item()
    return correct / total


def topk_accuracy(model, loader, device, k=5):
    """
    计算 Top-k 准确率。
    Top-k 准确率 = 真实标签出现在模型预测的前 k 个类别中的比例。
    """
    model.eval()
    correct = 0
    total = 0
    topk_results = {i: 0 for i in range(1, k + 1)}

    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            outputs = model(x)  # (batch, 10)

            # 获取每个样本的前 k 个预测类别
            _, topk_indices = torch.topk(outputs, k, dim=1)  # (batch, k)

            # Top-1 到 Top-k 准确率
            for i in range(1, k + 1):
                topk_results[i] += (topk_indices[:, :i] == y.view(-1, 1)).any(dim=1).sum().item()

            total += y.size(0)

    for i in range(1, k + 1):
        topk_results[i] /= total

    return topk_results
