# Base_B — Git 使用

## 自我介绍

我是张杨亦航（学号 2524030231）。在本次招新之前，我已经用 Git 管理过个人项目，GitHub 账号 `chrysos371` 上也有 41 个公开仓库。但这次考核的要求更系统化——不只是会用 `add/commit/push`，而是要从初始化到分支管理到远程协作，建立一套规范的版本控制流程，服务全部 14 道题的开发。

Git 对我来说不仅是"备份工具"，更是**思考过程的记录**。每题拆成 3-5 次 commit，每次提交对应一个明确的功能增量，回头看 git log 就像读开发日记。这次考核的 Git 配置我选择了 SSH 免密验证，省去每次输入密码或 token 的麻烦。

后续 Git 使用规范：每题在 `master` 分支上渐进式提交，重大功能用 `feature/*` 分支开发再 `--no-ff` 合并，保持历史可追溯。

---

## 仓库概览

| 项目 | 详情 |
|------|------|
| **本地路径** | `C:\Users\31633\Desktop\智泽实验室招新\` |
| **远程地址** | `git@github.com:chrysos371/recruitment-2026.git`（SSH） |
| **Git 版本** | 2.53.0.windows.2 |
| **用户** | chrysos371 |
| **邮箱** | 3163385811@qq.com |
| **认证方式** | SSH Key（ED25519）→ `~/.ssh/github_chrysos371` |
| **默认分支** | `master`（本地） → `main`（远程） |
| **LFS** | 已启用，追踪 `Software_E2/mnist_x.txt`（122MB） |

---

## 当前提交历史

```
*   e33bbcc  [Base_B] 合并 feature/git-demo 分支演示 --no-ff 合并
|\
| * 9e19555  [Base_B] 在 feature/git-demo 分支创建演示文件
|/
* 95362f1  [Base_A] 修正：主力 IDE 从 VS Code 改为 PyCharm 2025.3.3
* 89c27c4  [Base_A] 个性化重写：融入真实开发环境与个人信息
* 437eda9  [Base_A] 完成 Markdown 语法学习与文档编写
* c494f6f  Initial commit: 智泽实验室 2026 招新考核项目
```

---

## Git 核心操作速查

### 基础三连

```bash
git add <file>          # 暂存
git commit -m "..."     # 提交
git push origin HEAD:main  # 推送到远程 main 分支
```

### 状态查看

```bash
git status              # 工作区变化
git log --oneline --graph -10  # 提交历史树状图
git diff                # 未暂存的改动
git diff --staged       # 已暂存、未提交的改动
```

### 分支操作

```bash
git branch <name>               # 创建分支
git checkout -b <name>          # 创建并切换
git merge <branch> --no-ff      # 合并（保留分支历史）
git branch -d <name>            # 删除已合并的分支
git branch -D <name>            # 强制删除
```

### 撤销与回退

```bash
git checkout -- <file>          # 丢弃工作区改动
git reset HEAD <file>           # 取消暂存
git reset --soft HEAD~1         # 撤销最近一次 commit（保留改动）
git revert <commit>             # 创建反向提交（安全撤销）
```

### 远程同步

```bash
git remote -v                   # 查看远程仓库
git fetch origin                # 拉取远程更新（不合并）
git pull origin main            # 拉取并合并
```

---

## .gitignore 配置亮点

项目 `.gitignore` 覆盖以下类别（完整 62 行）：

| 类别 | 示例 |
|------|------|
| Python | `__pycache__/`, `*.pyc`, `*.egg-info/` |
| C++ | `*.o`, `*.obj`, `*.exe`, `build/` |
| 模型权重 | `*.pth`, `*.pt`, `*.onnx`, `*.h5`, `*.ckpt` |
| 训练产物 | `runs/`, `logs/` |
| IDE | `.vscode/`, `.idea/`, `*.swp` |
| 系统 | `.DS_Store`, `Thumbs.db` |
| 环境 | `venv/`, `.venv/`, `env/` |

---

## Git 工作流约定（本次考核全 14 题通用）

```
每题 3-5 次 commit，格式：[题目编号] 简短描述

示例：
  [C1] 实现 OpenCV Haar Cascade 人脸检测
  [C1] 添加 GaussianBlur 模糊处理
  [C1] 完成文档和截图

分支策略：
  - 日常开发在 master 上渐进提交
  - 实验性改动开 feature/* 分支
  - 合并用 --no-ff 保留分支痕迹
```
