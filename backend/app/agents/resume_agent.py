from .base import BaseAgent
from pydantic import BaseModel


class ResumeInput(BaseModel):
    content: str


class ResumeAnalysis(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]


class ResumeAgent(BaseAgent[ResumeInput, ResumeAnalysis]):
    system_prompt = "你是一位资深简历顾问。分析简历并提供改进建议。"

    async def run(self, input_data: ResumeInput) -> ResumeAnalysis:
        raise NotImplementedError("ResumeAgent.run() — coming soon")
