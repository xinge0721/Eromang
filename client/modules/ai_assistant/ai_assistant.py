#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话接口主程序
使用 AIManager.py 中的 AIFactory 进行双AI协同对话
"""

import os
import sys
import json

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from module.Agent.AIManager import AIFactory
from module.Agent.ConversationHandler import ConversationHandler

class AIAssistant:
    """
    AI助手类
    """
    def __init__(self):
        self.factory = AIFactory()
        self.handler = ConversationHandler(
            knowledge_callback=self.factory.knowledge_callback,
            dialogue_callback=self.factory.dialogue_callback,
            knowledge_history=self.factory.knowledge_ai_client._history,
            dialogue_history=self.factory.dialogue_ai_client._history,
        )
    


if __name__ == "__main__":
    ai_assistant = AIAssistant()

