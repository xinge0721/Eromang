import threading
import time
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import queue
import uuid
import os
class MCPClient:
    """简单的线程类"""
    def __init__(self):
        self.thread = None#线程对象
        self.running = False#运行状态
        self.paused = False#暂停状态
        self.pause_lock = threading.Lock()#暂停锁

        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "server.py")

        self.server_params = StdioServerParameters(
            command="python",
            args=[server_path]
        )#服务器参数

        self.context = None # 上下文
        self.session = None # 会话
        self.tools = [] # 工具列表
        self.initialized = False # 初始化状态

        self.message_queue = queue.Queue() # 消息队列
        self.results = {} # 结果字典，key 为 uuid，value 为结果
    # ==================== 启动 ==================== 
    def start(self):
        """启动MCP客户端"""
        if self.thread is None or not self.thread.is_alive():
            self.running = True#设置运行状态为True
            self.paused = False#设置暂停状态为False
            self.thread = threading.Thread(target=self._run_sync)#创建线程
            self.thread.start()#启动线程

    # ==================== 关闭 ====================
    def close(self):
        """关闭MCP客户端"""
        self.running = False#设置运行状态为False
        self.paused = False#设置暂停状态为False
        if self.thread is not None:
            self.thread.join()#等待线程结束
            self.thread = None#设置线程为None
        
    # ==================== 暂停====================
    def pause(self):
        """暂停MCP客户端"""
        self.paused = True
    # ==================== 恢复====================  
    def resume(self):
        """恢复MCP客户端"""
        self.paused = False

    # ==================== 同步运行包装 ====================
    def _run_sync(self):
        """同步包装方法，在线程中运行事件循环"""
        try:
            asyncio.run(self._run_async())
        except Exception as e:
            print(f"[MCPClient] 运行时错误: {e}")
            import traceback
            traceback.print_exc()
            self.running = False

    # ==================== 异步运行====================
    async def _run_async(self):
        try:
            # 创建客户端
            # 参数：服务器参数
            # 返回：一个上下文管理器
            self.context = stdio_client(self.server_params)
            # 创建通信管道
            # read  管道：用来接收服务器发来的消息
            # write 管道：用来发送消息给服务器
            read, write = await self.context.__aenter__()

            # 创建会话
            self.session = ClientSession(read, write)
            # 启动后台监听任务
            await self.session.__aenter__()

            # 初始化（握手）
            await self.session.initialize()

            # 获取工具列表
            result = await self.session.list_tools()
            self.tools = result.tools if hasattr(result, 'tools') else result
            self.initialized = True

            while self.running:
                if self.paused:
                    time.sleep(0.1)
                    continue

                #如果队列为空
                if self.message_queue.empty():
                    continue
                # 取出顶部元素
                task = self.message_queue.get()
                # 移除顶部元素
                self.message_queue.task_done()

                task_id = task["id"]
                result = await self.session.call_tool(
                    task["name"],
                    task.get("arguments", {})
                )
                # 将结果存入字典
                self.results[task_id] = result

        finally:
            # 在异步环境中正确关闭资源
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self.context:
                await self.context.__aexit__(None, None, None)

    # ==================== 添加任务 ====================
    def add(self, data: dict) -> str:
        """
        添加任务到队列

        参数:
            data: 任务数据，包含 name 和 arguments

        返回:
            任务的 UUID
        """
        if data is None:
            raise ValueError("数据不能为空")
        if self.running is False:
            raise ValueError("MCP客户端未启动")

        # 生成 UUID
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "name": data["name"],
            "arguments": data.get("arguments", {})
        }
        self.message_queue.put(task)
        return task_id

    # ==================== 获取结果 ====================
    def get_result(self, task_id: str, block=True, timeout=None):
        """
        根据任务 ID 获取工具调用结果

        参数:
            task_id: 任务的 UUID
            block: 是否阻塞等待，默认 True
            timeout: 超时时间（秒），None 表示无限等待

        返回:
            工具调用的结果
        """
        if self.running is False:
            raise ValueError("MCP客户端未启动")

        if block:
            # 阻塞等待结果
            start_time = time.time()
            while True:
                if task_id in self.results:
                    result = self.results.pop(task_id)
                    return result

                # 检查超时
                if timeout is not None:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"等待任务 {task_id} 结果超时")

                time.sleep(0.01)
        else:
            # 非阻塞，直接返回
            if task_id in self.results:
                return self.results.pop(task_id)
            else:
                raise KeyError(f"任务 {task_id} 的结果尚未准备好")

    # ==================== 获得工具 ====================
    def list_tools(self) -> list:
        if self.running is False:
            raise ValueError("MCP客户端未启动")
        if self.tools is None:
            raise ValueError("工具列表为空")
        if len(self.tools) == 0:
            raise ValueError("工具列表为空")
        return self.tools

# ==================== 测试代码 ====================
if __name__ == "__main__":
    print("=" * 80)
    print("MCP 客户端测试")
    print("=" * 80)

    # 创建客户端
    client = MCPClient()

    try:
        # 启动客户端
        print("\n[1] 启动客户端...")
        client.start()
        time.sleep(5)  # 等待初始化完成
        print("✓ 客户端启动成功")

        # 获取工具列表
        print("\n[2] 获取工具列表...")
        tools = client.list_tools()
        print(f"✓ 找到 {len(tools)} 个工具:")
        for i, tool in enumerate(tools, 1):
            if hasattr(tool, 'name'):
                print(f"  {i}. {tool.name}: {tool.description if hasattr(tool, 'description') else ''}")
            else:
                print(f"  {i}. {tool.get('name', 'unknown')}: {tool.get('description', '')}")

        # 测试单个任务
        print("\n[3] 测试单个任务 (add)...")
        task_id = client.add({
            "name": "add",
            "arguments": {"a": 10, "b": 20}
        })
        print(f"✓ 任务已添加，UUID: {task_id}")

        print("  等待结果...")
        try:
            result = client.get_result(task_id, timeout=5)
            print(f"✓ 获取结果成功: {result}")
        except TimeoutError as e:
            print(f"✗ 超时: {e}")
        except Exception as e:
            print(f"✗ 错误: {e}")

        # 测试多个任务
        print("\n[4] 测试多个任务 (add)...")
        task_ids = []
        for i in range(3):
            task_id = client.add({
                "name": "add",
                "arguments": {"a": i, "b": i + 1}
            })
            task_ids.append(task_id)
            print(f"  任务 {i+1} 已添加 (计算 {i} + {i+1})，UUID: {task_id}")

        print("\n  获取所有结果...")
        for i, task_id in enumerate(task_ids):
            try:
                result = client.get_result(task_id, timeout=5)
                print(f"  ✓ 任务 {i+1} 结果: {result}")
            except TimeoutError:
                print(f"  ✗ 任务 {i+1} 超时")
            except Exception as e:
                print(f"  ✗ 任务 {i+1} 错误: {e}")

        # 测试非阻塞获取
        print("\n[5] 测试非阻塞获取 (add)...")
        task_id = client.add({
            "name": "add",
            "arguments": {"a": 100, "b": 200}
        })
        print(f"✓ 任务已添加 (计算 100 + 200)，UUID: {task_id}")

        try:
            result = client.get_result(task_id, block=False)
            print(f"✓ 立即获取到结果: {result}")
        except KeyError:
            print("  结果尚未准备好（符合预期）")
            print("  等待 1 秒后重试...")
            time.sleep(1)
            try:
                result = client.get_result(task_id, block=False)
                print(f"✓ 获取到结果: {result}")
            except KeyError:
                print("  结果仍未准备好")

    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 关闭客户端
        print("\n[6] 关闭客户端...")
        client.close()
        print("✓ 客户端已关闭")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
