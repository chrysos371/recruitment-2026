"""
Software_E2 — MLP 手写数字识别 (main.py)
==========================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

包含超参数调优记录与对比实验。
"""

import torch
import torch.nn as nn
import torch.optim as optim
import os

from utils import load_mnist, split_data, get_dataloaders, evaluate

# ================================================================
#  MLP 模型
# ================================================================

class MLP(nn.Module):
    def __init__(self, hidden_sizes=(256, 128), dropout=0.2):
        super().__init__()
        layers = []
        in_features = 784  # 28*28

        for h in hidden_sizes:
            layers.append(nn.Linear(in_features, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            in_features = h

        layers.append(nn.Linear(in_features, 10))  # 输出 10 类

        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


# ================================================================
#  训练函数
# ================================================================

def train_mlp(model, train_loader, test_loader, epochs, lr, device):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    best_acc = 0.0
    history = {"train_loss": [], "test_acc": []}

    for epoch in range(1, epochs + 1):
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
        avg_loss = total_loss / len(train_loader)
        acc = evaluate(model, test_loader, device)
        history["train_loss"].append(avg_loss)
        history["test_acc"].append(acc)

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), "model/mlp.pth")

        if epoch == 1 or epoch % 5 == 0 or epoch == epochs:
            print(f"  Epoch {epoch:3d}/{epochs}  Loss: {avg_loss:.4f}  Test Acc: {acc:.4f}  Best: {best_acc:.4f}")

    return best_acc, history


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

    # ---------- 调参实验 ----------
    print("\n" + "=" * 60)
    print("  超参数调优实验")
    print("=" * 60)

    configs = [
        # ---- 基线 ----
        {"hidden": (128,),   "bs": 64,  "lr": 0.001, "ep": 15, "dropout": 0.0, "label": "基线: 单隐层128"},
        # ---- 加深 ----
        {"hidden": (256, 128), "bs": 64, "lr": 0.001, "ep": 15, "dropout": 0.2, "label": "加深: (256,128)+Drop0.2"},
        # ---- batch_size 对比 ----
        {"hidden": (256, 128), "bs": 128, "lr": 0.001, "ep": 15, "dropout": 0.2, "label": "调参: batch_size=128"},
        # ---- learning_rate 对比 ----
        {"hidden": (256, 128), "bs": 64, "lr": 0.003, "ep": 15, "dropout": 0.2, "label": "调参: lr=0.003"},
        # ---- 最优组合 ----
        {"hidden": (512, 256, 128), "bs": 64, "lr": 0.001, "ep": 30, "dropout": 0.3, "label": "最优: (512,256,128)+Drop0.3 lr=0.001 ep=30"},
    ]

    results = []
    for cfg in configs:
        print(f"\n{'─' * 50}")
        print(f"  {cfg['label']}")
        print(f"  hidden={cfg['hidden']}, bs={cfg['bs']}, lr={cfg['lr']}, ep={cfg['ep']}, dropout={cfg['dropout']}")
        print(f"{'─' * 50}")

        train_loader, test_loader = get_dataloaders(
            X_train, X_test, y_train, y_test, batch_size=cfg["bs"]
        )

        model = MLP(hidden_sizes=cfg["hidden"], dropout=cfg["dropout"]).to(device)
        best_acc, _ = train_mlp(model, train_loader, test_loader,
                                epochs=cfg["ep"], lr=cfg["lr"], device=device)

        results.append({**cfg, "acc": best_acc})
        # 调参记录注释 (题目要求格式)
        print(f"  # batch_size: {cfg['bs']}  lr: {cfg['lr']}  hidden: {cfg['hidden']}  dropout: {cfg['dropout']}  acc: {best_acc:.4f}")

    # ---------- 结果汇总 ----------
    print("\n" + "=" * 60)
    print("  调参结果汇总")
    print("=" * 60)
    print(f"{'配置':<35} {'Acc':>8}")
    print("-" * 45)
    for r in results:
        print(f"{r['label']:<35} {r['acc']:>7.4f}")

    best = max(results, key=lambda r: r['acc'])
    print(f"\n  [BEST] 最优: {best['label']} - Acc: {best['acc']:.4f}")
