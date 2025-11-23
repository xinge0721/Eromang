"""
Eromang项目结构创建脚本
一键创建完整的客户端-服务器架构目录和文件
"""

import os
from pathlib import Path


def create_file(file_path: Path, content: str = ""):
    """创建文件并写入内容"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] 创建文件: {file_path}")


def create_init_file(dir_path: Path):
    """创建__init__.py文件"""
    init_file = dir_path / "__init__.py"
    if not init_file.exists():
        create_file(init_file, '"""Package initialization."""\n')


def create_directory(dir_path: Path):
    """创建目录"""
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"[OK] 创建目录: {dir_path}")


# 项目根目录
ROOT = Path(__file__).parent.parent

# ============================================
# 客户端结构
# ============================================
CLIENT_STRUCTURE = {
    "client/app": ["main.py", "app.py"],
    "client/modules/manga/ui": [],
    "client/modules/manga/services": [],
    "client/modules/manga/models": [],
    "client/modules/manga/parsers": [],
    "client/modules/video/ui": [],
    "client/modules/video/services": [],
    "client/modules/video/models": [],
    "client/modules/video/player": [],
    "client/modules/document/ui": [],
    "client/modules/document/services": [],
    "client/modules/document/models": [],
    "client/modules/document/parsers": [],
    "client/modules/ai_assistant/ui": [],
    "client/modules/ai_assistant/services": [],
    "client/modules/ai_assistant/models": [],
    "client/modules/ai_assistant/engines": [],
    "client/modules/ai_assistant/plugins": [],
    "client/modules/settings/ui": [],
    "client/modules/settings/services": [],
    "client/modules/auth/ui": [],
    "client/modules/auth/services": [],
    "client/modules/auth/models": [],
    "client/core/database": ["connection.py", "models.py"],
    "client/core/cache": ["cache_manager.py", "lru_cache.py"],
    "client/core/api_client": ["client.py", "websocket.py", "endpoints.py"],
    "client/core/sources/manga": ["base.py", "manager.py"],
    "client/core/sources/video": ["base.py", "manager.py"],
    "client/core/sources/document": ["base.py", "manager.py"],
    "client/core/thread": ["thread_manager.py", "thread_pool.py", "worker.py"],
    "client/core/exception": ["exceptions.py", "error_handler.py"],
    "client/common/ui/widgets": [],
    "client/common/ui/dialogs": [],
    "client/common/utils": ["file_utils.py", "image_utils.py", "logger.py"],
    "client/common/globals": ["app_state.py", "event_bus.py"],
    "client/resources/images/icons": [],
    "client/resources/images/backgrounds": [],
    "client/resources/images/avatars": [],
    "client/resources/images/splash": [],
    "client/resources/styles/themes": [],
    "client/resources/styles/components": [],
    "client/resources/fonts": [],
    "client/resources/i18n": [],
}

# ============================================
# 服务器结构
# ============================================
SERVER_STRUCTURE = {
    "server/app": ["main.py", "config.py"],
    "server/api": ["server.py", "schemas.py"],
    "server/api/routes": ["auth.py", "manga.py", "video.py", "document.py", "sync.py", "user.py"],
    "server/api/middleware": ["auth.py", "cors.py", "logging.py"],
    "server/websocket": ["server.py", "handlers.py", "events.py"],
    "server/services": [
        "manga_service.py",
        "video_service.py",
        "document_service.py",
        "user_service.py",
        "sync_service.py"
    ],
    "server/database": ["connection.py"],
    "server/database/models": ["user.py", "manga.py", "video.py", "document.py"],
    "server/database/repository": ["user_repo.py", "manga_repo.py", "video_repo.py"],
    "server/storage": ["local.py", "oss.py", "manager.py"],
    "server/sources/crawler": ["base.py", "engine.py"],
    "server/sources/manga": ["parser.py", "manager.py"],
    "server/sources/video": ["parser.py", "manager.py"],
    "server/utils": ["auth.py", "cache.py", "logger.py"],
}

# ============================================
# 共享代码结构
# ============================================
SHARED_STRUCTURE = {
    "shared/models": ["base.py", "manga.py", "video.py", "document.py"],
    "shared/constants": ["app_constants.py", "format_constants.py"],
    "shared/utils": ["common_utils.py"],
}

# ============================================
# 测试结构
# ============================================
TEST_STRUCTURE = {
    "tests/client/unit": [],
    "tests/client/integration": [],
    "tests/server/unit": [],
    "tests/server/integration": [],
    "tests/fixtures": [],
}

# ============================================
# 文档和脚本
# ============================================
DOCS_STRUCTURE = {
    "docs": ["architecture.md", "api.md", "development.md"],
}


def create_structure(structure: dict, base_path: Path = ROOT):
    """根据结构字典创建目录和文件"""
    for dir_path, files in structure.items():
        full_dir_path = base_path / dir_path
        create_directory(full_dir_path)

        # 创建__init__.py（如果是Python包）
        if "client" in dir_path or "server" in dir_path or "shared" in dir_path:
            create_init_file(full_dir_path)

        # 创建文件
        for file_name in files:
            file_path = full_dir_path / file_name
            if not file_path.exists():
                # 根据文件类型添加基础内容
                content = get_file_template(file_name, dir_path)
                create_file(file_path, content)


def get_file_template(file_name: str, dir_path: str) -> str:
    """根据文件名和路径返回模板内容"""

    # 主程序模板
    if file_name == "main.py":
        if "client" in dir_path:
            return '''"""
Eromang客户端主程序
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))


def main():
    """客户端主函数"""
    print("Eromang客户端启动中...")
    # TODO: 初始化客户端应用
    pass


if __name__ == "__main__":
    main()
'''
        elif "server" in dir_path:
            return '''"""
Eromang服务器主程序
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))


def main():
    """服务器主函数"""
    print("Eromang服务器启动中...")
    # TODO: 初始化FastAPI服务器
    pass


if __name__ == "__main__":
    main()
'''

    # 配置文件模板
    elif file_name == "config.py":
        return '''"""
配置管理
"""

from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent.parent.parent

# 数据库配置
DATABASE_URL = "sqlite:///eromang.db"

# 服务器配置
HOST = "0.0.0.0"
PORT = 8080

# 其他配置
DEBUG = True
'''

    # 事件总线模板
    elif file_name == "event_bus.py":
        return '''"""
全局事件总线
用于模块间通信
"""

from typing import Callable, Dict, List


class EventBus:
    """事件总线单例"""

    _instance = None
    _subscribers: Dict[str, List[Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def subscribe(self, event_name: str, callback: Callable):
        """订阅事件"""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, data=None):
        """发布事件"""
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                callback(data)

    def unsubscribe(self, event_name: str, callback: Callable):
        """取消订阅"""
        if event_name in self._subscribers:
            self._subscribers[event_name].remove(callback)


# 全局事件总线实例
event_bus = EventBus()
'''

    # 默认Python文件模板
    elif file_name.endswith(".py"):
        module_name = file_name.replace(".py", "").replace("_", " ").title()
        return f'''"""
{module_name}
"""

# TODO: 实现{module_name}功能
'''

    # Markdown文件模板
    elif file_name.endswith(".md"):
        title = file_name.replace(".md", "").replace("_", " ").title()
        return f'''# {title}

TODO: 编写文档内容
'''

    return ""


def create_root_files():
    """创建根目录文件"""

    # .gitignore
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.db
*.sqlite
*.sqlite3
logs/
cache/
temp/
*.log

# Resources (large files)
client/resources/images/
client/resources/fonts/
'''
    create_file(ROOT / ".gitignore", gitignore_content)

    # requirements.txt (客户端)
    client_requirements = '''# UI Framework
PyQt6>=6.6.0

# Database
SQLAlchemy>=2.0.0

# Network
httpx>=0.26.0
websockets>=12.0

# Image Processing
Pillow>=10.2.0

# PDF Processing
PyMuPDF>=1.23.0

# File Processing
chardet>=5.2.0

# Utilities
pyyaml>=6.0.1
loguru>=0.7.2

# AI (Optional)
openai>=1.0.0
edge-tts>=6.1.0
'''
    create_file(ROOT / "client" / "requirements.txt", client_requirements)

    # requirements.txt (服务器)
    server_requirements = '''# Web Framework
fastapi>=0.109.0
uvicorn>=0.27.0

# Database
SQLAlchemy>=2.0.0
alembic>=1.13.0

# WebSocket
websockets>=12.0

# HTTP Client
httpx>=0.26.0
requests>=2.31.0

# Web Scraping
beautifulsoup4>=4.12.0
lxml>=5.1.0

# Storage
boto3>=1.34.0  # AWS S3
oss2>=2.18.0   # Aliyun OSS

# Utilities
pyyaml>=6.0.1
loguru>=0.7.2
python-dotenv>=1.0.0

# Authentication
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.6
'''
    create_file(ROOT / "server" / "requirements.txt", server_requirements)

    # README.md (保持现有的)
    print("[OK] 保留现有 README.md")


def create_virtual_environments():
    """创建虚拟环境"""
    import subprocess
    import sys

    print()
    print("=" * 60)
    print("是否创建虚拟环境？")
    print("=" * 60)
    print("1. 创建客户端虚拟环境 (client/venv)")
    print("2. 创建服务器虚拟环境 (server/venv)")
    print("3. 创建两个虚拟环境")
    print("4. 跳过")
    print()

    choice = input("请选择 [1-4]: ").strip()

    if choice == "4":
        print("[SKIP] 跳过虚拟环境创建")
        return

    # 创建客户端虚拟环境
    if choice in ["1", "3"]:
        print()
        print("[INFO] 创建客户端虚拟环境...")
        client_venv = ROOT / "client" / "venv"
        try:
            subprocess.run([sys.executable, "-m", "venv", str(client_venv)], check=True)
            print(f"[OK] 客户端虚拟环境创建成功: {client_venv}")
            print("[INFO] 激活虚拟环境: client\\venv\\Scripts\\activate (Windows)")
            print("[INFO] 激活虚拟环境: source client/venv/bin/activate (Linux/Mac)")
        except Exception as e:
            print(f"[ERROR] 创建客户端虚拟环境失败: {e}")

    # 创建服务器虚拟环境
    if choice in ["2", "3"]:
        print()
        print("[INFO] 创建服务器虚拟环境...")
        server_venv = ROOT / "server" / "venv"
        try:
            subprocess.run([sys.executable, "-m", "venv", str(server_venv)], check=True)
            print(f"[OK] 服务器虚拟环境创建成功: {server_venv}")
            print("[INFO] 激活虚拟环境: server\\venv\\Scripts\\activate (Windows)")
            print("[INFO] 激活虚拟环境: source server/venv/bin/activate (Linux/Mac)")
        except Exception as e:
            print(f"[ERROR] 创建服务器虚拟环境失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("Eromang 项目结构创建脚本")
    print("=" * 60)
    print()

    # 创建客户端结构
    print("[1/6] 创建客户端结构...")
    create_structure(CLIENT_STRUCTURE)
    print()

    # 创建服务器结构
    print("[2/6] 创建服务器结构...")
    create_structure(SERVER_STRUCTURE)
    print()

    # 创建共享代码结构
    print("[3/6] 创建共享代码结构...")
    create_structure(SHARED_STRUCTURE)
    print()

    # 创建测试结构
    print("[4/6] 创建测试结构...")
    create_structure(TEST_STRUCTURE)
    print()

    # 创建文档结构
    print("[5/6] 创建文档结构...")
    create_structure(DOCS_STRUCTURE)
    print()

    # 创建根目录文件
    print("[6/6] 创建根目录文件...")
    create_root_files()
    print()

    print("=" * 60)
    print(">>> 项目结构创建完成！")
    print("=" * 60)

    # 创建虚拟环境
    create_virtual_environments()

    print()
    print("=" * 60)
    print("下一步:")
    print("=" * 60)
    print("1. 激活客户端虚拟环境:")
    print("   Windows: client\\venv\\Scripts\\activate")
    print("   Linux/Mac: source client/venv/bin/activate")
    print()
    print("2. 安装客户端依赖:")
    print("   cd client && pip install -r requirements.txt")
    print()
    print("3. 激活服务器虚拟环境:")
    print("   Windows: server\\venv\\Scripts\\activate")
    print("   Linux/Mac: source server/venv/bin/activate")
    print()
    print("4. 安装服务器依赖:")
    print("   cd server && pip install -r requirements.txt")
    print()
    print("5. 运行应用:")
    print("   客户端: python client/app/main.py")
    print("   服务器: python server/app/main.py")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
