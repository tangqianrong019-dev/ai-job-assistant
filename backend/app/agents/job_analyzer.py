"""
JD Analysis Agent — 岗位匹配语义分析
使用 LangChain + DeepSeek API 对简历和 JD 进行深度语义匹配
"""

from typing import Literal
from pydantic import BaseModel, Field
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage


# ---------------------------------------------------------------------------
# Output schemas
# ---------------------------------------------------------------------------

class SkillGap(BaseModel):
    """JD 要求但候选人缺失的技能"""

    skill: str = Field(description="技能名称")
    importance: Literal["required", "preferred", "bonus"] = Field(
        description="JD 中对这项技能的要求级别"
    )


class JDAnalysisResult(BaseModel):
    """简历 vs JD 语义匹配分析结果"""

    match_score: int = Field(description="综合匹配度评分 1-10", ge=1, le=10)
    match_summary: str = Field(description="2-3 句话的匹配度综合评价")
    core_overlap: list[str] = Field(description="候选人具备且 JD 明确要求的关键技能")
    missing_skills: list[SkillGap] = Field(
        description="JD 要求但候选人简历中未体现的技能"
    )
    strength_analysis: str = Field(description="候选人相对该岗位的核心优势")
    gap_analysis: str = Field(description="差距分析与针对性提升建议")


# ---------------------------------------------------------------------------
# Prompt engineering
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
你是一位资深技术招聘专家和职业顾问。你的任务是对比候选人简历与职位描述(JD)，进行深度语义匹配分析。

分析规则：
1. 综合评估技能、工作经验、项目复杂度、教育背景四个维度，给出 1-10 的匹配度评分
2. 逐条对比 JD 中列出的技术要求与简历中体现的能力，找出精确重合点
3. 理解技能间的等价与衍生关系（如"React 生态"包含 Redux/Next.js，"后端开发"包含 API 设计/数据库），不做死板关键词匹配
4. JD 中标记"必须"/"required"的技能缺失时，missing_skills 中 importance 标为"required"
5. 工作年限要求、行业背景等软性条件也纳入考量，体现在 match_score 和摘要中
6. gap_analysis 给出具体可行的提升路径，而非泛泛而谈
"""


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class JobAnalyzer:
    """JD 分析 Agent — 简历与岗位描述语义匹配"""

    def __init__(
        self,
        model_name: str = "deepseek-chat",
        temperature: float = 0.0,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        kwargs: dict = {"model": model_name, "temperature": temperature}
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["api_base"] = base_url

        self.llm = ChatDeepSeek(**kwargs)
        self.structured_llm = self.llm.with_structured_output(JDAnalysisResult)

    # ------------------------------------------------------------------
    # Core workflow
    # ------------------------------------------------------------------

    async def analysis_workflow(
        self, resume_text: str, jd_text: str
    ) -> JDAnalysisResult:
        """核心分析流程 — 简历 vs JD 语义匹配。

        Args:
            resume_text: 从 PDF 简历中提取的纯文本内容
            jd_text: 职位描述的完整文本

        Returns:
            JDAnalysisResult: 包含匹配度、技能重合/缺口的结构化分析
        """
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"## 候选人简历\n\n{resume_text}\n\n"
                    f"---\n\n## 职位描述 (JD)\n\n{jd_text}"
                )
            ),
        ]

        result: JDAnalysisResult = await self.structured_llm.ainvoke(messages)
        return result

    # ------------------------------------------------------------------
    # Sync wrapper
    # ------------------------------------------------------------------

    def analysis_workflow_sync(self, resume_text: str, jd_text: str) -> JDAnalysisResult:
        """analysis_workflow 的同步版本，用于不支持异步的调用场景"""
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"## 候选人简历\n\n{resume_text}\n\n"
                    f"---\n\n## 职位描述 (JD)\n\n{jd_text}"
                )
            ),
        ]
        return self.structured_llm.invoke(messages)

    # ------------------------------------------------------------------
    # Batch — 1 resume vs N JDs
    # ------------------------------------------------------------------

    async def analyze_batch(
        self, resume_text: str, jds: list[dict[str, str]]
    ) -> list[JDAnalysisResult]:
        """批量分析：一份简历对比多个岗位（岗位推荐场景）

        Args:
            resume_text: 简历文本
            jds: [{"title": "后端开发工程师", "text": "..."}, ...]

        Returns:
            按输入顺序返回每个 JD 的分析结果
        """
        results: list[JDAnalysisResult] = []
        for jd in jds:
            result = await self.analysis_workflow(resume_text, jd["text"])
            results.append(result)
        return results
