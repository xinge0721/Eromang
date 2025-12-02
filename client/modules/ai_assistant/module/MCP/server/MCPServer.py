from fastmcp import FastMCP
from fastmcp.tools import Tool
import os
import json
from tools import logger



class MCPServer:
    def __init__(self):
        # 创建MCP服务器节点
        self.mcp = FastMCP("测试服务器")


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

  


if __name__ == "__main__":
    _MCPServer = MCPServer()
    _MCPServer.start()