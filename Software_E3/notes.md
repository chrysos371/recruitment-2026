# 学习过程与踩坑记录 — Titanic Kaggle

## 学习过程

### 阶段一：回顾已有基础

之前在 PyCharmProjects 做泰坦尼克号时，用的是最简方案——Pclass、Age、Sex 三个特征 + DT/RF 模型 + GridSearchCV。准确率大约 78-80%。当时的理解是"能用就行"，没有深入想特征工程。

这次重新审视发现几个明显可以改进的地方：
- Name 字段完全没用到（但称谓 Mr/Mrs/Miss 和生还率强相关）
- Fare 票价分布极其偏斜（少数人买了天价票），取对数可以改善
- Cabin 虽然大量缺失但"有没有船舱信息"本身就是一个信号
- SibSp + Parch 可以合成 FamilySize

### 阶段二：特征工程扩展

从 3 特征扩展到 13 特征的过程：

| 步骤 | 新增特征 | 直觉 |
|------|----------|------|
| 1 | Title (称谓) | 已婚女性(Mrs)生还率远高于成年男性(Mr) |
| 2 | FamilySize | 有家庭的人可能互相帮助登救生艇 |
| 3 | IsAlone | 独自一人的人可能更难获救 |
| 4 | HasCabin | 有客舱号 = 上层船舱 = 更接近甲板 |
| 5 | FareLog | 票价取对数, 正态化分布 |
| 6 | AgeBin | 年龄分桶, 儿童优先登救生艇 |
| 7 | Embarked | 上船港口与船舱位置相关 |

每个新增特征都有领域直觉支撑，不是盲目堆砌。

### 阶段三：模型选择

题目要求"至少对比 2 种不同类别的模型"。选 LR 和 RF：

- **LogisticRegression**：线性模型, 假设特征和 log-odds 呈线性关系。简单、可解释，作为 baseline
- **RandomForest**：集成树模型, 自动捕捉非线性交互和特征重要性

两类模型在"模型类别"层面确实不同（线性 vs 树），而非只是换超参。

---

## 踩坑记录

### 坑 1：test.csv 需要单独下载

**现象**：Kaggle 数据页面把 `train.csv` 和 `test.csv` 分开提供，后者不随项目 repo 自带。

**影响**：代码有 `pd.read_csv('test.csv')` 但文件不存在时会报 `FileNotFoundError`。

**解决**：去 [Kaggle Titanic Data](https://www.kaggle.com/competitions/titanic/data) 下载 `test.csv` 放到同目录。README 中已注明。

### 坑 2：train 和 test 的特征列不一致

**现象**：有时 One-Hot 编码后 train 和 test 的列数不同——比如 test 的 Embarked 没有 Q 港导致少一列。

**原因**：`pd.get_dummies` 根据实际出现值创建列。如果某个类别在 test 中没出现，就不会生成对应列。

**解决**：
```python
common_cols = X.columns.intersection(X_test.columns)
X = X[common_cols]
X_test = X_test[common_cols]
```
确保两边的特征列完全对齐。如果 test 多了 train 没有的类别（理论上不应发生），也会被安全剔除。

### 坑 3：标准化对 RF 无害但对 LR 必须

**背景**：LR 的权重更新受特征量纲影响（FareLog ≈ 0~5, AgeBin ≈ 0~4 还好，但不同 Title one-hot 的方差不同）。

**设计**：代码对 LR 做了 StandardScaler 标准化，RF 用原始值（RF 基于分裂阈值，不依赖特征尺度）。两套流程分开处理，互不干扰。
