from .base import BaseAgent
from pydantic import BaseModel


class InterviewInput(BaseModel):
    jd_text: str
    question_count: int = 5


class InterviewQuestion(BaseModel):
    question: str
    expected_points: list[str]


class InterviewOutput(BaseModel):
    questions: list[InterviewQuestion]


class InterviewAgent(BaseAgent[InterviewInput, InterviewOutput]):
    system_prompt = "你是一位资深技术面试官。根据 JD 生成针对性的面试题。"

    async def run(self, input_data: InterviewInput) -> InterviewOutput:
        raise NotImplementedError("InterviewAgent.run() — coming soon")
