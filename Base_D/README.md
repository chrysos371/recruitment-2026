# Base_D — 科学上网与账户注册

## 自我介绍

我是张杨亦航（学号 2524030231）。科学上网和平台账户注册是本次招新考核的**网络基础设施**——没有稳定的国际互联网访问，后续 C2/C3 的 Colab GPU 训练、E3 的 Kaggle 提交、各种模型权重的下载都会遇到障碍。

在实验室刘鸿宇学长的帮助下，我已经配置好了 Clash Verge 客户端，订阅节点使用 [cokecloud.biz](https://cokecloud.biz/)，访问 GitHub、Google、Kaggle 等平台都很稳定。在此特别感谢刘鸿宇学长提供的订阅资源和技术指导。

本地有 RTX 5070 可以跑大部分模型，但 Google Colab 的免费 T4 是很好的补充——特别是跑长时间训练不想占本地资源的时候。

---

## 科学上网方案

| 组件 | 详情 |
|------|------|
| **客户端** | Clash Verge（Windows 桌面端） |
| **订阅服务** | [cokecloud.biz](https://cokecloud.biz/) |
| **协议** | 支持 SS/V2Ray/Trojan 等多种协议 |
| **使用方式** | 订阅链接导入 → 节点选择 → 系统代理（开机自启） |

> 特别感谢**实验室刘鸿宇学长**提供 cokecloud 订阅链接和使用指导。

**验证网络是否正常**（终端测试）：
```bash
curl -I https://github.com       # 应返回 200
curl -I https://www.google.com   # 应返回 200
```

---

## 需要的账户及与后续题目的关联

| 平台 | 用途 | 关联题目 | 状态 |
|------|------|----------|:----:|
| **GitHub** | 代码托管、版本控制 | 全部 14 题 | ✅ chrysos371 |
| **Google** | Colab GPU 训练、Gmail 注册各类服务 | C2、C3、E4 | ✅ 1623492124@qq.com |
| **Kaggle** | Titanic 竞赛提交、数据集下载 | E3 | ⬜ 待注册 |
| **HuggingFace** | 模型权重下载 | C2、E4 | ⬜ 可选 |
| **PyPI / Conda** | Python 包安装 | C1-C3、E1-E4 | ✅ 可用镜像 |

---

## GitHub — 已完成

- 用户名：`chrysos371`
- 仓库：[chrysos371/recruitment-2026](https://github.com/chrysos371/recruitment-2026)
- 认证：SSH Key（ED25519）免密推送

---

## Kaggle 注册指南

E3（泰坦尼克号）需要在这里提交预测结果获取排行榜排名。

**注册步骤：**

1. 打开 Clash Verge 确保代理已开启
2. 访问 [kaggle.com](https://www.kaggle.com/)，推荐直接用 Google 账号登录
3. 完成手机号验证（支持 +86）
4. Settings → API → **Create New API Token**，下载 `kaggle.json`
5. 将 `kaggle.json` 放到 `C:\Users\31633\.kaggle\`（没有就新建文件夹）

**Python 中使用：**
```bash
pip install kagglehub
```

---

## Google / Colab — 已完成

- 账号：`1623492124@qq.com`（外国手机号注册，已验证）
- Google Colab 提供免费 T4 GPU，C2/C3 训练时可直接使用

**Colab 使用步骤：**

1. 打开 Clash Verge 代理
2. 访问 [colab.research.google.com](https://colab.research.google.com/)，用已有 Google 账号登录
3. 新建 Notebook → 运行时 → 更改运行时类型 → **T4 GPU**
4. 验证 GPU：
```python
import torch
print(torch.cuda.is_available())     # True
print(torch.cuda.get_device_name(0)) # Tesla T4
```

**Colab 限制：** 免费版单次约 4-6 小时，闲置 30 分钟断开，训练中建议定时保存 checkpoint。

---

## HuggingFace 注册（可选）

C2（YOLO）和 E4（VGG/ResNet）可能需要下载预训练权重。

**注册步骤：**

1. 访问 [huggingface.co](https://huggingface.co/)
2. Sign Up，可用 Google 或 GitHub 直接登录
3. Settings → Access Tokens → 创建 Read token
4. 终端配置：`huggingface-cli login`

---

## 账户状态总结

| 平台 | 状态 | 备注 |
|------|:----:|------|
| Clash Verge + cokecloud | ✅ | 已配置，感谢刘鸿宇学长 |
| GitHub (chrysos371) | ✅ | SSH 免密，仓库已就绪 |
| Google / Colab | ✅ | 1623492124@qq.com，外国手机号已验证 |
| Kaggle | ⬜ | E3 开始前完成，可用 Google 直接登录 |
| HuggingFace | ⬜ | C2/E4 需要时注册 |
