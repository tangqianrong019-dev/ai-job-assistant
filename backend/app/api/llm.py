from fastapi import APIRouter
from pydantic import BaseModel, Field
from ..llm_service import call_llm

router = APIRouter()


class TestLLMRequest(BaseModel):
    prompt: str = Field(description="测试提示词")
    provider: str = Field(default="deepseek", description="LLM Provider: deepseek | gemini")
    system_prompt: str | None = Field(default=None, description="可选系统提示词")


class TestLLMResponse(BaseModel):
    provider: str
    prompt: str
    response: str


@router.post("/test", response_model=TestLLMResponse)
async def test_llm(request: TestLLMRequest):
    """测试 LLM 连通性 — 发送 prompt 并返回模型回复"""
    text = call_llm(
        prompt=request.prompt,
        provider=request.provider,
        system_prompt=request.system_prompt,
    )
    return TestLLMResponse(
        provider=request.provider,
        prompt=request.prompt,
        response=text,
    )
