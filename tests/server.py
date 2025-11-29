# server.py
from mcp.server.fastmcp import FastMCP

class DemoServer(FastMCP):
    def __init__(self):
        super().__init__("Demo Server")
        self.mcp = FastMCP("Demo Server")
        self.mcp.add_tool(self.add)
        self.mcp.add_tool(self.multiply)

    def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    def multiply(x: int, y: int) -> int:
        """Multiply two numbers"""
        return x * y

if __name__ == "__main__":
    # 使用 stdio 传输，这是客户端期望的方式
    server = DemoServer()
    server.mcp.run(transport="stdio")
    print("Server started")