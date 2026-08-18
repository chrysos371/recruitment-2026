# -*- coding: utf-8 -*-
"""
生成 自我介绍.pdf — 智泽实验室 2026 招新
=========================================
张杨亦航 (2524030231)
用 matplotlib 生成排版整洁的自我介绍 PDF, 含个人信息占位符。
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.backends.backend_pdf import PdfPages

# ---- 中文字体 ----
for f in ['Microsoft YaHei', 'SimHei', 'SimSun']:
    if any(f.lower() in x.name.lower() for x in font_manager.fontManager.ttflist):
        CJK = f
        break
else:
    CJK = 'sans-serif'
font_manager.fontManager.addfont  # no-op, keep simple
plt.rcParams['font.family'] = CJK
plt.rcParams['axes.unicode_minus'] = False

# ---- 内容 ----
# 每项: (type, text)  type in {title, sub, h, body, gap, line}
content = [
    ('title', '自 我 介 绍'),
    ('sub',   '河海大学 · 智泽实验室 2026 招新考核'),
    ('line',  ''),
    ('gap',   ''),
    ('h',     '一、基本信息'),
    ('body',  '姓    名：张杨亦航'),
    ('body',  '学    号：2524030231'),
    ('body',  '学    校：河海大学'),
    ('body',  '学院/专业：人工智能与自动化学院 · 智能科学与技术专业'),
    ('body',  '年    级：大二（2025 级）'),
    ('body',  '邮    箱：3163385811@qq.com'),
    ('body',  'GitHub ：chrysos371'),
    ('gap',   ''),
    ('h',     '二、技术栈'),
    ('body',  '编程语言：C++（C++20）、Python'),
    ('body',  '机器学习：NumPy、PyTorch、scikit-learn'),
    ('body',  '计算机视觉：OpenCV、YOLO（Ultralytics）、Haar Cascade'),
    ('body',  '开发工具：Git、Linux / WSL2、VS 2022、PyCharm、Conda'),
    ('gap',   ''),
    ('h',     '三、项目经历（本次招新考核）'),
    ('body',  '独立完成「软件类 + 计算机视觉(C) + 机器学习(E)」共 14 题：'),
    ('body',  '· 软件类：Rational 有理数类、Shape 图形类体系（C++ 多态 / 异常 / 运算符重载）'),
    ('body',  '· 计算机视觉：OpenCV 人脸模糊、YOLO 目标检测、红绿灯检测'),
    ('body',  '· 机器学习：BP 神经网络手写实现（MAE < 0.01）、MNIST MLP vs CNN'),
    ('body',  '  （98.64% vs 99.48%）、Titanic 生还预测、VGG vs ResNet 复现对比'),
    ('body',  '  （VGG 90.72% vs ResNet 93.96%）'),
    ('gap',   ''),
    ('h',     '四、自我评价'),
    ('body',  '做事有效率，自学能力强，对人工智能领域兴趣浓厚；'),
    ('body',  '能够快速上手新工具、新框架，独立完成从环境搭建到模型训练的全流程。'),
    ('gap',   ''),
    ('h',     '五、加入实验室的动机与期望'),
    ('body',  '对机器学习与计算机视觉方向有浓厚兴趣，希望在智泽实验室得到系统'),
    ('body',  '性的指导与实践机会，与志同道合的同学一起做项目、参加竞赛，'),
    ('body',  '进一步提升工程能力与科研素养。'),
    ('gap',   ''),
    ('line',  ''),
    ('gap',   ''),
    ('body',  '（此处粘贴个人照片）'),
]

# ---- 绘制 ----
PAGE_W = 8.27   # A4 宽 (inch)
PAGE_H = 11.69  # A4 高 (inch)
LEFT = 0.9
RIGHT = PAGE_W - 0.9
TOP = 10.9

with PdfPages('自我介绍.pdf') as pdf:
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.axis('off')

    y = TOP

    def new_page():
        global y
        pdf.savefig(fig, bbox_inches=None, facecolor='white')
        fig.clf()
        fig.patch.set_facecolor('white')
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, PAGE_W); ax.set_ylim(0, PAGE_H); ax.axis('off')
        y = TOP

    for typ, text in content:
        if y < 1.0:
            new_page()

        if typ == 'title':
            ax.text(PAGE_W/2, y, text, ha='center', va='top',
                    fontsize=26, fontweight='bold', color='#1a1a1a')
            y -= 0.55
        elif typ == 'sub':
            ax.text(PAGE_W/2, y, text, ha='center', va='top',
                    fontsize=12, color='#555555')
            y -= 0.4
        elif typ == 'h':
            ax.text(LEFT, y, text, ha='left', va='top',
                    fontsize=14, fontweight='bold', color='#1f3864')
            y -= 0.38
        elif typ == 'body':
            ax.text(LEFT, y, text, ha='left', va='top', fontsize=11, color='#222222')
            y -= 0.32
        elif typ == 'gap':
            y -= 0.18
        elif typ == 'line':
            ax.plot([LEFT, RIGHT], [y + 0.05, y + 0.05], color='#1f3864', lw=1.2)
            y -= 0.3

    pdf.savefig(fig, facecolor='white')
    plt.close(fig)

print('已生成 自我介绍.pdf')
