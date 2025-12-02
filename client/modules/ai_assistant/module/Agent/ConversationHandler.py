"""
对话处理模块

该模块提供完整的对话流程编排，协调知识模型和对话模型完成用户请求。

主要功能：
    - TODO规划：使用知识模型生成查询计划
    - 数据查询：根据TODO列表执行数据检索
    - 对话生成：使用对话模型生成最终回答
    - 文件监控：自动监控数据目录变化

典型用法：
    >>> handler = ConversationHandler(
    ...     knowledge_callback=factory.knowledge_callback,
    ...     dialogue_callback=factory.dialogue_callback,
    ...     knowledge_history=factory.knowledge_ai_client._history,
    ...     dialogue_history=factory.dialogue_ai_client._history,
    ...     default_output_file="output.txt"
    ... )
    >>> result = handler.send_message("查询无人机状态")
"""

import json
from typing import Callable, Dict, Any, Optional

from tools.log import logger
from ._Search import _Search
from ._Dialogue import _Dialogue


class ConversationHandler:
    """
    对话业务处理类

    负责完整的对话流程：TODO规划 -> 数据查询 -> 对话生成

    该类协调知识模型和对话模型，实现三阶段对话流程：
    1. 阶段一：使用知识模型生成TODO搜索规划
    2. 阶段二：根据TODO列表执行数据查询
    3. 阶段三：使用对话模型生成最终回答

    属性:
        knowledge_callback: 知识模型回调函数
        dialogue_callback: 对话模型回调函数
        knowledge_history: 知识模型历史管理器
        dialogue_history: 对话模型历史管理器
        default_output_file: 默认输出文件路径
        search: 知识检索处理器（_Search实例）
        dialogue: 对话生成处理器（_Dialogue实例）
    """

    def __init__(
        self,
        knowledge_callback: Callable[[str], Any],
        dialogue_callback: Callable[[str], Any],
        knowledge_history: Any,
        dialogue_history: Any,
        default_output_file: Optional[str],
        watch_directory: str = "./Data"
    ) -> None:
        """
        初始化对话处理器
        
        参数:
            knowledge_callback: 知识模型回调函数，接受message，返回生成器
            dialogue_callback: 对话模型回调函数，接受message，返回生成器
            knowledge_history: 知识模型的历史管理器
            dialogue_history: 对话模型的历史管理器
            default_output_file: 默认输出文件路径
            watch_directory: 需要监控的目录路径（默认 ./Data）
        """
        self.knowledge_callback = knowledge_callback
        self.dialogue_callback = dialogue_callback
        self.knowledge_history = knowledge_history
        self.dialogue_history = dialogue_history
        self.default_output_file = default_output_file
        
        # 在内部创建 search 和 dialogue 实例
        self.search = _Search(
            knowledge_history=knowledge_history,
            knowledge_callback=knowledge_callback,
            printf_callback=self.printf,
            watch_directory=watch_directory
        )
        self.dialogue = _Dialogue(
            dialogue_callback=dialogue_callback,
            dialogue_history=dialogue_history,
            default_output_file=default_output_file,
            printf_callback=self.printf
        )
    
    def printf(self, data, msg_type="info", flush=True, add_prefix=False):
        """
        统一的输出接口，后续可改为向前端发送数据
        
        参数:
            data: 要输出的数据（字符串、字典、列表等）
            msg_type: 消息类型 ("info", "warning", "error", "success")
            flush: 是否立即刷新输出
            add_prefix: 是否添加消息类型前缀（流式输出时应设为False）
        """
        # 消息类型前缀
        prefix_map = {
            "info": "[信息]",
            "warning": "[警告]",
            "error": "[错误]",
            "success": "[成功]"
        }
        
        # 格式化输出
        if isinstance(data, (dict, list)):
            formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
            if add_prefix:
                output = f"{prefix_map.get(msg_type, '[信息]')} {formatted_data}"
            else:
                output = formatted_data
        else:
            if add_prefix:
                output = f"{prefix_map.get(msg_type, '[信息]')} {data}"
            else:
                output = str(data)
        
        # 当前使用print，后续替换为前端发送函数
        print(output, flush=flush, end='')
        
        # TODO: 后续在此处添加前端发送逻辑
        # 例如: self._send_to_frontend(output, msg_type)
    
    def send_message(self, message):
        """
        完整的对话流程：
        1. 使用知识模型生成TODO列表（搜索规划）- 委托给 _Search
        2. 遍历TODO列表，逐个查询数据 - 委托给 _Search
        3. 使用对话模型生成最终回答 - 委托给 _Dialogue
        """
        # ===== 阶段一：生成TODO搜索规划 =====
        todo_list = self.search.generate_todo_plan(message)
        
        # ===== 阶段二：执行TODO列表 =====
        query_results = self.search.execute_todo_list(todo_list)
        
        # ===== 阶段四：使用对话模型生成最终回答 =====
        dialogue_result = self.dialogue.generate_response(message, query_results)
        
        return {
            "query_results": query_results,
            "dialogue_response": dialogue_result.get("dialogue_response"),
            "output_file": dialogue_result.get("output_file")
        }

