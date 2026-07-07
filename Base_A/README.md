# Base_A — Markdown 使用

## 自我介绍

选择软件方向加入智泽实验室的招新考核，源于我对"让机器看见世界"这件事的强烈兴趣。计算机视觉和机器学习是当下 AI 浪潮中最具感知力的分支，从自动驾驶到医疗影像，它们正在重新定义技术与社会的关系。

我选择从最基础的 Markdown 语法开始，因为**文档能力是工程师的隐性竞争力**。再好的算法，如果无法清晰传达思路、记录过程和分享结果，影响力都会大打折扣。我的规划是：在本次考核中，所有文档均使用 Markdown 编写，形成一套可复用的文档模板，为后续所有题目提供规范化的输出标准。

本次 Markdown 的学习目标是：不仅能写，还要写得规范、美观、可维护。

---

## Markdown 语法速查

### 1. 标题

```markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
```

### 2. 文本样式

| 效果 | 语法 |
|------|------|
| **粗体** | `**粗体**` |
| *斜体* | `*斜体*` |
| ~~删除线~~ | `~~删除线~~` |
| `行内代码` | `` `行内代码` `` |

### 3. 列表

**无序列表：**
```markdown
- 项目一
- 项目二
  - 子项目
```

**有序列表：**
```markdown
1. 第一步
2. 第二步
3. 第三步
```

### 4. 代码块

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### 5. 表格

```markdown
| 列 A | 列 B | 列 C |
|------|------|------|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |
```

支持 `:--`（左对齐）、`:--:`（居中）、`--:`（右对齐）。

### 6. 图片

```markdown
![替代文本](path/to/image.png)
```

### 7. 链接

```markdown
[链接文本](https://example.com)
```

### 8. 引用

```markdown
> 这是一段引用文字。
> 可以跨多行。
```

### 9. 分隔线

```markdown
---
```

### 10. 任务列表

```markdown
- [x] 已完成
- [ ] 待完成
```

### 11. 数学公式（LaTeX）

GitHub 渲染需用 `$` 包裹：

```markdown
行内公式：$E = mc^2$

块级公式：
$$
\frac{\partial L}{\partial w} = \frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i) \cdot x_i
$$
```

> **注意**：GitHub 的 Markdown 渲染器原生不支持 LaTeX，建议使用 VS Code 的 Markdown Preview Enhanced 插件预览，或使用 [CodeCogs](https://www.codecogs.com/latex/eqneditor.php) 生成公式图片。

### 12. HTML 嵌入

Markdown 支持内嵌 HTML：

```html
<div align="center">
  <b>居中粗体文本</b>
</div>
```

<div align="center">
  <b>居中粗体文本</b>
</div>

---

## Markdown 编辑器推荐

| 编辑器 | 特点 |
|--------|------|
| **VS Code** | Markdown Preview Enhanced 插件，实时预览，支持 LaTeX |
| **Typora** | 所见即所得，导出 PDF/HTML |
| **Obsidian** | 双向链接，知识库管理 |

---

## 本套文档规范

以下规范将应用于本次考核的全部 14 道题：

| 文件 | 内容 |
|------|------|
| `README.md` | 自我介绍 + 题目概述 + 实现方案 + 使用方法 + 结果展示 |
| `notes.md` | 学习过程 + 踩坑记录 + 实操截图 |
| `screenshots/` | 存放 PNG 格式截图 |

**代码块注明语言，便于语法高亮；表格对齐规范；截图统一放 `screenshots/` 目录；标题层级不超过三级。**
