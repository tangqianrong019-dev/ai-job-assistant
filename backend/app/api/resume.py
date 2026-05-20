from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..llm_service import call_llm
from ..services.user_service import require_user, increment_usage
import json
import re

router = APIRouter()


class ResumeOptimizeRequest(BaseModel):
    resume_text: str = Field(description="原始简历文本")
    jd_text: str = Field(description="目标岗位 JD 文本")


class RewrittenProject(BaseModel):
    original: str
    rewritten: str


class ResumeOptimizeResponse(BaseModel):
    strength_discovery: list[str]
    missing_skills: list[str]
    rewritten_projects: list[RewrittenProject]
    summary: str


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

RESUME_OPTIMIZE_PROMPT = """你是一位资深职业顾问和简历专家。对比候选人简历和目标岗位JD，输出严格的 JSON 格式（不要 Markdown 代码块，只输出纯 JSON）。

分析任务：
1. strength_discovery: 挖掘简历中被低估的亮点（量化成果、隐藏技能），输出 3-5 条
2. missing_skills: JD 明确要求但简历未提及的技能，输出 3-5 条
3. rewritten_projects: 挑出简历中 2-3 个核心项目，用 JD 中出现的术语和关键词重写描述（保留数据指标），每条含 original 和 rewritten
4. summary: 一句话总结优化方向

JSON 格式：
{
  "strength_discovery": ["亮点1", "亮点2"],
  "missing_skills": ["技能1", "技能2"],
  "rewritten_projects": [
    {"original": "原项目描述", "rewritten": "优化后描述"}
  ],
  "summary": "一句话总结"
}"""


def _extract_json(text: str) -> dict:
    """从 LLM 返回提取 JSON，兼容 Markdown 代码块"""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        text = match.group(1)
    return json.loads(text)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/optimize", response_model=ResumeOptimizeResponse)
async def optimize_resume(request: ResumeOptimizeRequest, user_id: str = Depends(require_user)):
    """简历优化 — 根据 JD 挖掘优势、发现缺失、重写项目描述"""
    raw = call_llm(
        prompt=(
            f"## 目标岗位 JD\n\n{request.jd_text}\n\n"
            f"---\n\n## 候选人简历\n\n{request.resume_text}"
        ),
        system_prompt=RESUME_OPTIMIZE_PROMPT,
    )
    data = _extract_json(raw)
    await increment_usage(user_id)
    return ResumeOptimizeResponse(**data)
