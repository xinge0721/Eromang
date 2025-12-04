# -*- coding: utf-8 -*-
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

class TaskManager:
    """
    任务管理工具
    用于管理 AI 生成的 TODO 任务列表
    """

    def __init__(self):
        # 内存存储任务列表
        self.task_lists = {}

    def create_task_list(self, tasks: List[Dict], list_name: Optional[str] = None) -> Dict:
        """
        创建任务列表

        参数:
            tasks: 任务列表，每个任务是一个字典
                   格式: [
                       {
                           "task_id": "task_001",
                           "description": "读取配置文件",
                           "tool": "file_content",
                           "arguments": {"file_path": "./Data/config.json"},
                           "priority": 1,
                           "depends_on": []
                       }
                   ]
            list_name: 任务列表名称（可选）

        返回:
            包含 list_id 的字典
        """
        if not tasks:
            return {"error": "任务列表不能为空"}

        if not isinstance(tasks, list):
            return {"error": "tasks 必须是列表类型"}

        # 生成唯一的列表 ID
        list_id = str(uuid.uuid4())

        # 验证并初始化任务
        validated_tasks = []
        for idx, task in enumerate(tasks):
            if not isinstance(task, dict):
                return {"error": f"任务 {idx} 必须是字典类型"}

            # 确保每个任务有必要的字段
            task_id = task.get("task_id", f"task_{idx+1:03d}")

            validated_task = {
                "task_id": task_id,
                "description": task.get("description", ""),
                "tool": task.get("tool", ""),
                "arguments": task.get("arguments", {}),
                "priority": task.get("priority", idx + 1),
                "depends_on": task.get("depends_on", []),
                "status": "pending",  # pending, running, completed, failed
                "result": None,
                "error": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "started_at": None,
                "completed_at": None
            }
            validated_tasks.append(validated_task)

        # 存储任务列表
        self.task_lists[list_id] = {
            "list_id": list_id,
            "list_name": list_name or f"TaskList_{list_id[:8]}",
            "tasks": validated_tasks,
            "total_tasks": len(validated_tasks),
            "completed_tasks": 0,
            "failed_tasks": 0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "created"  # created, running, completed, failed
        }

        return {
            "list_id": list_id,
            "list_name": self.task_lists[list_id]["list_name"],
            "total_tasks": len(validated_tasks),
            "message": f"成功创建任务列表，包含 {len(validated_tasks)} 个任务"
        }

    def get_task_list(self, list_id: str) -> Dict:
        """
        获取任务列表

        参数:
            list_id: 任务列表 ID

        返回:
            任务列表详情
        """
        if not list_id or list_id == "":
            return {"error": "任务列表 ID 不能为空"}

        if list_id not in self.task_lists:
            return {"error": f"任务列表不存在: {list_id}"}

        return self.task_lists[list_id]

    def get_next_task(self, list_id: str) -> Dict:
        """
        获取下一个待执行的任务（考虑依赖关系）

        参数:
            list_id: 任务列表 ID

        返回:
            下一个任务或 None
        """
        if not list_id or list_id == "":
            return {"error": "任务列表 ID 不能为空"}

        if list_id not in self.task_lists:
            return {"error": f"任务列表不存在: {list_id}"}

        task_list = self.task_lists[list_id]
        tasks = task_list["tasks"]

        # 查找下一个可执行的任务
        for task in sorted(tasks, key=lambda x: x["priority"]):
            if task["status"] != "pending":
                continue

            # 检查依赖是否满足
            dependencies_met = True
            for dep_id in task["depends_on"]:
                dep_task = next((t for t in tasks if t["task_id"] == dep_id), None)
                if not dep_task or dep_task["status"] != "completed":
                    dependencies_met = False
                    break

            if dependencies_met:
                return {
                    "has_next": True,
                    "task": task
                }

        return {
            "has_next": False,
            "message": "没有可执行的任务"
        }

    def update_task_status(self, list_id: str, task_id: str, status: str,
                          result: Optional[Any] = None, error: Optional[str] = None) -> Dict:
        """
        更新任务状态

        参数:
            list_id: 任务列表 ID
            task_id: 任务 ID
            status: 新状态 (pending, running, completed, failed)
            result: 任务结果（可选）
            error: 错误信息（可选）

        返回:
            更新结果
        """
        if not list_id or list_id == "":
            return {"error": "任务列表 ID 不能为空"}

        if not task_id or task_id == "":
            return {"error": "任务 ID 不能为空"}

        if list_id not in self.task_lists:
            return {"error": f"任务列表不存在: {list_id}"}

        task_list = self.task_lists[list_id]
        task = next((t for t in task_list["tasks"] if t["task_id"] == task_id), None)

        if not task:
            return {"error": f"任务不存在: {task_id}"}

        # 更新任务状态
        old_status = task["status"]
        task["status"] = status

        if status == "running" and not task["started_at"]:
            task["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if status in ["completed", "failed"]:
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if result is not None:
            task["result"] = result

        if error is not None:
            task["error"] = error

        # 更新任务列表统计
        if status == "completed" and old_status != "completed":
            task_list["completed_tasks"] += 1
        elif status == "failed" and old_status != "failed":
            task_list["failed_tasks"] += 1

        # 检查任务列表是否全部完成
        all_done = all(t["status"] in ["completed", "failed"] for t in task_list["tasks"])
        if all_done:
            task_list["status"] = "completed"

        return {
            "list_id": list_id,
            "task_id": task_id,
            "status": status,
            "message": f"任务状态已更新为: {status}"
        }

    def add_task(self, list_id: str, task: Dict) -> Dict:
        """
        向现有任务列表添加新任务

        参数:
            list_id: 任务列表 ID
            task: 任务字典

        返回:
            添加结果
        """
        if not list_id or list_id == "":
            return {"error": "任务列表 ID 不能为空"}

        if list_id not in self.task_lists:
            return {"error": f"任务列表不存在: {list_id}"}

        if not isinstance(task, dict):
            return {"error": "任务必须是字典类型"}

        task_list = self.task_lists[list_id]

        # 生成任务 ID
        task_id = task.get("task_id", f"task_{len(task_list['tasks']) + 1:03d}")

        new_task = {
            "task_id": task_id,
            "description": task.get("description", ""),
            "tool": task.get("tool", ""),
            "arguments": task.get("arguments", {}),
            "priority": task.get("priority", len(task_list["tasks"]) + 1),
            "depends_on": task.get("depends_on", []),
            "status": "pending",
            "result": None,
            "error": None,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "started_at": None,
            "completed_at": None
        }

        task_list["tasks"].append(new_task)
        task_list["total_tasks"] += 1

        return {
            "list_id": list_id,
            "task_id": task_id,
            "message": f"成功添加任务: {task_id}"
        }

    def clear_task_list(self, list_id: str) -> Dict:
        """
        清空任务列表

        参数:
            list_id: 任务列表 ID

        返回:
            清空结果
        """
        if not list_id or list_id == "":
            return {"error": "任务列表 ID 不能为空"}

        if list_id not in self.task_lists:
            return {"error": f"任务列表不存在: {list_id}"}

        del self.task_lists[list_id]

        return {
            "list_id": list_id,
            "message": f"任务列表已清空: {list_id}"
        }

    def get_task_summary(self, list_id: str) -> Dict:
        """
        获取任务列表摘要

        参数:
            list_id: 任务列表 ID

        返回:
            任务列表摘要
        """
        if not list_id or list_id == "":
            return {"error": "任务列表 ID 不能为空"}

        if list_id not in self.task_lists:
            return {"error": f"任务列表不存在: {list_id}"}

        task_list = self.task_lists[list_id]

        pending_count = sum(1 for t in task_list["tasks"] if t["status"] == "pending")
        running_count = sum(1 for t in task_list["tasks"] if t["status"] == "running")

        return {
            "list_id": list_id,
            "list_name": task_list["list_name"],
            "status": task_list["status"],
            "total_tasks": task_list["total_tasks"],
            "pending_tasks": pending_count,
            "running_tasks": running_count,
            "completed_tasks": task_list["completed_tasks"],
            "failed_tasks": task_list["failed_tasks"],
            "created_at": task_list["created_at"]
        }

    def get_all_task_lists(self) -> Dict:
        """
        获取所有任务列表的摘要

        返回:
            所有任务列表的摘要
        """
        summaries = []

        for list_id in self.task_lists:
            summary = self.get_task_summary(list_id)
            if "error" not in summary:
                summaries.append(summary)

        return {
            "total_lists": len(summaries),
            "lists": summaries
        }

    def get_task_results(self, list_id: str) -> Dict:
        """
        获取任务列表中所有已完成任务的结果

        参数:
            list_id: 任务列表 ID

        返回:
            任务结果列表
        """
        if not list_id or list_id == "":
            return {"error": "任务列表 ID 不能为空"}

        if list_id not in self.task_lists:
            return {"error": f"任务列表不存在: {list_id}"}

        task_list = self.task_lists[list_id]
        results = []

        for task in task_list["tasks"]:
            if task["status"] == "completed":
                results.append({
                    "task_id": task["task_id"],
                    "description": task["description"],
                    "result": task["result"],
                    "completed_at": task["completed_at"]
                })

        return {
            "list_id": list_id,
            "total_results": len(results),
            "results": results
        }
