# FastMCP 隐藏功能文档

官方文档藏着掖着的好用功能，这里全给你列出来。

## 1. Tool 相关隐藏参数

### `structured_output` - 控制工具输出格式

官方文档基本没提，但这个参数超级有用！

```python
@mcp.tool(structured_output=True)  # 强制结构化输出
def my_tool(x: int) -> dict:
    return {"result": x * 2, "status": "ok"}

@mcp.tool(structured_output=False)  # 强制非结构化输出
def simple_tool(x: int) -> str:
    return f"Result: {x}"

@mcp.tool()  # structured_output=None，自动检测
def auto_tool(x: int) -> str:
    return "Auto detected"
```

**参数说明：**
- `None`（默认）：根据函数返回类型注解自动检测
- `True`：强制创建结构化工具（如果返回类型支持）
- `False`：强制创建非结构化工具

**使用场景：**
- 返回复杂数据结构时用 `True`
- 返回简单文本时用 `False`
- 不确定时用 `None` 让它自动判断

### `icons` - 给工具添加图标

```python
from mcp.types import Icon

@mcp.tool(
    icons=[
        Icon(url="https://example.com/icon.png", mimeType="image/png")
    ]
)
def fancy_tool(x: int) -> str:
    return str(x)
```

### `meta` - 工具元数据

```python
@mcp.tool(
    meta={
        "version": "1.0.0",
        "author": "Your Name",
        "category": "data-processing"
    }
)
def my_tool(x: int) -> str:
    return str(x)
```

**用途：**
- 存储自定义元数据
- 工具分类
- 版本管理
- 任何你想附加的信息

### `annotations` - 工具注解

```python
from mcp.types import ToolAnnotations

@mcp.tool(
    annotations=ToolAnnotations(
        audience=["developers", "data-scientists"],
        priority=0.9
    )
)
def important_tool(x: int) -> str:
    return str(x)
```

### `add_tool` - 编程式注册工具

官方文档几乎不提，但这是比装饰器更灵活的注册方式：

```python
from mcp.types import Icon, ToolAnnotations

# 定义工具函数
def my_function(x: int, y: str) -> dict:
    """处理数据"""
    return {"result": x, "message": y}

# 编程式注册，支持所有参数
mcp.add_tool(
    fn=my_function,
    name="custom_name",           # 自定义名称（不用函数名）
    title="我的工具",              # 人类可读标题
    description="这是详细描述",    # 详细说明
    annotations=ToolAnnotations(
        audience=["developers"],
        priority=0.8
    ),
    icons=[
        Icon(url="https://example.com/icon.png", mimeType="image/png")
    ],
    meta={
        "version": "2.0.0",
        "category": "data"
    },
    structured_output=True        # 控制输出格式
)
```

**使用场景：**

1. **动态注册工具**
```python
# 根据配置动态注册
tools_config = load_config("tools.json")
for tool_def in tools_config:
    func = import_function(tool_def["module"], tool_def["function"])
    mcp.add_tool(
        fn=func,
        name=tool_def["name"],
        description=tool_def["description"]
    )
```

2. **批量注册**
```python
# 批量注册一组函数
tool_functions = [func1, func2, func3]
for func in tool_functions:
    mcp.add_tool(func)
```

3. **条件注册**
```python
# 根据环境变量决定是否注册
if os.getenv("ENABLE_EXPERIMENTAL"):
    mcp.add_tool(experimental_function, name="experimental_tool")
```

4. **运行时修改工具属性**
```python
# 先移除旧的，再用新配置注册
mcp.remove_tool("my_tool")
mcp.add_tool(
    fn=my_function,
    name="my_tool",
    description="更新后的描述",
    structured_output=False  # 改变输出格式
)
```

5. **Lambda 或匿名函数**
```python
# 注册 lambda（虽然不推荐，但可以）
mcp.add_tool(
    fn=lambda x: x * 2,
    name="double",
    description="将数字翻倍"
)
```

**对比装饰器：**

```python
# 装饰器方式 - 简洁，适合静态定义
@mcp.tool(name="tool1")
def my_tool(x: int) -> str:
    return str(x)

# add_tool 方式 - 灵活，适合动态注册
def my_function(x: int) -> str:
    return str(x)

mcp.add_tool(my_function, name="tool1")
```

**注意事项：**
- `add_tool` 和 `@tool` 装饰器功能完全相同，只是调用方式不同
- 支持所有和 `@tool` 一样的参数
- 可以注册任何可调用对象（函数、方法、lambda）
- 函数可以是同步或异步的
- 支持 `Context` 参数注入

## 2. Resource 相关隐藏功能

### `add_resource` - 编程式注册资源

官方文档几乎不提，但这是比装饰器更灵活的注册方式：

```python
from mcp.server.fastmcp.resources import (
    TextResource,
    BinaryResource,
    FileResource,
    HttpResource,
    DirectoryResource,
    FunctionResource
)
from pathlib import Path

# 1. 文本资源
text_res = TextResource(
    uri="text://greeting",
    name="greeting",
    title="问候语",
    description="简单的问候文本",
    text="Hello, World!",
    mime_type="text/plain"
)
mcp.add_resource(text_res)

# 2. 二进制资源
binary_res = BinaryResource(
    uri="binary://data",
    name="binary_data",
    data=b"\x00\x01\x02\x03",
    mime_type="application/octet-stream"
)
mcp.add_resource(binary_res)

# 3. 文件资源
file_res = FileResource(
    uri="file:///config.json",
    name="config",
    path=Path("G:/config.json"),  # 必须是绝对路径
    is_binary=False,
    mime_type="application/json"
)
mcp.add_resource(file_res)

# 4. HTTP 资源
http_res = HttpResource(
    uri="http://api.example.com/data",
    name="api_data",
    url="https://api.example.com/data",
    mime_type="application/json"
)
mcp.add_resource(http_res)

# 5. 目录资源（列出文件）
dir_res = DirectoryResource(
    uri="dir:///project",
    name="project_files",
    path=Path("G:/project"),
    recursive=True,           # 递归列出子目录
    pattern="*.py",           # 只列出 Python 文件
    mime_type="application/json"
)
mcp.add_resource(dir_res)

# 6. 函数资源（最灵活）
def get_dynamic_data():
    return {"timestamp": time.time(), "data": "dynamic"}

func_res = FunctionResource.from_function(
    fn=get_dynamic_data,
    uri="dynamic://data",
    name="dynamic_data",
    title="动态数据",
    description="实时生成的数据",
    mime_type="application/json"
)
mcp.add_resource(func_res)
```

**使用场景：**

1. **动态注册资源**
```python
# 根据配置文件批量注册
config = load_config("resources.json")
for res_def in config["resources"]:
    if res_def["type"] == "file":
        mcp.add_resource(FileResource(
            uri=res_def["uri"],
            name=res_def["name"],
            path=Path(res_def["path"])
        ))
```

2. **条件性注册**
```python
# 根据环境变量决定资源来源
if os.getenv("USE_LOCAL_FILES"):
    mcp.add_resource(FileResource(uri="data://config", path=Path("./config.json")))
else:
    mcp.add_resource(HttpResource(uri="data://config", url="https://api.example.com/config"))
```

3. **运行时更新资源**
```python
# 先移除旧资源，再添加新的
# 注意：FastMCP 没有 remove_resource 方法，需要重启服务器
```

**注意事项：**
- `FileResource` 和 `DirectoryResource` 的 `path` 必须是绝对路径
- `FunctionResource` 支持同步和异步函数
- 所有资源类型都继承自 `Resource` 基类
- 资源的 `uri` 必须是唯一的

### 动态资源模板

官方示例太简单，实际上可以这样玩：

```python
@mcp.resource("data://{dataset}/{year}/{month}")
async def get_monthly_data(dataset: str, year: int, month: int, ctx: Context) -> str:
    """
    URI 参数会自动映射到函数参数
    支持类型转换（year 和 month 会自动转成 int）
    """
    ctx.info(f"Fetching {dataset} for {year}-{month}")
    data = await fetch_data(dataset, year, month)
    return data

# 客户端调用：
# read_resource("data://sales/2024/03")
```

**关键点：**
- URI 中的 `{参数}` 必须和函数参数名完全匹配
- 支持类型注解，会自动转换
- 可以注入 `Context` 参数（但不会算在 URI 参数里）

### Resource 的 `mime_type` 参数

```python
@mcp.resource(
    "file://config.json",
    mime_type="application/json"
)
def get_config() -> dict:
    return {"key": "value"}

@mcp.resource(
    "image://logo",
    mime_type="image/png"
)
def get_logo() -> bytes:
    with open("logo.png", "rb") as f:
        return f.read()
```

## 3. Prompt 相关隐藏功能

### `add_prompt` - 编程式注册提示词

官方文档几乎不提，但这是比装饰器更灵活的注册方式：

```python
from mcp.server.fastmcp.prompts import Prompt, UserMessage, AssistantMessage
from mcp.types import Icon

# 方式1：使用 Prompt.from_function 创建
def analyze_code(language: str, code: str) -> list:
    """分析代码并给出建议"""
    return [
        UserMessage(f"请分析以下 {language} 代码：\n\n{code}"),
        AssistantMessage("我会仔细分析这段代码的结构、性能和潜在问题。")
    ]

prompt = Prompt.from_function(
    fn=analyze_code,
    name="analyze_code",
    title="代码分析",
    description="分析代码并提供改进建议",
    icons=[Icon(url="https://example.com/icon.png", mimeType="image/png")]
)
mcp.add_prompt(prompt)

# 方式2：直接创建 Prompt 对象
from mcp.server.fastmcp.prompts.base import PromptArgument

async def review_pr(pr_number: int, ctx: Context) -> list:
    """审查 Pull Request"""
    pr_data = await fetch_pr_data(pr_number)
    return [
        UserMessage(f"请审查 PR #{pr_number}:\n\n{pr_data}")
    ]

prompt2 = Prompt(
    name="review_pr",
    title="PR 审查",
    description="审查 GitHub Pull Request",
    arguments=[
        PromptArgument(
            name="pr_number",
            description="Pull Request 编号",
            required=True
        )
    ],
    fn=review_pr
)
mcp.add_prompt(prompt2)
```

**使用场景：**

1. **动态注册提示词**
```python
# 从配置文件加载提示词模板
prompts_config = load_config("prompts.json")
for prompt_def in prompts_config:
    def create_prompt_fn(template):
        def prompt_fn(**kwargs):
            return [UserMessage(template.format(**kwargs))]
        return prompt_fn

    fn = create_prompt_fn(prompt_def["template"])
    prompt = Prompt.from_function(
        fn=fn,
        name=prompt_def["name"],
        description=prompt_def["description"]
    )
    mcp.add_prompt(prompt)
```

2. **条件性注册**
```python
# 根据用户权限注册不同的提示词
if user.has_permission("admin"):
    mcp.add_prompt(Prompt.from_function(
        fn=admin_prompt_fn,
        name="admin_tools",
        description="管理员专用提示词"
    ))
```

3. **多语言提示词**
```python
# 根据语言环境注册不同版本
language = os.getenv("LANGUAGE", "zh")
if language == "zh":
    mcp.add_prompt(Prompt.from_function(fn=chinese_prompt, name="greeting"))
else:
    mcp.add_prompt(Prompt.from_function(fn=english_prompt, name="greeting"))
```

**返回值格式：**

提示词函数可以返回多种格式：

```python
# 1. 返回字符串（自动转为 UserMessage）
def simple_prompt():
    return "请帮我分析这段代码"

# 2. 返回 Message 对象
def message_prompt():
    return UserMessage("请帮我分析这段代码")

# 3. 返回字典（会被转换为 Message）
def dict_prompt():
    return {"role": "user", "content": "请帮我分析这段代码"}

# 4. 返回列表（多轮对话）
def multi_turn_prompt():
    return [
        UserMessage("我有一段代码需要优化"),
        AssistantMessage("好的，请把代码发给我"),
        UserMessage("代码如下：...")
    ]

# 5. 异步函数
async def async_prompt(file_path: str):
    content = await read_file_async(file_path)
    return [UserMessage(f"请分析这个文件：\n\n{content}")]
```

**注意事项：**
- 提示词函数可以是同步或异步的
- 支持 `Context` 参数注入（用于访问资源、日志等）
- 参数会自动转换为 `PromptArgument`
- 返回值必须是字符串、Message 对象、字典或它们的列表

## 4. `remove_tool` - 动态移除工具

官方文档几乎没提，但这个功能很实用：

```python
mcp = FastMCP("my-server")

@mcp.tool()
def temp_tool(x: int) -> str:
    return str(x)

# 运行时移除工具
mcp.remove_tool("temp_tool")

# 条件性注册工具
if os.getenv("ENABLE_ADVANCED_TOOLS"):
    @mcp.tool()
    def advanced_tool(x: int) -> str:
        return str(x)
else:
    # 如果已经注册了，可以移除
    try:
        mcp.remove_tool("advanced_tool")
    except:
        pass
```

## 4. Context 的隐藏能力

### `elicit` - 交互式询问用户

这个功能文档里有，但藏得很深：

```python
from pydantic import BaseModel

class UserChoice(BaseModel):
    action: str
    confirm: bool

@mcp.tool()
async def interactive_tool(ctx: Context) -> str:
    # 向用户询问信息
    result = await ctx.elicit(
        message="请选择操作并确认",
        schema=UserChoice
    )

    if result.action == "accept":
        return f"用户选择: {result.data.action}, 确认: {result.data.confirm}"
    else:
        return "用户取消了操作"
```

### `read_resource` - 在工具中读取资源

```python
@mcp.tool()
async def process_data(dataset: str, ctx: Context) -> str:
    # 在工具中读取其他资源
    resource_data = await ctx.read_resource(f"data://{dataset}")

    # 处理数据
    processed = process(resource_data)
    return processed
```

### 日志级别方法

```python
@mcp.tool()
async def debug_tool(x: int, ctx: Context) -> str:
    await ctx.debug("调试信息")
    await ctx.info("普通信息")
    await ctx.warning("警告信息")
    await ctx.error("错误信息")

    # 或者用通用方法
    await ctx.log("info", "通用日志方法", logger_name="my_tool")

    return str(x)
```

### `report_progress` - 进度报告

```python
@mcp.tool()
async def long_task(ctx: Context) -> str:
    total = 100
    for i in range(total):
        await ctx.report_progress(i, total, f"处理中: {i}/{total}")
        await asyncio.sleep(0.1)

    return "完成"
```

## 5. `completion` - 自动补全处理器

官方文档提了一句就没了，实际用法：

```python
from mcp.types import Completion

@mcp.completion()
async def handle_completion(ref, argument, context):
    """
    ref: PromptReference 或 ResourceTemplateReference
    argument: CompletionArgument (name, value)
    context: CompletionContext (已解析的其他参数)
    """
    if isinstance(ref, ResourceTemplateReference):
        if argument.name == "dataset":
            # 返回数据集名称的补全建议
            return Completion(values=["sales", "users", "products"])

        if argument.name == "year":
            # 根据已输入的 dataset 返回年份建议
            dataset = context.arguments.get("dataset")
            if dataset == "sales":
                return Completion(values=["2023", "2024"])

    return None
```

## 6. `custom_route` - 自定义 HTTP 路由

这个功能超级隐蔽，但很强大：

```python
from starlette.requests import Request
from starlette.responses import JSONResponse

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "version": "1.0.0"})

@mcp.custom_route("/webhook", methods=["POST"])
async def webhook_handler(request: Request) -> JSONResponse:
    data = await request.json()
    # 处理 webhook
    return JSONResponse({"received": True})

@mcp.custom_route("/admin/stats", methods=["GET"], name="admin_stats")
async def admin_stats(request: Request) -> JSONResponse:
    return JSONResponse({
        "tools": len(mcp._tool_manager.list_tools()),
        "resources": len(mcp._resource_manager.list_resources())
    })
```

## 7. `session_manager` - 会话管理器

高级用法，用于多服务器挂载：

```python
from fastapi import FastAPI

app = FastAPI()
mcp = FastMCP("my-server")

# 先创建 streamable_http_app
starlette_app = mcp.streamable_http_app()

# 然后可以访问 session_manager
session_mgr = mcp.session_manager

# 挂载到 FastAPI
app.mount("/mcp", starlette_app)
```

## 8. 环境变量配置

所有设置都可以通过环境变量配置（前缀 `FASTMCP_`）：

```bash
# .env 文件
FASTMCP_DEBUG=true
FASTMCP_LOG_LEVEL=DEBUG
FASTMCP_HOST=0.0.0.0
FASTMCP_PORT=8080
FASTMCP_WARN_ON_DUPLICATE_TOOLS=false
```

```python
# 会自动读取 .env 文件
mcp = FastMCP("my-server")
```

## 9. 认证相关（高级）

```python
from mcp.server.auth.settings import AuthSettings
from mcp.server.auth.provider import OAuthAuthorizationServerProvider

auth_settings = AuthSettings(
    issuer_url="https://auth.example.com",
    required_scopes=["read", "write"]
)

mcp = FastMCP(
    "secure-server",
    auth=auth_settings,
    token_verifier=my_token_verifier  # 自定义 token 验证器
)
```

## 10. Transport Security（DNS 重绑定保护）

```python
from mcp.server.transport_security import TransportSecuritySettings

security = TransportSecuritySettings(
    allowed_origins=["https://example.com"],
    allowed_hosts=["api.example.com"]
)

mcp = FastMCP(
    "secure-server",
    transport_security=security
)
```

## 总结

FastMCP 的这些隐藏功能都很实用，但官方文档要么一笔带过，要么根本不提。主要的坑点：

### 编程式注册方法（官方几乎不提）
1. **`add_tool`** - 编程式注册工具，比装饰器更灵活，支持动态注册
2. **`add_resource`** - 编程式注册资源，支持 6 种资源类型
3. **`add_prompt`** - 编程式注册提示词，支持多种返回格式
4. **`remove_tool`** - 动态移除工具，文档几乎没提

### 隐藏的资源类型（官方文档没列全）
5. **`TextResource`** - 文本资源
6. **`BinaryResource`** - 二进制资源
7. **`FileResource`** - 文件资源（支持二进制模式）
8. **`HttpResource`** - HTTP 资源
9. **`DirectoryResource`** - 目录资源（支持递归和模式匹配）
10. **`FunctionResource`** - 函数资源（最灵活）

### 工具和提示词的隐藏参数
11. **`structured_output`** - 控制工具输出格式，很有用但文档没详细说
12. **`meta`** - 工具元数据，文档一句话带过
13. **`icons`** - 工具/资源/提示词图标，文档一句话带过
14. **`annotations`** - 工具注解（audience, priority），文档没详细说
15. **`title`** - 所有类型都支持，但文档没强调

### Context 的隐藏能力
16. **`Context.elicit`** - 交互式询问用户，藏在深处
17. **`Context.read_resource`** - 在工具中读取其他资源
18. **`Context.report_progress`** - 进度报告
19. **`Context.debug/info/warning/error`** - 日志快捷方法

### 高级功能
20. **`completion`** - 自动补全处理器，文档说得不清楚
21. **`custom_route`** - 自定义 HTTP 路由，文档提了但没示例
22. **`session_manager`** - 会话管理器，用于多服务器挂载
23. **环境变量配置** - 所有参数都能用 `FASTMCP_` 前缀配置，但没人告诉你
24. **认证和安全** - OAuth、Token 验证、DNS 重绑定保护，文档藏得很深

### 提示词的返回格式（官方没详细说）
25. **`UserMessage/AssistantMessage`** - 提示词消息类型
26. **多种返回格式** - 字符串、Message、字典、列表都支持

建议直接看源码，官方文档确实藏东西。这份文档涵盖了大部分隐藏功能，但可能还有更多未发现的。
