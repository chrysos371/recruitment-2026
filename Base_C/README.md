# Base_C — Linux 使用

## 自我介绍

我是张杨亦航（学号 2524030231）。这次考核的 Linux 部分，我选择用 **WSL2（Windows Subsystem for Linux）** 来完成——它让我在 Win11 上无缝使用原生 Ubuntu，无需双系统或虚拟机，既满足日常开发（跑 Python/OpenCV 训练脚本），又能完成本题的 Linux 实操。

对我来说，Linux 不是"会敲几个命令"，而是**理解文件系统、权限、进程、管道这些底层机制**。这次考核我系统梳理了一遍常用命令，把每类操作都实际跑了一遍并截图留档。下面 `demo.sh` 是本次实操的核心脚本，覆盖 8 大类操作。

---

## 环境概览

| 项目         | 详情                                        |
| ---------- | ----------------------------------------- |
| **虚拟化方案**  | WSL2（Windows Subsystem for Linux）          |
| **发行版**    | Ubuntu 26.04 LTS（Resolute Raccoon）          |
| **内核**     | 6.18.33.2-microsoft-standard-WSL2          |
| **用户**     | zyyh（uid 1000，属于 sudo 组）                  |
| **包管理器**   | apt 3.2.0（已安装 549 个软件包）                     |
| **网络模式**   | NAT（eth0 172.22.190.159/20）               |
| **安装日期**   | 2026/08/11                                 |
| **实操脚本**   | `demo.sh`（8 大类操作，见下）                       |

---

## 核心命令速查

### 1. 系统信息

```bash
uname -a                 # 内核/架构信息
cat /etc/os-release      # 发行版版本
whoami / id              # 当前用户 / UID、GID、所属组
hostname                 # 主机名
```

### 2. 文件系统导航

```bash
pwd                      # 当前目录
ls -la                   # 详细列表（含隐藏文件）
mkdir -p a/b             # 递归创建目录
cp src dst               # 拷贝
mv src dst               # 移动/重命名
rm file                  # 删除
find dir -name '*.txt'   # 按名称查找
```

### 3. 文本处理与管道

```bash
cat file                 # 查看文件
head -n 3 / tail -n 5    # 头部/尾部 N 行
grep 'pattern' file      # 过滤匹配行
wc -l file               # 统计行数
sort | uniq -c           # 排序 + 去重计数
cut -d: -f1              # 按分隔符取列
command1 | command2      # 管道：前一个输出作后一个输入
```

### 4. 权限管理

```bash
chmod 755 file           # rwxr-xr-x（属主全权限，其他读+执行）
chmod 644 file           # rw-r--r--（属主读写，其他只读）
ls -l                    # 查看权限位
```

> 权限数字：`r=4 w=2 x=1`，三位分别代表 属主/属组/其他。

### 5. 进程管理

```bash
ps aux                   # 查看所有进程
kill PID                 # 结束进程
top                      # 实时进程监控
command &                # 后台运行
```

### 6. 网络工具

```bash
ip -4 addr show eth0     # 查看 IP
ping -c 2 223.5.5.5      # 连通性测试
curl -sI url             # 查看响应头
```

### 7. 压缩归档

```bash
tar -czf out.tar.gz dir  # 打包压缩
tar -tzf out.tar.gz      # 查看包内容
tar -xzf out.tar.gz      # 解压
```

### 8. 包管理

```bash
sudo apt update          # 更新索引
sudo apt install pkg     # 安装
apt --version            # 查看版本
dpkg -l | wc -l          # 统计已安装包数
```

---

## 实操截图

| 截图 | 内容 |
|------|------|
| `output/c1_sys_fs.png` | 系统信息 + 文件系统导航操作 |
| `output/c2_text_perm.png` | 文本处理/管道 + 权限管理 |
| `output/c3_proc_net.png` | 进程管理 + 网络工具 |
| `output/c4_arch_pkg.png` | 压缩归档 + 包管理 |

---

## 配置亮点

- **sudo 免密**：用户 `zyyh` 已加入 `sudo` 组，可直接执行管理命令。
- **Windows 文件互通**：`/mnt/c` 挂载了 Windows C 盘，本项目源码在 WSL 内可直接访问。
- **中文路径兼容**：项目路径含中文，WSL 通过 UTF-8 正确挂载，脚本正常读写。
