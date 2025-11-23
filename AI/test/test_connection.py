"""
通义千问 API 连接测试脚本
用于诊断 SSL 连接问题
"""

import json
import sys
import os
from openai import OpenAI
import httpx

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
        # 读取 API Key
        with open('Role/secret_key.json', 'r', encoding='utf-8') as f:
            secret_keys = json.load(f)
        
        # 读取配置
        with open('Role/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = secret_keys.get('qwen')
        model_config = config['qwen']['qwen-plus']
        
        return api_key, model_config
    except Exception as e:
        print(f"✗ 读取配置文件失败: {e}")
        sys.exit(1)

def test_basic_info():
    """测试基础信息"""
    print_section("[测试 1/6] 基础环境检查")
    
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    try:
        import openai
        print(f"OpenAI 库版本: {openai.__version__}")
    except:
        print("OpenAI 库版本: 未知")
    
    try:
        import httpx
        print(f"httpx 库版本: {httpx.__version__}")
    except:
        print("httpx 库版本: 未知")
    
    print("\n✓ 基础环境检查完成")

def test_network_basic(base_url):
    """测试基本网络连接"""
    print_section("[测试 2/6] 基本网络连接测试")
    
    import socket
    from urllib.parse import urlparse
    
    parsed = urlparse(base_url)
    host = parsed.netloc
    
    print(f"目标主机: {host}")
    print(f"尝试解析域名...")
    
    try:
        ip = socket.gethostbyname(host)
        print(f"✓ DNS 解析成功: {ip}")
        return True
    except socket.gaierror as e:
        print(f"✗ DNS 解析失败: {e}")
        return False

def test_https_request(base_url):
    """测试 HTTPS 请求"""
    print_section("[测试 3/6] HTTPS 连接测试 (带SSL验证)")
    
    try:
        client = httpx.Client(verify=True, timeout=30.0)
        print(f"请求地址: {base_url}")
        response = client.get(base_url)
        print(f"✓ HTTPS 连接成功")
        print(f"  状态码: {response.status_code}")
        print(f"  响应头: {dict(response.headers)}")
        client.close()
        return True
    except httpx.ConnectError as e:
        print(f"✗ HTTPS 连接失败 (ConnectError): {e}")
        return False
    except Exception as e:
        print(f"✗ HTTPS 连接失败: {type(e).__name__}: {e}")
        return False

def test_https_no_verify(base_url):
    """测试不验证SSL的HTTPS请求"""
    print_section("[测试 4/6] HTTPS 连接测试 (不验证SSL)")
    
    try:
        client = httpx.Client(verify=False, timeout=30.0)
        print(f"请求地址: {base_url}")
        response = client.get(base_url)
        print(f"✓ HTTPS 连接成功 (不验证SSL)")
        print(f"  状态码: {response.status_code}")
        client.close()
        return True
    except Exception as e:
        print(f"✗ HTTPS 连接失败: {type(e).__name__}: {e}")
        return False

def test_proxy_settings():
    """检查代理设置"""
    print_section("[测试 5/6] 代理设置检查")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']
    has_proxy = False
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"发现代理设置: {var} = {value}")
            has_proxy = True
    
    if not has_proxy:
        print("✓ 未检测到系统代理设置")
    else:
        print("\n⚠ 检测到代理设置，这可能导致 SSL 连接问题")
        print("建议: 尝试临时关闭代理再测试")
    
    return not has_proxy

def test_openai_api(api_key, model_config):
    """测试 OpenAI API 调用"""
    print_section("[测试 6/6] OpenAI API 调用测试")
    
    base_url = model_config['base_url']
    model = model_config['model']
    
    print(f"API 地址: {base_url}")
    print(f"模型: {model}")
    print(f"API Key: {api_key[:10]}..." + "*" * 20)
    
    # 测试 1: 使用默认SSL验证
    print("\n[6.1] 使用默认配置 (SSL验证=True)...")
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10,
            stream=False
        )
        
        print(f"✓ API 调用成功!")
        print(f"  响应: {response.choices[0].message.content}")
        return True, "default"
    except Exception as e:
        print(f"✗ API 调用失败: {type(e).__name__}")
        print(f"  错误详情: {e}")
    
    # 测试 2: 禁用SSL验证
    print("\n[6.2] 禁用SSL验证 (SSL验证=False)...")
    try:
        http_client = httpx.Client(verify=False, timeout=30.0)
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10,
            stream=False
        )
        
        print(f"✓ API 调用成功 (禁用SSL验证)!")
        print(f"  响应: {response.choices[0].message.content}")
        print("\n⚠ 建议: 如果此方法成功,说明是SSL证书验证问题")
        return True, "no_verify"
    except Exception as e:
        print(f"✗ API 调用失败: {type(e).__name__}")
        print(f"  错误详情: {e}")
    
    # 测试 3: 使用更长的超时时间
    print("\n[6.3] 增加超时时间 (timeout=60秒)...")
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60.0
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10,
            stream=False
        )
        
        print(f"✓ API 调用成功 (增加超时)!")
        print(f"  响应: {response.choices[0].message.content}")
        return True, "long_timeout"
    except Exception as e:
        print(f"✗ API 调用失败: {type(e).__name__}")
        print(f"  错误详情: {e}")
    
    return False, None

def main():
    """主函数"""
    print_section("通义千问 API 连接诊断工具")
    print("此工具将帮助您诊断 SSL 连接问题\n")
    
    # 加载配置
    api_key, model_config = load_config()
    base_url = model_config['base_url']
    
    print(f"配置信息:")
    print(f"  供应商: qwen")
    print(f"  模型: {model_config['model']}")
    print(f"  API 地址: {base_url}")
    print(f"  API Key: {api_key[:10]}..." + "*" * 20)
    
    # 运行测试
    results = {}
    
    # 测试 1: 基础环境
    test_basic_info()
    
    # 测试 2: 网络连接
    results['network'] = test_network_basic(base_url)
    
    # 测试 3: HTTPS (带验证)
    results['https_verify'] = test_https_request(base_url)
    
    # 测试 4: HTTPS (不验证)
    results['https_no_verify'] = test_https_no_verify(base_url)
    
    # 测试 5: 代理检查
    results['no_proxy'] = test_proxy_settings()
    
    # 测试 6: API 调用
    api_success, method = test_openai_api(api_key, model_config)
    results['api'] = api_success
    
    # 总结报告
    print_section("诊断总结")
    
    print("测试结果:")
    print(f"  DNS 解析: {'✓ 通过' if results.get('network') else '✗ 失败'}")
    print(f"  HTTPS (带SSL验证): {'✓ 通过' if results.get('https_verify') else '✗ 失败'}")
    print(f"  HTTPS (不验证SSL): {'✓ 通过' if results.get('https_no_verify') else '✗ 失败'}")
    print(f"  无代理冲突: {'✓ 是' if results.get('no_proxy') else '✗ 否'}")
    print(f"  API 调用: {'✓ 通过' if results.get('api') else '✗ 失败'}")
    
    if results.get('api'):
        print(f"\n✓ 连接测试成功! (使用方法: {method})")
        
        if method == "no_verify":
            print("\n建议修复方案:")
            print("1. 更新系统 SSL 证书")
            print("2. 在 OPEN_AI.py 中临时禁用 SSL 验证 (不推荐用于生产环境)")
            print("3. 检查是否有中间人代理或防火墙")
    else:
        print("\n✗ 连接测试失败")
        
        print("\n可能的原因:")
        if not results.get('network'):
            print("  • DNS 解析失败 - 检查网络连接或 DNS 设置")
        if not results.get('https_verify') and results.get('https_no_verify'):
            print("  • SSL 证书验证问题 - 尝试更新证书或临时禁用验证")
        if not results.get('no_proxy'):
            print("  • 代理配置冲突 - 尝试禁用代理")
        if not results.get('https_no_verify'):
            print("  • 网络连接问题 - 检查防火墙或网络设置")
        
        print("\n建议操作:")
        print("1. 尝试更换网络环境 (如切换到手机热点)")
        print("2. 检查防火墙设置,允许访问 dashscope.aliyuncs.com")
        print("3. 临时关闭 VPN 或代理")
        print("4. 更新 Python SSL 库: pip install --upgrade certifi")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

