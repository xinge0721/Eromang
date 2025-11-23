# Eromang

一个多功能媒体管理软件，集成了漫画阅读、视频播放、文档管理和AI助手四大功能模块。

## 功能特性

### 漫画阅读器
- **本地支持**：CBZ, CBR, ZIP, RAR, PDF, 图片文件夹
- **在线漫画源**：支持添加自定义漫画网站源
- 单页/双页/连续阅读模式
- 阅读进度自动保存
- 书签和收藏功能

### 视频播放器
- **本地支持**：MP4, MKV, AVI, FLV, MOV等
- **在线视频源**：支持在线视频网站解析
- 播放列表管理
- 字幕支持
- 断点续播

### 文档管理
- **本地支持**：PDF, TXT, Markdown
- **在线文档**：支持在线文档库
- 标签分类系统
- 全文搜索
- 云端同步（可选）

### AI助手（新增）
- 语音唤醒："小爱同学"
- 智能控制：语音控制各模块
- 智能推荐：基于历史推荐
- 对话功能：闲聊、问答

### 网络功能
- **REST API**：提供完整的HTTP API接口
- **WebSocket**：实时双向通信
- **远程控制**：通过网络控制应用
- **多设备同步**：跨设备同步阅读进度和收藏
- **在线资源管理**：统一管理在线漫画源、视频源

## 项目架构

### 核心设计：模块高内聚

每个功能模块的所有代码集中在一个文件夹，出问题直接找对应模块。

```
Eromang/
├── client/              # 客户端（桌面应用）
│   ├── app/             # 应用入口
│   │   ├── main.py      # 客户端主程序
│   │   └── app.py       # 应用类
│   │
│   ├── modules/         # 功能模块
│   │   ├── manga/       # 漫画模块
│   │   ├── video/       # 视频模块
│   │   ├── document/    # 文档模块
│   │   ├── ai_assistant/# AI助手模块
│   │   ├── settings/    # 设置模块
│   │   └── auth/        # 登录注册模块
│   │
│   ├── core/            # 客户端核心
│   │   ├── database/    # 本地数据库（缓存、配置）
│   │   ├── cache/       # 本地缓存
│   │   ├── api_client/  # 服务器API客户端
│   │   │   ├── client.py          # HTTP客户端
│   │   │   ├── websocket.py       # WebSocket客户端
│   │   │   └── endpoints.py       # API端点定义
│   │   ├── sources/     # 在线资源源解析器
│   │   │   ├── manga/   # 漫画源解析器
│   │   │   ├── video/   # 视频源解析器
│   │   │   └── document/# 文档源解析器
│   │   └── thread/      # 线程管理
│   │
│   ├── common/          # 通用组件
│   │   ├── ui/          # UI组件
│   │   ├── utils/       # 工具函数
│   │   └── globals/     # 全局变量、事件总线
│   │
│   └── resources/       # 资源文件
│       ├── images/      # 图片
│       ├── styles/      # 样式
│       └── fonts/       # 字体
│
├── server/              # 服务器（独立部署）
│   ├── app/             # 服务器入口
│   │   ├── main.py      # 服务器主程序
│   │   └── config.py    # 服务器配置
│   │
│   ├── api/             # REST API
│   │   ├── server.py    # FastAPI服务器
│   │   ├── routes/      # API路由
│   │   │   ├── auth.py        # 认证API
│   │   │   ├── manga.py       # 漫画API
│   │   │   ├── video.py       # 视频API
│   │   │   ├── document.py    # 文档API
│   │   │   ├── sync.py        # 同步API
│   │   │   └── user.py        # 用户API
│   │   ├── middleware/  # 中间件
│   │   │   ├── auth.py        # 认证中间件
│   │   │   ├── cors.py        # CORS中间件
│   │   │   └── logging.py     # 日志中间件
│   │   └── schemas.py   # 数据模型（Pydantic）
│   │
│   ├── websocket/       # WebSocket服务
│   │   ├── server.py    # WS服务器
│   │   ├── handlers.py  # 消息处理器
│   │   └── events.py    # 事件定义
│   │
│   ├── services/        # 业务逻辑层
│   │   ├── manga_service.py   # 漫画服务
│   │   ├── video_service.py   # 视频服务
│   │   ├── document_service.py# 文档服务
│   │   ├── user_service.py    # 用户服务
│   │   └── sync_service.py    # 同步服务
│   │
│   ├── database/        # 服务器数据库
│   │   ├── connection.py      # 数据库连接
│   │   ├── models/      # 数据模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── manga.py       # 漫画模型
│   │   │   ├── video.py       # 视频模型
│   │   │   └── document.py    # 文档模型
│   │   └── repository/  # 数据访问层
│   │       ├── user_repo.py
│   │       ├── manga_repo.py
│   │       └── video_repo.py
│   │
│   ├── storage/         # 文件存储
│   │   ├── local.py     # 本地存储
│   │   ├── oss.py       # 对象存储（阿里云OSS/AWS S3）
│   │   └── manager.py   # 存储管理器
│   │
│   ├── sources/         # 在线资源源（服务器端）
│   │   ├── crawler/     # 爬虫引擎
│   │   ├── manga/       # 漫画源
│   │   └── video/       # 视频源
│   │
│   └── utils/           # 工具函数
│       ├── auth.py      # 认证工具
│       ├── cache.py     # 缓存工具
│       └── logger.py    # 日志工具
│
├── shared/              # 客户端和服务器共享代码
│   ├── models/          # 共享数据模型
│   ├── constants/       # 共享常量
│   └── utils/           # 共享工具函数
│
└── tests/               # 测试
    ├── client/          # 客户端测试
    └── server/          # 服务器测试
```

## 技术栈

- **UI框架**: PyQt6
- **数据库**: SQLite + SQLAlchemy
- **性能优化**: C++ (pybind11)
- **网络通信**: FastAPI + WebSocket + httpx
- **在线资源解析**: BeautifulSoup4 + lxml + requests
- **AI引擎**: OpenAI API / Ollama, Whisper, edge-tts

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m app.main
```

## 开发路线图

### Phase 1: 基础框架重构
- [ ] 重新组织目录结构
- [ ] 实现事件总线
- [ ] 实现线程管理
- [ ] 实现网络通信基础（HTTP客户端）

### Phase 2: 核心模块实现
- [ ] 文档模块（本地）
- [ ] 漫画模块（本地）
- [ ] 视频模块（本地）

### Phase 3: 网络功能
- [ ] REST API服务器
- [ ] WebSocket实时通信
- [ ] 在线漫画源解析器
- [ ] 在线视频源解析器
- [ ] 远程控制功能

### Phase 4: AI助手
- [ ] 语音识别（STT）
- [ ] 语音合成（TTS）
- [ ] 基础对话功能
- [ ] 智能控制集成

### Phase 5: 高级功能
- [ ] 多设备同步
- [ ] 云端备份
- [ ] 插件系统
- [ ] 自定义资源源

## 许可证

MIT License
