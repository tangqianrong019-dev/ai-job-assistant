"""
统一 LLM 服务层 — 基于 OpenAI SDK 兼容接口
支持 DeepSeek / Gemini，通过环境变量切换 Provider
"""

import os
from openai import OpenAI


class LLMService:
    """OpenAI SDK 兼容的 LLM 客户端，支持多 Provider 切换"""

    def __init__(self, provider: str = "deepseek"):
        self.provider = provider

        if provider == "deepseek":
            self.client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1",
            )
            self.model = "deepseek-chat"

        elif provider == "gemini":
            self.client = OpenAI(
                api_key=os.getenv("GEMINI_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            self.model = "gemini-2.0-flash"

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def call_llm(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """调用 LLM 并返回文本响应

        Args:
            prompt: 用户输入
            system_prompt: 可选系统提示词
            temperature: 生成温度 (0-2)
            max_tokens: 最大输出 token 数

        Returns:
            LLM 返回的文本内容
        """
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def call_llm(
    prompt: str,
    provider: str = "deepseek",
    system_prompt: str | None = None,
    temperature: float = 0.7,
) -> str:
    """便捷函数 — 单次 LLM 调用，无需手动管理实例"""
    service = LLMService(provider=provider)
    return service.call_llm(prompt, system_prompt=system_prompt, temperature=temperature)
