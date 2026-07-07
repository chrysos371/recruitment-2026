"""
用pytorch框架搭建鸢尾花分类的人工神经网络
"""
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from torch import optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

def data_processing():
    data = load_iris()
    x = data['data']
    y = data['target']
    transfer = StandardScaler()
    x = transfer.fit_transform(x)
    x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.2,random_state=42)
    train_data = TensorDataset(torch.from_numpy(x_train).float(), torch.from_numpy(y_train).long())
    test_data = TensorDataset(torch.from_numpy(x_test).float(), torch.from_numpy(y_test).long())
    return train_data,test_data,x_train.shape[1],len(np.unique(y))
class NeuralNetwork(nn.Module):
    def __init__(self,input_dim,output_dim):
        super(NeuralNetwork,self).__init__()
        self.fc1 = nn.Linear(input_dim,32)
        self.fc2 = nn.Linear(32,64)
        self.fc3 = nn.Linear(64,output_dim)
    def forward(self,x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        output = self.fc3(x)
        return output
def train_model(train_dataset,input_dim,output_dim):
    torch.manual_seed(42)
    dataloader = DataLoader(train_dataset,batch_size=32,shuffle=True)
    model = NeuralNetwork(input_dim,output_dim)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(),lr=0.001)
    epoches = 250
    train_losses = []
    train_accs = []
    for epoch in range(epoches):
        running_loss = 0
        model.train()
        correct = 0
        total = 0
        for x,y in dataloader:
            output = model(x)
            loss = criterion(output,y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.item()*x.size(0)
            _, preds = torch.max(output, dim=1)  # preds是每个样本的预测类别（0/1/2）
            correct += (preds == y).sum().item()  # 统计正确数
            total += x.size(0)
        avg_loss = running_loss / len(train_dataset)
        avg_acc = correct / total
        train_losses.append(avg_loss)
        train_accs.append(avg_acc)
        print(f'Epoch [{epoch+1}/{epoches}], Loss: {avg_loss:.6f}, Acc: {avg_acc:.4f}')
    torch.save(model.state_dict(), 'iris.pth')
    return model,train_losses,train_accs


# 新增测试函数
def evaluate_model(model, test_dataset):
    model.eval()  # 评估模式
    dataloader = DataLoader(test_dataset, batch_size=32, shuffle=False)  # 测试集不打乱
    criterion = nn.CrossEntropyLoss()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():  # 禁用梯度，提速+省显存
        for x, y in dataloader:
            output = model(x)
            loss = criterion(output, y)
            total_loss += loss.item() * x.size(0)
            _, preds = torch.max(output, dim=1)
            correct += (preds == y).sum().item()
            total += x.size(0)

    avg_test_loss = total_loss / len(test_dataset)
    avg_test_acc = correct / total
    print(f'\nTest Loss: {avg_test_loss:.6f}, Test Acc: {avg_test_acc:.4f}')


def plot_history(train_losses, train_accs):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # 画损失曲线
    ax1.plot(range(1, len(train_losses) + 1), train_losses, 'r-', label='Train Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Loss Change')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.3)

    # 画准确率曲线
    ax2.plot(range(1, len(train_accs) + 1), train_accs, 'b-', label='Train Acc')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Training Accuracy Change')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.3)

    plt.show()

# 主函数中调用
if __name__ == '__main__':
    train_dataset, test_dataset, input_dim, output_dim = data_processing()
    model, train_losses, train_accs = train_model(train_dataset, input_dim, output_dim)
    evaluate_model(model, test_dataset)  # 新增：评估测试集
    plot_history(train_losses, train_accs)



