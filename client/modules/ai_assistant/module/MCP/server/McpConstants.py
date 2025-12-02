
class tools_config:
    # 默认配置参数
    config = {
        "server_name": "MCP工具服务器",
        "tools": [
            {
                "enabled": "true",
                "module": "module.MCP.server.tools.FileEditor",
                "class": "FileEditor",
                "methods": "all",
                "description": "文件编辑工具"
            },
            {
                "enabled": "true",
                "module": "module.MCP.server.tools.DatabaseEditor",
                "class": "DatabaseEditor",
                "methods": "all",
                "description": "数据库编辑工具"
            },
            {
                "enabled": "true",
                "module": "module.MCP.server.tools.DataInquire",
                "class": "inquire",
                "methods": "all",
                "description": "数据查询工具"
            }
        ]
    }

class server_ERROR:
    # 错误码
    ERROR_INVALID_REQUEST = 1001
    ERROR_UNAUTHORIZED = 1002
    ERROR_SERVER_ERROR = 1003

    # 配置常量
    DEFAULT_PORT = 8080
    MAX_CONNECTIONS = 100
    TIMEOUT = 30

    # 服务器状态
    STATUS_RUNNING = "running"
    STATUS_STOPPED = "stopped"
    STATUS_ERROR = "error"