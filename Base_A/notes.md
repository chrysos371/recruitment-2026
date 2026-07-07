# 学习过程与踩坑记录 — Markdown

## 学习过程

### 阶段一：为什么是 Markdown

我之前写代码注释和 README 时已经零零散散用过 Markdown，但没有系统学过语法规范。这次招新考核要求所有文档用 Markdown 写，正好借机把基础夯实。

参考资源：[Markdown 官方中文教程](https://markdown.com.cn/basic-syntax/)，大概花了 20 分钟过完核心语法。对我日常写技术文档来说，以下 7 类是高频使用的：

| 类别 | 典型场景 |
|------|----------|
| 标题 `#` | 文档层级 |
| 代码块 ` ``` ` | 贴代码片段、终端输出 |
| 表格 | 模型对比、参数说明 |
| 图片 `![]()` | loss 曲线、检测效果截图 |
| 链接 `[]()` | 引用论文、GitHub 仓库 |
| 列表 `-` / `1.` | 依赖项、操作步骤 |
| 强调 `**` | 关键结论 |

剩下引用、分隔线、任务列表、HTML 嵌入属于锦上添花，知道有就行。

### 阶段二：确定文档规范

反复改排版是效率黑洞。趁这次做第一题，我给自己定了规矩，后面 13 题一律照搬：

- `README.md`：自我介绍 + 方案 + 用法 + 结果
- `notes.md`：学习过程 + 踩坑 + 截图
- `screenshots/`：截图集中放
- 标题最深三级、代码块必标语言、表格要对齐

### 阶段三：在自己的环境里验证

我的日常配置：Windows 11 + PyCharm 2025.3.3 + Git Bash 2.53。PyCharm 自带 Markdown 分屏预览，右侧实时渲染，LaTeX 公式也能正常显示。GitHub 上看不了 LaTeX 是个小遗憾，但项目代码里公式出现频率不高，必要时用 CodeCogs 生成图片挂上去。

---

## 踩坑记录

### 坑 1：代码块里演示代码块——反引号嵌套

想在 Markdown 里教别人怎么写 Markdown 代码块，结果写成这样：

```markdown
```python
print("hello")
```
```

外层三个反引号吃掉了内层的三个反引号，渲染直接炸掉。

**解决**：外层用四个反引号包住内层三个反引号：

`````markdown
````markdown
```python
print("hello")
```
````
`````

### 坑 2：GitHub 不支持 LaTeX 渲染

写了半天 `$$ \frac{\partial L}{\partial w} $$`，push 到 GitHub 一看——纯文本。

**解决**：本地方案用 VS Code Markdown Preview Enhanced 预览；跨平台方案用 [CodeCogs](https://latex.codecogs.com/) 生成公式 PNG 再嵌入。对我本次考核来说，公式主要在 E1（BP 推导）和 E4（ResNet 论文分析）中出现，届时用 CodeCogs 生成图片即可。

### 坑 3：表格里的管道符

表格单元格里写 shell 管道的 `|` 会被当成列分隔符。

**解决**：用 `\|` 转义。

### 坑 4：Windows CRLF vs Linux LF

Git Bash 里写 `.md` 默认 CRLF 换行，Linux 环境（WSL）打开多了一堆 `^M`。

**解决**：VS Code 右下角把默认换行符改成 LF，一劳永逸——所有题目文档都用 LF。
