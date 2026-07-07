# 学习过程与踩坑记录 — 科学上网与账户注册

## 学习过程

### 阶段一：理解为什么需要科学上网

在国内做 AI/CV 开发，以下场景几乎无法绕开国际互联网访问：

- **GitHub**：虽然能直接访问，但不稳定，clone 大仓库经常断
- **Google Colab**：完全不挂代理访问不了
- **Kaggle**：同样需要代理
- **PyTorch/torchvision 预训练权重**：下载源在海外，直连极慢
- **HuggingFace**：模型和数据集托管在海外
- **论文/文档**：arXiv、Papers with Code、各类英文文档

没有稳定的国际网络，后续的 C2（YOLO）、C3（红绿灯检测）、E3（Titanic）、E4（VGG vs ResNet）都会严重受阻。

### 阶段二：搭建代理环境

在刘鸿宇学长的推荐下，使用 **Clash Verge** 作为桌面客户端。Clash Verge 是 Clash 内核的图形化前端，比原始的配置文件管理方便很多。

**配置过程：**

1. 下载 Clash Verge（GitHub Release 页面）
2. 将 cokecloud 的订阅链接粘贴进客户端，自动拉取节点列表
3. 开启系统代理，浏览器和终端自动走代理
4. 设置开机自启，确保一直在代理环境

**为什么选 Clash Verge 而不是其他工具：**

| 特性 | Clash Verge | 其他客户端 |
|------|:-----------:|:---------:|
| 订阅链接直接导入 | ✅ | 部分不支持 |
| 规则分流（国内直连/国外代理） | ✅ | 部分需要手动配置 |
| 图形化界面 | ✅ | 部分只有命令行 |
| 开源 | ✅ | 商业软件 |

### 阶段三：账户注册

GitHub 账号 `chrysos371` 此前已注册并长期使用。Google 和 Kaggle 账户在 E3 和 C2/C3 开始前按需注册即可——有代理环境后，这些注册流程都是常规操作。

---

## 踩坑记录

### 坑 1：终端不走系统代理

**现象**：浏览器能正常访问 Google，但 Git Bash 里 `curl https://www.google.com` 超时。

**原因**：Clash Verge 的系统代理只对 Windows 图形程序生效（走系统代理设置），终端程序默认不跟随。

**解决**：在 Git Bash 里手动设置代理环境变量：
```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
```
或者打开 Clash Verge 的 **TUN 模式**——虚拟网卡级别代理，终端和所有程序都自动走代理，无需额外配置。

### 坑 2：代理环境下 Git SSH push 失败

**现象**：开了代理后 `git push` 报 connection refused。

**原因**：Git 用的是 SSH 协议（端口 22），代理只转发 HTTP/HTTPS，SSH 连接被绕过。

**解决**：GitHub 的 SSH 在国内通常能直连，Clash Verge 的规则分流也默认让国内流量直连，所以 SSH push 一般不受影响。如果遇到极端情况，可以用 `HTTPS` 协议替代 SSH，或者给 SSH 配置代理跳板。

### 坑 3：订阅链接失效

**现象**：某天打开 Clash Verge 发现所有节点不可用。

**原因**：cokecloud 订阅链接有时效性，过期后需要刷新。

**解决**：Clash Verge 有"更新订阅"按钮，点一下重新拉取即可。如果订阅长期失效，联系 cokecloud 客服或查看网站公告。
