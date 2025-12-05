#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试数学工具调用
"""

import os
import sys

# 添加父目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from module.AICore.AIManager import AIFactory
from module.MCP.client.MCPClient import MCPClient
import time
import json


def test_math_tools():
    """测试数学工具调用"""
    #print("\n" + "=" * 80)
    #print("测试：数学工具调用")
    #print("=" * 80)

    # 初始化AI
    factory = AIFactory()
    factory.connect(
        dialogue_vendor="deepseek",
        dialogue_model_name="deepseek-reasoner",
        knowledge_vendor="deepseek",
        knowledge_model_name="deepseek-reasoner"
    )

    # 启动MCP客户端
    mcp_client = MCPClient()
    mcp_client.start()

    # 等待MCP初始化
    #print("\n等待MCP初始化...")
    while not mcp_client.get_initialized():
        time.sleep(0.1)

    # 获取工具列表
    tools = mcp_client.list_tools()
    #print(f"\n✓ 已获取 {len(tools)} 个工具")
    # for tool in tools:
        #print(f"  - {tool['function']['name']}: {tool['function'].get('description', '无描述')}")

    # 添加工具到对话模型
    factory.add_tools(tools, "dialogue")

    # 测试数学计算
    message = "帮我计算 123 + 456 的结果"
    #print(f"\n用户输入: {message}")
    #print("\nAI回复: ", end='', flush=True)

    response = ""
    tool_calls = []
    for chunk in factory.dialogue_callback(message):
        type = list(chunk.keys())[0] if chunk else "None"
        content = chunk.get(type)
        if type in ["content", "thinking"]:
            response += content
            print(content, end='', flush=True)
        elif type == "tool_calls":
            tool_calls.append(content[0])
    print("\n\n" + "-" * 80)
    print(f"\n工具调用: {tool_calls}")

    merged_tools = []
    # 如果有工具调用，执行工具
    if tool_calls:
        # 第一个元素是完整结构（但arguments为空），后续元素是arguments的碎片
        # 取第一个完整的工具调用结构
        base_tool = tool_calls[0]
        print(f"\n第一个工具调用: {base_tool}")
        # 拼接后续的arguments碎片
        arguments_str = ""
        for i in range(1, len(tool_calls)):
            fragment = tool_calls[i]
            print(f"\n第{i}个工具调用: {fragment}")
            if fragment.get('function', {}).get('arguments'):
                arguments_str += fragment['function']['arguments']

        # 更新第一个工具调用的arguments
        if arguments_str:
            base_tool['function']['arguments'] = arguments_str

        merged_tools.append(base_tool)
            #print(f"\n合并后的工具调用: {merged_tools}")

        # 批量添加任务
        task_ids = []
        for tool in merged_tools:
            task_id = mcp_client.add(tool)
            task_ids.append(task_id)
            print(f"✓ 已添加任务: {tool['function']['name']}")

        # 批量获取结果
        #print("\n执行结果:")
        for task_id in task_ids:
            result = mcp_client.get_result(task_id)
            print(f"  结果: {result}")
    else:
        print("未检测到工具调用")

    # 清理
    mcp_client.close()

    #print("\n" + "=" * 80)
    #print("测试完成")
    #print("=" * 80)

    return response


if __name__ == "__main__":
    try:
        test_math_tools()


    except Exception as e:
        #print(f"\n\n测试失败: {e}")
        import traceback
        traceback.print_exc()
