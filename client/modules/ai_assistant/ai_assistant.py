#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话接口主程序
使用 AIManager.py 中的 AIFactory 进行双AI协同对话
基于 MCP 工具的简化架构
"""

import os
import sys
import json

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from module.AICore.AIManager import AIFactory
from module.Agent.SimpleConversationHandler import SimpleConversationHandler
from module.MCP.client.MCPClient import MCPClient

class AIAssistant:
    """
    AI助手类

    架构说明：
    - 双AI协同：对话模型负责规划和回答，知识模型负责数据收集
    - MCP工具：所有操作通过标准化的MCP工具完成
    - 简化流程：1个while循环 + 2个for循环实现完整对话
    """
    def __init__(self):
        print("\n" + "=" * 80)
        print("AI 助手初始化中...")
        print("=" * 80)

        # 初始化 AI 工厂
        print("\n[1/3] 初始化 AI 模型...")
        self.factory = AIFactory()

        self.factory.connect(
            dialogue_vendor="deepseek",
            dialogue_model_name="deepseek-reasoner",
            knowledge_vendor="deepseek",
            knowledge_model_name="deepseek-reasoner"
        )
        print("✓ AI 模型连接成功")

        # 创建并启动 MCP 客户端
        print("\n[2/3] 启动 MCP 服务...")
        self.mcp_client = MCPClient()
        self.mcp_client.start()
        print("✓ MCP 服务启动成功")

        # 创建对话处理器
        print("\n[3/3] 初始化对话处理器...")
        self.handler = SimpleConversationHandler(
            dialogue_callback=self.factory.dialogue_callback,
            knowledge_callback=self.factory.knowledge_callback,
            mcp_client=self.mcp_client,
            dialogue_history=self.factory.dialogue_ai_client._history,
            knowledge_history=self.factory.knowledge_ai_client._history
        )
        print("✓ 对话处理器初始化完成")

        print("\n" + "=" * 80)
        print("初始化完成！")
        print("=" * 80)

    def run(self):
        """运行 AI 助手"""
        try:
            self.handler.run()
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
        except Exception as e:
            print(f"\n✗ 运行时错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        """清理资源"""
        print("\n正在清理资源...")
        try:
            if hasattr(self, 'mcp_client'):
                self.mcp_client.close()
                print("✓ MCP 客户端已关闭")
        except Exception as e:
            print(f"清理资源时出错: {e}")

if __name__ == "__main__":
    try:
        ai_assistant = AIAssistant()
        ai_assistant.run()
    except KeyboardInterrupt:
        print("\n\n程序启动被中断")
    except Exception as e:
        print(f"\n✗ 启动失败: {e}")
        import traceback
        traceback.print_exc()  

