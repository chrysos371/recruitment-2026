"""
Software_E2 — CNN 手写数字识别 (cnn.py)
========================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)
"""

import torch
import torch.nn as nn
import torch.optim as optim
import time
import os

from utils import load_mnist, split_data, get_dataloaders, evaluate


# ================================================================
#  CNN 模型
# ================================================================

class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        # 卷积部分
        self.conv = nn.Sequential(
            # 输入: (1, 28, 28) → 输出: (32, 26, 26)
            nn.Conv2d(1, 32, kernel_size=3, padding=0),
            nn.ReLU(),
            # → (32, 13, 13)
            nn.MaxPool2d(2),

            # → (64, 11, 11)
            nn.Conv2d(32, 64, kernel_size=3, padding=0),
            nn.ReLU(),
            # → (64, 5, 5)
            nn.MaxPool2d(2),
        )
        # 全连接部分
        self.fc = nn.Sequential(
            nn.Dropout(0.25),
            nn.Linear(64 * 5 * 5, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        # x shape: (batch, 784) → reshape 为 (batch, 1, 28, 28)
        x = x.view(-1, 1, 28, 28)
        x = self.conv(x)
        x = x.view(x.size(0), -1)  # flatten
        x = self.fc(x)
        return x


# ================================================================
#  训练
# ================================================================

def train_cnn(model, train_loader, test_loader, epochs, lr, device):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    best_acc = 0.0
    epoch_times = []

    for epoch in range(1, epochs + 1):
        t_start = time.time()

        model.train()
        total_loss = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        scheduler.step()
        epoch_time = time.time() - t_start
        epoch_times.append(epoch_time)

        avg_loss = total_loss / len(train_loader)
        acc = evaluate(model, test_loader, device)

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), "model/cnn.pth")

        if epoch == 1 or epoch % 5 == 0 or epoch == epochs:
            print(f"  Epoch {epoch:3d}/{epochs}  Loss: {avg_loss:.4f}  "
                  f"Test Acc: {acc:.4f}  Time: {epoch_time:.2f}s  Best: {best_acc:.4f}")

    avg_epoch_time = sum(epoch_times) / len(epoch_times)
    return best_acc, avg_epoch_time


# ================================================================
#  主程序
# ================================================================

if __name__ == "__main__":
    os.makedirs("model", exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[DEVICE] {device}")

    # ---------- 加载数据 ----------
    X, y = load_mnist("mnist_x.txt", "mnist_y.txt")
    X_train, X_test, y_train, y_test = split_data(X, y)

    # ---------- 训练 CNN ----------
    print("\n" + "=" * 60)
    print("  CNN 训练")
    print("=" * 60)

    train_loader, test_loader = get_dataloaders(
        X_train, X_test, y_train, y_test, batch_size=64
    )

    model = CNN().to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  参数量: {total_params:,}")

    best_acc, avg_time = train_cnn(model, train_loader, test_loader,
                                   epochs=15, lr=0.001, device=device)

    print(f"\n  CNN Final Acc: {best_acc:.4f}")
    print(f"  平均 epoch 耗时: {avg_time:.2f}s")
