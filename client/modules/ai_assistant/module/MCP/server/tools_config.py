import os
import json
from tools import logger
from McpConstants import tools_config

class ToolsConfig:
    """MCP工具配置管理器：负责配置文件的初始化和读写"""

    def __init__(self):
        """初始化配置文件路径，不存在时创建默认配置"""
        self._encoding = 'utf-8'  # 文件编码
        self.current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前目录位置
        self.config_dir = os.path.join(self.current_dir, "config")  # 获取config文件夹路径
        self.tools_config_path = os.path.join(self.config_dir, "tools_config.json")  # 获取tools_config.json文件路径

        try:
            os.makedirs(self.config_dir, exist_ok=True)  # 创建config文件夹
            if not os.path.exists(self.tools_config_path):  # 检查文件是否存在
                self._write_default_config()
        except OSError as e:
            logger.error(f"初始化配置失败: {e}")
            raise



    # ==================== 读取文件 ====================
    def read(self):
        """读取配置文件

        :return: JSON数据
        :raises: OSError, json.JSONDecodeError
        """
        try:
            with open(self.tools_config_path, 'r', encoding=self._encoding) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"读取配置文件失败: {e}")
            raise

    # ==================== 写入文件 ====================
    def write(self, data: dict):
        """覆盖写入配置文件

        :param data: 完整的配置数据（会完全覆盖原有配置）
        :return: 是否成功
        """
        try:
            with open(self.tools_config_path, 'w', encoding=self._encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"写入配置文件失败: {e}")
            return False


    # ==================== 写入默认配置文件 ====================
    def _write_default_config(self):
        """写入默认配置文件

        :return: 是否成功
        """
        default_config = getattr(tools_config, "config", {})  # 获取默认配置
        return self.write(default_config)