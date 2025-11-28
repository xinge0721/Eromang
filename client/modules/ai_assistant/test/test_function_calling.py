"""
OpenAI Function Calling 测试脚本
演示如何使用 OpenAI 的 Function Calling 功能调用工具
"""

import json
import sys
import os
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


def load_config():
    """加载配置文件"""
    try:
        # 获取脚本所在目录的父目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)

        # 读取配置
        config_path = os.path.join(parent_dir, 'role', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 尝试读取 API Key
        secret_key_path = os.path.join(parent_dir, 'role', 'secret_key.json')
        api_key = None

        if os.path.exists(secret_key_path):
            with open(secret_key_path, 'r', encoding='utf-8') as f:
                secret_keys = json.load(f)
                api_key = secret_keys.get('deepseek')

        # 如果没有配置文件，尝试从环境变量读取
        if not api_key:
            api_key = os.environ.get('DEEPSEEK_API_KEY')

        # 如果还是没有，提示用户
        if not api_key:
            print("\n⚠ 未找到 API Key！")
            print("\n请通过以下方式之一提供 DeepSeek API Key：")
            print("1. 创建 role/secret_key.json 文件，格式如下：")
            print('   {"deepseek": "your-api-key-here"}')
            print("\n2. 设置环境变量：")
            print("   export DEEPSEEK_API_KEY=your-api-key-here")
            print("\n3. 直接在命令行输入（仅用于测试）：")
            api_key = input("\n请输入 DeepSeek API Key: ").strip()

            if not api_key:
                print("✗ 未提供 API Key，退出测试")
                sys.exit(1)

        # 使用 deepseek 作为测试模型（支持 Function Calling）
        model_config = config['deepseek']['deepseek-chat']

        return api_key, model_config
    except Exception as e:
        print(f"✗ 读取配置文件失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# 工具定义（OpenAI 标准格式）
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "时间格式，可选值：'full'（完整格式）或 'simple'（简单格式）",
                        "enum": ["full", "simple"]
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行简单的数学计算（加减乘除）",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如：'100 + 200' 或 '50 * 3'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


# ============================================================================
# 工具执行函数
# ============================================================================

def get_current_time(format="full"):
    """获取当前时间"""
    now = datetime.now()
    if format == "simple":
        return now.strftime("%H:%M:%S")
    else:
        return now.strftime("%Y年%m月%d日 %H:%M:%S")


def calculate(expression):
    """执行数学计算"""
    try:
        # 安全的数学表达式求值
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"

        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


def execute_tool(tool_name, arguments):
    """执行工具调用"""
    print(f"  🔧 执行工具: {tool_name}")
    print(f"  📥 参数: {json.dumps(arguments, ensure_ascii=False)}")

    if tool_name == "get_current_time":
        result = get_current_time(**arguments)
    elif tool_name == "calculate":
        result = calculate(**arguments)
    else:
        result = f"未知工具: {tool_name}"

    print(f"  📤 结果: {result}")
    return result


# ============================================================================
# 工具调用循环
# ============================================================================

def chat_with_tools(client, model, messages, max_iterations=5):
    """
    带工具调用的对话循环

    Args:
        client: OpenAI 客户端
        model: 模型名称
        messages: 消息列表
        max_iterations: 最大迭代次数（防止无限循环）

    Returns:
        最终的 AI 回答
    """
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- 第 {iteration} 轮调用 ---")

        # 调用 OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"  # 让 AI 自动决定是否调用工具
        )

        assistant_message = response.choices[0].message

        # 检查是否有工具调用
        if assistant_message.tool_calls:
            print(f"✓ AI 请求调用 {len(assistant_message.tool_calls)} 个工具")

            # 将 AI 的消息添加到历史
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # 执行每个工具调用
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # 执行工具
                function_result = execute_tool(function_name, function_args)

                # 将工具结果添加到消息历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_result
                })

            # 继续循环，让 AI 基于工具结果生成回答
            continue

        else:
            # 没有工具调用，返回最终回答
            print("✓ AI 生成最终回答（无需工具调用）")
            return assistant_message.content

    # 达到最大迭代次数
    print(f"⚠ 达到最大迭代次数 ({max_iterations})")
    return assistant_message.content if assistant_message.content else "无法生成回答"


# ============================================================================
# 测试场景
# ============================================================================

def test_scenario_1(client, model):
    """测试场景 1: 单次工具调用"""
    print_section("测试场景 1: 单次工具调用")
    print("用户问题: 现在几点了？")

    messages = [
        {"role": "user", "content": "现在几点了？"}
    ]

    answer = chat_with_tools(client, model, messages)

    print(f"\n最终回答: {answer}")


def test_scenario_2(client, model):
    """测试场景 2: 多次工具调用"""
    print_section("测试场景 2: 多次工具调用")
    print("用户问题: 现在几点了？帮我算一下 100 + 200 等于多少")

    messages = [
        {"role": "user", "content": "现在几点了？帮我算一下 100 + 200 等于多少"}
    ]

    answer = chat_with_tools(client, model, messages)

    print(f"\n最终回答: {answer}")


def test_scenario_3(client, model):
    """测试场景 3: 不需要工具"""
    print_section("测试场景 3: 不需要工具")
    print("用户问题: 你好，请介绍一下你自己")

    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]

    answer = chat_with_tools(client, model, messages)

    print(f"\n最终回答: {answer}")


def test_scenario_4(client, model):
    """测试场景 4: 复杂计算"""
    print_section("测试场景 4: 复杂计算")
    print("用户问题: 帮我算一下 (100 + 50) * 2 - 30")

    messages = [
        {"role": "user", "content": "帮我算一下 (100 + 50) * 2 - 30"}
    ]

    answer = chat_with_tools(client, model, messages)

    print(f"\n最终回答: {answer}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    print_section("OpenAI Function Calling 测试")
    print("此测试将演示如何使用 OpenAI 的 Function Calling 功能\n")

    # 加载配置
    api_key, model_config = load_config()
    base_url = model_config['base_url']
    model = model_config['model']

    print(f"配置信息:")
    print(f"  供应商: deepseek")
    print(f"  模型: {model}")
    print(f"  API 地址: {base_url}")
    print(f"  API Key: {api_key[:10]}..." + "*" * 20)

    # 创建 OpenAI 客户端
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=30.0
    )

    # 运行测试场景
    try:
        test_scenario_1(client, model)
        test_scenario_2(client, model)
        test_scenario_3(client, model)
        test_scenario_4(client, model)

        print_section("测试完成")
        print("✓ 所有测试场景执行完毕")
        print("\n关键要点:")
        print("1. 工具定义使用 OpenAI 标准格式")
        print("2. AI 自动决定是否需要调用工具")
        print("3. 支持单次和多次工具调用")
        print("4. 工具结果会返回给 AI 生成最终回答")

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
