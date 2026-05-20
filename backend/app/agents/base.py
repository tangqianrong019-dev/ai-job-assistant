from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from pydantic import BaseModel

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class BaseAgent(ABC, Generic[TInput, TOutput]):
    """AI Agent 抽象基类 — 所有业务 Agent 继承此类。

    子类只需定义 system_prompt 并实现 run() 方法，
    基类统一管理 LLM 客户端、消息构建和响应解析。
    """

    system_prompt: str
    model_name: str = "deepseek-chat"
    temperature: float = 0.0

    @abstractmethod
    async def run(self, input_data: TInput) -> TOutput:
        """Agent 执行入口 — 子类必须实现"""
        ...

    def _build_messages(self, user_content: str) -> list[dict[str, str]]:
        """构建标准消息对 [system, user]"""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]

    def _parse_response(self, raw: Any) -> TOutput:
        """解析 LLM 原始响应为 Pydantic 模型 — 子类可覆写"""
        return raw
