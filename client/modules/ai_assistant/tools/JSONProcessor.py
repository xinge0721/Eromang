# -*- coding: utf-8 -*-
import os
import sys
from pydantic import BaseModel, ValidationError, field_validator
from typing import List, Optional
import sqlite3
from .FileEditor import FileEditor
from .DatabaseEditor import DatabaseEditor
from .DataInquire import inquire
from .log import logger



# 设置控制台输出编码为UTF-8（解决Windows中文乱码问题）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# ================ JSONProcessor类 ================

class JSONProcessor:
    # ================ 初始化 ================
    def __init__(self, default_filepath: str = None, base_directory: str = None):
        # 工具类直接引用，不需要实例化（全部为静态方法）
        self.file_line_editor = FileEditor
        self.database_editor = DatabaseEditor
        self.data_inquire = inquire
        self.default_filepath = default_filepath  # 默认文件路径，用于file_edit操作
        self.base_directory = base_directory  # 基础目录，用于解析相对路径
    
    def _resolve_filepath(self, filepath: str) -> str:
        """
        解析文件路径：如果是相对路径且设置了base_directory，则转换为完整路径
        
        参数:
            filepath (str): 原始文件路径
            
        返回:
            str: 解析后的文件路径
        """
        if not filepath:
            return filepath
        
        # 如果是绝对路径，直接返回
        if os.path.isabs(filepath):
            return filepath
        
        # 如果设置了base_directory且是相对路径，拼接路径
        if self.base_directory:
            resolved_path = os.path.join(self.base_directory, filepath)
            # 如果拼接后的路径存在，使用它；否则尝试原始路径
            if os.path.exists(resolved_path):
                return resolved_path
        
        # 默认返回原始路径
        return filepath

    # ================ 提取字符串中的JSON数据 ================
    def extract_json(self, text):
        """
        提取字符串中的JSON对象，解析并验证格式。
        
        返回:
            (json_dict, None) - 成功，返回解析后的字典对象和None
            (None, error_msg) - 失败，返回None和错误信息
        """
        import json
        
        # 找第一个左花括号
        start = text.find('{')
        if start == -1:
            return None, "未找到JSON数据（缺少左花括号）"
        
        # 找最后一个右花括号
        end = text.rfind('}')
        if end == -1 or end < start:
            return None, "未找到JSON数据（缺少右花括号）"
        
        # 提取JSON字符串
        json_str = text[start:end + 1]
        
        # 仅验证JSON语法是否合法
        try:
            json_data = json.loads(json_str)
            return json_data, None
        except json.JSONDecodeError as e:
            return None, f"JSON格式错误: {str(e)}"


    # 根据JSON数据执行对应的操作
    def execute_json(self, json_data):
        """
        根据传入的json_data字典执行具体操作。
        支持中文和英文字段名。

        参数:
            json_data (dict): 包含操作类型和参数的JSON数据。
                英文格式:
                    {
                        "type": "file_edit",
                        "params": {
                            "add": [{"line": 1, "content": "content1"}],
                            "modify": [{"line": 2, "content": "content2"}],
                            "delete": [{"line": 3}]
                        }
                        or
                        "type": "database_edit",
                        "params": {
                            "add": [{"database": "database1", "data_id": "dataID1", "content": "content1"}],
                            "modify": [{"database": "database2", "data_id": "dataID2", "content": "content2"}],
                            "delete": [{"database": "database3", "data_id": "dataID3"}]
                        }
                    }
                中文格式:
                    {
                        "类型": "文件编辑",
                        "参数": {
                            "新增": [{"文件路径": "文件路径1", "行": 1, "内容": "内容1"}],
                            "修改": [{"文件路径": "文件路径2", "行": 2, "内容": "内容2"}],
                            "删除": [{"文件路径": "文件路径3", "行": 3}]
                            “创建文件”: [{"文件路径": "文件路径4"}]
                            “删除文件”: [{"文件路径": "文件路径5"}]
                        }
                    }
                    或：
                    {
                        "类型": "数据库编辑",
                        "参数": {
                            "插入数据": [{"数据库": "数据库1", "数据表": "数据表1", "数据ID": "数据ID1", "内容": "内容1"}],
                            "修改数据": [{"数据库": "数据库2", "数据表": "数据表2", "数据ID": "数据ID2", "内容": "内容2"}],
                            "删除数据": [{"数据库": "数据库3", "数据表": "数据表3", "数据ID": "数据ID3"}]
                            “创建数据库”: [{"数据库": "数据库4"}]
                            “删除数据库”: [{"数据库": "数据库5"}]
                            “创建数据表”: [{"数据库": "数据库4","数据表": "数据表4"}]
                            “删除数据表”: [{"数据库": "数据库5","数据表": "数据表5"}]
                        }
                    }
                    或：
                    {
                        "类型": "数据查询",
                        "参数": {
                            "查询所有数据表": [{"数据库": "数据库1"}],
                            "查询表中所有数据": [{"数据库": "数据库1", "数据表": "数据表1"}],
                            "检查数据是否存在": [{"数据库": "数据库1", "数据表": "数据表1", "数据ID": "数据ID1"}],
                            "统计数据数量": [{"数据库": "数据库1", "数据表": "数据表1"}],
                            "批量查询": [{"数据库": "数据库1", "数据表": "数据表1", "数据ID列表": ["ID1", "ID2"]}],
                            "按条件筛选": [{"数据库": "数据库1", "数据表": "数据表1", "关键词": "关键词1"}],
                            "全库模糊查询": [{"数据库": "数据库1", "关键词": "关键词1"}],
                            "查询文件目录": [{"文件路径": "路径1"}],
                            "查询文件内容": [{"文件路径": "路径1"}],
                            "查询文件行数": [{"文件路径": "路径1"}],
                            "模糊查询文件": [{"文件路径": "路径1", "关键词": "关键词1"}]
                        }
                    }
                    英文格式:
                    {
                        "type": "data_query",
                        "params": {
                            "query_tables": [{"database": "db1"}],
                            "query_table_content": [{"database": "db1", "table": "table1"}],
                            "check_exists": [{"database": "db1", "table": "table1", "data_id": "id1"}],
                            "count_data": [{"database": "db1", "table": "table1"}],
                            "batch_query": [{"database": "db1", "table": "table1", "data_ids": ["id1", "id2"]}],
                            "filter_data": [{"database": "db1", "table": "table1", "keyword": "keyword1"}],
                            "fuzzy_query": [{"database": "db1", "keyword": "keyword1"}],
                            "query_file_directory": [{"filepath": "path1"}],
                            "query_file_content": [{"filepath": "path1"}],
                            "query_file_line_count": [{"filepath": "path1"}],
                            "fuzzy_query_file": [{"filepath": "path1", "keyword": "keyword1"}]
                        }
                    }
        """
        # 兼容中文和英文字段名
        action_type = json_data.get('type') or json_data.get('类型')
        params = json_data.get('params') or json_data.get('参数')
        
        # -------------------- 文件编辑 --------------------
        if action_type in ['file_edit', '文件编辑']:
            add_list = params.get('add') or params.get('新增') or []
            modify_list = params.get('modify') or params.get('修改') or []
            delete_list = params.get('delete') or params.get('删除') or []
            
            # ⚠️ 策略：如果有add或modify操作，先清空文件再执行add（全量重写）
            # 只有纯delete操作才执行真正的行删除
            if add_list or modify_list:
                # 确定目标文件路径（严格模式：必须明确指定）
                filepath = None
                if add_list and (add_list[0].get('filepath') or add_list[0].get('文件路径')):
                    filepath = add_list[0].get('filepath') or add_list[0].get('文件路径')
                elif modify_list and (modify_list[0].get('filepath') or modify_list[0].get('文件路径')):
                    filepath = modify_list[0].get('filepath') or modify_list[0].get('文件路径')
                elif self.default_filepath:
                    # 只有在设置了 default_filepath 时才使用（向后兼容）
                    filepath = self.default_filepath
                
                # 严格检查：如果没有文件路径，抛出错误
                if not filepath:
                    error_msg = "❌ 文件编辑操作失败：未指定文件路径！文件操作必须明确指定目标文件路径。"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # 解析文件路径
                filepath = self._resolve_filepath(filepath)
                
                # 清空文件（保留目录结构）
                dir_path = os.path.dirname(filepath)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    pass  # 清空文件
                logger.debug(f"✓ 文件已清空，准备重写: {filepath}")
                
                # 只处理add操作（从第1行开始重写整个文件）
                for item in add_list:
                    item_filepath = item.get('filepath') or item.get('文件路径')
                    if not item_filepath and not self.default_filepath:
                        error_msg = f"❌ 文件编辑操作失败：第{item.get('line') or item.get('行')}行未指定文件路径！"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    item_filepath = item_filepath or self.default_filepath
                    item_filepath = self._resolve_filepath(item_filepath)
                    line = item.get('line') or item.get('行')
                    content = item.get('content') or item.get('内容')
                    if content is None:
                        content = ""
                    self.file_line_editor.insert_line(item_filepath, line, content)
                
                # modify和delete被忽略（因为文件已清空重写）
                if modify_list or delete_list:
                    logger.debug(f"✓ 已采用全量重写（忽略{len(modify_list)}个modify和{len(delete_list)}个delete）")
            
            # 如果只有delete操作（没有add和modify），才执行真正的行删除
            elif delete_list:
                for item in delete_list:
                    item_filepath = item.get('filepath') or item.get('文件路径')
                    if not item_filepath and not self.default_filepath:
                        error_msg = f"❌ 文件删除操作失败：第{item.get('line') or item.get('行')}行未指定文件路径！"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    item_filepath = item_filepath or self.default_filepath
                    item_filepath = self._resolve_filepath(item_filepath)
                    line = item.get('line') or item.get('行')
                    self.file_line_editor.delete_line(item_filepath, line)
                logger.info(f"✓ 已删除{len(delete_list)}行")
            
            # 处理创建文件
            create_file_list = params.get('create_file') or params.get('创建文件') or []
            for item in create_file_list:
                filepath = item.get('filepath') or item.get('文件路径')
                if not filepath:
                    error_msg = "❌ 创建文件操作失败：未指定文件路径！"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                filepath = self._resolve_filepath(filepath)
                # 确保目录存在，然后创建空文件
                dir_path = os.path.dirname(filepath)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    pass
                logger.info(f"✓ 文件创建成功: {filepath}")
            
            # 处理删除文件
            delete_file_list = params.get('delete_file') or params.get('删除文件') or []
            for item in delete_file_list:
                filepath = item.get('filepath') or item.get('文件路径')
                if not filepath:
                    error_msg = "❌ 删除文件操作失败：未指定文件路径！"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                filepath = self._resolve_filepath(filepath)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.info(f"✓ 文件删除成功: {filepath}")
                else:
                    logger.warning(f"文件不存在，无法删除: {filepath}")
        # -------------------- 数据库编辑 --------------------
        elif action_type in ['数据库编辑', 'database_edit']:
            # 插入数据
            insert_list = params.get('插入数据') or params.get('insert') or []
            for item in insert_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                data_id = item.get('数据ID') or item.get('data_id')
                content = item.get('内容') or item.get('content')
                self.database_editor.insert_data(db, table, data_id, content)
            # 修改数据
            update_list = params.get('修改数据') or params.get('update') or []
            for item in update_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                data_id = item.get('数据ID') or item.get('data_id')
                content = item.get('内容') or item.get('content')
                self.database_editor.update_data(db, table, data_id, content)
            # 删除数据
            delete_list = params.get('删除数据') or params.get('delete') or []
            for item in delete_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                data_id = item.get('数据ID') or item.get('data_id')
                self.database_editor.delete_data(db, table, data_id)
            # 创建数据库
            create_db_list = params.get('创建数据库') or params.get('create_database') or []
            for item in create_db_list:
                db = item.get('数据库') or item.get('database')
                self.database_editor.connect(db)
            # 删除数据库
            delete_db_list = params.get('删除数据库') or params.get('delete_database') or []
            for item in delete_db_list:
                db = item.get('数据库') or item.get('database')
                self.database_editor.delete(db)
            # 创建数据表
            create_table_list = params.get('创建数据表') or params.get('create_table') or []
            for item in create_table_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                self.database_editor.create_table(db, table)
            # 删除数据表
            delete_table_list = params.get('删除数据表') or params.get('delete_table') or []
            for item in delete_table_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                self.database_editor.delete_table(db, table)
        # -------------------- 数据查询 --------------------
        elif action_type in ['数据查询', 'data_query']:
            results = {}
            
            # 查询文件目录
            query_file_dir_list = params.get('查询文件目录') or params.get('query_file_directory') or []
            for item in query_file_dir_list:
                filepath = item.get('文件路径') or item.get('filepath')
                result = self.data_inquire.file_directory(filepath)
                # 将 os.walk 生成器转换为列表，方便后续处理和序列化
                if result:
                    result_list = [(root, dirs, files) for root, dirs, files in result]
                    results[f'查询文件目录_{filepath}'] = result_list
                    logger.debug(f"查询目录 {filepath}: 找到 {len(result_list)} 个条目")
                else:
                    results[f'查询文件目录_{filepath}'] = []
                    logger.warning(f"查询目录 {filepath}: 未找到结果")
            
            # 查询文件内容
            query_file_content_list = params.get('查询文件内容') or params.get('query_file_content') or []
            for item in query_file_content_list:
                filepath = item.get('文件路径') or item.get('filepath')
                resolved_filepath = self._resolve_filepath(filepath)
                result = self.data_inquire.file_content(resolved_filepath)
                results[f'查询文件内容_{filepath}'] = result
            
            # 查询文件行数
            query_file_line_count_list = params.get('查询文件行数') or params.get('query_file_line_count') or []
            for item in query_file_line_count_list:
                filepath = item.get('文件路径') or item.get('filepath')
                resolved_filepath = self._resolve_filepath(filepath)
                result = self.data_inquire.file_line_count(resolved_filepath)
                results[f'查询文件行数_{filepath}'] = result
            
            # 模糊查询文件内容
            fuzzy_query_file_list = params.get('模糊查询文件') or params.get('fuzzy_query_file') or []
            for item in fuzzy_query_file_list:
                filepath = item.get('文件路径') or item.get('filepath')
                resolved_filepath = self._resolve_filepath(filepath)
                keyword = item.get('关键词') or item.get('keyword') or item.get('内容') or item.get('content')
                result = self.data_inquire.file_content_fuzzy(resolved_filepath, keyword)
                results[f'模糊查询文件_{filepath}'] = result
            
            # 查询所有数据表
            query_tables_list = params.get('查询所有数据表') or params.get('query_tables') or []
            for item in query_tables_list:
                db = item.get('数据库') or item.get('database')
                result = self.data_inquire.database_all_table(db)
                results[f'查询所有数据表_{db}'] = result
            
            # 查询表中所有数据
            query_table_content_list = params.get('查询表中所有数据') or params.get('query_table_content') or []
            for item in query_table_content_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                result = self.data_inquire.database_table_content(db, table)
                results[f'查询表数据_{db}_{table}'] = result
            
            # 检查数据是否存在
            check_exists_list = params.get('检查数据是否存在') or params.get('check_exists') or []
            for item in check_exists_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                data_id = item.get('数据ID') or item.get('data_id')
                result = self.data_inquire.database_table_data_exists(db, table, data_id)
                results[f'检查存在_{db}_{table}_{data_id}'] = result
            
            # 统计数据数量
            count_data_list = params.get('统计数据数量') or params.get('count_data') or []
            for item in count_data_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                result = self.data_inquire.database_table_data_count(db, table)
                results[f'统计数量_{db}_{table}'] = result
            
            # 批量查询
            batch_query_list = params.get('批量查询') or params.get('batch_query') or []
            for item in batch_query_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                data_ids = item.get('数据ID列表') or item.get('data_ids') or []
                result = self.data_inquire.database_table_data_batch(db, table, data_ids)
                results[f'批量查询_{db}_{table}'] = result
            
            # 按条件筛选（单表模糊查询）
            filter_data_list = params.get('按条件筛选') or params.get('filter_data') or []
            for item in filter_data_list:
                db = item.get('数据库') or item.get('database')
                table = item.get('数据表') or item.get('table')
                content = item.get('内容') or item.get('content') or item.get('关键词') or item.get('keyword')
                result = self.data_inquire.database_table_data_filter(db, table, content)
                results[f'筛选数据_{db}_{table}'] = result
            
            # 全库模糊查询
            fuzzy_query_list = params.get('全库模糊查询') or params.get('fuzzy_query') or []
            for item in fuzzy_query_list:
                db = item.get('数据库') or item.get('database')
                content = item.get('内容') or item.get('content') or item.get('关键词') or item.get('keyword')
                result = self.data_inquire.database_content_fuzzy(db, content)
                results[f'全库查询_{db}'] = result
            
            # 返回所有查询结果
            return results
            
    # 提取TODO列表
    def load_json(self, json_data: dict) -> list:
        """
        从搜索规划JSON中提取TODO任务列表。
        
        参数:
            json_data (dict 或 str): 搜索规划JSON数据
                中文格式:
                    {
                        "类型": "搜索规划",
                        "用户需求": "...",
                        "搜索策略": "...",
                        "任务列表": [
                            {
                                "任务ID": 1,
                                "操作类型": "...",
                                "目标对象": "...",
                                "参数": {},
                                "目的": "...",
                                "是否联网": false
                            }
                        ]
                    }
                英文格式:
                    {
                        "type": "search_plan",
                        "user_query": "...",
                        "search_strategy": "...",
                        "task_list": [...]
                    }
        
        返回:
            list: 任务列表，每个任务是一个字典
                中文格式任务结构:
                {
                    "任务ID": 1,
                    "操作类型": "查询数据库表",
                    "目标对象": "config_db",
                    "参数": {"数据库": "config_db"},
                    "目的": "列出所有表",
                    "是否联网": false
                }
                英文格式任务结构:
                {
                    "task_id": 1,
                    "operation_type": "query_tables",
                    "target": "config_db",
                    "params": {"database": "config_db"},
                    "purpose": "...",
                    "use_web": false
                }
            
            如果不是搜索规划JSON或格式错误，返回空列表[]
        """
        import json
        
        # 如果是字符串，先解析成字典
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                logger.error("无法解析JSON字符串")
                return []
        
        # 验证是否是字典类型
        if not isinstance(json_data, dict):
            logger.error("输入数据不是有效的JSON对象")
            return []
        
        # 兼容中文和英文字段名
        json_type = json_data.get('类型') or json_data.get('type')
        
        # 验证是否是搜索规划类型
        if json_type not in ['搜索规划', 'search_plan']:
            logger.debug(f"这不是搜索规划JSON（类型为：{json_type}），无TODO列表可提取")
            return []
        
        # 提取任务列表（兼容中英文）
        task_list = json_data.get('任务列表') or json_data.get('task_list') or []
        
        # 验证任务列表是否为列表类型
        if not isinstance(task_list, list):
            logger.error("任务列表格式不正确")
            return []
        
        # 返回任务列表
        return task_list