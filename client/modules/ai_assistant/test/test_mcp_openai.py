"""
MCP + OpenAI 集成测试
测试 MCP 协议与 OpenAI Function Calling 的集成
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from openai import OpenAI

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def print_section(title):
    """打印分隔线"""
    print("\n" + "="*80)
    print(f"{title}")
    print("="*80 + "\n")


# ============================================================================
# 简单的 MCP 服务器（stdio 协议）
# ============================================================================

MCP_SERVER_CODE = '''
import json
import sys
from datetime import datetime

def send_response(response):
    """发送 JSON-RPC 响应"""
    sys.stdout.write(json.dumps(response) + "\\n")
    sys.stdout.flush()

def handle_request(request):
    """处理 MCP 请求"""
    method = request.get("method")
    request_id = request.get("id")

    if method == "tools/list":
        # 返回工具列表
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "get_current_time",
                        "description": "获取当前的日期和时间",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "format": {
                                    "type": "string",
                                    "description": "时间格式",
                                    "enum": ["full", "simple"]
                                }
                            }
                        }
                    },
                    {
                        "name": "calculate",
                        "description": "执行简单的数学计算",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "expression": {
                                    "type": "string",
                                    "description": "数学表达式"
                                }
                            },
                            "required": ["expression"]
                        }
                    }
                ]
            }
        }

    elif method == "tools/call":
        # 执行工具调用
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "get_current_time":
            fmt = arguments.get("format", "full")
            now = datetime.now()
            if fmt == "simple":
                result = now.strftime("%H:%M:%S")
            else:
                result = now.strftime("%Y年%m月%d日 %H:%M:%S")

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": result}]
                }
            }

        elif tool_name == "calculate":
            expression = arguments.get("expression", "")
            try:
                result = eval(expression)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": f"{expression} = {result}"}]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -1, "message": str(e)}
                }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": "Method not found"}
    }

# 主循环
while True:
    try:
        line = sys.stdin.readline()
        if not line:
            break

        request = json.loads(line.strip())
        response = handle_request(request)
        send_response(response)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\\n")
        sys.stderr.flush()
'''


# ============================================================================
# 简单的 MCP 客户端
# ============================================================================

class SimpleMCPClient:
    """简单的 MCP 客户端（stdio 传输）"""

    def __init__(self):
        """启动 MCP 服务器进程"""
        self.process = subprocess.Popen(
            [sys.executable, "-c", MCP_SERVER_CODE],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.request_id = 0
        self.tools = []

        # 发现工具
        self._discover_tools()

    def _send_request(self, method, params=None):
        """发送 MCP 请求"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id
        }
        if params:
            request["params"] = params

        # 发送请求
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()

        # 读取响应
        response_line = self.process.stdout.readline()
        return json.loads(response_line)

    def _discover_tools(self):
        """发现可用工具"""
        response = self._send_request("tools/list")
        self.tools = response.get("result", {}).get("tools", [])
        print(f"✓ 从 MCP 服务器发现 {len(self.tools)} 个工具")

    def call_tool(self, name, arguments):
        """调用工具"""
        response = self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })

        if "result" in response:
            content = response["result"]["content"][0]["text"]
            return content
        else:
            error = response.get("error", {})
            raise Exception(f"工具调用失败: {error.get('message')}")

    def get_tools_for_openai(self):
        """转换为 OpenAI Function Calling 格式"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            }
            for tool in self.tools
        ]

    def close(self):
        """关闭客户端"""
        self.process.terminate()
        self.process.wait()


# ============================================================================
# MCP + OpenAI 集成测试
# ============================================================================

def test_mcp_openai():
    """测试 MCP + OpenAI 集成"""
    print_section("MCP + OpenAI 集成测试")

    # 1. 启动 MCP 客户端
    print("[步骤 1] 启动 MCP 客户端...")
    mcp_client = SimpleMCPClient()

    # 2. 获取工具列表
    print("\n[步骤 2] 从 MCP 获取工具列表...")
    tools = mcp_client.get_tools_for_openai()
    print(f"工具列表: {json.dumps(tools, ensure_ascii=False, indent=2)}")

    # 3. 创建 OpenAI 客户端（使用环境变量或配置文件）
    print("\n[步骤 3] 创建 OpenAI 客户端...")
    api_key = os.environ.get('DEEPSEEK_API_KEY')

    # 尝试从配置文件读取
    if not api_key:
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            secret_key_path = os.path.join(parent_dir, 'role', 'secret_key.json')

            if os.path.exists(secret_key_path):
                with open(secret_key_path, 'r', encoding='utf-8') as f:
                    secret_keys = json.load(f)
                    api_key = secret_keys.get('deepseek')
        except:
            pass

    if not api_key:
        print("✗ 未找到 API Key")
        print("请设置环境变量 DEEPSEEK_API_KEY 或创建 role/secret_key.json")
        mcp_client.close()
        return

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        timeout=30.0
    )

    # 4. 测试对话
    print("\n[步骤 4] 测试 AI 调用 MCP 工具...")
    print("用户问题: 现在几点了？")

    messages = [{"role": "user", "content": "现在几点了？"}]

    # 调用 OpenAI API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # 5. 处理工具调用
    if assistant_message.tool_calls:
        print(f"\n✓ AI 请求调用工具: {assistant_message.tool_calls[0].function.name}")

        tool_call = assistant_message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print(f"  工具名称: {function_name}")
        print(f"  参数: {json.dumps(function_args, ensure_ascii=False)}")

        # 通过 MCP 执行工具
        print("\n[步骤 5] 通过 MCP 执行工具...")
        result = mcp_client.call_tool(function_name, function_args)
        print(f"  MCP 返回结果: {result}")

        # 将结果返回给 AI
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [{
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": function_name,
                    "arguments": tool_call.function.arguments
                }
            }]
        })

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": result
        })

        # 再次调用 AI 生成最终回答
        print("\n[步骤 6] AI 生成最终回答...")
        final_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools
        )

        final_answer = final_response.choices[0].message.content
        print(f"\n最终回答: {final_answer}")

        print("\n" + "="*80)
        print("✓ 测试成功！MCP + OpenAI 集成正常工作")
        print("="*80)
    else:
        print("\n✗ AI 没有调用工具")

    # 清理
    mcp_client.close()


if __name__ == "__main__":
    try:
        test_mcp_openai()
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
