#!/bin/bash
# ================================================================
#  Base_C — Linux 实操演示脚本
#  河海大学智泽实验室 2026 招新考核
#  张杨亦航 (2524030231)
#
#  覆盖: 系统信息 / 文件系统 / 文本处理与管道 / 权限 / 进程 / 网络 / 脚本
#  运行环境: WSL2 Ubuntu 26.04 LTS
# ================================================================

set -u
C_G="\033[32m"; C_B="\033[34m"; C_Y="\033[33m"; C_N="\033[0m"

# 在 WSL 原生文件系统 (ext4, ~) 中演示, 确保 chmod 等权限操作真实生效
# (Windows 挂载的 /mnt/c 是 drvfs/9p, 不支持 Unix 权限位, chmod 无效)
cd ~

section() { echo -e "\n${C_B}==================== $1 ====================${C_N}"; }
cmd() { echo -e "${C_Y}\$ $*${C_N}"; }

# ---------------------------------------------------------------
section "1. 系统信息"
# ---------------------------------------------------------------
cmd uname -a
uname -a
cmd "cat /etc/os-release | grep PRETTY"
grep PRETTY /etc/os-release
cmd "whoami / id"
echo "当前用户: $(whoami)  UID=$(id -u)  GID=$(id -g)"
cmd "hostname / date"
echo "主机名: $(hostname)    时间: $(date '+%Y-%m-%d %H:%M:%S')"

# ---------------------------------------------------------------
section "2. 文件系统导航与操作"
# ---------------------------------------------------------------
cmd "pwd"
pwd
cmd "mkdir -p linux-demo/data && cd linux-demo"
mkdir -p linux-demo/data && cd linux-demo
echo "已进入: $(pwd)"
cmd "touch data/{a,b,c}.txt"
touch data/a.txt data/b.txt data/c.txt
cmd "ls -la data/"
ls -la data/
cmd "cp data/a.txt data/a_copy.txt"
cp data/a.txt data/a_copy.txt
cmd "mv data/a_copy.txt data/renamed.txt"
mv data/a_copy.txt data/renamed.txt
echo "拷贝/重命名后:"
ls -1 data/
cmd "rm data/b.txt"
rm data/b.txt
echo "删除 b.txt 后剩余 $(ls data/ | wc -l) 个文件"

# ---------------------------------------------------------------
section "3. 文本处理与管道 / 重定向"
# ---------------------------------------------------------------
printf "apple\nbanana\napple\ncherry\nbanana\napple\n" > data/fruits.txt
cmd "cat data/fruits.txt"
cat data/fruits.txt
cmd "sort data/fruits.txt | uniq -c"
sort data/fruits.txt | uniq -c
cmd "grep 'apple' data/fruits.txt"
grep 'apple' data/fruits.txt
cmd "wc -l data/fruits.txt"
echo "总行数: $(wc -l < data/fruits.txt)"
cmd "head -n 3 /etc/passwd | cut -d: -f1"
head -n 3 /etc/passwd | cut -d: -f1
cmd "find data -name '*.txt'"
find data -name '*.txt'

# ---------------------------------------------------------------
section "4. 文件权限管理"
# ---------------------------------------------------------------
cmd "touch data/run.sh"
touch data/run.sh
echo "初始权限:"
ls -l data/run.sh
cmd "chmod 755 data/run.sh"
chmod 755 data/run.sh
echo "chmod 755 后:"
ls -l data/run.sh
cmd "chmod 644 data/run.sh"
chmod 644 data/run.sh
echo "chmod 644 后:"
ls -l data/run.sh
echo "权限数字含义: r=4 w=2 x=1, 755=rwxr-xr-x, 644=rw-r--r--"

# ---------------------------------------------------------------
section "5. 进程管理"
# ---------------------------------------------------------------
cmd "sleep 60 &"
sleep 60 &
PID=$!
echo "后台进程 PID=$PID"
cmd "ps aux | grep -E 'sleep|PID' | head -3"
ps aux | grep -E "sleep 60|PID" | grep -v grep | head -3
cmd "kill $PID"
kill $PID && echo "已 kill 后台进程 $PID"
cmd "ps -p $PID"
if ps -p $PID > /dev/null 2>&1; then echo "进程仍在"; else echo "进程 $PID 已结束"; fi

# ---------------------------------------------------------------
section "6. 网络工具"
# ---------------------------------------------------------------
cmd "ip -4 addr show eth0 | grep inet"
ip -4 addr show eth0 2>/dev/null | grep inet || echo "(eth0 未就绪, WSL 使用 NAT 网络)"
cmd "ping -c 2 -W 2 223.5.5.5"
ping -c 2 -W 2 223.5.5.5 2>&1 | tail -2
cmd "curl -sI https://www.ubuntu.com | head -1"
curl -sI --max-time 8 https://www.ubuntu.com 2>/dev/null | head -1 || echo "(网络请求超时/无外网)"

# ---------------------------------------------------------------
section "7. 压缩归档"
# ---------------------------------------------------------------
cmd "tar -czf data-backup.tar.gz data"
tar -czf data-backup.tar.gz data
cmd "ls -lh data-backup.tar.gz"
ls -lh data-backup.tar.gz
cmd "tar -tzf data-backup.tar.gz"
tar -tzf data-backup.tar.gz

# ---------------------------------------------------------------
section "8. 包管理 (apt)"
# ---------------------------------------------------------------
cmd "apt --version | head -1"
apt --version | head -1
cmd "dpkg -l | wc -l"
echo "已安装软件包数: $(dpkg -l | wc -l)"

echo -e "\n${C_G}演示完成。${C_N}"
