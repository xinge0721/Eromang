# Eromang 架构设计文档

## 1. 概述

Eromang 是一个多功能媒体管理软件，采用 Python + C++ 混合开发，使用 PyQt6 作为 UI 框架。项目采用分层架构设计，具有良好的可扩展性和可维护性。

### 1.1 设计目标

- **模块化**: 三大功能模块（漫画、视频、文档）相对独立但风格统一
- **高性能**: 关键路径使用 C++ 实现，提供流畅的用户体验
- **可扩展**: 预留插件接口，支持格式扩展
- **跨平台**: 优先支持 Windows，架构设计考虑跨平台兼容性

### 1.2 技术选型

| 层次 | 技术栈 | 说明 |
|------|--------|------|
| UI层 | PyQt6 | 成熟的跨平台GUI框架 |
| 业务层 | Python 3.10+ | 快速开发，丰富的生态 |
| 核心层 | C++ + pybind11 | 高性能图像/视频处理 |
| 数据层 | SQLite + SQLAlchemy | 轻量级数据库，强大的ORM |
| 网络层 | FastAPI + WebSocket | 现代化API框架 |

## 2. 整体架构

### 2.1 分层架构图

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                     │
│  ┌──────────────┬──────────────┬──────────────────┐    │
│  │  Manga UI    │   Video UI   │   Document UI    │    │
│  │  - Reader    │  - Player    │   - Viewer       │    │
│  │  - Library   │  - Playlist  │   - Manager      │    │
│  │  - Settings  │  - Controls  │   - Search       │    │
│  └──────────────┴──────────────┴──────────────────┘    │
│           Common UI Components (PyQt6)                  │
├─────────────────────────────────────────────────────────┤
│                  Application Layer                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Service Layer (业务服务)                        │   │
│  │  - MangaService  - VideoService  - DocService   │   │
│  │  - LibraryService  - SearchService              │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Manager Layer (管理器)                          │   │
│  │  - ThreadPoolManager  - CacheManager            │   │
│  │  - NetworkManager  - ConfigManager              │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                    Core Layer                           │
│  ┌──────────────────┬──────────────────────────────┐   │
│  │  Parser Module   │   Decoder Module (C++)       │   │
│  │  - TxtParser     │   - ImageDecoder             │   │
│  │  - PdfParser     │   - VideoDecoder             │   │
│  │  - MdParser      │   - ArchiveDecoder           │   │
│  └──────────────────┴──────────────────────────────┘   │
│  ┌──────────────────┬──────────────────────────────┐   │
│  │  Indexer Module  │   Network Module             │   │
│  │  - FileWatcher   │   - RestAPI (FastAPI)        │   │
│  │  - MetaExtractor │   - WebSocket Server         │   │
│  │  - SearchEngine  │   - RemoteControl            │   │
│  └──────────────────┴──────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                   Data Layer                            │
│  ┌──────────────────┬──────────────────────────────┐   │
│  │  Database (ORM)  │   FileSystem Access          │   │
│  │  - Models        │   - LocalStorage             │   │
│  │  - Repository    │   - TempStorage              │   │
│  │  - Migration     │   - CacheStorage             │   │
│  └──────────────────┴──────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 模块依赖关系

```
UI Layer
   ↓ (调用)
Service Layer
   ↓ (使用)
Manager Layer + Core Layer
   ↓ (访问)
Data Layer
```

## 3. 核心模块设计

### 3.1 数据库设计

#### 3.1.1 核心表结构

**媒体库表 (libraries)**
- 管理不同类型的媒体集合
- 支持多个媒体库并存
- 记录扫描状态和配置

**漫画相关表**
- `manga`: 漫画基本信息
- `manga_progress`: 阅读进度
- `manga_bookmarks`: 书签

**视频相关表**
- `videos`: 视频基本信息
- `video_progress`: 播放进度
- `playlists`: 播放列表
- `playlist_items`: 播放列表项

**文档相关表**
- `documents`: 文档基本信息
- `document_progress`: 阅读进度
- `document_tags`: 文档标签
- `document_annotations`: 注释和高亮

**通用表**
- `tags`: 标签定义
- `favorites`: 收藏夹
- `search_index`: 全文搜索索引

#### 3.1.2 数据库优化

- 使用 WAL 模式提高并发性能
- 合理的索引设计（title, path, file_hash）
- 外键约束保证数据完整性
- 定期 VACUUM 优化数据库

### 3.2 配置管理系统

#### 3.2.1 配置文件结构

```yaml
app:
  theme: dark
  language: zh_CN

modules:
  manga:
    enabled: true
    formats: [cbz, cbr, zip, pdf]
  video:
    enabled: true
    formats: [mp4, mkv, avi]
  document:
    enabled: true
    formats: [txt, pdf]

network:
  api_enabled: false
  api_port: 8080
```

#### 3.2.2 配置管理特性

- YAML 格式，易读易写
- 支持热加载（部分配置）
- 配置导入/导出功能
- 默认值回退机制

### 3.3 多线程架构

#### 3.3.1 线程池分配

```python
UI Thread (主线程)
  - 界面渲染和事件处理
  - 不执行耗时操作

IO Thread Pool (4线程)
  - 文件读取
  - 数据库操作
  - 网络请求

Decode Thread Pool (2-4线程)
  - 图像解码
  - 视频解码
  - 文档解析

Index Thread Pool (2线程)
  - 文件扫描
  - 元数据提取
  - 缩略图生成
```

#### 3.3.2 线程通信

- 使用 Qt 信号槽机制
- 线程安全的队列
- 避免死锁和竞态条件

### 3.4 缓存策略

#### 3.4.1 多级缓存

```
L1: 内存缓存 (LRU)
  - 当前页面数据
  - 预加载数据（前后3页）
  - 最大 512MB

L2: 磁盘缓存
  - 缩略图（永久）
  - 解码后的图像（临时）
  - 视频关键帧

L3: 数据库缓存
  - 元数据
  - 搜索索引
```

#### 3.4.2 缓存管理

- C++ 实现 LRU 缓存算法
- 自动清理过期缓存
- 可配置缓存大小
- 支持手动清理

## 4. 功能模块设计

### 4.1 漫画模块

#### 4.1.1 支持格式

- **压缩包**: CBZ, CBR, ZIP, RAR
- **文档**: PDF
- **文件夹**: 包含图片的目录

#### 4.1.2 核心功能

1. **图像解码器 (C++)**
   - 高性能 JPEG/PNG 解码
   - 支持大图片处理
   - 内存优化

2. **阅读器**
   - 单页/双页/连续模式
   - 缩放：适应宽度/高度/原始大小
   - 预加载机制
   - 阅读进度自动保存

3. **媒体库管理**
   - 自动扫描和索引
   - 元数据提取
   - 封面生成
   - 重复检测（文件哈希）

### 4.2 视频模块

#### 4.2.1 支持格式

- MP4, MKV, AVI, FLV, MOV, WMV, WebM

#### 4.2.2 核心功能

1. **视频播放器**
   - 基于 VLC/FFmpeg
   - 硬件加速支持
   - 字幕加载
   - 倍速播放

2. **播放列表**
   - 创建自定义列表
   - 自动播放下一个
   - 列表导入/导出

3. **进度管理**
   - 断点续播
   - 观看历史
   - 播放统计

### 4.3 文档模块

#### 4.3.1 支持格式

**Phase 1 (已实现)**
- TXT: 纯文本
- PDF: PDF文档

**Phase 2 (预留)**
- MD: Markdown
- DOCX: Word文档
- EPUB: 电子书

#### 4.3.2 核心功能

1. **文档解析器**
   - 可扩展的解析器接口
   - 编码自动检测
   - 分页处理

2. **文档查看器**
   - 可调字体和行距
   - 主题切换（亮/暗/护眼）
   - 目录导航

3. **标签系统**
   - 自定义标签
   - 标签颜色
   - 按标签筛选

4. **搜索功能**
   - 全文搜索
   - 模糊搜索
   - 搜索结果高亮

### 4.4 网络模块

#### 4.4.1 REST API

```
GET  /api/v1/manga/list          # 获取漫画列表
GET  /api/v1/manga/{id}          # 获取漫画详情
POST /api/v1/manga/import        # 导入漫画
PUT  /api/v1/manga/{id}/progress # 更新进度

GET  /api/v1/video/list          # 获取视频列表
GET  /api/v1/video/{id}/stream   # 视频流
POST /api/v1/video/playlist      # 创建播放列表

GET  /api/v1/document/list       # 获取文档列表
GET  /api/v1/document/{id}       # 获取文档内容
POST /api/v1/document/search     # 搜索文档
```

#### 4.4.2 WebSocket

- 实时进度同步
- 远程控制指令
- 多客户端通知

## 5. 扩展性设计

### 5.1 插件系统（预留）

```python
class PluginInterface:
    def register_parser(self, format: str, parser: BaseParser)
    def register_decoder(self, format: str, decoder: BaseDecoder)
    def register_ui_component(self, component: QWidget)
```

### 5.2 格式扩展

通过实现 `BaseParser` 接口添加新格式支持：

```python
class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> Document

    @abstractmethod
    def extract_metadata(self) -> dict

    @abstractmethod
    def get_content(self, page: int) -> str
```

### 5.3 主题扩展

- QSS 样式表
- 支持自定义主题
- 主题热切换

## 6. 性能优化

### 6.1 启动优化

- 延迟加载模块
- 异步初始化数据库
- 缓存配置文件

### 6.2 运行时优化

- C++ 实现关键路径
- 多线程并行处理
- 智能预加载
- 内存池管理

### 6.3 数据库优化

- 批量操作
- 事务管理
- 索引优化
- 定期维护

## 7. 安全性考虑

### 7.1 文件安全

- 路径验证，防止目录遍历
- 文件类型检查
- 大小限制

### 7.2 数据安全

- SQL 注入防护（ORM）
- 输入验证
- 敏感数据加密（预留）

### 7.3 网络安全

- API 认证（预留）
- HTTPS 支持（预留）
- 跨域限制

## 8. 测试策略

### 8.1 单元测试

- 核心功能模块
- 数据库操作
- 文件解析器

### 8.2 集成测试

- 模块间交互
- 数据库迁移
- API 接口

### 8.3 性能测试

- 大文件处理
- 并发操作
- 内存泄漏检测

## 9. 部署方案

### 9.1 开发环境

```bash
python -m venv venv
pip install -r requirements-dev.txt
python -m src.main
```

### 9.2 生产环境

```bash
# 使用 PyInstaller 打包
pyinstaller --windowed --onefile src/main.py

# 或使用 cx_Freeze
python setup.py build
```

## 10. 未来规划

### 10.1 短期目标（3个月）

- 完成文档模块
- 实现漫画阅读器
- 基础视频播放功能

### 10.2 中期目标（6个月）

- 网络功能
- 性能优化
- 更多格式支持

### 10.3 长期目标（1年）

- 插件系统
- 云同步
- 移动端适配
- 社区功能

## 11. 技术债务

### 11.1 已知问题

- C++ 扩展尚未实现
- 网络模块仅有框架
- 缺少完整的错误处理

### 11.2 改进计划

- 添加更多单元测试
- 完善日志系统
- 优化内存使用
- 改进用户体验

## 12. 参考资料

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pybind11 Documentation](https://pybind11.readthedocs.io/)

---

**文档版本**: 1.0
**最后更新**: 2025-11-19
**维护者**: Eromang Team
