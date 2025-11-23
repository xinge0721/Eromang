"""
配置管理
"""

from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent.parent.parent

# 数据库配置
DATABASE_URL = "sqlite:///eromang.db"

# 服务器配置
HOST = "0.0.0.0"
PORT = 8080

# 其他配置
DEBUG = True
