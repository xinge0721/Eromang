from fastmcp import FastMCP
from fastmcp.tools import Tool
import os
import json

from Tools.DatabaseEditor import DatabaseEditor
from Tools.DataInquire import DataInquire
from Tools.FileEditor import FileEditor

class MCPServer:
    def __init__(self):
        # 创建MCP服务器节点
        self.mcp = FastMCP("测试服务器")

        self.database_editor = DatabaseEditor()
        self.data_inquire = DataInquire()
        self.file_editor = FileEditor()

        self.add_tool()

    # ==================== 启动服务器 ====================
    def start(self):
        """启动服务器"""
        self.mcp.run()

    # ==================== 停止服务器 ====================
    def stop(self):
        """停止服务器"""
        self.mcp.close()

    # ==================== 重启服务器 ====================
    def restart(self):
        """重启服务器"""
        self.stop()
        self.start()

    # ==================== 添加工具 ====================
    def add_tool(self):
        """注册所有工具到MCP服务器"""
        # DatabaseEditor 工具
        self.mcp.add_tool(Tool.from_function(self.database_editor.connect))
        self.mcp.add_tool(Tool.from_function(self.database_editor.delete))
        self.mcp.add_tool(Tool.from_function(self.database_editor.insert_data))
        self.mcp.add_tool(Tool.from_function(self.database_editor.update_data))
        self.mcp.add_tool(Tool.from_function(self.database_editor.delete_data))
        self.mcp.add_tool(Tool.from_function(self.database_editor.create_table))
        self.mcp.add_tool(Tool.from_function(self.database_editor.delete_table))
        self.mcp.add_tool(Tool.from_function(self.database_editor.write))
        self.mcp.add_tool(Tool.from_function(self.database_editor.read))
        self.mcp.add_tool(Tool.from_function(self.database_editor.list_tables))
        self.mcp.add_tool(Tool.from_function(self.database_editor.list_all_data))
        self.mcp.add_tool(Tool.from_function(self.database_editor.count_records))
        self.mcp.add_tool(Tool.from_function(self.database_editor.data_exists))

        # DataInquire 工具
        self.mcp.add_tool(Tool.from_function(self.data_inquire.file_directory))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.file_content))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.file_line_count))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.file_content_fuzzy))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.database_all_table))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.database_table_content))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.database_table_data_exists))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.database_content_fuzzy))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.database_table_data_count))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.database_table_data_batch))
        self.mcp.add_tool(Tool.from_function(self.data_inquire.database_table_data_filter))

        # FileEditor 工具
        self.mcp.add_tool(Tool.from_function(self.file_editor.read_line))
        self.mcp.add_tool(Tool.from_function(self.file_editor.read_all))
        self.mcp.add_tool(Tool.from_function(self.file_editor.update_line))
        self.mcp.add_tool(Tool.from_function(self.file_editor.delete_line))
        self.mcp.add_tool(Tool.from_function(self.file_editor.insert_line))
        self.mcp.add_tool(Tool.from_function(self.file_editor.append_line))
        self.mcp.add_tool(Tool.from_function(self.file_editor.clear_file))
        self.mcp.add_tool(Tool.from_function(self.file_editor.read_JSON))
        self.mcp.add_tool(Tool.from_function(self.file_editor.write_JSON))
        self.mcp.add_tool(Tool.from_function(self.file_editor.append_JSON))

if __name__ == "__main__":
    _MCPServer = MCPServer()
    _MCPServer.start()