# -*- coding: utf-8 -*-
"""
简化的对话处理器
使用 MCP 工具实现简单的对话流程
"""
import json
import time
from typing import Callable, Any

class SimpleConversationHandler:
    """
    简化的对话处理器

    流程：
    1. while 循环：对话模型判断是否结束对话
    2. 第一个 for：知识模型生成并执行 TODO 列表（通过 MCP）
    3. 第二个 for：对话模型的 TODO 列表（通过 MCP）
    """

    def __init__(
        self,
        dialogue_callback: Callable[[str], Any],
        knowledge_callback: Callable[[str], Any],
        mcp_client: Any,
        dialogue_history: Any,
        knowledge_history: Any
    ):
        """
        初始化简化对话处理器

        参数:
            dialogue_callback: 对话模型回调函数
            knowledge_callback: 知识模型回调函数
            mcp_client: MCP 客户端实例
            dialogue_history: 对话模型历史管理器
            knowledge_history: 知识模型历史管理器
        """
        self.dialogue_callback = dialogue_callback
        self.knowledge_callback = knowledge_callback
        self.mcp_client = mcp_client
        self.dialogue_history = dialogue_history
        self.knowledge_history = knowledge_history

        # 等待 MCP 初始化
        print("等待 MCP 客户端初始化...")
        while not self.mcp_client.get_initialized():
            time.sleep(0.1)
        print("✓ MCP 客户端已就绪")

        # 获取工具列表并注入到知识模型
        tools = self.mcp_client.list_tools()
        tool_descriptions = self._format_tool_list(tools)
        self.knowledge_history.insert("system", f"可用的 MCP 工具列表：\n{tool_descriptions}")
        print(f"✓ 已注入 {len(tools)} 个 MCP 工具到知识模型")

    def _format_tool_list(self, tools):
        """格式化工具列表为可读文本"""
        lines = []
        for tool in tools:
            lines.append(f"- {tool.name}: {tool.description if hasattr(tool, 'description') else '无描述'}")
        return "\n".join(lines)

    def run(self):
        """运行对话循环"""
        print("\n" + "=" * 80)
        print("AI 助手已启动（输入 'exit' 或 'quit' 退出）")
        print("=" * 80 + "\n")

        while True:
            # 获取用户输入
            user_input = input("用户: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', '退出']:
                print("\n再见！")
                break

            # 处理消息
            try:
                self.send_message(user_input)
            except KeyboardInterrupt:
                print("\n\n对话被中断")
                break
            except Exception as e:
                print(f"\n✗ 错误: {e}")
                import traceback
                traceback.print_exc()

    def send_message(self, message: str):
        """
        处理单条消息的完整流程

        流程：
        1. 对话模型判断是否需要知识模型
        2. 如果需要，知识模型生成 TODO 列表（通过 MCP 的 create_task_list）
        3. 执行知识模型的 TODO（第一个 for 循环）
        4. 对话模型生成回答（可能也有 TODO，第二个 for 循环）
        """
        print("\n" + "-" * 80)

        # ===== 步骤 1: 对话模型判断是否需要知识模型 =====
        print("\n[步骤 1] 对话模型分析问题...")

        # 构造判断 prompt
        judge_prompt = f"""用户问题：{message}

请判断这个问题是否需要知识模型来收集数据。

如果需要知识模型（例如需要读取文件、查询数据库、搜索信息等），请回复：
{{"need_knowledge": true, "reason": "需要的原因"}}

如果不需要知识模型（例如简单的对话、解释概念等），请回复：
{{"need_knowledge": false, "reason": "不需要的原因"}}

只输出 JSON，不要其他内容。"""

        # 调用对话模型
        response = ""
        for chunk in self.dialogue_callback(judge_prompt):
            response += chunk

        # 解析判断结果
        try:
            # 提取 JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                judge_result = json.loads(json_str)
                need_knowledge = judge_result.get("need_knowledge", False)
                reason = judge_result.get("reason", "")
                print(f"✓ 判断结果: {'需要' if need_knowledge else '不需要'}知识模型")
                print(f"  原因: {reason}")
            else:
                # 如果没有找到 JSON，默认不需要知识模型
                need_knowledge = False
                print("✓ 判断结果: 不需要知识模型（默认）")
        except Exception as e:
            print(f"  警告: 解析判断结果失败，默认不需要知识模型: {e}")
            need_knowledge = False

        # 清理对话历史中的判断消息（避免污染历史）
        try:
            history = self.dialogue_history.get()
            if len(history) >= 2:
                # 删除最后两条（用户的判断请求和助手的判断回复）
                self.dialogue_history.delete(len(history) - 1)
                self.dialogue_history.delete(len(history) - 2)
        except:
            pass

        knowledge_results = []

        # ===== 步骤 2: 如果需要知识模型，生成并执行 TODO =====
        if need_knowledge:
            print("\n[步骤 2] 知识模型生成 TODO 列表...")

            # 构造 TODO 生成 prompt
            todo_prompt = f"""用户问题：{message}

请使用 MCP 工具 create_task_list 来创建任务列表。

任务格式：
{{
  "tasks": [
    {{
      "task_id": "task_001",
      "description": "任务描述",
      "tool": "MCP工具名称",
      "arguments": {{"参数名": "参数值"}},
      "priority": 1
    }}
  ]
}}

请直接输出调用 create_task_list 工具的 JSON 格式，不要其他内容。"""

            # 调用知识模型
            response = ""
            for chunk in self.knowledge_callback(todo_prompt):
                response += chunk
                print(chunk, end='', flush=True)
            print()

            # 解析并调用 create_task_list
            try:
                # 提取 JSON
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    task_data = json.loads(json_str)

                    # 调用 MCP 创建任务列表
                    print("\n[步骤 3] 创建任务列表...")
                    task_id = self.mcp_client.add({
                        "name": "create_task_list",
                        "arguments": task_data
                    })
                    result = self.mcp_client.get_result(task_id, timeout=10)

                    # 解析 list_id
                    result_text = result.content[0].text if hasattr(result, 'content') else str(result)
                    print(f"✓ {result_text}")

                    result_dict = json.loads(result_text)
                    list_id = result_dict.get("list_id")

                    if list_id:
                        # ===== 第一个 for 循环：执行知识模型的 TODO =====
                        print("\n[步骤 4] 执行任务列表...")

                        while True:
                            # 获取下一个任务
                            task_id = self.mcp_client.add({
                                "name": "get_next_task",
                                "arguments": {"list_id": list_id}
                            })
                            next_task_result = self.mcp_client.get_result(task_id, timeout=10)
                            next_task_text = next_task_result.content[0].text if hasattr(next_task_result, 'content') else str(next_task_result)
                            next_task_data = json.loads(next_task_text)

                            if not next_task_data.get("has_next"):
                                print("✓ 所有任务已完成")
                                break

                            task = next_task_data.get("task")
                            task_id_str = task.get("task_id")
                            tool_name = task.get("tool")
                            arguments = task.get("arguments", {})

                            print(f"\n  执行任务 {task_id_str}: {task.get('description')}")
                            print(f"    工具: {tool_name}")

                            # 更新任务状态为 running
                            self.mcp_client.add({
                                "name": "update_task_status",
                                "arguments": {
                                    "list_id": list_id,
                                    "task_id": task_id_str,
                                    "status": "running"
                                }
                            })

                            # 执行工具
                            try:
                                tool_task_id = self.mcp_client.add({
                                    "name": tool_name,
                                    "arguments": arguments
                                })
                                tool_result = self.mcp_client.get_result(tool_task_id, timeout=10)
                                tool_result_text = tool_result.content[0].text if hasattr(tool_result, 'content') else str(tool_result)

                                print(f"    ✓ 结果: {tool_result_text[:200]}...")

                                # 更新任务状态为 completed
                                self.mcp_client.add({
                                    "name": "update_task_status",
                                    "arguments": {
                                        "list_id": list_id,
                                        "task_id": task_id_str,
                                        "status": "completed",
                                        "result": tool_result_text
                                    }
                                })

                                knowledge_results.append({
                                    "task_id": task_id_str,
                                    "description": task.get("description"),
                                    "result": tool_result_text
                                })

                            except Exception as e:
                                print(f"    ✗ 失败: {e}")
                                # 更新任务状态为 failed
                                self.mcp_client.add({
                                    "name": "update_task_status",
                                    "arguments": {
                                        "list_id": list_id,
                                        "task_id": task_id_str,
                                        "status": "failed",
                                        "error": str(e)
                                    }
                                })

                        # 获取任务摘要
                        task_id = self.mcp_client.add({
                            "name": "get_task_summary",
                            "arguments": {"list_id": list_id}
                        })
                        summary_result = self.mcp_client.get_result(task_id, timeout=10)
                        summary_text = summary_result.content[0].text if hasattr(summary_result, 'content') else str(summary_result)
                        print(f"\n✓ 任务摘要: {summary_text}")

            except Exception as e:
                print(f"✗ 处理 TODO 列表失败: {e}")
                import traceback
                traceback.print_exc()

        # ===== 步骤 5: 对话模型生成最终回答 =====
        print("\n[步骤 5] 对话模型生成回答...")

        # 将知识结果注入到对话历史
        if knowledge_results:
            results_summary = "\n\n".join([
                f"任务 {r['task_id']}: {r['description']}\n结果: {r['result'][:500]}"
                for r in knowledge_results
            ])
            self.dialogue_history.insert("system", f"知识模型收集的数据：\n{results_summary}")

        # 调用对话模型生成最终回答
        print("\nAI: ", end='', flush=True)
        response = ""
        for chunk in self.dialogue_callback(message):
            response += chunk
            print(chunk, end='', flush=True)
        print("\n")

        # 清理临时注入的知识结果
        if knowledge_results:
            try:
                history = self.dialogue_history.get()
                for i in range(len(history) - 1, -1, -1):
                    if history[i].get("role") == "system" and "知识模型收集的数据" in history[i].get("content", ""):
                        self.dialogue_history.delete(i)
                        break
            except:
                pass

        print("-" * 80)
