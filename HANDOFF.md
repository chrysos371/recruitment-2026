# 交接文档 — 智泽实验室 2026 招新

> 把这个文件内容复制给新会话的 Claude，即可无缝继续。

---

## 背景

我正在做**河海大学智泽实验室 2026 年招新考核**，选的是**软件类 + CV(C类) + 机器学习(E类)**。

原始材料在桌面：
- `C:\Users\31633\Desktop\招新题目.pdf`（完整题目说明）
- `C:\Users\31633\Desktop\参考材料及部分模版和数据集.zip`（已解压到项目里）

## 项目位置

```
C:\Users\31633\Desktop\智泽实验室招新\
```

已初始化 Git 仓库，Git 用户配置：`chrysos371` / `3163385811@qq.com`

## 题目清单（共 14 题）

| 编号 | 题目 | 难度 | 状态 |
|------|------|------|------|
| Base_A | Markdown 使用 | 基础 | ⬜ 未开始 |
| Base_B | Git 使用 | 基础 | ⬜ 未开始 |
| Base_C | Linux 使用 | 基础 | ⬜ 未开始 |
| Base_D | 科学上网 | 基础 | ⬜ 未开始 |
| Software_A1 | Rational 有理数类 (C++) | 简单 | ⬜ 未开始 |
| Software_A2 | Shape 图形类体系 (C++) | 简单 | ⬜ 未开始 |
| Software_C1 | OpenCV 基础 + 人脸模糊 | 简单 | ⬜ 未开始 |
| Software_C2 | YOLO 目标检测 (人/电动车) | 中等 | ⬜ 已有数据集 |
| Software_C3 | 红绿灯检测 (强鲁棒性) | 困难 | ⬜ 已有数据集 |
| Software_E1 | BP 神经网络手写实现 | 简单 | ⬜ 已有模板 |
| Software_E2 | 手写数字识别 MLP vs CNN | 中等 | ⬜ 已有数据集 |
| Software_E3 | 泰坦尼克号 Kaggle 竞赛 | 中等 | ⬜ 未开始 |
| Software_E4 | VGG vs ResNet 对比复现 | 困难 | ⬜ 未开始 |

## 已有数据文件

| 位置 | 内容 |
|------|------|
| `Software_C2/` | 68张电动车行人图片 + 1张标注参考图 |
| `Software_C3/` | 40张红绿灯场景图片 |
| `Software_E1/` | C++ 和 Python 的 BP 神经网络模板 |
| `Software_E2/` | MNIST 数据集 (mnist_x.txt 70000行, mnist_y.txt 70000行) + 手写数字识别作业说明.docx |

## 待办：GitHub 远程仓库

- GitHub 用户名：`chrysos371`
- Token 已配置到系统环境变量（`GITHUB_PERSONAL_ACCESS_TOKEN`）
- **下一步：让 Claude 用 GitHub MCP 创建远程仓库并 push**

> 告诉新会话：**"请用 GitHub MCP 帮我在 chrysos371 账号下创建一个智泽实验室招新的远程仓库，然后把本地项目 push 上去"**

## 提交要求速览

- 截止：**8 月 20 日前后**
- 提交：百度网盘（永久有效）+ 邮箱 yuanzhechn@163.com
- 格式：`学号_姓名.zip`
- 所有文档用 Markdown 写，每题需包含学习过程、踩坑记录、实操截图
- 允许用大模型辅助，但要理解并记录过程
- 每题额外需独立自我介绍，重动机和规划，不写学生履历

## 评分规则

- A 类必做（简单题 1 分）
- 从 B/C/D/E 四类中我选了 C 和 E 两个方向
- C1(1分) + C2(3分) + C3(5分) + E1(1分) + E2(3分) + E3(3分) + E4(5分) = 21分（远超9分门槛）
