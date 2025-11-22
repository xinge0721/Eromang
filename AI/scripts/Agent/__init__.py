"""
Agent 模块

该模块提供了 AI 管理和对话处理的核心功能。

主要类：
    - AIFactory: AI 工厂类，用于创建和管理 AI 客户端
    - ConversationHandler: 对话处理类，负责完整的对话流程
    - _Search: 知识模型处理类（私有）
    - _Dialogue: 对话模型处理类（私有）
"""

from .AIManager import AIFactory
from .ConversationHandler import ConversationHandler

# 定义模块导出的公共接口
__all__ = [
    'AIFactory',
    'ConversationHandler'
]

# 模块版本
__version__ = '1.0.0'

