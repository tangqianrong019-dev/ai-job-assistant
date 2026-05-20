from .base import BaseAgent
from pydantic import BaseModel


class CareerInput(BaseModel):
    resume_text: str
    target_role: str


class CareerAdvice(BaseModel):
    career_path: list[str]
    skill_roadmap: list[str]
    short_term_goals: list[str]
    long_term_goals: list[str]


class CareerAdvisor(BaseAgent[CareerInput, CareerAdvice]):
    system_prompt = "你是一位资深职业规划师。根据候选人背景提供职业发展建议。"

    async def run(self, input_data: CareerInput) -> CareerAdvice:
        raise NotImplementedError("CareerAdvisor.run() — coming soon")
