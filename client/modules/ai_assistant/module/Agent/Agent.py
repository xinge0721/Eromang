# -*- coding: utf-8 -*-
"""
简化的对话处理器
使用 MCP 工具实现简单的对话流程
"""
import json
import time
from typing import Callable, Any
import asyncio

import logging
from typing import List, Dict, Any, Generator, Tuple
from enum import Enum
from dataclasses import dataclass
# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class State(Enum):
    """
    状态枚举：定义系统所有可能的状态
    """
    IDLE = 1                      #空闲状态
    MODEL_A_DECIDING = 2          #模型A正在做决策（判断走哪个分支）
    DIRECT_ANSWER = 3             #模型A直接回答问题
    CALL_MCP_TOOL = 4             #调用MCP工具
    COMPLEX_TASK_PLANNING = 5     #复杂任务：生成目标规划
    MODEL_B_JUDGING = 6           #模型B判断是否需要介入
    MODEL_B_EXECUTING = 7         #模型B细化规划并执行TODO
    MODEL_A_SUMMARIZING = 8       #模型A汇总模型B的数据
    ENDING = 9                    #结束状态


class Agent:
    """
    简化的对话处理器
Agent
    流程：
    1. while 循环：对话模型判断是否结束对话
    2. 第一个 for：知识模型生成并执行 TODO 列表（通过 MCP）
    3. 第二个 for：对话模型的 TODO 列表（通过 MCP）
    """

    def __init__(
        self,
        dialogue_callback: Callable[[str], Any],
        knowledge_callback: Callable[[str], Any],

        mcp_client_add_task_callback: Callable[[dict], Any],
        mcp_client_execute_task_callback: Callable[[dict], Any]
    ):
        """
        初始化简化对话处理器
        """
        self.dialogue_callback = dialogue_callback  # 对话模型回调函数
        self.knowledge_callback = knowledge_callback  # 知识模型回调函数


        self.mcp_client_add_task_callback = mcp_client_add_task_callback  # MCP 客户端添加任务回调函数
        self.mcp_client_execute_task_callback = mcp_client_execute_task_callback  # MCP 客户端获取结果回调函数


    async def run(self, user_input: str):
        """
        运行对话循环

        这是一个自主决策的循环系统：
        - 对话模型会不断评估当前状态，决定下一步行动
        - 直到任务完成或用户结束对话
        """
        state = State.IDLE #初始化状态为空闲状态
        while True: #循环直到结束状态
            match state:
              case State.IDLE:
                
                response, tool_calls = self.gather(self.dialogue_callback(user_input)) # 向AI模型提问
                

                if len(response) > 0 :  #说明此刻AI模型已经回答了问题,结束本轮对话
                  break
                if len(tool_calls) > 0 :  #说明此刻AI模型已经调用了工具，解析工具调用，并执行工具
                  tool_results = self.execute(self.merge(tool_calls)) # 合并并执行工具调用，获取工具执行结果

                  # 解析第一个工具的返回结果
                  if len(tool_results) > 0:
                    try:
                      result_data = json.loads(tool_results[0]) # 解析JSON结果
                      task_type = result_data.get("task_type", "") # 获取任务类型
                      # 根据任务类型决定下一个状态
                      match task_type:
                        case "PLAN":
                          state = State.COMPLEX_TASK_PLANNING # 进入复杂任务规划状态
                        case "TODO_LIST":
                          state = State.MODEL_B_EXECUTING # 进入模型B执行TODO状态
                        case _:
                          state = State.DIRECT_ANSWER # 其他情况，直接回答
                    except json.JSONDecodeError:
                      # 如果不是JSON格式（如普通工具调用结果），直接回答
                      state = State.DIRECT_ANSWER
                  

              case State.MODEL_A_DECIDING:
                state = State.DIRECT_ANSWER #模型A直接回答问题
              case State.DIRECT_ANSWER:
                state = State.CALL_MCP_TOOL #调用MCP工具
              case State.CALL_MCP_TOOL:
                state = State.COMPLEX_TASK_PLANNING #复杂任务：生成目标规划
              case State.COMPLEX_TASK_PLANNING:
                state = State.MODEL_B_JUDGING #模型B判断是否需要介入
              case State.MODEL_B_JUDGING:
                state = State.MODEL_B_EXECUTING #模型B细化规划并执行TODO
              case State.MODEL_B_EXECUTING:
                state = State.MODEL_A_SUMMARIZING #模型A汇总模型B的数据
              case State.MODEL_A_SUMMARIZING:
                state = State.ENDING #结束状态


    def gather(response_generator: Generator) -> Tuple[str, List[Dict[str, Any]]]:
        """
        处理AI的流式响应，提取内容和工具调用

        AI的流式响应是一个生成器，每次yield一个字典，包含不同类型的数据：
        - content: AI生成的文本内容
        - tool_calls: AI决定调用的工具信息

        参数:
            response_generator: AI返回的流式响应生成器
        返回:
            (完整响应文本, 工具调用列表) 的元组
        """
        response = ""
        tool_calls = []
        # 遍历流式响应的每个数据块
        for chunk in response_generator:
            # 获取数据块的类型（content/thinking/tool_calls等）
            chunk_type = list(chunk.keys())[0] if chunk else "None"
            content = chunk.get(chunk_type)

            # 处理文本内容和思考过程
            if chunk_type == "content": #文本内容
                response += content
                print(f"[对话模型] 回答: {response}", end='', flush=True)
            elif chunk_type == "thinking": #思考过程（思考无作用，仅打印，不返回）
                print(f"[思考过程] {content}", end='', flush=True)
            elif chunk_type == "tool_calls": #工具调用
                # content是一个列表，取第一个元素
                tool_calls.append(content[0])

        return response, tool_calls
    #  ================================================合并工具调用碎片================================================
    def merge(self,tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并流式返回的工具调用碎片

        在流式响应中，AI模型会将工具调用分成多个碎片返回：
        - 第一个碎片包含完整的工具调用结构（id, type, function.name等），但arguments字段为空
        - 后续碎片只包含arguments的部分内容，需要拼接起来

        参数:
            tool_calls: 从AI流式响应中收集的工具调用碎片列表

        返回:
            合并后的完整工具调用列表，每个工具调用的arguments已完整拼接

        示例:
            输入: [
                  {'index': 0, 'id': 'call_00_5mkYO9b2I0Myf5IGSxbl6o4D', 'function': {'arguments': '', 'name': 'add'}, 'type': 'function'}
                  {'index': 0, 'id': None, 'function': {'arguments': '{', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': '"', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': 'a', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': '"', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': ': ', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': '123', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': ', ', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': '"', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': 'b', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': '"', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': ': ', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': '456', 'name': None}, 'type': None}
                  {'index': 0, 'id': None, 'function': {'arguments': '}', 'name': None}, 'type': None}
            ]
            输出: [
                  {'index': 0,'id': '1', 'function': {'name': 'add', 'arguments': '{"a":123,"b":456}'}, 'type': 'function'}
            ]
        """
        if not tool_calls:
            return []

        merged = {}#合并后的工具调用列表
        
        for tool in tool_calls:#遍历工具调用列表
            index = tool.get("index", 0)#获取工具索引
            
            if index not in merged:#如果索引不在合并后的工具调用列表中
                # 初始化第一个碎片
                merged[index] = {#初始化第一个碎片
                    "index": index,
                    "id": tool.get("id", ""),#工具ID
                    "type": tool.get("type", ""),#工具类型
                    "function": {
                        "name": tool.get("function", {}).get("name", ""),#工具名称
                        "arguments": tool.get("function", {}).get("arguments", "")#工具参数
                    }
                }
            else:#如果索引在合并后的工具调用列表中
                # 合并后续碎片
                merged_tool = merged[index]#获取合并后的工具调用
                
                # 只更新非空值
                if tool.get("id"):
                    merged_tool["id"] = tool["id"]#更新工具ID
                if tool.get("type"):#更新工具类型
                    merged_tool["type"] = tool["type"]
                    
                func = tool.get("function", {})#获取工具函数
                if func.get("name"):
                    merged_tool["function"]["name"] = func["name"]#更新工具名称
                if func.get("arguments"):
                    merged_tool["function"]["arguments"] += func["arguments"]#更新工具参数
        
        return [merged[key] for key in sorted(merged.keys())]#按索引排序并返回列表

    #  ================================================执行工具调用并获取结果================================================
    def execute(self,merged_tools: List[Dict[str, Any]]) -> List[str]:
        """
        批量执行工具调用并获取结果

        将合并后的工具调用提交给MCP客户端执行，并收集所有工具的执行结果。
        MCP（Model Context Protocol）客户端负责实际执行工具调用。

        参数:
            mcp_client: MCP客户端实例，用于执行工具调用
            merged_tools: 合并后的完整工具调用列表

        返回:
            工具执行结果的文本列表

        异常处理:
            如果工具执行出错（result.isError为True），会打印错误信息但不会中断流程
        """
        # 第一步：批量提交所有工具调用任务
        task_ids = [] #创建任务ID列表
        for tool in merged_tools:#遍历合并后的工具调用列表
            task_id = self.mcp_client_add_task_callback(tool)#添加任务
            task_ids.append(task_id)#添加任务ID
            print(f"[OK] 已添加任务: {tool['function']['name']}")#打印添加任务信息

        # 第二步：批量获取所有任务的执行结果
        tool_results = []#创建工具执行结果列表
        for task_id in task_ids:
            result = self.mcp_client_execute_task_callback(task_id)#获取任务执行结果

            # 打印详细的执行结果信息（用于调试）
            print(f"  meta: {result.meta}")#打印元数据
            print(f"  content: {result.content}")#打印内容
            print(f"  structuredContent: {result.structuredContent}")#打印结构化内容
            print(f"  isError: {result.isError}")#打印是否出错

            # 检查是否执行出错
            if result.isError:#如果执行出错
                print(f"[WARNING] 工具执行出错: {result.content}")#打印工具执行出错信息

            # 提取工具结果的文本内容
            if result.content:#如果内容不为空
                tool_results.append(str(result.content))#添加工具执行结果

        return tool_results#返回工具执行结果列表