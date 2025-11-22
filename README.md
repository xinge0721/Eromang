# Eromang

一个多功能媒体管理软件，集成了漫画阅读、视频播放和文档管理三大功能模块。

## 功能特性

### 📚 漫画阅读器
- 支持多种格式：CBZ, CBR, ZIP, RAR, PDF, 图片文件夹
- 单页/双页/连续阅读模式
- 阅读进度自动保存
- 书签功能
- 高性能图像解码（C++实现）

### 🎬 视频播放器
- 支持主流视频格式：MP4, MKV, AVI, FLV, MOV等
- 播放列表管理
- 字幕支持
- 断点续播
- 倍速播放

### 📄 文档管理
- 支持格式：PDF, TXT, Markdown（可扩展）
- 标签分类系统
- 全文搜索
- 阅读进度跟踪
- 注释和高亮功能

### 🌐 网络功能
- REST API接口
- WebSocket实时通信
- 远程控制支持
- 多设备同步（预留）

## 技术栈

- **UI框架**: PyQt6
- **数据库**: SQLite + SQLAlchemy ORM
- **性能优化**: C++ (pybind11绑定)
- **网络**: FastAPI + WebSocket
- **图像处理**: Pillow, OpenCV
- **视频处理**: VLC/FFmpeg
- **文档解析**: PyMuPDF, pdfplumber

## 项目结构

```
Eromang/
├── src/                      # 源代码
│   ├── ui/                   # UI层（PyQt6）
│   │   ├── main_window.py    # 主窗口
│   │   ├── manga/            # 漫画模块UI
│   │   ├── video/            # 视频模块UI
│   │   └── document/         # 文档模块UI
│   ├── services/             # 业务逻辑层
│   ├── managers/             # 管理器层
│   │   ├── config_manager.py # 配置管理
│   │   ├── cache_manager.py  # 缓存管理
│   │   └── thread_manager.py # 线程管理
│   ├── core/                 # 核心层
│   │   ├── parsers/          # 文件解析器
│   │   ├── decoders/         # 解码器（C++）
│   │   ├── indexer/          # 文件索引
│   │   └── network/          # 网络模块
│   ├── database/             # 数据层
│   │   ├── models/           # ORM模型
│   │   └── repository/       # 数据访问层
│   ├── utils/                # 工具类
│   └── constants/            # 常量定义
├── resources/                # 资源文件
├── tests/                    # 测试
├── docs/                     # 文档
├── requirements.txt          # Python依赖
├── setup.py                  # 安装配置
├── CMakeLists.txt           # C++构建配置
└── README.md                # 项目说明
```

## 安装指南

### 环境要求

- Python 3.10+
- C++ 编译器（MSVC 2019+）
- CMake 3.15+
- Git

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/eromang.git
cd eromang
```

2. **创建虚拟环境**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **安装Python依赖**
```bash
pip install -r requirements.txt
```

4. **安装开发依赖（可选）**
```bash
pip install -r requirements-dev.txt
```

5. **构建C++扩展（可选，用于性能优化）**
```bash
# 安装pybind11
pip install pybind11

# 使用CMake构建
mkdir build
cd build
cmake ..
cmake --build . --config Release
cd ..

# 或使用setup.py构建
python setup.py build_ext --inplace
```

6. **运行应用**
```bash
python -m src.main
```

## 开发指南

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest

# 代码格式化
black src/
isort src/

# 代码检查
flake8 src/
mypy src/
```

### 项目架构

项目采用分层架构设计：

1. **表示层（UI Layer）**: PyQt6界面，负责用户交互
2. **应用层（Application Layer）**: 业务逻辑和服务管理
3. **核心层（Core Layer）**: 文件解析、解码、索引等核心功能
4. **数据层（Data Layer）**: 数据库访问和文件系统操作

### 配置文件

应用配置文件位于 `~/.eromang/config.yaml`，首次运行时自动创建。

主要配置项：
- 主题设置
- 模块启用/禁用
- 网络设置
- 缓存设置
- 性能优化选项

## 使用说明

### 首次使用

1. 启动应用后，点击"文件" -> "导入媒体库"
2. 选择包含媒体文件的文件夹
3. 应用会自动扫描并索引文件
4. 在左侧导航栏切换不同模块

### 漫画阅读

1. 在漫画模块中选择要阅读的漫画
2. 使用方向键或鼠标滚轮翻页
3. 右键菜单可调整阅读模式和缩放
4. 阅读进度自动保存

### 视频播放

1. 在视频模块中选择视频
2. 支持常用播放控制（播放/暂停/快进/快退）
3. 可创建播放列表
4. 支持字幕加载

### 文档管理

1. 在文档模块中浏览文档
2. 使用搜索功能快速查找
3. 可添加标签进行分类
4. 支持添加注释和高亮

## 开发路线图

### Phase 1: 基础框架 ✅
- [x] 项目结构搭建
- [x] 数据库模型设计
- [x] 主窗口和导航
- [x] 配置管理系统

### Phase 2: 文档模块（优先）
- [ ] TXT解析器
- [ ] PDF解析器
- [ ] 文档查看器UI
- [ ] 搜索和标签功能

### Phase 3: 漫画模块
- [ ] C++图像解码器
- [ ] 压缩包解析
- [ ] 漫画阅读器UI
- [ ] 阅读进度管理

### Phase 4: 视频模块
- [ ] 视频解码集成
- [ ] 播放器UI
- [ ] 播放列表
- [ ] 字幕支持

### Phase 5: 高级功能
- [ ] 多线程优化
- [ ] 网络API
- [ ] 远程控制
- [ ] 缓存优化

### Phase 6: 扩展功能（预留）
- [ ] 插件系统
- [ ] 更多格式支持
- [ ] 云同步
- [ ] 移动端适配

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 Python代码规范
- 使用 Black 进行代码格式化
- 添加适当的注释和文档字符串
- 编写单元测试

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

- PyQt6 - 强大的Python GUI框架
- SQLAlchemy - 优秀的Python ORM
- FastAPI - 现代化的Web框架
- 所有开源贡献者

## 联系方式

- 项目主页: https://github.com/yourusername/eromang
- 问题反馈: https://github.com/yourusername/eromang/issues

## 更新日志

### v0.1.0 (2025-11-19)
- 初始版本
- 完成基础架构搭建
- 实现主窗口框架
- 数据库模型设计
- 配置管理系统