"""
Eromang客户端主程序
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))


def main():
    """客户端主函数"""
    print("Eromang客户端启动中...")
    # TODO: 初始化客户端应用
    pass


if __name__ == "__main__":
    main()
