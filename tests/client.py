import asyncio
import json
import sys
import os
from pydantic import AnyUrl
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent, ImageContent, EmbeddedResource

async def debug_mcp_server():
    """详细调试MCP服务器，打印所有可用信息"""
    
    # 配置服务器参数
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"]  # 替换为您的服务器文件
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("=" * 60)
                print("MCP 服务器调试信息")
                print("=" * 60)
                
                # 1. 初始化连接
                print("\n1. 初始化连接...")
                init_result = await session.initialize()
                print(f"初始化结果: {init_result}")
                
                # 2. 获取服务器信息
                print("\n2. 服务器信息:")
                print(f"   - 协议版本: {getattr(init_result, 'protocolVersion', 'N/A')}")
                print(f"   - 服务器版本: {getattr(init_result, 'serverVersion', 'N/A')}")
                print(f"   - 服务器能力: {getattr(init_result, 'capabilities', 'N/A')}")
                
                # 3. 列出所有工具
                print("\n3. 可用工具:")
                tools_response = await session.list_tools()
                # for i, tool in enumerate(tools_response.tools):
                #     print(f"   [{i}] {tool.name}")
                #     print(f"       描述: {tool.description}")
                #     print(f"       输入模式: {tool.inputSchema}")
                #     if hasattr(tool, 'outputSchema'):
                #         print(f"       输出模式: {tool.outputSchema}")
                #     if hasattr(tool, 'title'):
                #         print(f"       标题: {tool.title}")
                #     print()
                print(tools_response.tools[1]) 
                # 4. 列出所有资源模板
                print("\n4. 资源模板:")
                templates_response = await session.list_resource_templates()
                for i, template in enumerate(templates_response.resourceTemplates):
                    print(f"   [{i}] {template.uriTemplate}")
                    print(f"       名称: {template.name}")
                    print(f"       描述: {template.description}")
                    if hasattr(template, 'title'):
                        print(f"       标题: {template.title}")
                    print()
                
                # 5. 列出所有资源
                print("\n5. 具体资源:")
                resources_response = await session.list_resources()
                for i, resource in enumerate(resources_response.resources):
                    print(f"   [{i}] {resource.uri}")
                    print(f"       名称: {resource.name}")
                    print(f"       描述: {resource.description}")
                    if hasattr(resource, 'mimeType'):
                        print(f"       MIME类型: {resource.mimeType}")
                    print()
                
                # 6. 列出所有提示词
                print("\n6. 提示词:")
                prompts_response = await session.list_prompts()
                for i, prompt in enumerate(prompts_response.prompts):
                    print(f"   [{i}] {prompt.name}")
                    print(f"       描述: {prompt.description}")
                    if hasattr(prompt, 'arguments'):
                        print(f"       参数: {prompt.arguments}")
                    print()
                
                # 7. 测试工具调用（如果有工具）
                if tools_response.tools:
                    print("\n7. 工具调用测试:")
                    first_tool = tools_response.tools[0]
                    print(f"   测试工具: {first_tool.name}")
                    
                    try:
                        # 尝试调用工具，使用简单的参数
                        test_args = {}
                        if hasattr(first_tool, 'inputSchema') and first_tool.inputSchema:
                            schema = first_tool.inputSchema
                            # 尝试从输入模式中提取简单参数
                            if 'properties' in schema:
                                for prop_name, prop_details in schema['properties'].items():
                                    if 'type' in prop_details:
                                        if prop_details['type'] == 'string':
                                            test_args[prop_name] = "test"
                                        elif prop_details['type'] == 'number':
                                            test_args[prop_name] = 1
                                        elif prop_details['type'] == 'integer':
                                            test_args[prop_name] = 1
                                        elif prop_details['type'] == 'boolean':
                                            test_args[prop_name] = True
                        
                        print(f"   调用参数: {test_args}")
                        tool_result = await session.call_tool(first_tool.name, arguments=test_args)
                        
                        print(f"   调用结果:")
                        print(f"     - 是否错误: {tool_result.isError}")
                        print(f"     - 内容类型: {type(tool_result.content)}")
                        print(f"     - 内容长度: {len(tool_result.content)}")
                        
                        for j, content in enumerate(tool_result.content):
                            print(f"       [{j}] {type(content)}")
                            if hasattr(content, 'type'):
                                print(f"           类型: {content.type}")
                            if hasattr(content, 'text'):
                                print(f"           文本: {content.text}")
                            if hasattr(content, 'data'):
                                print(f"           数据大小: {len(content.data)} 字节")
                            if hasattr(content, 'mimeType'):
                                print(f"           MIME类型: {content.mimeType}")
                        
                        if hasattr(tool_result, 'structuredContent') and tool_result.structuredContent:
                            print(f"     - 结构化内容: {json.dumps(tool_result.structuredContent, indent=10, ensure_ascii=False)}")
                        
                    except Exception as e:
                        print(f"   工具调用失败: {e}")
                
                # 8. 测试资源读取（如果有资源）
                if resources_response.resources:
                    print("\n8. 资源读取测试:")
                    first_resource = resources_response.resources[0]
                    print(f"   测试资源: {first_resource.uri}")
                    
                    try:
                        resource_result = await session.read_resource(AnyUrl(str(first_resource.uri)))
                        print(f"   资源读取结果:")
                        print(f"     - 内容类型: {type(resource_result.contents)}")
                        print(f"     - 内容长度: {len(resource_result.contents)}")
                        
                        for k, content in enumerate(resource_result.contents):
                            print(f"       [{k}] {type(content)}")
                            if hasattr(content, 'type'):
                                print(f"           类型: {content.type}")
                            if hasattr(content, 'text'):
                                print(f"           文本: {content.text}")
                            if hasattr(content, 'data'):
                                print(f"           数据大小: {len(content.data)} 字节")
                            if hasattr(content, 'mimeType'):
                                print(f"           MIME类型: {content.mimeType}")
                                
                    except Exception as e:
                        print(f"   资源读取失败: {e}")
                
                # 9. 测试提示词获取（如果有提示词）
                if prompts_response.prompts:
                    print("\n9. 提示词获取测试:")
                    first_prompt = prompts_response.prompts[0]
                    print(f"   测试提示词: {first_prompt.name}")
                    
                    try:
                        # 尝试获取提示词
                        prompt_args = {}
                        if hasattr(first_prompt, 'arguments'):
                            for arg in first_prompt.arguments:
                                if hasattr(arg, 'name'):
                                    prompt_args[arg.name] = "示例值"
                        
                        prompt_result = await session.get_prompt(first_prompt.name, arguments=prompt_args)
                        print(f"   提示词获取结果:")
                        print(f"     - 描述: {getattr(prompt_result, 'description', 'N/A')}")
                        print(f"     - 消息数量: {len(prompt_result.messages)}")
                        
                        for m, message in enumerate(prompt_result.messages):
                            print(f"       消息 [{m}]:")
                            print(f"         - 角色: {message.role}")
                            if hasattr(message, 'content'):
                                content = message.content
                                if hasattr(content, 'text'):
                                    print(f"         - 文本: {content.text}")
                    
                    except Exception as e:
                        print(f"   提示词获取失败: {e}")
                
                print("\n" + "=" * 60)
                print("调试完成!")
                print("=" * 60)
                
    except Exception as e:
        print(f"连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 检查服务器文件是否存在
    if not os.path.exists("server.py"):
        print("错误: 当前目录下没有找到 server.py 文件")
        print("请确保服务器文件存在，或者修改脚本中的服务器路径")
    else:
        asyncio.run(debug_mcp_server())