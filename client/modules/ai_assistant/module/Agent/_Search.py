import os
import sys

# 添加父目录到系统路径
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from Tools.JSONProcessor import JSONProcessor
from Tools.log import logger
from Tools.DataInquire import inquire
from Tools.AllEventsHandler import AllEventsHandler

class _Search:
    """知识模型管理 - 生成TODO计划并执行操作"""

    def __init__(self, knowledge_history, knowledge_callback, printf_callback, watch_directory="./Data"):
        self.knowledge_history = knowledge_history
        self.knowledge_callback = knowledge_callback
        self.printf = printf_callback
        
        # 处理监控目录路径
        if not os.path.isabs(watch_directory):
            # 相对路径：相对于脚本目录
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.watch_directory = os.path.join(base_dir, watch_directory)
        else:
            self.watch_directory = watch_directory
        
        # 初始化JSONProcessor，传递监控目录作为基础目录
        self.json_processor = JSONProcessor(base_directory=self.watch_directory)
        
        # 文件监控
        self.file_monitor = AllEventsHandler()
        
        # 初始化：扫描文件并注入上下文
        self._init_file_context()
    
    def _init_file_context(self):
        """初始化文件上下文"""
        if os.path.exists(self.watch_directory):
            # 1. 扫描文件并注入到知识模型历史
            file_context = self._scan_files()
            self.knowledge_history.insert("system", file_context)
            logger.info(f"✓ 已注入文件上下文到知识模型")
            
            # 2. 启动文件监控
            try:
                self.file_monitor.start_monitoring(self.watch_directory, recursive=True)
                logger.info(f"✓ 已启动文件监控: {self.watch_directory}")
            except Exception as e:
                logger.warning(f"文件监控启动失败: {e}")
        else:
            logger.warning(f"监控目录不存在: {self.watch_directory}")
    
    def _scan_files(self) -> str:
        """扫描文件并格式化为文本"""
        file_catalog = inquire.file_directory(self.watch_directory)
        
        if not file_catalog:
            return f"【工作目录】{self.watch_directory}\n（目录为空或不存在）"
        
        lines = [f"【工作目录文件结构】{self.watch_directory}"]
        
        try:
            for root, dirs, files in file_catalog:
                level = root.replace(self.watch_directory, '').count(os.sep)
                indent = '  ' * level
                
                folder_name = os.path.basename(root) or root
                if level > 0:
                    lines.append(f"{indent}📁 {folder_name}/")
                
                sub_indent = '  ' * (level + 1)
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        ext = os.path.splitext(file)[1]
                        lines.append(f"{sub_indent}- {file} ({ext}, {size} bytes)")
                    except:
                        lines.append(f"{sub_indent}- {file}")
        except Exception as e:
            logger.warning(f"扫描文件失败: {e}")
        
        return '\n'.join(lines)
    
    def _update_file_context(self):
        """检查文件变化并更新上下文"""
        events = self.file_monitor.get_events()
        if events:
            logger.info(f"检测到 {len(events)} 个文件变化")
            # 重新扫描并更新系统上下文
            history = self.knowledge_history.get()
            for i, msg in enumerate(history):
                if msg.get("role") == "system" and "工作目录文件结构" in msg.get("content", ""):
                    # 找到旧的文件上下文，更新它
                    new_context = self._scan_files()
                    self.knowledge_history.replace(i, "system", new_context)
                    logger.info("✓ 已更新文件上下文")
                    break
    
    # ===== 阶段一：生成TODO搜索规划 =====
    def generate_todo_plan(self, message: str):
        """
        使用知识模型生成TODO搜索规划
        
        参数:
            message: 用户输入的消息
            
        返回:
            list: TODO任务列表
        """
        logger.info("\n[阶段一] 使用知识模型生成TODO搜索规划...")
        
        # 检查文件变化并更新上下文
        self._update_file_context()
        
        # 流式调用AI
        planning_response = self._call_ai_stream(message)
        
        # 从响应中提取TODO列表
        history = self.knowledge_history.get()
        todo_list = self.extract_todo_list({"messages": history})
        logger.info(f"✓ 成功生成 {len(todo_list)} 个查询任务")
        
        return todo_list
    
    # ===== 阶段二：执行TODO列表 =====
    def execute_todo_list(self, todo_list: list):
        """
        根据TODO列表逐个执行查询任务
        
        参数:
            todo_list: TODO任务列表
            
        返回:
            list: 查询结果列表
        """
        logger.info("\n[阶段二] 根据TODO列表执行数据查询...")
        
        # 保存系统设定
        system_prompt = self._get_system_prompt()
        
        results = []  # 存储所有查询结果
        context = ""  # 累积的查询数据，供后续查询参考
        
        # 遍历TODO列表，逐个执行任务
        for idx, todo in enumerate(todo_list, 1):
            # 执行单个任务
            result = self._execute_single_todo(todo, idx, len(todo_list), 
                                               system_prompt, context)
            results.append(result)
            
            # 累积上下文（限制长度避免上下文过长）
            if result:
                context += f"\n\n任务{idx}结果：\n{str(result)[:500]}..."
        
        return results
        
    # ===== 提取TODO列表 =====
    def extract_todo_list(self, message: dict):
        """
        从AI响应消息中提取TODO任务列表
        
        参数:
            message (dict): 包含messages字段的字典，格式为 {"messages": [...]}
        
        返回:
            list: TODO任务列表，每个任务是一个字典
        """
        # 获取最后一条AI回复
        msgs = message.get("messages", [])
        if not msgs or msgs[-1].get('role') != "assistant":
            logger.warning("没有有效的AI回复")
            return []
        
        # 提取JSON
        content = msgs[-1].get('content', '')
        json_data, error = self.json_processor.extract_json(content)
        
        if error or not json_data:
            logger.error(f"JSON提取失败: {error}")
            return []
        
        # 加载TODO列表
        todo_list = self.json_processor.load_json(json_data)
        
        if not isinstance(todo_list, list):
            logger.error(f"TODO列表格式错误")
            return []
        
        logger.debug(f"成功提取 {len(todo_list)} 个TODO任务")
        return todo_list
    # ===== 工具方法 =====
    def _execute_single_todo(self, todo: dict, idx: int, total: int,
                            system_prompt: dict, context: str):
        """执行单个TODO任务"""
        # 解析任务信息
        task = self._parse_todo(todo)
        logger.info(f"\n--- 任务 {idx}/{total}: {task['operation']} -> {task['target']} ---")
        
        # 准备历史上下文
        self._prepare_history(system_prompt, context)
        
        # 生成JSON指令
        instruction = self._build_instruction(task)
        json_response = self._call_ai_stream(instruction)
        
        # 执行JSON
        return self._execute_json_response(json_response, task['operation'])
    # ===== 解析TODO任务 =====
    def _parse_todo(self, todo: dict) -> dict:
        """解析TODO任务（兼容中英文）"""
        return {
            'task_id': todo.get('任务ID') or todo.get('task_id'),
            'operation': todo.get('操作类型') or todo.get('operation_type'),
            'target': todo.get('目标对象') or todo.get('target'),
            'params': todo.get('参数') or todo.get('params') or {},
            'purpose': todo.get('目的') or todo.get('purpose')
        }
    # ===== 获取系统提示词 =====
    def _get_system_prompt(self) -> dict:
        """获取系统提示词"""
        full_history = self.knowledge_history.get()
        if full_history and full_history[0].get("role") == "system":
            logger.info("✓ 已保存系统角色设定")
            return full_history[0]
        return None
    # ===== 准备历史记录 =====
    def _prepare_history(self, system_prompt: dict, context: str):
        """准备历史记录"""
        # 清空历史记录
        self.knowledge_history.clear()
        
        # 重新插入系统设定（如果存在）
        if system_prompt:
            self.knowledge_history.insert(
                system_prompt["role"], 
                system_prompt["content"]
            )
        
        # 插入之前累积的查询数据作为上下文（如果有）
        if context:
            context_message = f"已查询到的数据：\n{context}\n\n请基于这些数据继续执行下一个查询任务。"
            self.knowledge_history.insert("system", context_message)
    # ===== 构建任务指令 =====
    def _build_instruction(self, task: dict) -> str:
        """构建任务指令"""
        return f"""请根据以下TODO任务生成相应的JSON指令：

        任务信息：
        - 任务ID: {task['task_id']}
        - 操作类型: {task['operation']}
        - 目标对象: {task['target']}
        - 参数: {task['params']}
        - 目的: {task['purpose']}

        ⚠️ 根据操作类型输出对应格式的JSON：
        - 如果是"创建文件"：输出"文件编辑"类型JSON，使用"创建文件"字段
        - 如果是查询操作：输出"数据查询"类型JSON
        - 如果是其他文件操作：输出"文件编辑"类型JSON

        请输出完整的JSON指令。"""
    # ===== 流式调用AI =====
    def _call_ai_stream(self, message: str) -> str:
        """流式调用AI"""
        response = ""
        for chunk in self.knowledge_callback(message):
            response += chunk
            self.printf(chunk)
        print()
        return response
    # ===== 执行JSON响应 =====
    def _execute_json_response(self, json_response: str, operation: str):
        """执行JSON响应"""
        json_data, error = self.json_processor.extract_json(json_response)
        
        if json_data and not error:
            action_type = json_data.get('type') or json_data.get('类型')
            logger.info(f"✓ 生成JSON成功，类型: {action_type}")
            
            try:
                result = self.json_processor.execute_json(json_data)
                if result:
                    logger.info(f"✓ 任务执行成功")
                    return result
                else:
                    logger.warning("任务未返回结果")
                    return {"status": "success", "operation": operation}
            except Exception as e:
                logger.error(f"任务执行失败: {e}")
                import traceback
                traceback.print_exc()
                return None
        else:
            logger.error(f"无法提取JSON: {error}")
            return None
    
    def __del__(self):
        """析构函数：停止文件监控"""
        if hasattr(self, 'file_monitor'):
            try:
                self.file_monitor.stop_monitoring()
                logger.debug("✓ 已停止文件监控")
            except:
                pass
