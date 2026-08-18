"""
Software_E3 — 生成运行截图 (Titanic 生还预测)
=============================================
重跑 LogisticRegression vs RandomForest, 绘制特征重要性与模型对比图。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

from titanic_solution import feature_engineering

os.makedirs('output', exist_ok=True)

# ---------- 数据 + 特征 ----------
train_raw = pd.read_csv('train.csv')
test_raw = pd.read_csv('test.csv')
y = train_raw['Survived']
X = feature_engineering(train_raw)
X_test = feature_engineering(test_raw)
common = X.columns.intersection(X_test.columns)
X = X[common]; X_test = X_test[common]

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_val_s = scaler.transform(X_val)

# ---------- 模型拟合 ----------
lr = LogisticRegression(max_iter=2000, random_state=42)
lr_gs = GridSearchCV(lr, {'C': [0.01, 0.1, 1.0, 10.0],
                          'solver': ['liblinear', 'lbfgs']},
                     cv=5, scoring='accuracy', n_jobs=-1)
lr_gs.fit(X_train_s, y_train)
lr_acc = accuracy_score(y_val, lr_gs.predict(X_val_s))

rf = RandomForestClassifier(random_state=42)
rf_gs = GridSearchCV(rf, {'n_estimators': [50, 100, 150],
                          'max_depth': [4, 6, 8, None],
                          'min_samples_split': [2, 5]},
                     cv=5, scoring='accuracy', n_jobs=-1)
rf_gs.fit(X_train, y_train)
rf_acc = accuracy_score(y_val, rf_gs.predict(X_val))

# ---------- 图1: 模型对比 ----------
plt.figure(figsize=(7, 5))
names = ['LogisticRegression', 'RandomForest']
vals = [lr_acc, rf_acc]
bars = plt.bar(names, vals, color=['#4C72B0', '#DD8452'], width=0.5)
for b, v in zip(bars, vals):
    plt.text(b.get_x() + b.get_width() / 2, v + 0.003, f'{v:.4f}',
             ha='center', fontweight='bold')
plt.ylim(0, 1)
plt.ylabel('Validation Accuracy')
plt.title('Titanic: LogisticRegression vs RandomForest')
plt.tight_layout()
plt.savefig('output/e3_model_comparison.png', dpi=130)
plt.close()

# ---------- 图2: RF 特征重要性 ----------
importances = rf_gs.best_estimator_.feature_importances_
order = np.argsort(importances)[::-1]
plt.figure(figsize=(8, 5))
plt.barh([X.columns[i] for i in order][::-1], importances[order][::-1],
         color='#55A868')
plt.xlabel('Feature Importance')
plt.title('RandomForest Feature Importance (Top features)')
plt.tight_layout()
plt.savefig('output/e3_feature_importance.png', dpi=130)
plt.close()

# ---------- 输出 ----------
print('=' * 60)
print('  Software_E3 — Titanic 模型对比')
print('=' * 60)
print(f'  LogisticRegression  验证 Acc: {lr_acc:.4f}  (CV: {lr_gs.best_score_:.4f})')
print(f'  RandomForest        验证 Acc: {rf_acc:.4f}  (CV: {rf_gs.best_score_:.4f})')
print(f'  LR 最优参数: {lr_gs.best_params_}')
print(f'  RF 最优参数: {rf_gs.best_params_}')
print(f'[图] 模型对比   -> output/e3_model_comparison.png')
print(f'[图] 特征重要性 -> output/e3_feature_importance.png')
print('完成。')
