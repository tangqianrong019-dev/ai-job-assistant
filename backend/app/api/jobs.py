from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..agents.job_analyzer import JobAnalyzer, JDAnalysisResult
from ..llm_service import call_llm
from ..core.auth_deps import get_current_user_with_quota
from ..services.user_service import increment_usage
import json
import re

router = APIRouter()


class JDAnalyzeRequest(BaseModel):
    resume_text: str = Field(description="PDF 简历提取后的纯文本")
    jd_text: str = Field(description="职位描述完整文本")


class JDAnalyzeResponse(BaseModel):
    match_score: int
    match_summary: str
    core_overlap: list[str]
    missing_skills: list[dict]
    strength_analysis: str
    gap_analysis: str


# ---------------------------------------------------------------------------
# System prompt for JD analysis via simple LLM call (no LangChain)
# ---------------------------------------------------------------------------

JD_MATCH_SYSTEM_PROMPT = """你是一位资深技术招聘专家。对比候选人简历与职位描述(JD)，输出严格的 JSON 格式（不要 Markdown 代码块，只输出纯 JSON）。

分析要求：
1. 综合技能、经验、学历给出 match_percentage (0-100)
2. core_overlap: JD 和简历都具备的技能
3. missing_skills: JD 要求但简历缺失的 [{ "skill": "技能名", "importance": "required|preferred|bonus" }]
4. suggestions: 3-5 条具体可行的提升建议

JSON 格式：
{
  "match_percentage": 75,
  "match_summary": "2-3句综合评语",
  "core_overlap": ["Python", "Django"],
  "missing_skills": [{"skill": "K8s", "importance": "required"}],
  "suggestions": ["建议1", "建议2", "建议3"]
}"""


def _extract_json(text: str) -> dict:
    """从 LLM 返回文本中提取 JSON，兼容 Markdown 代码块包裹"""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        text = match.group(1)
    return json.loads(text)


# ---------------------------------------------------------------------------
# Existing endpoint — LangChain-based
# ---------------------------------------------------------------------------

@router.post("/analyze", response_model=JDAnalyzeResponse)
async def analyze_jd(request: JDAnalyzeRequest):
    """简历 vs JD 语义匹配分析（LangChain structured output）"""
    agent = JobAnalyzer()
    result: JDAnalysisResult = await agent.analysis_workflow(
        resume_text=request.resume_text,
        jd_text=request.jd_text,
    )
    return JDAnalyzeResponse(
        match_score=result.match_score,
        match_summary=result.match_summary,
        core_overlap=result.core_overlap,
        missing_skills=[s.model_dump() for s in result.missing_skills],
        strength_analysis=result.strength_analysis,
        gap_analysis=result.gap_analysis,
    )


# ---------------------------------------------------------------------------
# New endpoint — llm_service.py based (simpler, user-requested)
# ---------------------------------------------------------------------------

class JDMatchResponse(BaseModel):
    match_percentage: int
    match_summary: str
    core_overlap: list[str]
    missing_skills: list[dict]
    suggestions: list[str]


@router.post("/match", response_model=JDMatchResponse)
async def jd_match(request: JDAnalyzeRequest, user_id: str = Depends(get_current_user_with_quota)):
    """简历 vs JD 匹配度分析 — 基于 llm_service.call_llm()"""
    raw = call_llm(
        prompt=f"## 候选人简历\n\n{request.resume_text}\n\n---\n\n## 职位描述\n\n{request.jd_text}",
        system_prompt=JD_MATCH_SYSTEM_PROMPT,
    )
    data = _extract_json(raw)
    await increment_usage(user_id)
    return JDMatchResponse(**data)
