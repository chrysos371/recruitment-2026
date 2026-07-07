import torch
import torch.nn as nn
from torchsummary import summary
from torch.utils.data import TensorDataset, DataLoader
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
"""
class model(nn.Module):
    #初始化属性值
    def __init__(self):
        super(model, self).__init__()#调用父类的初始化属性和方法
        self.linear1 = nn.Linear(3,3)#创建第一个隐藏层模型，三个输入三个输出
        nn.init.xavier_uniform_(self.linear1.weight)#初始化权重
        nn.init.zeros_(self.linear1.bias)#偏置初始化为零
        #创建第二个隐藏层，三个输入两个输出
        self.linear2 = nn.Linear(3,2)
        #初始化权重
        nn.init.kaiming_normal_(self.linear2.weight)
        nn.init.zeros_(self.linear2.bias)
        #创建输出层
        self.out = nn.Linear(2,2)
    #创建前向传播方法，自动执行
    def forward(self, x):
        #数据经过第一个线性层
        x = self.linear1(x)
        #经过激活函数
        x = torch.sigmoid(x)
        #经过第二个线性层
        x = self.linear2(x)
        #经过第二个激活函数
        x = torch.relu(x)
        #最后到输出层
        x = self.out(x)
        #经过第三个激活函数
        x = torch.softmax(x, dim=-1)
        return x
if __name__ == '__main__':
    #实例化模型
    model = model()
    #随机产生数据集
    data = torch.randn(5,3)
    print('datashape:', data.shape)
    #数据经过神经网络训练
    output = model(data)
    print('output.shape:', output.shape)
    #计算模型参数
    #计算每层每个神经元的W和B的总和
    summary(model, input_size=(3,),batch_size=5)
    #查看模型参数
    for name,parameters in model.named_parameters():
        print(name,parameters)
"""
#构建数据集
def create_dataset():
    #导入CSV文件
    data = pd.read_csv('手机价格预测.csv')
    #区分出特征和标签
    x,y = data.iloc[:,:-1],data.iloc[:,-1]
    #数据类型转换
    x = x.astype(np.float32)
    y = y.astype(np.int32)
    #划分数据集
    x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.8,random_state=42)
    #将数据集转化为pytorch张量的形式
    train_dataset = TensorDataset(torch.from_numpy(x_train),torch.from_numpy(y_train))
    test_dataset = TensorDataset(torch.from_numpy(x_test),torch.from_numpy(y_test))
    return train_dataset,test_dataset,x_train.shape[1],len(np.unique(y))
class NeuralNetwork(nn.Module):
    def __init__(self,input_dim,output_dim):
        super(NeuralNetwork, self).__init__()
        #第一层输入维度为20，输出维度为128
        self.linear1 = nn.Linear(input_dim,128)
        #第二层输入维度为128，输出维度为256
        self.linear2 = nn.Linear(128,256)
        #第三层输入维度为256，输出维度为4
        self.linear3 = nn.Linear(256,4)
    def forward(self,x):
        #前向传播过程
        x = torch.relu(self.linear1(x))
        x = torch.relu(self.linear2(x))
        output = self.linear3(x)
        #获取数据结果
        return output
def train_model(train_dataset,input_dim,class_num):
    #固定随机种子
    torch.manual_seed(1)
    #初始化数据加载器
    dataloader = DataLoader(train_dataset,batch_size=8,shuffle=True)
    #初始化模型
    model = NeuralNetwork(input_dim,class_num)
    #构建损失函数
    criterion = nn.CrossEntropyLoss()
    #优化器
    optimizer = optim.SGD(model.parameters(),lr=0.001)
    #训练轮数
    num_epochs = 50
    #对每个轮次的数据进行遍历
    for epoch in range(num_epochs):
        #计算下训练时间
        start = time.time()
        #计算损失
        total_loss = 0.0
        total_num = 0
        for x,y in dataloader:
            #先将数据送入神经网络进行预测
            output = model(x)
            #计算损失
            loss = criterion(output,y)
            #梯度清零防止叠加
            optimizer.zero_grad()
            #然后反向传播
            loss.backward()
            #优化参数
            optimizer.step()
            #计算损失
            total_num += 1
            total_loss += loss.item()
    #打印损失变化的结果
        print('epoch:')
        torch.save(model.state_dict(),'model.pth')
def test(test_dataset,input_dim,class_num):
    #加载模型和训练好的网络参数
    model = NeuralNetwork(input_dim,class_num)
    model.load_state_dict(torch.load('model.pth'))
    #构建加载器
    dataloader = DataLoader(test_dataset,batch_size=8,shuffle=False)
    #评估测试集
    correct = 0
    #遍历数据集的数据
    for x,y in dataloader:
        #用神经网络进行预测
        output = model(x)
        #获取类别结果
        y_pred = torch.argmax(output,dim=1)
        #获取预测正确的个数
        correct += torch.sum(y_pred == y)
    #预测准确度
    print('accuracy:',correct.item()/len(test_dataset))




if __name__ == '__main__':
    train_dataset,test_dataset,input_dim,class_num = create_dataset()
    train_model(train_dataset,input_dim,class_num)






















