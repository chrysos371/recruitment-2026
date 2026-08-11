"""
泰坦尼克号案例
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

def demo01():
    #导入数据集
    dataset = pd.read_csv('train.csv')
    #分出特征和标签
    x = dataset[['Pclass','Age', 'Sex']].copy()
    y = dataset['Survived']
    #处理数据集，
    x['Age'].fillna(x['Age'].mean(),inplace=True)#用其余游客年龄的均值去填充缺失的数据
    print(x.head())
    #one-hot编码
    x = pd.get_dummies(x)
    #切分数据集
    x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=7)

    #单一的决策树算法
    dtc = DecisionTreeClassifier()
    dtc.fit(x_train, y_train)
    dtc_y_pred = dtc.predict(x_test)
    accuracy = dtc.score(x_test, y_test)
    print('单一决策树accuracy-->\n', accuracy)

    #随机森林算法
    rfc = RandomForestClassifier(max_depth=6,random_state=7)
    rfc.fit(x_train, y_train)
    rfc_y_pred = rfc.predict(x_test)
    accuracy = rfc.score(x_test, y_test)
    print('随机森林accuracy-->\n', accuracy)

    #用交叉验证网格搜索去优化随机森林的超参
    estimator = RandomForestClassifier()
    param = {'n_estimators':[40,50,60,70],"max_depth":[2,4,6,8]}
    grid_search = GridSearchCV(estimator,param_grid=param,cv=2)
    grid_search.fit(x_train,y_train)
    accuracy = grid_search.score(x_test,y_test)
    print(grid_search.best_params_)

if __name__ == '__main__':
    demo01()
