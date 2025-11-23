"""
Eromang服务器主程序
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))


def main():
    """服务器主函数"""
    print("Eromang服务器启动中...")
    # TODO: 初始化FastAPI服务器
    pass


if __name__ == "__main__":
    main()
