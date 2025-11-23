#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话接口主程序
使用 AIManager.py 中的 AIFactory 进行双AI协同对话
"""

import os
import sys
import json

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from Agent.AIManager import AIFactory
from Agent.ConversationHandler import ConversationHandler


def main():
    """主函数"""
    print("=" * 80)
    print("双AI协同对话系统")
    print("=" * 80)
    
    # 创建 AIFactory 实例
    print("\n[初始化] 创建 AIFactory 实例...")
    factory = AIFactory()
    print("✓ AIFactory 实例创建成功")
    
    # 配置双模型
    dialogue_vendor = "deepseek"        # 对话模型供应商
    dialogue_model = "deepseek-chat"    # 对话模型名称
    knowledge_vendor = "deepseek"       # 知识模型供应商
    knowledge_model = "deepseek-chat"   # 知识模型名称
    
    try:
        # 连接双AI模型
        print("\n[连接] 正在连接双AI模型...")
        print(f"  - 对话模型: {dialogue_vendor}/{dialogue_model}")
        print(f"  - 知识模型: {knowledge_vendor}/{knowledge_model}")
        
        factory.connect(
            dialogue_vendor=dialogue_vendor,
            dialogue_model_name=dialogue_model,
            knowledge_vendor=knowledge_vendor,
            knowledge_model_name=knowledge_model
        )
        print("✓ 双AI模型连接成功！")
        
        # 创建对话处理器
        print("\n[初始化] 创建对话处理器...")
        conversation_handler = ConversationHandler(
            knowledge_callback=factory.knowledge_callback,
            dialogue_callback=factory.dialogue_callback,
            knowledge_history=factory.knowledge_ai_client._history,
            dialogue_history=factory.dialogue_ai_client._history,
            default_output_file=factory.default_output_file
        )
        print("✓ 对话处理器创建成功！")
        
        # 显示模型信息
        print(f"\n[对话模型信息]")
        if factory.dialogue_ai:
            print(f"  供应商: {dialogue_vendor}")
            print(f"  模型: {factory.dialogue_ai.model}")
            print(f"  Max Tokens: {factory.dialogue_ai.max_tokens}")
        
        print(f"\n[知识模型信息]")
        if factory.knowledge_ai:
            print(f"  供应商: {knowledge_vendor}")
            print(f"  模型: {factory.knowledge_ai.model}")
            print(f"  Max Tokens: {factory.knowledge_ai.max_tokens}")
        
        print(f"\n[文件操作配置]")
        if factory.default_output_file:
            print(f"  默认输出路径: {factory.default_output_file}")
        else:
            print(f"  ⚠️  严格模式：所有文件操作必须在 JSON 中明确指定文件路径")
        
        # 开始对话循环
        print("\n" + "=" * 80)
        print("开始对话（输入 'exit' 或 'quit' 退出，Ctrl+C 强制退出）")
        print("=" * 80)
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n用户: ").strip()
                
                if not user_input:
                    continue
                
                # 检查退出命令
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("\n再见！")
                    break
                
                # 发送消息并获取回复
                print("\nAI: ", end="", flush=True)
                result = conversation_handler.send_message(user_input)
                
                # 显示结果摘要
                if result:
                    query_results = result.get("query_results", [])
                    if query_results:
                        print(f"\n[信息] 本次查询共执行了 {len(query_results)} 个数据查询任务")
                    
                    # 显示输出文件信息
                    output_file = result.get("output_file")
                    if output_file:
                        print(f"\n" + "=" * 80)
                        print(f"[文件输出] PLC程序已保存")
                        print(f"文件路径: {output_file}")
                        print("=" * 80)
            
            except KeyboardInterrupt:
                print("\n\n程序被中断，再见！")
                break
            except Exception as e:
                print(f"\n[错误] 处理消息时出错: {e}")
                import traceback
                traceback.print_exc()
        
        # 断开连接
        print("\n[断开] 正在断开连接...")
        factory.disconnect()
        print("✓ 已断开所有模型连接")
        
    except FileNotFoundError as e:
        print(f"\n✗ 错误: {e}")
        print("请检查配置文件是否存在：")
        print("  - Role/secret_key.json")
        print("  - Role/config.json")
    except ValueError as e:
        print(f"\n✗ 错误: {e}")
        print("请检查配置文件中的模型配置")
    except Exception as e:
        print(f"\n✗ 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n[提示]")
    print("1. 确保 Role/secret_key.json 中已配置正确的 API 密钥")
    print("2. 确保 Role/config.json 中有对应模型的配置")
    print("3. 系统使用双AI协同：知识模型负责查询规划，对话模型负责生成回答")


if __name__ == "__main__":
    main()
