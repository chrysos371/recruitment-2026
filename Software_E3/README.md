# Software_E3 — 泰坦尼克号生还预测 (Kaggle)

## 自我介绍

我是张杨亦航（学号 2524030231）。泰坦尼克号是我在学 sklearn 时做过的基础练习——之前在 PyCharmProjects 里用 DT + RF + GridSearchCV 跑过（见 `src/random forest.py` 和 `src/titanic_decision_tree.py`）。这次在此基础上完善了特征工程、加入 LogisticRegression 做不同类别模型对比，并生成 Kaggle 标准的 submission.csv。

---

## 方案设计

### 特征工程

对比我此前只用了 Pclass/Age/Sex 三个特征的版本，本次扩展为 13 个特征：

| 特征 | 来源 | 处理 |
|------|------|------|
| Pclass | 原始 | 1/2/3 直接使用 |
| Sex | 原始 | male→0, female→1 |
| AgeBin | Age | 中位数填充缺失 → 5 段分桶 |
| FareLog | Fare | 中位数填充 → log(1+x) 压缩极端值 |
| Embarked | 原始 | 众数填充 → One-Hot (Q/S) |
| Title | Name | 正则提取称谓 → 归并为 Mr/Mrs/Miss/Master/Other |
| FamilySize | SibSp+Parch+1 | 直接计算 |
| IsAlone | FamilySize==1 | 二值特征 |
| HasCabin | Cabin | 是否有客舱号 (0/1) |

### 模型对比

| 模型 | 类型 | 超参搜索 |
|------|------|----------|
| LogisticRegression | 线性模型 | GridSearchCV: C, solver |
| RandomForestClassifier | 集成树模型 | GridSearchCV: n_estimators, max_depth, min_samples_split |

两类模型分别代表 **线性决策边界** 和 **非线性组合特征** 两条路线，满足题目"至少对比 2 种不同类别的模型"的要求。

### 评估策略

- 5 折交叉验证 (GridSearchCV)
- 20% hold-out 验证集
- 最优模型 → test.csv 预测 → submission.csv

---

## 使用方法

### 1. 下载数据

从 [Kaggle Titanic](https://www.kaggle.com/competitions/titanic/data) 下载 `test.csv`，放到 `Software_E3/` 目录下。

> `train.csv` 已存在（来自本人之前的 PyCharmProjects）。

### 2. 运行

```bash
cd Software_E3
python titanic_solution.py
```

### 3. 提交

将生成的 `submission.csv` 上传到 [Kaggle Titanic 竞赛页](https://www.kaggle.com/competitions/titanic/submit)，截图 Leaderboard 得分和排名。

---

## 文件结构

```
Software_E3/
├── train.csv                      # 训练数据 (来自本人之前项目)
├── titanic_solution.py            # 完整方案: 特征工程 + LR vs RF + submission
├── submission.csv                 # 生成物: Kaggle 提交文件
├── src/
│   ├── random forest.py           # 本人此前写的 DT+RF+GridSearchCV 基础版
│   └── titanic_decision_tree.py   # 本人此前写的 DT + 可视化版
├── README.md
└── notes.md
```

---

## 与本人此前版本的对比

| 方面 | 此前版本 (src/) | 本次 E3 版本 |
|------|:---:|:---:|
| 特征数 | 3 | 13 |
| 模型 | DT + RF | LR + RF |
| 缺失值处理 | Age.fillna(mean) | Age→median/分桶, Fare→log, Embarked→mode |
| 超参搜索 | GridSearchCV (仅 RF) | GridSearchCV (LR + RF) |
| 测试集预测 | ✗ | submission.csv |
| 特征类别 | 纯数值 | 数值 + One-Hot + 衍生特征 |
