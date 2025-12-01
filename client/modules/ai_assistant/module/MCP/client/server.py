from fastmcp import FastMCP

# 创建服务器
mcp = FastMCP("简单服务器")

# 定义工具
@mcp.tool
def add(a: int, b: int) -> int:
    """两个数相加"""
    return a + b


mcp.run()