from mcp import mcp
from tools_config import ToolsConfig
class ToolAdapter:
    """工具适配器"""
    def __init__(self, tools_config: ToolsConfig):
        self.mcp = mcp()
        self.tools_config = tools_config
        self.tools = self.tools_config.read()
    # ==================== 添加工具 ====================
    def add(self, filepath: str):
        """查询文件"""
        self.mcp.add_tool(tool)
    # ==================== 删除工具 ====================
    def remove(self, filepath: str):
        """删除工具"""
        self.mcp.add_tool(tool)
    # ==================== 查询工具 ====================
    def query(self, filepath: str):
        """查询工具"""
        self.mcp.add_tool(tool)
    # ==================== 修改工具 ====================
    def modify(self, filepath: str):
        """修改工具"""
        self.mcp.add_tool(tool)
    # ==================== 批量添加工具 ====================
    def add_batch(self, filepath: str):
        """批量添加工具"""
        self.mcp.add_tool(tool)
    # ==================== 批量删除工具 ====================
    def remove_batch(self, filepath: str):
        """批量删除工具"""
        self.mcp.add_tool(tool)