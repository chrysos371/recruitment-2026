"""
Software_E4 — VGG-16 vs ResNet-18 对比复现 (cifar10_train.py)
===============================================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

纯 PyTorch 手写 VGG-16 和 ResNet-18, 严禁预封装模型。
CIFAR-10 图像分类, 对比训练速度、参数量、准确率。

用法:
  python cifar10_train.py          # 完整训练 VGG + ResNet
  python cifar10_train.py --quick  # 快速验证 (3 epochs)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import time, os, sys, argparse
import numpy as np


# ================================================================
#  VGG-16 (手写实现)
# ================================================================

class VGG16(nn.Module):
    """
    VGG-16 结构 (适配 CIFAR-10: 32×32 输入)

    原版 VGG-16 为 ImageNet (224×224) 设计, 最后 FC 层极大。
    CIFAR-10 版本保留全部卷积层, 缩小 FC 层适配 10 类输出。
    """
    def __init__(self, num_classes=10):
        super().__init__()
        # Block 1: 3→64
        self.block1 = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        # Block 2: 64→128
        self.block2 = nn.Sequential(
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        # Block 3: 128→256
        self.block3 = nn.Sequential(
            nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        # Block 4: 256→512
        self.block4 = nn.Sequential(
            nn.Conv2d(256, 512, 3, padding=1), nn.BatchNorm2d(512), nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1), nn.BatchNorm2d(512), nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1), nn.BatchNorm2d(512), nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        # Block 5: 512→512
        self.block5 = nn.Sequential(
            nn.Conv2d(512, 512, 3, padding=1), nn.BatchNorm2d(512), nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1), nn.BatchNorm2d(512), nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1), nn.BatchNorm2d(512), nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        # CIFAR-10 适配 FC: 512*1*1 → 512 → 10
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(512, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),
        )

        # 权重初始化
        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        x = self.block5(x)
        x = x.view(x.size(0), -1)  # 512 * 1 * 1 = 512
        x = self.classifier(x)
        return x


# ================================================================
#  ResNet-18 (手写实现)
# ================================================================

class BasicBlock(nn.Module):
    """ResNet 基础残差块: Conv→BN→ReLU→Conv→BN, +skip connection"""
    expansion = 1

    def __init__(self, in_planes, planes, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)

        # shortcut: 维度不匹配时用 1×1 卷积对齐
        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != self.expansion * planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, self.expansion * planes, 1, stride=stride, bias=False),
                nn.BatchNorm2d(self.expansion * planes),
            )

    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = torch.relu(out)
        return out


class ResNet18(nn.Module):
    """
    ResNet-18 结构 (适配 CIFAR-10: 32×32 输入)

    相比 ImageNet 版本:
      - 首个卷积: 7×7→3×3, stride 2→1 (保留空间信息)
      - 去掉首个 MaxPool (32×32 不需要下采样)
    """
    def __init__(self, num_classes=10):
        super().__init__()
        self.in_planes = 64

        # CIFAR-10 适配: 3×3 conv, stride=1, 无 MaxPool
        self.conv1 = nn.Conv2d(3, 64, 3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)

        self.layer1 = self._make_layer(64, 2, stride=1)
        self.layer2 = self._make_layer(128, 2, stride=2)
        self.layer3 = self._make_layer(256, 2, stride=2)
        self.layer4 = self._make_layer(512, 2, stride=2)

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * BasicBlock.expansion, num_classes)

        self._initialize_weights()

    def _make_layer(self, planes, num_blocks, stride):
        layers = []
        layers.append(BasicBlock(self.in_planes, planes, stride))
        self.in_planes = planes * BasicBlock.expansion
        for _ in range(1, num_blocks):
            layers.append(BasicBlock(self.in_planes, planes))
        return nn.Sequential(*layers)

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.avgpool(out)
        out = out.view(out.size(0), -1)
        out = self.fc(out)
        return out


# ================================================================
#  训练工具
# ================================================================

def get_cifar10(batch_size=128):
    """加载 CIFAR-10, 标准化 + 数据增强"""
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])

    train_set = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform_train)
    test_set = datasets.CIFAR10(root='./data', train=False, download=True, transform=transform_test)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False, num_workers=2)

    return train_loader, test_loader


def evaluate(model, loader, device):
    """计算准确率"""
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            outputs = model(x)
            _, predicted = outputs.max(1)
            total += y.size(0)
            correct += predicted.eq(y).sum().item()
    return correct / total


def train_one_epoch(model, loader, optimizer, criterion, device):
    """训练一个 epoch, 返回 loss 和 acc"""
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        outputs = model(x)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * y.size(0)
        _, predicted = outputs.max(1)
        total += y.size(0)
        correct += predicted.eq(y).sum().item()

    return total_loss / total, correct / total


def train_model(model, train_loader, test_loader, epochs, lr, device, name=""):
    """完整训练流程, 返回历史记录"""
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    history = {"train_loss": [], "train_acc": [], "test_acc": [], "epoch_time": []}
    best_acc = 0.0

    print(f"\n{'='*60}")
    print(f"  Training: {name}")
    print(f"  Params: {sum(p.numel() for p in model.parameters()):,}")
    print(f"  Epochs: {epochs}, LR: {lr}, Device: {device}")
    print(f"{'='*60}")

    for epoch in range(1, epochs + 1):
        t0 = time.time()

        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        test_acc = evaluate(model, test_loader, device)
        scheduler.step()

        epoch_time = time.time() - t0
        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["test_acc"].append(test_acc)
        history["epoch_time"].append(epoch_time)

        if test_acc > best_acc:
            best_acc = test_acc
            torch.save(model.state_dict(), f"output/{name}_best.pth")

        if epoch == 1 or epoch % 20 == 0 or epoch == epochs:
            print(f"  Epoch {epoch:3d}/{epochs} | Loss: {train_loss:.4f} | "
                  f"Train Acc: {train_acc:.4f} | Test Acc: {test_acc:.4f} | "
                  f"Time: {epoch_time:.1f}s | Best: {best_acc:.4f}")

    avg_time = np.mean(history["epoch_time"])
    print(f"\n  {name} Final: Test Acc={best_acc:.4f}, Avg Epoch={avg_time:.1f}s")
    return history, best_acc, avg_time


# ================================================================
#  主程序
# ================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='快速验证 (3 epochs)')
    parser.add_argument('--epochs', type=int, default=80, help='训练轮数')
    args = parser.parse_args()

    if args.quick:
        args.epochs = 3

    os.makedirs("output", exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # 加载数据
    print("\n[1] Loading CIFAR-10...")
    train_loader, test_loader = get_cifar10(batch_size=128)

    results = {}

    # ---- 训练 VGG-16 ----
    print("\n[2] Training VGG-16...")
    vgg = VGG16().to(device)
    hist_vgg, best_vgg, time_vgg = train_model(
        vgg, train_loader, test_loader, args.epochs, lr=0.01, device=device, name="VGG-16"
    )
    results["VGG-16"] = {"history": hist_vgg, "best_acc": best_vgg, "avg_time": time_vgg,
                          "params": sum(p.numel() for p in vgg.parameters())}

    # ---- 训练 ResNet-18 ----
    print("\n[3] Training ResNet-18...")
    resnet = ResNet18().to(device)
    hist_resnet, best_resnet, time_resnet = train_model(
        resnet, train_loader, test_loader, args.epochs, lr=0.05, device=device, name="ResNet-18"
    )
    results["ResNet-18"] = {"history": hist_resnet, "best_acc": best_resnet, "avg_time": time_resnet,
                             "params": sum(p.numel() for p in resnet.parameters())}

    # ---- 对比分析 ----
    print("\n" + "=" * 60)
    print("  VGG-16 vs ResNet-18 对比结果")
    print("=" * 60)
    print(f"  {'指标':<20} {'VGG-16':>15} {'ResNet-18':>15}")
    print(f"  {'─'*50}")
    print(f"  {'参数量':<20} {results['VGG-16']['params']:>15,} {results['ResNet-18']['params']:>15,}")
    print(f"  {'最佳准确率':<20} {results['VGG-16']['best_acc']:>15.4f} {results['ResNet-18']['best_acc']:>15.4f}")
    print(f"  {'平均 epoch 耗时':<20} {results['VGG-16']['avg_time']:>14.1f}s {results['ResNet-18']['avg_time']:>14.1f}s")

    if args.quick:
        print("\n  ⚠️  Quick mode — 仅验证管线, 完整训练请运行: python cifar10_train.py")


if __name__ == "__main__":
    main()
