# Linux Monitor Dashboard

## 项目简介
本项目是一个基于 Linux 的轻量级系统监控实验项目。  
通过 Shell 脚本采集系统运行状态（CPU、内存、磁盘、进程），并使用 Flask 构建 Web Dashboard 进行统一展示，适用于 Linux 系统管理与应用课程的实验与演示。

项目以**可复现、结构清晰、易理解**为目标，侧重展示 Linux 系统监控与进程管理的基本方法。

---

## 功能模块
- CPU 使用率监控
- 内存使用情况监控
- 磁盘使用情况监控
- 进程 Top5（按 CPU / 内存排序）
- Web Dashboard 实时展示（只读，每 5 秒刷新）

---

## 技术栈
- Linux Shell（bash）
- Python 3
- Flask
- Linux 系统接口与命令  
  - `/proc/meminfo`
  - `ps`
  - `top`
  - `df`
  - `awk`

---

## 运行环境说明
- **操作系统**：Linux（Kali / Debian / Ubuntu 等主流发行版）
- **Python**：Python 3
- **说明**：
  - 本项目依赖 Linux `/proc` 文件系统与常用系统命令  
  - 适用于 **Linux 环境**
  - 不适用于 Windows / macOS（需修改实现方式）

---

## 安装与运行

### （推荐）：系统级安装（Kali / Debian / Ubuntu）
适合实验环境，稳定、简单。

```bash
sudo apt update
sudo apt install -y python3-flask

