# 学习过程与踩坑记录 — Git

## 学习过程

### 阶段一：回顾基础

我之前零零散散用过 Git，但主要是 `add/commit/push` 三板斧。这次系统过了一遍：

- [廖雪峰 Git 教程](https://liaoxuefeng.com/books/git/)——中文社区经典，把工作区/暂存区/版本库的概念讲得很清楚
- [Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN)——交互式学习分支操作，可视化非常直观

加深理解的关键概念：

| 概念                      | 理解                                           |
| ----------------------- | -------------------------------------------- |
| 工作区 vs 暂存区              | `git add` 是工作区 → 暂存区，`git commit` 是暂存区 → 版本库 |
| HEAD 指针                 | 指向当前分支的最新 commit                             |
| Fast-forward vs --no-ff | ff 直接移动指针（历史是直线），--no-ff 保留分支痕迹（能看到合并点）      |
| Git LFS                 | 大文件不存仓库本体，只存指针，实际文件托管在 LFS 服务器               |

### 阶段二：本次考核的 Git 配置

**初始化**：项目初始化时就做了 `git init`，创建了标准 `.gitignore`（62 行覆盖 Python/C++/模型/IDE）。

**SSH 认证**：不用 token 每次输入，直接生成 ED25519 密钥对，公钥加到 GitHub，配置 `~/.ssh/config` 指定 github.com 用这个 key。之后 `git push` 全程免密。

**大文件处理**：`mnist_x.txt` 122MB 超过 GitHub 100MB 限制。用 `git lfs track` 追踪，首次推送时 LFS 对象上传成功后再推常规对象。

**分支演示**：为满足题目"需包含分支操作"的要求，创建 `feature/git-demo` 分支 → 添加文件 → `--no-ff` 合并回 `master`，在 git log 中留下清晰的分支图。

### 阶段三：规范建立

每题 3-5 个 commit，格式 `[题号] 简短描述`，中文提交信息。这比零散的英文 commit message 更容易回顾。

---

## 踩坑记录

### 坑 1：`master` vs `main` 分支名不一致

**现象**：本地是 `master`，GitHub 默认创建的是 `main`。直接 `git push` 报错：

```
fatal: The upstream branch of your current branch does not match
the name of your current branch.
```

**原因**：GitHub 2020 年起把默认分支从 `master` 改为 `main`，本地和远程分支名不同。

**解决**：用 `git push origin HEAD:main` 显式指定映射。也可以在远程把默认分支改成 `master`，但我选择了接受这个差异——本地 `master` 推远程 `main`。

### 坑 2：Git LFS push 时 lock verify 失败

**现象**：第二次 push 时报：

```
Remote "origin" does not support the Git LFS locking API.
Post "https://lfs.github.com/.../locks/verify": EOF
```

**原因**：Git LFS 默认尝试与远程服务器验证文件锁定权限，但 GitHub 的 LFS 实现不完全支持 locking API。

**解决**：`git config lfs.https://github.com/<user>/<repo>.git/info/lfs.locksverify false` 禁用锁定验证。不影响 LFS 存储和下载功能。

### 坑 3：大文件首次 push 被拒

**现象**：初始 commit 包含 122MB 的 `mnist_x.txt`，直接 push 被 GitHub 拒绝：

```
File mnist_x.txt is 121.81 MB; this exceeds GitHub's file size limit of 100.00 MB
```

**原因**：GitHub 单文件限制 100MB，超出必须用 Git LFS。

**解决**：三步走：

1. `git lfs track "Software_E2/mnist_x.txt"`——让 LFS 接管此文件
2. `git rm --cached` + `git add`——移除普通缓存，让 LFS 重新 add
3. `git commit --amend`——重写最近一次提交

### 坑 4：敏感信息泄露（Token 在命令输出中暴露）

**现象**：第一次配置远程仓库时，用了 `https://<username>:<token>@github.com/...` 格式的 URL，`git remote -v` 输出里 token 明文可见。

**解决**：

1. 立即撤销那个 token（GitHub Settings → Developer settings → Tokens）
2. 切换到 SSH 认证，远程 URL 改为 `git@github.com:chrysos371/recruitment-2026.git`
3. 以后永远不在 URL 里嵌入密码/token

---

## 合并冲突演示

题目要求"能查看修改记录并处理冲突"，下面通过一个实验场景展示 merge conflict 的产生和解决。

### 场景模拟

假设两个分支同时修改同一个文件的同一行：

```bash
# 1. 从 master 创建两个实验分支
git checkout -b feature/conflict-demo
echo "version A: 使用高斯模糊" > conflict-test.txt
git add conflict-test.txt && git commit -m "[demo] A 方案：高斯模糊"

git checkout master
git checkout -b feature/conflict-demo-b
echo "version B: 使用中值滤波" > conflict-test.txt
git add conflict-test.txt && git commit -m "[demo] B 方案：中值滤波"
```

### 制造冲突

```bash
git checkout master
git merge feature/conflict-demo --no-ff    # 先合并 A 方案, 成功
git merge feature/conflict-demo-b --no-ff  # 再合并 B 方案 → 冲突！
```

此时 Git 输出:

```
Auto-merging conflict-test.txt
CONFLICT (add/add): Merge conflict in conflict-test.txt
Automatic merge failed; fix conflicts and then commit the result.
```

### 查看冲突标记

```bash
git status           # 显示 both modified: conflict-test.txt
cat conflict-test.txt
```

文件内容:

```
<<<<<<< HEAD
version A: 使用高斯模糊
=======
version B: 使用中值滤波
>>>>>>> feature/conflict-demo-b
```

**冲突标记含义：**

| 区域 | 含义 |
|------|------|
| `<<<<<<< HEAD` 到 `=======` | 当前分支 (master, 已合并 A 方案) 的内容 |
| `=======` 到 `>>>>>>> branch` | 待合并分支 (B 方案) 的内容 |

### 解决冲突

```bash
# 手动编辑 conflict-test.txt，决定最终内容:
echo "最终方案: 高斯模糊 + 中值滤波 (自适应切换)" > conflict-test.txt

git add conflict-test.txt
git commit -m "[demo] 解决合并冲突：融合 A/B 方案"
```

### 冲突解决后的历史

```
*   9f2a3d1 [demo] 解决合并冲突：融合 A/B 方案
|\
| * 6b1f8a2 [demo] B 方案：中值滤波
* | 4c5d7e3 Merge branch 'feature/conflict-demo'
|\|
| * 2a1b3c4 [demo] A 方案：高斯模糊
```

### 实用技巧

| 场景 | 命令 |
|------|------|
| 放弃合并，恢复冲突前状态 | `git merge --abort` |
| 全部采用当前分支版本 | `git checkout --ours <file>` |
| 全部采用对方版本 | `git checkout --theirs <file>` |
| 可视化冲突解决 (PyCharm) | 右键 → Git → Resolve Conflicts |
| 查看冲突文件列表 | `git diff --name-only --diff-filter=U` |

> PyCharm 的 Git 集成提供了图形化的三方合并界面，比手动编辑 `<<<<<<` 标记更直观。需要时配合使用效果更好。
