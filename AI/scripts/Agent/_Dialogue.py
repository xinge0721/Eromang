import os
import sys

# 添加父目录到系统路径
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from Tools.log import logger
from Tools.JSONProcessor import JSONProcessor


class _Dialogue:
    """
    对话模型处理类
    负责使用对话模型生成最终回答
    """
    
    def __init__(self, dialogue_callback, dialogue_history, default_output_file, printf_callback):
        """
        初始化对话处理器
        
        参数:
            dialogue_callback: 对话模型回调函数，接受message，返回生成器
            dialogue_history: 对话模型的历史管理器
            default_output_file: 默认输出文件路径
            printf_callback: 打印回调函数
        """
        self.dialogue_callback = dialogue_callback
        self.dialogue_history = dialogue_history
        self.default_output_file = default_output_file
        self.printf = printf_callback
        self.json_processor = JSONProcessor(default_filepath=default_output_file)
    
    def generate_response(self, message: str, query_results: list):
        """
        使用对话模型生成最终回答
        
        参数:
            message: 用户原始消息
            query_results: 查询结果列表
            
        返回:
            dict: 包含 dialogue_response 和 output_file 的字典
        """
        # ===== 检查对话模型是否可用 =====
        if not self.dialogue_callback:
            logger.warning("对话模型未连接，跳过对话生成")
            return {"dialogue_response": None, "output_file": None}
        
        if not query_results or all(r is None for r in query_results):
            logger.warning("查询结果为空，仍然继续对话")
        
        # ===== 将查询结果插入对话历史 =====
        search_results_summary = "\n\n".join([str(r) for r in query_results if r])
        if search_results_summary:
            self.dialogue_history.insert("system", f"数据查询结果：\n{search_results_summary}")

        # ===== 注入全量重写提醒 =====
        rewrite_reminder = (
            "⚠️ 重要提醒：\n"
            "1. 你即将生成的代码会覆盖整个文件（从第1行开始）\n"
            "2. 必须回顾对话历史，总结用户之前要求的所有功能\n"
            "3. 然后融合当前新需求，从头输出完整程序\n"
            "4. 不能只根据最新问题来写，否则会丢失之前的功能！\n"
            "5. 从 FUNCTION_BLOCK 第1行开始，输出完整结构"
        )
        
        # ===== 使用对话模型生成回答 =====
        logger.info("\n[阶段四] 使用对话模型生成最终回答...")
        
        # 注入全量重写提醒
        self.dialogue_history.insert("system", rewrite_reminder)
        
        dialogue_response = ""
        for chunk in self.dialogue_callback(message):
            dialogue_response += chunk
            self.printf(chunk)  # AI流式输出（不加前缀）
        print()  # 换行
        
        # ===== 删除临时注入的重写提醒 =====
        try:
            history = self.dialogue_history.get()
            # 找到并删除刚刚注入的重写提醒
            for i in range(len(history) - 1, -1, -1):
                if history[i].get("role") == "system" and "全量重写策略" in history[i].get("content", ""):
                    self.dialogue_history.delete(i)
                    break
        except Exception as e:
            logger.warning(f"清理重写提醒失败: {e}")
        
        # ===== 执行JSON指令（如果有） =====
        extract_json, error = self.json_processor.extract_json(dialogue_response)
        output_file = None
        
        if extract_json:
            action_type = extract_json.get('type') or extract_json.get('类型')
            self.json_processor.execute_json(extract_json)
            
            # 如果是文件编辑操作，简化历史记录
            if action_type in ['file_edit', '文件编辑']:
                # 尝试从JSON中提取实际操作的文件路径
                params = extract_json.get('params') or extract_json.get('参数') or {}
                add_list = params.get('add') or params.get('新增') or []
                create_list = params.get('create_file') or params.get('创建文件') or []
                
                if add_list and (add_list[0].get('filepath') or add_list[0].get('文件路径')):
                    output_file = add_list[0].get('filepath') or add_list[0].get('文件路径')
                elif create_list and (create_list[0].get('filepath') or create_list[0].get('文件路径')):
                    output_file = create_list[0].get('filepath') or create_list[0].get('文件路径')
                elif self.default_output_file:
                    output_file = self.default_output_file
                else:
                    output_file = "指定的文件路径"
                
                print(f"\n[成功] ✓ 文件操作已完成: {output_file}")
                if output_file.endswith('.st'):
                    print(f"[提示] ✓ 您可以在 TIA Portal 中导入该 PLC 程序文件")
                
                # 简化历史记录：删除冗长的JSON，只保留简短提示
                try:
                    history = self.dialogue_history.get()
                    last_index = len(history) - 1
                    if last_index >= 0 and history[last_index].get("role") == "assistant":
                        # 只保留简短的完成提示，删除JSON和思考过程
                        simple_response = "✓ 已完成代码修改并保存到文件"
                        self.dialogue_history.replace(
                            index=last_index,
                            role="assistant",
                            content=simple_response
                        )
                        logger.info("✓ 已简化历史记录（下次对话将读取实际文件）")
                except Exception as e:
                    logger.warning(f"简化历史记录失败: {e}")
        
        return {
            "dialogue_response": dialogue_response,
            "output_file": output_file
        }

