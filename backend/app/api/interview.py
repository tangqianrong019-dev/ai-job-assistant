import uuid
import json
import re
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..llm_service import call_llm
from ..services.user_service import require_user, increment_usage

router = APIRouter()

# ---------------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------------

sessions: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

INTERVIEWER_SYSTEM = """你是一位资深技术面试官。你正在对候选人进行一场结构化的技术面试。

规则：
1. 根据 JD 和工作年限，提出由浅入深的技术问题
2. 每个回答后给出评分(1-10)、简短反馈、改进建议(2-3条)
3. 下一个问题基于候选人上一轮的表现调整难度
4. 保持专业、鼓励性的语气，但也要指出不足
5. 面试结束后给出总结性评价

输出严格的 JSON 格式（不要 Markdown 代码块）：
{
  "score": 8,
  "feedback": "回答准确，提到了XXX关键点，但可以补充YYY",
  "suggestions": ["建议1", "建议2"],
  "next_question": "下一道面试题...",
  "is_complete": false
}

当所有问题问完后，is_complete 为 true，next_question 为空字符串，feedback 改为面试总结。"""

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class StartRequest(BaseModel):
    jd_text: str = Field(description="目标岗位 JD")
    resume_text: str = Field(default="", description="候选人简历（可选）")
    question_count: int = Field(default=5, ge=3, le=10)


class StartResponse(BaseModel):
    session_id: str
    question: str
    question_number: int
    total: int


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


class AnswerResponse(BaseModel):
    score: int
    feedback: str
    suggestions: list[str]
    next_question: str
    question_number: int
    total: int
    is_complete: bool


def _extract_json(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        text = match.group(1)
    return json.loads(text)


# ---------------------------------------------------------------------------
# POST /start — begin interview session
# ---------------------------------------------------------------------------

@router.post("/start", response_model=StartResponse)
async def start_interview(request: StartRequest, user_id: str = Depends(require_user)):
    session_id = uuid.uuid4().hex[:12]

    # Generate first question
    raw = call_llm(
        prompt=(
            f"## 岗位描述\n{request.jd_text}\n\n"
            + (f"## 候选人简历\n{request.resume_text}\n\n" if request.resume_text else "")
            + f"请提出第 1 道技术面试题（共 {request.question_count} 题）。只输出纯 JSON，不要 Markdown。"
        ),
        system_prompt="""你是资深技术面试官。根据 JD 提出第一道技术面试题。
输出 JSON：{"question": "面试题内容"}""",
    )
    data = _extract_json(raw)

    sessions[session_id] = {
        "jd_text": request.jd_text,
        "resume_text": request.resume_text,
        "question_count": request.question_count,
        "current_number": 1,
        "history": [
            {"role": "assistant", "content": data["question"]}
        ],
    }

    await increment_usage(user_id)
    return StartResponse(
        session_id=session_id,
        question=data["question"],
        question_number=1,
        total=request.question_count,
    )


# ---------------------------------------------------------------------------
# POST /answer — evaluate & next question
# ---------------------------------------------------------------------------

@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(request: AnswerRequest, user_id: str = Depends(require_user)):
    session = sessions.get(request.session_id)
    if not session:
        raise ValueError("Session not found")

    q_num = session["current_number"]
    total = session["question_count"]
    is_last = q_num >= total

    session["history"].append({"role": "user", "content": request.answer})

    # Build conversation context
    context = "\n\n".join(
        f"{'面试官' if m['role'] == 'assistant' else '候选人'}：{m['content']}"
        for m in session["history"]
    )

    completion_hint = "这是最后一道题。" if is_last else ""

    raw = call_llm(
        prompt=(
            f"## 面试历史\n{context}\n\n"
            f"候选人的最新回答已经收到。{completion_hint}"
            f"请评分并{'给出总结' if is_last else '提出下一道题'}（当前第{q_num}/{total}题）。"
        ),
        system_prompt=INTERVIEWER_SYSTEM,
    )
    data = _extract_json(raw)

    session["current_number"] = q_num + 1

    if not is_last and data.get("next_question"):
        session["history"].append(
            {"role": "assistant", "content": data["next_question"]}
        )

    await increment_usage(user_id)
    return AnswerResponse(
        score=data.get("score", 0),
        feedback=data.get("feedback", ""),
        suggestions=data.get("suggestions", []),
        next_question=data.get("next_question", ""),
        question_number=q_num,
        total=total,
        is_complete=data.get("is_complete", is_last),
    )
