# 学习过程与踩坑记录 — Linux

## 学习过程

### 阶段一：安装 WSL2 + Ubuntu

之前的 Linux 基础主要是零散的服务器操作（AutoDL 上跑 E4 训练时用过 `ssh`、`scp`、`nvidia-smi` 等）。这次为了系统性地完成 Linux 题，在 Win11 上安装了 WSL2：

```powershell
wsl --install -d Ubuntu    # 安装 Ubuntu
wsl --set-default-version 2
```

装的是 Ubuntu 26.04 LTS。相比双系统/虚拟机，WSL2 启动快、内存占用小，而且 `/mnt/c` 直接挂载 Windows 盘，本项目的 Python/C++ 源码两边都能访问。

### 阶段二：系统梳理常用命令

按 8 大类把常用命令过了一遍并实际跑通（见 `demo.sh` 与截图）：

| 类别 | 核心命令 | 理解重点 |
|------|----------|----------|
| 系统信息 | `uname` / `whoami` / `id` | UID/GID、所属组 |
| 文件系统 | `ls` / `mkdir` / `cp` / `mv` / `rm` | 目录树与相对/绝对路径 |
| 文本处理 | `cat` / `grep` / `sort` / `uniq` / `cut` | 管道让命令组合 |
| 权限 | `chmod` / `ls -l` | rwx 与数字表示 |
| 进程 | `ps` / `kill` / `top` | 前台/后台、信号 |
| 网络 | `ip` / `ping` / `curl` | NAT 模式下的地址 |
| 归档 | `tar -czf/-tzf/-xzf` | 打包与压缩 |
| 包管理 | `apt` / `dpkg` | 依赖管理 |

### 阶段三：写实操脚本

把散碎的命令整理成 `demo.sh`，用 `section()` 分段、`cmd()` 高亮提示正在执行的命令，一次运行即可复现全部 8 类操作，输出直接用于截图。

---

## 踩坑记录

### 坑 1：`/mnt/c` 下 chmod 无效

**现象**：第一次把 demo 脚本放在 `/mnt/c/Users/.../智泽实验室招新/`（Windows 挂载目录）里跑，`chmod 755` 后 `ls -l` 显示依然是 `-rwxrwxrwx`，权限根本没变。

**原因**：WSL2 挂载 Windows 盘用的是 drvfs/9p 文件系统，**不支持 Unix 权限位**。所有文件都显示 777，chmod 是无效操作。

**解决**：把演示放到 WSL 原生文件系统（`~`，即 `/home/zyyh`，ext4）里执行，chmod 才真正生效：

```
$ chmod 755 run.sh   →  -rwxr-xr-x
$ chmod 644 run.sh   →  -rw-r--r--
```

> 这也说明：跨盘开发时，代码放 `/mnt/c` 方便，但涉及权限/符号链接/性能敏感的操作应放原生 ext4。

### 坑 2：WSL2 NAT 模式不镜像 Windows 代理

**现象**：启动 WSL 时终端报：

```
wsl: 检测到 localhost 代理配置，但未镜像到 WSL。
NAT 模式下的 WSL 不支持 localhost 代理。
```

**原因**：Windows 上开着 Clash Verge（cokecloud 代理），WSL2 默认 NAT 模式不会自动把 Windows 的 localhost 代理配置镜像进 Linux。所以 WSL 内直接访问外网可能走不通。

**解决**：本次实测 WSL 内 `ping` 和 `curl` 都能直接出网（NAT 下访问外网本身没问题），只是**不会自动继承 Windows 的代理软件**。若需要走代理，可手动 `export http_proxy=http://<windows_ip>:7890`。

### 坑 3：中文路径在 Windows ↔ WSL 之间传递

**现象**：项目路径是 `C:\Users\31633\Desktop\智泽实验室招新\`，在 WSL 里对应 `/mnt/c/Users/31633/Desktop/智泽实验室招新/`。从 Git Bash 调用 `wsl.exe` 跑含中文路径的脚本时，偶尔出现乱码。

**原因**：Windows 终端（GBK 代码页）与 Linux（UTF-8）编码不一致，中文字符在两者之间传递需要正确转码。

**解决**：确保脚本文件本身是 UTF-8 编码，WSL 侧统一按 UTF-8 处理即可正常读写中文路径。本次 demo 脚本含中文注释，在 WSL 内运行无乱码。

---

## 与考核其他题目的衔接

Linux 环境贯穿整个考核：

- **E4（VGG vs ResNet）**：在 AutoDL 的 Linux 服务器上用 `ssh` 登录、`scp` 传代码、`nvidia-smi` 看 GPU、`python cifar10_train.py` 训练。
- **Git（Base_B）**：Linux 的 `git` 命令行是版本控制的基础。
- **日常开发**：WSL 里可以跑 Python 脚本，与 Windows 侧共享同一份项目源码。

这次 Linux 题的完成，让我把之前零散的服务器操作串成了体系，也补齐了文件系统、权限、进程、管道这些最基础但最常用的知识。
