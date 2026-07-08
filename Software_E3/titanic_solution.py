"""
Software_E3 — 泰坦尼克号生还预测 (titanic_solution.py)
==========================================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

基于本人此前在 PyCharmProjects 中写的 DT+RF+GridSearchCV 基础,
加入: 完整特征工程、LogisticRegression 对比、submission.csv 生成。

使用前: 从 Kaggle Titanic 下载 train.csv 和 test.csv 放到本目录。
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')


# ================================================================
#  特征工程
# ================================================================

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    统一特征工程, train 和 test 共用同一套逻辑。

    特征设计 (与本人此前只用 Pclass/Age/Sex 的版本相比大幅扩展):
      Pclass      — 船舱等级 (1/2/3)
      Sex         — 性别 (male/female → 0/1)
      Age         — 年龄 (缺失用中位数填充, 后分桶)
      Fare        — 票价 (缺失用中位数填充, 取对数)
      Embarked    — 登船港口 (C/Q/S, 缺失用众数)
      Title       — 从姓名提取称谓 (Mr/Mrs/Miss/Master/Other)
      FamilySize  — SibSp + Parch + 1
      IsAlone     — 是否独自一人
      HasCabin    — 是否有客舱号
    """
    data = df.copy()

    # --- Title (从 Name 提取) ---
    data['Title'] = data['Name'].str.extract(r',\s*([^\.]+)\.', expand=False)
    title_map = {
        'Mr': 'Mr', 'Mrs': 'Mrs', 'Miss': 'Miss', 'Master': 'Master',
        'Ms': 'Miss', 'Mlle': 'Miss', 'Mme': 'Mrs',
        'Dr': 'Other', 'Rev': 'Other', 'Col': 'Other',
        'Major': 'Other', 'Capt': 'Other', 'Don': 'Other',
        'Lady': 'Other', 'Sir': 'Other', 'Countess': 'Other',
        'Jonkheer': 'Other', 'Dona': 'Other',
    }
    data['Title'] = data['Title'].map(title_map).fillna('Other')

    # --- Sex ---
    data['Sex'] = data['Sex'].map({'male': 0, 'female': 1})

    # --- Age (缺失 → 中位数, 然后分桶) ---
    data['Age'] = data['Age'].fillna(data['Age'].median())
    data['AgeBin'] = pd.cut(data['Age'], bins=[0, 12, 18, 35, 60, 100],
                            labels=[0, 1, 2, 3, 4]).astype(int)

    # --- Fare (缺失 → 中位数, 取对数压缩极端值) ---
    data['Fare'] = data['Fare'].fillna(data['Fare'].median())
    data['FareLog'] = np.log1p(data['Fare'])

    # --- Embarked (缺失 → 众数) ---
    data['Embarked'] = data['Embarked'].fillna(data['Embarked'].mode()[0])

    # --- FamilySize & IsAlone ---
    data['FamilySize'] = data['SibSp'] + data['Parch'] + 1
    data['IsAlone'] = (data['FamilySize'] == 1).astype(int)

    # --- HasCabin ---
    data['HasCabin'] = data['Cabin'].notna().astype(int)

    # --- 选取最终特征列 ---
    features = ['Pclass', 'Sex', 'AgeBin', 'FareLog', 'FamilySize',
                'IsAlone', 'HasCabin']
    # one-hot: Embarked, Title
    X = pd.get_dummies(data[features + ['Embarked', 'Title']],
                       columns=['Embarked', 'Title'],
                       drop_first=True,
                       dtype=int)
    return X


# ================================================================
#  主程序
# ================================================================

def main():
    print("=" * 60)
    print("  Software_E3 — Titanic Kaggle 生还预测")
    print("  张杨亦航 (2524030231)")
    print("=" * 60)

    # ---------- 1. 加载数据 ----------
    train_raw = pd.read_csv('train.csv')
    test_raw = pd.read_csv('test.csv')
    print(f"\n[1] 数据加载: train={train_raw.shape}, test={test_raw.shape}")

    # ---------- 2. 特征工程 ----------
    y = train_raw['Survived']
    X = feature_engineering(train_raw)
    X_test = feature_engineering(test_raw)

    # 确保 train 和 test 的特征列对齐
    common_cols = X.columns.intersection(X_test.columns)
    X = X[common_cols]
    X_test = X_test[common_cols]

    print(f"[2] 特征工程完成: {X.shape[1]} 个特征")
    print(f"    特征列表: {list(X.columns)}")

    # ---------- 3. 划分验证集 ----------
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 标准化 (LR 需要, RF 不需要但无害)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    # ---------- 4. 模型 1: LogisticRegression + GridSearchCV ----------
    print("\n" + "-" * 50)
    print("  模型 1: LogisticRegression + GridSearchCV")
    print("-" * 50)

    lr = LogisticRegression(max_iter=2000, random_state=42)
    lr_params = {
        'C': [0.01, 0.1, 1.0, 10.0],
        'solver': ['liblinear', 'lbfgs'],
    }
    lr_gs = GridSearchCV(lr, lr_params, cv=5, scoring='accuracy', n_jobs=-1)
    lr_gs.fit(X_train_s, y_train)

    lr_val_acc = accuracy_score(y_val, lr_gs.predict(X_val_s))
    print(f"  最优参数: {lr_gs.best_params_}")
    print(f"  验证集准确率: {lr_val_acc:.4f}")
    print(f"  交叉验证均分: {lr_gs.best_score_:.4f}")

    # ---------- 5. 模型 2: RandomForest + GridSearchCV ----------
    print("\n" + "-" * 50)
    print("  模型 2: RandomForestClassifier + GridSearchCV")
    print("-" * 50)

    rf = RandomForestClassifier(random_state=42)
    rf_params = {
        'n_estimators': [50, 100, 150],
        'max_depth': [4, 6, 8, None],
        'min_samples_split': [2, 5],
    }
    rf_gs = GridSearchCV(rf, rf_params, cv=5, scoring='accuracy', n_jobs=-1)
    rf_gs.fit(X_train, y_train)  # RF 不需要标准化

    rf_val_acc = accuracy_score(y_val, rf_gs.predict(X_val))
    print(f"  最优参数: {rf_gs.best_params_}")
    print(f"  验证集准确率: {rf_val_acc:.4f}")
    print(f"  交叉验证均分: {rf_gs.best_score_:.4f}")

    # ---------- 6. 对比 & 选择最优 ----------
    print("\n" + "=" * 60)
    print("  模型对比")
    print("=" * 60)
    print(f"  {'模型':<25} {'验证 Acc':>10} {'CV 均分':>10}")
    print(f"  {'─' * 45}")
    print(f"  {'LogisticRegression':<25} {lr_val_acc:>10.4f} {lr_gs.best_score_:>10.4f}")
    print(f"  {'RandomForest':<25} {rf_val_acc:>10.4f} {rf_gs.best_score_:>10.4f}")

    if rf_val_acc >= lr_val_acc:
        best_model = rf_gs
        best_name = "RandomForest"
        use_scaled = False
    else:
        best_model = lr_gs
        best_name = "LogisticRegression"
        use_scaled = True

    print(f"\n  最优模型: {best_name} (验证 Acc: {max(rf_val_acc, lr_val_acc):.4f})")

    # ---------- 7. 生成 submission.csv ----------
    X_final = X_test_s if use_scaled else X_test
    predictions = best_model.predict(X_final)

    submission = pd.DataFrame({
        'PassengerId': test_raw['PassengerId'],
        'Survived': predictions
    })
    submission.to_csv('submission.csv', index=False)
    print(f"\n[3] submission.csv 已生成 ({len(submission)} 行)")
    print(f"    格式: PassengerId,Survived")


if __name__ == "__main__":
    main()
