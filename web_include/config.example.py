"""NIST 测试平台配置模板
复制此文件为 config.py 并按需修改。
"""

# ---------- Linux / VPS 部署 ----------
# NIST STS 套件所在目录（assess 二进制在此目录下）
NIST_DIR = "/home/ubuntu/sts-2.1.2"

# ---------- Windows WSL 部署 ----------
# 仅当在 Windows 上通过 WSL 运行时需要
NIST_DIR_WIN = r"\\wsl.localhost\Ubuntu\home\ubuntu\sts-2.1.2"
NIST_DIR_WSL = "/home/ubuntu/sts-2.1.2"
