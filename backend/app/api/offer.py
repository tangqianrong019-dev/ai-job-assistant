from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..llm_service import call_llm
from ..services.user_service import require_user, increment_usage
import json
import re

router = APIRouter()


class OfferItem(BaseModel):
    company: str = Field(description="公司名称")
    salary: str = Field(description="薪资待遇")
    benefits: str = Field(description="福利")
    commute: str = Field(description="通勤时间")
    growth: str = Field(description="发展前景")


class OfferCompareRequest(BaseModel):
    offers: list[OfferItem] = Field(min_length=2, max_length=5)


class OfferCompareResponse(BaseModel):
    score_table: list[dict]
    analysis: str


ANALYZE_SYSTEM_PROMPT = """你是一位资深职业规划顾问。对比多个 Offer，从薪资、福利、通勤、发展前景四个维度评分并给出综合建议。

评分规则：
- 每个维度 1-10 分
- 综合分 = 各维度加权平均（薪资30%、福利15%、通勤15%、发展40%）
- 输出严格的 JSON 格式（不要 Markdown 代码块）

JSON 格式：
{
  "score_table": [
    {"company":"A公司","salary_score":8,"benefits_score":7,"commute_score":6,"growth_score":9,"overall":8.0},
    {"company":"B公司","salary_score":7,"benefits_score":9,"commute_score":8,"growth_score":6,"overall":7.0}
  ],
  "analysis": "综合分析建议（3-5段，含推荐意见、风险提示、谈判建议）"
}"""


def _extract_json(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        text = match.group(1)
    # Find outermost JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    # Fix common trailing-comma issues
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return json.loads(text)


@router.post("/compare", response_model=OfferCompareResponse)
async def compare_offers(request: OfferCompareRequest, user_id: str = Depends(require_user)):
    """多 Offer 对比分析 — 评分表 + 综合建议"""
    offer_text = "\n\n".join(
        f"Offer {i+1}：{o.company}\n"
        f"- 薪资：{o.salary}\n- 福利：{o.benefits}\n"
        f"- 通勤：{o.commute}\n- 发展前景：{o.growth}"
        for i, o in enumerate(request.offers)
    )
    raw = call_llm(prompt=offer_text, system_prompt=ANALYZE_SYSTEM_PROMPT)
    data = _extract_json(raw)
    await increment_usage(user_id)
    return OfferCompareResponse(**data)
