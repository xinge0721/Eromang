# FastMCP `_setup_handlers` 方法说明

## 概述

`_setup_handlers` 是 FastMCP 内部的核心初始化方法，在 `FastMCP.__init__` 中自动调用（第225行）。它负责将 FastMCP 的高层 API 方法绑定到底层 MCP 协议处理器上。

## 源码位置

文件：`mcp/server/fastmcp/server.py:288-299`

## 作用

这个方法建立了 MCP 协议请求和 FastMCP 处理方法之间的映射关系：

```python
def _setup_handlers(self) -> None:
    """Set up core MCP protocol handlers."""
    self._mcp_server.list_tools()(self.list_tools)
    self._mcp_server.call_tool(validate_input=False)(self.call_tool)
    self._mcp_server.list_resources()(self.list_resources)
    self._mcp_server.read_resource()(self.read_resource)
    self._mcp_server.list_prompts()(self.list_prompts)
    self._mcp_server.get_prompt()(self.get_prompt)
    self._mcp_server.list_resource_templates()(self.list_resource_templates)
```

## 绑定的协议处理器

| MCP 协议方法 | FastMCP 处理方法 | 功能 |
|-------------|-----------------|------|
| `list_tools` | `self.list_tools` | 列出所有可用工具 |
| `call_tool` | `self.call_tool` | 调用指定工具（禁用输入验证） |
| `list_resources` | `self.list_resources` | 列出所有资源 |
| `read_resource` | `self.read_resource` | 读取指定资源 |
| `list_prompts` | `self.list_prompts` | 列出所有提示词 |
| `get_prompt` | `self.get_prompt` | 获取指定提示词 |
| `list_resource_templates` | `self.list_resource_templates` | 列出资源模板 |

## 关键细节

### 1. 输入验证被禁用

```python
self._mcp_server.call_tool(validate_input=False)(self.call_tool)
```

FastMCP 在 `call_tool` 时禁用了底层服务器的输入验证，因为它会在自己的层面做临时转换和验证（为了向后兼容）。

### 2. 装饰器模式

这里用的是装饰器模式：
```python
self._mcp_server.list_tools()(self.list_tools)
# 等价于
decorator = self._mcp_server.list_tools()
decorator(self.list_tools)
```

底层 `MCPServer` 返回装饰器，然后立即应用到 FastMCP 的方法上。

## 使用场景

### 普通用户：不需要关心

作为 FastMCP 用户，你**不需要**直接调用或修改 `_setup_handlers`。它在初始化时自动执行：

```python
from mcp.server.fastmcp import FastMCP

# _setup_handlers 会在这里自动调用
mcp = FastMCP("my-server")

# 直接使用装饰器注册功能即可
@mcp.tool()
def my_tool(x: int) -> str:
    return str(x)
```

### 高级用户：扩展协议处理

如果你需要自定义 MCP 协议处理（比如添加自定义协议方法），可以继承 FastMCP 并重写：

```python
from mcp.server.fastmcp import FastMCP

class CustomMCP(FastMCP):
    def _setup_handlers(self) -> None:
        # 先调用父类的标准绑定
        super()._setup_handlers()

        # 添加自定义协议处理
        self._mcp_server.custom_method()(self.handle_custom)

    async def handle_custom(self, param: str):
        # 自定义处理逻辑
        return {"result": f"Custom: {param}"}
```

## 相关方法

- `FastMCP.__init__`: 调用此方法的地方
- `MCPServer.list_tools/call_tool/...`: 底层协议装饰器
- `ToolManager/ResourceManager/PromptManager`: 实际管理工具/资源/提示词的管理器

## 注意事项

1. **私有方法**：方法名以 `_` 开头，表示这是内部实现，不应该在外部直接调用
2. **自动执行**：在 `FastMCP` 实例化时自动执行，无需手动调用
3. **顺序重要**：必须在 `_tool_manager`、`_resource_manager`、`_prompt_manager` 初始化之后调用
4. **不可重复调用**：重复调用会导致处理器被多次绑定，可能引发问题

## 总结

`_setup_handlers` 是 FastMCP 的"接线员"，负责把 MCP 协议的请求路由到正确的处理方法。普通使用不需要关心，高级定制时可以继承重写。
