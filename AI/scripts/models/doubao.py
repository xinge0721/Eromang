# 豆包大模型API封装类（字节跳动）
import json
import tiktoken

class Doubao:
    def __init__(self, message: dict):
        self.api_key = message.get("key")
        self.base_url = message.get("params").get("base_url")
        self.model = message.get("params").get("model")
        self.max_tokens = message.get("params").get("max_tokens", 32000)  # 从配置读取，默认32000

        # 豆包模型兼容OpenAI接口，使用tiktoken进行token计算
        # 根据官方文档，豆包使用cl100k_base编码器（与OpenAI的GPT-3.5/4相同）
        try:
            print(f"正在加载 Doubao tokenizer (cl100k_base)...")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            print(f"✓ Tokenizer 加载成功")
        except Exception as e:
            print(f"警告：无法加载tiktoken，将回退到字符计数估算。错误: {e}")
            self.tokenizer = None
        
    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def set_base_url(self, base_url: str):
        self.base_url = base_url

    def set_model(self, model: str):
        self.model = model

    #  ============ 生成链接参数 ============
    def gen_params(self):
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
        }
    #  ============ 生成请求参数 ============
    def gen_request(self, messages: list):
        """
        生成请求参数
        会读取和保存对话历史，并生成请求体
        """
        # 生成请求参数
        return {
            "model": self.model,
            "messages": messages,  # 豆包使用标准的messages格式
        }
        
    #  ============ 生成请求参数(流式) ============
    def gen_params_stream(self, messages: list):
        """
        生成流式请求参数
        """
        return {
            "model": self.model,
            "messages": messages,  # 豆包使用标准的messages格式
            "stream": True,
            "stream_options": {"include_usage": True}
        }

    #  ============ 判断流式是否结束 ============
    def is_stream_end(self, stream_options: dict) -> bool:
        """
        判断流式是否结束
        usage 字段为 None 表示还在传输数据，否则为结束
        """
        # usage 字段为 None，则说明还在传输，非None视为结束
        usage = stream_options.get("usage", None)
        return usage is not None
        
    #  ============ 提取流式信息数据 ============
    def extract_stream_info(self, stream_options: dict) -> str:
        """
        提取流式信息数据, 提取delta.content字段
        """
        # 'choices' 应为一个list
        choices = stream_options.get('choices', [])
        if not choices or not isinstance(choices, list):
            return None
        choice = choices[0]
        delta = choice.get('delta', {}) if isinstance(choice, dict) else {}
        return delta.get('content', None)

    #  ============ 计算token的回调函数 ============
    def token_callback(self, content: str) -> int:
        """
        计算豆包模型的token数
        豆包兼容OpenAI接口，使用tiktoken的cl100k_base编码器计算token
        如果tiktoken不可用，则回退到字符数估算（1个汉字≈2token，英文约4字符≈1token）
        """
        if not content:
            return 0
        
        if self.tokenizer:
            # 使用tiktoken计算（精确）
            return len(self.tokenizer.encode(content))
        else:
            # 回退方案：简单估算
            # 统计中文字符和其他字符
            chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
            other_chars = len(content) - chinese_chars
            # cl100k_base编码：1个汉字≈2token（根据官方数据），英文约4字符≈1token
            return int(chinese_chars * 2 + other_chars / 4)
