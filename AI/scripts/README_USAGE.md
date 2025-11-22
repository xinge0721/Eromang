# OPEN_AI 类使用指南

## 📖 简介

`OPEN_AI` 类是一个对话 API 封装，特点：
- 自动管理对话历史
- 智能 Token 裁剪
- 完整的错误处理
- 集成日志记录
- 支持多种 AI 模型（DeepSeek、通义千问、Kimi、讯飞星火等）

## 🔐 配置管理（新增）

### 方式一：使用网页配置管理系统（推荐）

我们提供了可视化的网页配置管理系统，方便管理所有 AI 模型的 API 密钥。

1. **启动配置管理系统**：
```bash
cd window
python app.py
# 或直接双击：启动配置管理.bat
```

2. **在浏览器中打开**：
```
http://localhost:5000
```

3. **在网页界面中配置**：
   - 🤖 **DeepSeek** - API Key、Base URL、Model
   - 🌟 **通义千问 (Qwen)** - API Key、Base URL、Model
   - 🌙 **Kimi** - API Key、Base URL、Model、Tier
   - ⚡ **讯飞星火** - APPID、API Secret、API Key、Domain、Spark URL

4. **点击"保存配置"**，所有配置自动保存到 `role/secret_key.Json`

**特点**：
- ✅ 美观的现代化界面
- ✅ 实时配置状态指示
- ✅ 自动保存和加载
- ✅ 表单验证
- ✅ 详细的操作提示

### 方式二：手动编辑配置文件

直接编辑 `role/secret_key.Json` 文件：

```json
{
  "deepseek": {
    "api_key": "your_deepseek_api_key_here",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat"
  },
  "qwen": {
    "api_key": "your_qwen_api_key_here",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-turbo"
  },
  "kimi": {
    "api_key": "your_kimi_api_key_here",
    "base_url": "https://api.moonshot.cn/v1",
    "model": "moonshot-v1-8k",
    "tier": "Free"
  },
  "xinhuo": {
    "appid": "your_xinhuo_appid_here",
    "api_secret": "your_xinhuo_api_secret_here",
    "api_key": "your_xinhuo_api_key_here",
    "domain": "4.0Ultra",
    "Spark_url": "wss://spark-api.xf-yun.com/v4.0/chat"
  }
}
```

## 🚀 快速开始

### 基本使用（3轮对话示例）

```bash
python main.py
```

### 交互式对话

```bash
python main.py --interactive
# 或
python main.py -i
```

命令：
- 直接输入问题 - 对话
- `exit` / `quit` - 退出
- `clear` - 清空历史
- `history` - 查看历史

## 💻 代码示例

### 方式一：使用配置文件（推荐）

```python
from models.qwen import Qwen
from serve.OPEN_AI import OPEN_AI
import os, json

# 1. 从配置文件加载密钥
def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "role", "secret_key.Json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
qwen_config = config.get("qwen", {})

# 2. 初始化 Qwen 模型
qwen = Qwen(
    api_key=qwen_config.get("api_key"),
    base_url=qwen_config.get("base_url"),
    model=qwen_config.get("model")
)

# 3. 定义 get_params_callback
def get_params_callback(problem: str) -> dict:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_path = os.path.join(script_dir, "role", "history.JSON")
    
    try:
        with open(history_path, "r", encoding="utf-8") as f:
            messages = json.load(f)
    except:
        messages = []
    
    return {"model": qwen.model, "messages": messages}

# 4. 创建 AI 客户端
ai = OPEN_AI(
    request_params=qwen.gen_params(),
    max_tokens=4000,
    get_params_callback=get_params_callback,
    token_callback=qwen.token_callback
)

# 5. 使用
ai._history.clear()
ai._history.insert("system", "你是AI助手")
response = ai.send("你好")
print(response)
```

### 方式二：直接指定参数

```python
from models.qwen import Qwen
from serve.OPEN_AI import OPEN_AI

# 直接初始化（适合测试）
qwen = Qwen(
    api_key="your-api-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus"
)

# ... 其他步骤同上
```

## 🔧 核心组件

### 1. models/ - AI 模型封装

支持多种 AI 模型：

**models/qwen.py** - 通义千问
- `gen_params()` - 生成连接参数（api_key, base_url）
- `token_callback(content)` - 精确计算 token 数（使用 transformers）

**models/deepseek.py** - DeepSeek
- 高性价比的深度推理模型

**models/Kiimi.py** - Kimi（月之暗面）
- 支持长文本对话

**models/xinhuo.py** - 讯飞星火
- 国产大模型

### 2. serve/OPEN_AI.py

核心对话类：
- `send(problem)` - 发送消息并获取回答
- `_history` - 历史管理对象（insert/get/clear/extend）

### 3. window/ - 配置管理系统（新增）

可视化 Web 界面：
- `app.py` - Flask 后端服务
- `templates/index.html` - 前端界面
- 支持所有 AI 模型的密钥配置

### 4. log/log.py

日志系统：
- 自动输出到终端和文件
- 按日期分类存储（`log/record/YYYY-MM-DD.log`）

## 📊 历史管理

```python
# 清空历史
ai._history.clear()

# 设置系统提示词
ai._history.insert("system", "你是专业的编程助手")

# 插入对话
ai._history.insert("user", "问题")
ai._history.insert("assistant", "回答")

# 批量插入
ai._history.extend([
    {"role": "user", "content": "问题1"},
    {"role": "assistant", "content": "回答1"}
])

# 获取历史
history = ai._history.get()
print(f"共 {len(history)} 条记录")
```

## ⚙️ 配置

### 更换模型

**选项 1：使用 DeepSeek**
```python
from models.deepseek import DeepSeek

config = load_config()
model = DeepSeek(
    api_key=config["deepseek"]["api_key"],
    base_url=config["deepseek"]["base_url"],
    model=config["deepseek"]["model"]
)
```

**选项 2：使用通义千问（Qwen）**
```python
from models.qwen import Qwen

config = load_config()
model = Qwen(
    api_key=config["qwen"]["api_key"],
    base_url=config["qwen"]["base_url"],
    model=config["qwen"]["model"]  # qwen-turbo / qwen-plus / qwen-max
)
```

**选项 3：使用 Kimi**
```python
from models.Kiimi import Kimi

config = load_config()
model = Kimi(
    api_key=config["kimi"]["api_key"],
    base_url=config["kimi"]["base_url"],
    model=config["kimi"]["model"]
)
```

**选项 4：使用讯飞星火**
```python
from models.xinhuo import Xinhuo

config = load_config()
model = Xinhuo(
    appid=config["xinhuo"]["appid"],
    api_secret=config["xinhuo"]["api_secret"],
    api_key=config["xinhuo"]["api_key"],
    domain=config["xinhuo"]["domain"]
)
```

### Token 限制

```python
ai = OPEN_AI(
    ...,
    max_tokens=4000  # 历史记录最大 token 数
)
```

超过限制会自动裁剪最旧的对话。

## 📁 文件结构

```
scripts/
├── main.py                    # 使用示例
├── models/                    # AI 模型封装
│   ├── deepseek.py           # DeepSeek 模型
│   ├── qwen.py               # 通义千问模型
│   ├── Kiimi.py              # Kimi 模型
│   ├── xinhuo.py             # 讯飞星火模型
│   ├── doubao.py             # 豆包模型
│   └── claude.py             # Claude 模型
├── serve/
│   └── OPEN_AI.py            # OPEN_AI 核心类
├── role/
│   ├── secret_key.Json       # API 密钥配置（重要）
│   ├── history.JSON          # 对话历史
│   ├── user.JSON             # 用户配置
│   └── config.json           # 其他配置
├── window/                    # 配置管理系统（新增）
│   ├── app.py                # Flask 后端服务
│   ├── templates/
│   │   └── index.html        # 前端界面
│   ├── requirements.txt      # Python 依赖
│   ├── README.md             # 配置系统说明
│   └── 启动配置管理.bat      # Windows 启动脚本
└── log/
    └── record/               # 日志文件
```

## 🔍 Token 计算

Qwen 使用 `transformers` 库的 tokenizer 进行精确计算：

```python
# 自动处理中英文混合文本
token_count = qwen.token_callback("你好，Hello World!")
```

第一次运行会下载 tokenizer（约 2MB），之后会缓存。

## ⚠️ 注意事项

1. **API 密钥安全**：
   - ⚠️ 不要将 `secret_key.Json` 提交到版本控制
   - ⚠️ 使用网页配置系统时注意网络安全
   - ⚠️ 建议在局域网内使用配置管理系统

2. **Token 管理**：
   - 合理设置 `max_tokens` 控制成本
   - 不同模型的 token 计算方式可能不同

3. **首次运行**：
   - Qwen 模型会下载 tokenizer（约 2MB）
   - 需要网络连接

4. **编码问题**：
   - Windows 终端可能显示乱码
   - 日志文件使用 UTF-8 编码，显示正常

5. **配置文件**：
   - 所有 API 密钥统一存储在 `role/secret_key.Json`
   - 可以通过网页界面或手动编辑

## 🐛 常见问题

**Q: 如何配置 API 密钥？**
A: 使用网页配置系统（`cd window && python app.py`）或手动编辑 `role/secret_key.Json`

**Q: transformers 相关错误？**
A: 安装依赖：`pip install transformers`

**Q: 配置管理系统启动失败？**
A: 
1. 确保已安装依赖：`pip install flask flask-cors`
2. 检查端口 5000 是否被占用
3. 查看终端错误信息

**Q: 如何查看完整日志？**
A: 查看 `log/record/YYYY-MM-DD.log` 文件（UTF-8 编码）

**Q: 如何清空所有历史？**
A: 调用 `ai._history.clear()` 或交互模式输入 `clear`

**Q: 支持哪些 AI 模型？**
A: 目前支持：
- DeepSeek
- 通义千问（Qwen）
- Kimi（月之暗面）
- 讯飞星火
- 豆包
- Claude

**Q: 不同模型如何切换？**
A: 
1. 在配置管理系统中配置对应模型的密钥
2. 在代码中导入并初始化对应的模型类
3. 传入 `OPEN_AI` 类使用

## 📝 更多示例

### 多轮上下文对话

```python
ai._history.clear()
ai._history.insert("system", "你是编程助手")

r1 = ai.send("Python 如何读文件？")
r2 = ai.send("那 JSON 呢？")  # AI 会记住之前的上下文
```

### 查看 Token 使用

```python
history = ai._history.get()
total = sum(qwen.token_callback(item["content"]) for item in history)
print(f"使用: {total} / {ai._max_tokens} tokens")
```

### 完整示例：使用配置管理系统

```python
from models.deepseek import DeepSeek
from models.qwen import Qwen
from serve.OPEN_AI import OPEN_AI
import json
import os

def load_config():
    """从配置文件加载密钥"""
    config_path = os.path.join(os.path.dirname(__file__), "role", "secret_key.Json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def create_ai_client(model_type="qwen"):
    """创建 AI 客户端"""
    config = load_config()
    
    if model_type == "deepseek":
        model = DeepSeek(
            api_key=config["deepseek"]["api_key"],
            base_url=config["deepseek"]["base_url"],
            model=config["deepseek"]["model"]
        )
    elif model_type == "qwen":
        model = Qwen(
            api_key=config["qwen"]["api_key"],
            base_url=config["qwen"]["base_url"],
            model=config["qwen"]["model"]
        )
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")
    
    # 创建 AI 客户端
    def get_params_callback(problem: str) -> dict:
        return {"model": model.model, "messages": []}
    
    ai = OPEN_AI(
        request_params=model.gen_params(),
        max_tokens=4000,
        get_params_callback=get_params_callback,
        token_callback=model.token_callback
    )
    
    return ai

# 使用
ai = create_ai_client("qwen")
ai._history.insert("system", "你是AI助手")
response = ai.send("你好")
print(response)
```

---

## 🎯 快速上手流程

1. **配置 API 密钥**（二选一）：
   - 使用网页：`cd window && python app.py`，访问 http://localhost:5000
   - 手动编辑：修改 `role/secret_key.Json`

2. **运行示例程序**：
   ```bash
   python main.py
   ```

3. **交互式对话**：
   ```bash
   python main.py --interactive
   ```

4. **切换模型**：
   - 在网页配置其他模型的密钥
   - 修改代码中的模型初始化部分

---

更多问题请查看源代码或提 issue。

### 4. tools/ExcelProcessor.py - Excel 读写工具（新增）

- `read_sheet(path, sheet_name="Sheet1")` - 读取指定工作表，可返回 List[Dict] 或 List[List]
- `write_sheet(path, data, sheet_name="Sheet1")` - 覆盖写入，支持字典/序列数据结构
- `append_rows(path, data)` - 追加新行，不清空现有内容
- `list_sheets(path)` - 查看可用工作表

依赖 openpyxl，如未安装请执行：

```bash
pip install openpyxl
```

```python
from tools import ExcelProcessor

excel = ExcelProcessor()

excel.write_sheet(
    'Data/output/demo.xlsx',
    data=[
        {'drone_id': 'H001', 'battery': 92},
        {'drone_id': 'H002', 'battery': 88},
    ],
)

excel.append_rows(
    'Data/output/demo.xlsx',
    data=[["H003", 79]],
    headers=['drone_id', 'battery'],
)

records = excel.read_sheet('Data/output/demo.xlsx')
print(records)
```
