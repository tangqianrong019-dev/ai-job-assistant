from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..llm_service import call_llm
from ..services.user_service import require_user, increment_usage

router = APIRouter()


class ProjectGenRequest(BaseModel):
    project_name: str = Field(description="项目名称")
    tech_stack: str = Field(description="核心技术栈，逗号分隔")
    achievements: str = Field(description="主要成就，逗号分隔")


class ProjectGenResponse(BaseModel):
    markdown: str


STAR_SYSTEM_PROMPT = """你是一位资深简历撰写专家。将用户提供的项目关键词，扩写成一条符合 STAR 原则（Situation-Task-Action-Result）的项目经历描述。

要求：
1. 使用量化数据增强说服力（如 "提升 30%", "支撑日均 10 万+ 请求"）
2. 突出个人贡献，使用动词开头（设计、主导、优化、搭建）
3. 技术关键词自然融入描述中，不堆砌
4. 控制长度在 60-120 字，简洁有力
5. 输出纯 Markdown 格式（不要代码块包裹），适合直接粘贴到简历中
6. 用 ### 打头作为项目标题，下方一段描述"""


@router.post("/generate", response_model=ProjectGenResponse)
async def generate_project(request: ProjectGenRequest, user_id: str = Depends(require_user)):
    """根据关键词生成 STAR 原则的项目经历 Markdown"""
    raw = call_llm(
        prompt=(
            f"项目名称：{request.project_name}\n"
            f"核心技术栈：{request.tech_stack}\n"
            f"主要成就：{request.achievements}"
        ),
        system_prompt=STAR_SYSTEM_PROMPT,
    )
    await increment_usage(user_id)
    return ProjectGenResponse(markdown=raw.strip())
