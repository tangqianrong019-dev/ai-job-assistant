"""AI 求职助手 — Vercel Python Serverless 后端"""
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel

from _lib.llm import call_llm, call_llm_json
from _lib.auth import get_current_user, get_current_user_with_quota
from _lib.user_service import get_user_profile, increment_usage

app = FastAPI(title="AI 求职助手 API")

cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000,https://frontend-xi-one-82.vercel.app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins.split(",") if o.strip()],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# ============================================================
# Models
# ============================================================
class JDMatchRequest(BaseModel):
    resume_text: str
    jd_text: str

class ResumeOptimizeRequest(BaseModel):
    resume_text: str
    jd_text: str

class InterviewStartRequest(BaseModel):
    jd_text: str
    resume_text: str = ""
    question_count: int = 5

class InterviewAnswerRequest(BaseModel):
    session_id: str
    answer: str

class ProjectGenRequest(BaseModel):
    project_name: str
    tech_stack: str
    achievements: str

class OfferCompareRequest(BaseModel):
    offers: list

class PaymentRequest(BaseModel):
    annual: bool = False

# ============================================================
# Health
# ============================================================
@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "app": "AI 求职助手 (Vercel)"}

# ============================================================
# JD 匹配分析
# ============================================================
@app.post("/api/v1/jobs/match")
async def jd_match(req: JDMatchRequest, user_id: str = Depends(get_current_user_with_quota)):
    result = call_llm_json(
        prompt=f"## 简历\n{req.resume_text}\n\n## JD\n{req.jd_text}",
        system_prompt="""你是资深招聘专家。分析简历和JD的匹配度，返回严格JSON（不要markdown代码块）：
{"match_percentage": 85, "match_summary": "2-3句总结", "core_overlap": ["技能1","技能2"], "missing_skills": [{"skill":"技能名","importance":"required"}], "suggestions": ["改进建议1","改进建议2"]}""",
    )
    await increment_usage(user_id)
    return result

# ============================================================
# 简历优化
# ============================================================
@app.post("/api/v1/resume/optimize")
async def resume_optimize(req: ResumeOptimizeRequest, user_id: str = Depends(get_current_user_with_quota)):
    result = call_llm_json(
        prompt=f"## 简历\n{req.resume_text}\n\n## JD\n{req.jd_text}",
        system_prompt="""你是资深职业顾问。根据JD深度优化简历，返回严格JSON：
{"strength_discovery": ["隐藏优势1"], "missing_skills": ["缺失技能1"], "rewritten_projects": [{"original":"原版","rewritten":"优化版"}], "summary": "总体评价"}""",
    )
    await increment_usage(user_id)
    return result

# ============================================================
# AI 模拟面试
# ============================================================
INTERVIEW_SESSIONS: dict = {}

@app.post("/api/v1/interview/start")
async def interview_start(req: InterviewStartRequest, user_id: str = Depends(get_current_user_with_quota)):
    import uuid
    sid = str(uuid.uuid4())[:8]
    question = call_llm(
        prompt=f"JD: {req.jd_text}\n简历: {req.resume_text}\n请出第1道面试题（共{req.question_count}题）。只返回题目本身。",
        system_prompt="你是资深面试官。根据JD和简历出针对性面试题。只返回题目本身，不要额外解释。",
    )
    INTERVIEW_SESSIONS[sid] = {"current": 1, "total": req.question_count, "jd": req.jd_text, "resume": req.resume_text}
    await increment_usage(user_id)
    return {"session_id": sid, "question": question.strip(), "question_number": 1, "total": req.question_count}

@app.post("/api/v1/interview/answer")
async def interview_answer(req: InterviewAnswerRequest, user_id: str = Depends(get_current_user)):
    session = INTERVIEW_SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")
    result = call_llm_json(
        prompt=f"用户回答：{req.answer}\n当前第{session['current']}/{session['total']}题",
        system_prompt="""你是面试官。评估回答并决定是否继续。返回严格JSON：
{"score": 8, "feedback": "评价内容", "suggestions": ["改进建议1"], "next_question": "下一题（最后一题时返回空字符串）", "question_number": 1, "total": 5, "is_complete": false}
评分1-10。is_complete在当前题目等于total时为true。""",
    )
    session["current"] += 1
    return result

# ============================================================
# 项目经历生成
# ============================================================
@app.post("/api/v1/project/generate")
async def project_gen(req: ProjectGenRequest, user_id: str = Depends(get_current_user_with_quota)):
    markdown = call_llm(
        prompt=f"项目名称：{req.project_name}\n技术栈：{req.tech_stack}\n主要成就：{req.achievements}\n请用STAR原则生成专业项目描述。",
        system_prompt="你是技术写作专家。用STAR原则（情境、任务、行动、结果）生成专业项目描述Markdown。以"## 项目描述"开头。",
    )
    await increment_usage(user_id)
    return {"markdown": markdown.strip()}

# ============================================================
# Offer 对比
# ============================================================
@app.post("/api/v1/offer/compare")
async def offer_compare(req: OfferCompareRequest, user_id: str = Depends(get_current_user_with_quota)):
    result = call_llm_json(
        prompt=f"请对比分析以下Offer：{req.offers}",
        system_prompt="""你是职业规划顾问。从薪资、福利、通勤、成长四个维度打分（1-10），返回JSON：
{"score_table": [{"company":"公司名","salary_score":8,"benefits_score":7,"commute_score":6,"growth_score":9,"overall":7.5}], "analysis": "对比分析总结"}""",
    )
    await increment_usage(user_id)
    return result

# ============================================================
# 文件解析
# ============================================================
@app.post("/api/v1/files/parse")
async def files_parse(request: Request, user_id: str = Depends(get_current_user)):
    try:
        content_type = request.headers.get("content-type", "")
        if "multipart" not in content_type:
            raise HTTPException(status_code=400, detail="仅支持multipart上传")

        form = await request.form()
        file = form.get("file")
        if not file:
            raise HTTPException(status_code=400, detail="未找到文件")

        filename = (file.filename or "").lower()
        raw = await file.read()

        if filename.endswith(".pdf"):
            try:
                from PyPDF2 import PdfReader
                import io
                text = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(raw)).pages)
            except ImportError:
                text = f"[PDF文件] {file.filename}"
        elif filename.endswith((".docx", ".doc")):
            try:
                from docx import Document
                import io
                text = "\n".join(p.text for p in Document(io.BytesIO(raw)).paragraphs)
            except ImportError:
                text = f"[Word文件] {file.filename}"
        else:
            text = raw.decode("utf-8", errors="ignore")

        return {"text": text, "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# 支付
# ============================================================
@app.post("/api/v1/payment/create-checkout")
async def create_checkout(req: PaymentRequest = PaymentRequest(), user_id: str = Depends(get_current_user)):
    checkout_url = os.environ.get("LEMON_SQUEEZY_CHECKOUT_URL", "")
    if req.annual:
        checkout_url = os.environ.get("LEMON_SQUEEZY_CHECKOUT_URL_YEARLY", checkout_url)
    return {"checkout_url": f"{checkout_url}?checkout[custom][user_id]={user_id}"}

@app.post("/api/v1/payment/webhook")
async def payment_webhook(request: Request):
    return {"received": True}

# ============================================================
# 用户信息
# ============================================================
@app.get("/api/v1/user/profile")
async def user_profile(user_id: str = Depends(get_current_user)):
    profile = await get_user_profile(user_id)
    return profile or {"id": user_id, "subscription_status": "free", "usage_count": 0}

# ============================================================
# Vercel handler
# ============================================================
handler = Mangum(app, lifespan="off")
