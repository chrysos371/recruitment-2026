"""
决策树案例：泰坦尼克号乘客生存预测
"""
#导包
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier                   #决策树api
from sklearn.tree import DecisionTreeRegressor                    #回归树
from sklearn.linear_model import LinearRegression                 #线性回归模型
from sklearn.tree import plot_tree
from sklearn.model_selection import train_test_split              #分割数据集为训练集和测试集
from sklearn.model_selection import GridSearchCV                  #交叉验证和网格搜索
from sklearn.metrics import accuracy_score,roc_auc_score          #模型评估
from sklearn.preprocessing import StandardScaler                  #数据标准化
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

def decision_tree():
    #导入数据集
    taitan = pd.read_csv('train.csv')
    taitan.head()
    taitan.info()
    #提取特征和标签
    x = taitan[['Pclass','Age','Sex']].copy()
    y = taitan['Survived']
    #处理缺失值: 用均值填充 Age 的 NaN
    x['Age'].fillna(x['Age'].mean(), inplace=True)
    #对类别型数据进行one_hot编码
    print('x -->1\n', x)
    x.info()
    x = pd.get_dummies(x)
    print('x -->2\n', x)
    x.info()
    #数据集划分
    x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=7)
    #实例化决策树模型
    estimator = DecisionTreeClassifier()
    estimator.fit(x_train,y_train)
    #模型预测
    y_pred = estimator.predict(x_test)
    #输出准确率
    myret = estimator.score(x_test,y_test)
    print('myret:',myret)
    #展示分类性能
    myreport = classification_report(y_test,y_pred,target_names=['Died','Survived'])
    print('myreport:',myreport)
    #决策树可视化
    plt.figure(figsize=(20,10))
    plot_tree(estimator,
        max_depth=10,
        filled=True,
        feature_names=['Pclass', 'Age', 'Sex_female', 'Sex_male'],
        class_names = ['died', 'survived']
    )
    plt.show()
def regressiontree():
    #手搓一堆莫名其妙的数据
    x = np.array(list(range(1,11))).reshape(-1,1)
    y = np.array([5.56, 5.70, 5.91, 6.40, 6.80, 7.05, 8.90, 8.70, 9.00, 9.05])
    print('x -->1\n', x)
    print('y -->2\n', y)
    #实例化模型并训练
    model1 = DecisionTreeRegressor(max_depth = 1)
    model2 = DecisionTreeRegressor(max_depth = 3)
    model3 = LinearRegression()
    model1.fit(x,y)
    model2.fit(x,y)
    model3.fit(x,y)
    #模型预测
    x_test = np.arange(0.0,10.0,0.01).reshape(-1,1)
    y_pred1 = model1.predict(x_test)
    y_pred2 = model2.predict(x_test)
    y_pred3 = model3.predict(x_test)
    print(y_pred1,y_pred2,y_pred3)
    #结果可视化
    plt.figure(figsize=(10,6),dpi=100)
    plt.scatter(x,y,label='data')

    plt.plot(x_test,y_pred1,label='max_depth=1')
    plt.plot(x_test,y_pred2,label='max_depth=3')
    plt.plot(x_test,y_pred3,label='linear model')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Decision Tree Regression')
    plt.legend()
    plt.show()
if __name__ == '__main__':
    decision_tree()
    regressiontree()