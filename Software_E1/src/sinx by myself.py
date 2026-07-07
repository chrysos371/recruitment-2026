"""
用pytorch框架搭建拟合sinx图像的神经网络
"""

#导包
import torch
import torch.nn as nn
import numpy as np
from sympy import evaluate
import matplotlib.pyplot as plt
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split

#构建数据集
def create_dataset():
    x = torch.linspace(0,2*torch.pi,1000)
    y = torch.sin(x)
    x = x.reshape(-1,1).float().numpy()
    y = y.reshape(-1,1).float().numpy()
    x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=42)
    train_dataset = TensorDataset(torch.from_numpy(x_train),torch.from_numpy(y_train))
    test_dataset = TensorDataset(torch.from_numpy(x_test),torch.from_numpy(y_test))
    return train_dataset,test_dataset

#构造神经网络结构
class sinx(nn.Module):
    def __init__(self):
        super(sinx,self).__init__()
        #第一层输入一层，输出32
        self.fc1 = nn.Linear(1,32)
        self.fc2 = nn.Linear(32,64)
        self.fc3 = nn.Linear(64,1)
    def forward(self,x):
        #前向传播
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        output = self.fc3(x)
        return output

#模型训练函数
def train_model(train_dataset):
    torch.manual_seed(56)
    #构建数据加载器
    dataloader = DataLoader(train_dataset,batch_size=32,shuffle=True)
    #实例化模型
    model = sinx()
    #构建损失函数
    criterion = nn.MSELoss()
    #构建优化器
    optimizer = torch.optim.Adam(model.parameters(),lr = 0.001)
    #训练轮数
    epochs = 250
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for x,y in dataloader:
            output = model(x)
            loss = criterion(output,y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()*x.size(0)
        average_loss = total_loss / len(dataloader)
        print(f'epoch:{epoch},loss:{average_loss:.6f}')
    torch.save(model.state_dict(),'sinx.pth')
    return model
def evaluate(model,test_dataset):
    model.eval()
    dataloader = DataLoader(test_dataset,batch_size=32,shuffle=False)
    criterion = nn.MSELoss()
    total_loss = 0
    with torch.no_grad():
        for x,y in dataloader:
            output = model(x)
            loss = criterion(output,y)
            total_loss += loss.item()*x.size(0)
    avg_test_loss = total_loss / len(test_dataset)
    print(f'\nTest Set Average MSE Loss: {avg_test_loss:.6f}')
def draw(model):
    model.eval()
    x = np.linspace(0, 2 * torch.pi, 1000)
    y = np.sin(x)
    plt.plot(x,y,label = 'real line',color = 'r',linewidth=2)
    with torch.no_grad():
        x_test = torch.linspace(0, 2 * torch.pi, 1000).reshape(-1,1).float()
        y_pred = model(x_test).detach().numpy().flatten()
    plt.plot(x_test,y_pred,label = 'predict line',color ='b',linestyle = '--',linewidth=2)
    plt.title('fittting line of sinx')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True,linestyle='--',alpha=0.3)
    plt.legend()
    plt.show()
if __name__ == '__main__':
    train_dataset,test_dataset= create_dataset()
    model = train_model(train_dataset)
    evaluate(model,test_dataset)
    draw(model)





