# 项目目录结构

## 📁 完整目录树

```
scripts/
├── main.py                          # 主程序入口
├── README_USAGE.md                  # 使用说明文档
│
├── Agent/                           # AI代理模块
│   ├── __init__.py
│   ├── AIManager.py                 # AI管理器（工厂类）
│   ├── ConversationController.py    # 对话控制器
│   └── _Search.py                   # 搜索功能
│
├── Business/                        # 业务逻辑模块（预留）
│
├── Models/                          # AI模型封装
│   ├── __init__.py
│   ├── CharGPT.py                   # ChatGPT模型
│   ├── claude.py                    # Claude模型
│   ├── deepseek.py                  # DeepSeek模型
│   ├── doubao.py                    # 豆包模型
│   ├── Gemini.py                    # Gemini模型
│   ├── Kiimi.py                     # Kimi模型
│   ├── qwen.py                      # 通义千问模型
│   └── xinhuo.py                    # 讯飞星火模型
│
├── Serve/                           # 服务层
│   ├── __init__.py
│   ├── HTTP.py                      # HTTP服务
│   ├── OPEN_AI.py                   # OpenAI封装
│   └── Web.py                       # Web服务
│
├── Tools/                           # 工具模块
│   ├── __init__.py
│   ├── DatabaseEditor.py            # 数据库编辑器
│   ├── DataInquire.py               # 数据查询器
│   ├── FileEditor.py                # 文件编辑器
│   ├── HistoryManager.py            # 历史记录管理器
│   ├── JSONProcessor.py             # JSON处理器
│   └── log.py                       # 日志工具
│
├── Role/                            # 角色配置
│   ├── config.json                  # 配置文件
│   ├── secret_key.Json              # API密钥配置
│   ├── system.json                  # 系统配置
│   ├── user.json                    # 用户配置
│   │
│   ├── role_A/                      # 角色A配置（对话AI）
│   │   ├── assistant.json           # 助手配置
│   │   ├── history.json             # 对话历史
│   │   └── prompts/                 # 提示词模板
│   │       ├── 01_base_role.txt
│   │       ├── 02_output_decision.txt
│   │       ├── 03_json_format.txt
│   │       ├── 04_code_structure.txt
│   │       ├── 05_pid_requirements.txt
│   │       ├── 06_examples_correct.txt
│   │       ├── 07_examples_wrong.txt
│   │       ├── 08_anti_history_pollution.txt
│   │       ├── 09_deep_thinking.txt
│   │       ├── build_prompt.py
│   │       └── README.md
│   │
│   └── role_B/                      # 角色B配置（知识AI）
│       ├── assistant.json           # 助手配置
│       ├── history.json             # 对话历史
│       └── prompts/                 # 提示词模板
│           ├── 01_base_role.txt
│           ├── 02_output_decision.txt
│           ├── 03_json_format.txt
│           ├── 04_code_structure.txt
│           ├── 05_pid_requirements.txt
│           ├── 06_examples_correct.txt
│           ├── 07_examples_wrong.txt
│           ├── 08_anti_history_pollution.txt
│           ├── 09_deep_thinking.txt
│           ├── build_prompt.py
│           └── README.md
│
├── Window/                          # 配置管理界面
│   ├── app.py                       # Flask应用
│   ├── requirements.txt             # 依赖列表
│   ├── README.md                    # 说明文档
│   ├── 启动配置管理.bat             # 启动脚本
│   └── templates/
│       └── index.html               # 前端页面
│
├── Data/                            # 数据存储目录
│   ├── output/                      # AI生成的代码文件
│   ├── databases/                   # 数据库文件（*.db）
│   ├── abstracts/                   # 代码抽象缓存
│   └── record/                      # 日志记录
│       ├── 2025-10-27.log
│       ├── 2025-10-28.log
│       ├── 2025-10-31.log
│       └── 2025-11-01.log
│
└── test/                            # 测试目录
```

## 📦 模块说明

### 核心模块
- **Agent/** - AI代理模块（AI管理器、对话控制器、搜索功能）
- **Business/** - 业务逻辑模块（预留扩展）
- **Models/** - AI模型封装（支持8种模型）
- **Serve/** - 服务层封装（HTTP、OpenAI适配器、Web服务）
- **Tools/** - 工具集（文件编辑、数据库、JSON处理、历史管理、日志）

### 配置与数据
- **Role/** - 角色配置和提示词管理（对话AI和知识AI）
- **Window/** - Web配置管理界面
- **Data/** - 数据存储目录
  - `output/` - AI生成的代码文件
  - `databases/` - 数据库文件
  - `abstracts/` - 代码抽象缓存
  - `record/` - 日志记录
- **test/** - 测试文件（预留）

## 🎯 支持的AI模型

1. **ChatGPT** (CharGPT.py)
2. **Claude** (claude.py)
3. **DeepSeek** (deepseek.py)
4. **豆包** (doubao.py)
5. **Gemini** (Gemini.py)
6. **Kimi** (Kiimi.py)
7. **通义千问** (qwen.py)
8. **讯飞星火** (xinhuo.py)

## 📝 主要文件

| 文件 | 说明 |
|------|------|
| `main.py` | 程序主入口 |
| `README_USAGE.md` | 详细使用说明 |
| `Role/secret_key.Json` | API密钥配置（重要） |
| `Role/config.json` | 系统配置文件 |
| `Agent/AIManager.py` | AI工厂类（双模型管理） |
| `Agent/ConversationController.py` | 对话控制器 |
| `Tools/JSONProcessor.py` | JSON处理器 |
| `Tools/HistoryManager.py` | 历史记录管理器 |
| `Serve/OPEN_AI.py` | OpenAI标准接口封装 |
| `Window/app.py` | 配置管理Web界面 |

## 🔧 工具说明

- **FileEditor.py** - 文件行级编辑工具
- **DatabaseEditor.py** - SQLite数据库编辑工具  
- **DataInquire.py** - 数据查询工具
- **JSONProcessor.py** - JSON数据处理器
- **HistoryManager.py** - 对话历史管理器
- **log.py** - 日志工具

## 📌 备注

- `Data/` 目录结构：
  - `output/` - 存放AI生成的代码文件
  - `databases/` - 存放SQLite数据库文件
  - `abstracts/` - 存放代码抽象缓存
  - `record/` - 存放日志记录
- `test/` 目录预留用于测试文件
- 所有API密钥统一在 `Role/secret_key.Json` 中管理
- 支持双AI协作：role_A（对话AI）和 role_B（知识AI）

