"""
卷积神经网络案例：图像识别
"""
import torch
import os
import torch.nn as nn
from torchvision.datasets import CIFAR10
from torchvision.transforms import ToTensor
import torch.optim as optim
from torch.utils.data import DataLoader
from torchsummary import summary
import time
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='torch.cuda')
os.environ["TORCH_CUDA_ARCH_LIST"] = "8.9"


def data_processing():
    #加载数据集
    #Totensor: 将image转换为一个Tensor,并自动将其归一化到[0，1]上
    train = CIFAR10(root='./data', train=True, transform=ToTensor(),download=True)
    test = CIFAR10(root='./data', train=False, transform=ToTensor(),download=True)
    return train, test
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        #卷积层和池化层
        self.conv1 = nn.Conv2d(3, 6,3, 1)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 3,1)
        self.pool2 = nn.MaxPool2d(2, 2)
        #全连接层
        self.fc1 = nn.Linear(576, 120)
        self.fc2 = nn.Linear(120, 84)
        self.out = nn.Linear(84, 10)
    def forward(self, x):
        #第一个卷积，激活，池化
        x = torch.relu(self.conv1(x))
        x = self.pool1(x)
        #第二个卷积，激活，池化
        x = torch.relu(self.conv2(x))
        x = self.pool2(x)
        #特征图转向量
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.out(x)
def train_model(model,train,device):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    epochs = 200
    for epoch in range(epochs):
        dataloader = DataLoader(train,batch_size=256,shuffle=True)
        sam_num = 0
        total_loss = 0
        start = time.time()
        for x,y in dataloader:
            x = x.to(device)
            y = y.to(device)
            output = model(x)
            loss = criterion(output, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()*len(y)
            sam_num += len(y)
        print(f'epoch {epoch+1} loss: {total_loss/sam_num:.5f} time:{time.time()-start:.2f}s')
    torch.save(model.state_dict(),'./model.pth')
def evaluate(test):
    dataloader = DataLoader(test,batch_size=8,shuffle=True)
    model = Net()
    model.load_state_dict(torch.load('./model.pth'))
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in dataloader:
            output = model(x)
            correct += (output.argmax(1) == y).sum().item()
            total += len(y)
        print('Acc:%.2f'%(correct/total))
if __name__ == '__main__':
    train, test = data_processing()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[DEVICE] {device}")
    model = Net().to(device)  # 模型移到GPU/CPU
    train_model(model, train, device)  # 传递device参数
    evaluate(test)
    """
    # 1. 核心检查：CUDA是否可用
    cuda_available = torch.cuda.is_available()
    print(f"✅ CUDA是否可用: {cuda_available}")

    if cuda_available:
        # 2. 查看GPU基本信息
        print(f"可用GPU数量: {torch.cuda.device_count()}")
        print(f"当前使用GPU编号: {torch.cuda.current_device()}")
        print(f"GPU名称: {torch.cuda.get_device_name(0)}")
        print(f"CUDA版本: {torch.version.cuda}")
        print(f"GPU架构: {torch.cuda.get_device_capability(0)}")

        # 3. 验证GPU计算（关键：实际跑一个张量运算）
        test_tensor = torch.randn(10, 10).cuda()  # 创建张量并移到GPU
        test_result = test_tensor * 2  # 简单运算
        print(f"\nGPU计算正常: {test_result.is_cuda}")  # 输出True则计算正常
    else:
        print("\n未检测到可用GPU，当前使用CPU运行")
    """