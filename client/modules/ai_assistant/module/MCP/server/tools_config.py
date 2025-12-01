import os
import json
from tools import logger
class ToolsConfig:

    def __init__(self):
        self._encoding = 'utf-8'# 文件编码
        # 检查配置文件是否存在
        try:
            self.current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前目录位置
            self.tools_config_path = os.path.join(self.current_dir, "config", "tools_config.json")# 获取tools_config.json文件路径
            if not os.path.exists(self.tools_config_path):# 检查文件是否存在
                raise FileNotFoundError(f"tools_config.json文件不存在: {self.tools_config_path}")# 文件不存在，抛出异常
        except Exception as e:
            logger.error(f"初始化失败: {e}")# 记录错误日志

    # ==================== 读取文件 ====================
    def read(self):
        """读取文件"""
        """
        读取JSON文件
        :return: JSON数据
        :error: 文件不存在
        """
        try:
          # 读取文件
          with open(self.tools_config_path, 'r', encoding=self._encoding) as f:# 以utf-8编码读取文件
              return json.load(f)# 返回JSON数据
        except Exception as e:
          logger.error(f"读取文件失败: {e}") # 记录错误日志
          return None # 读取文件失败，返回None

    # ==================== 写入文件 ====================
    def write(self, data: dict):
        """写入文件"""
        """
        写入文件
        :param data: JSON数据
        :return: 是否成功
        :error: 文件不存在
        """
        try:
            # 写入文件
            Json = {}

            with  open(self.tools_config_path, 'r', encoding=self._encoding) as f :# 以utf-8编码读取文件
                Json = json.load(f)# 返回JSON数据

            Json.update(data)# 添加JSON数据

            with open(self.tools_config_path, 'w', encoding=self._encoding) as f:# 以utf-8编码写入文件
                json.dump(Json, f, ensure_ascii=False, indent=2)# 写入JSON数据到文件

            return True # 写入文件成功，返回True
        except Exception as e:
          logger.error(f"写入文件失败: {e}") # 记录错误日志
          return False # 写入文件失败，返回False
    # ==================== 删除文件 ====================
    def delete(self):
        """删除文件"""
        try:
            # 删除文件
            os.remove(self.tools_config_path)# 删除文件
            return True # 删除文件成功，返回True
        except Exception as e:
          logger.error(f"删除文件失败: {e}") # 记录错误日志
          return False # 删除文件失败，返回False