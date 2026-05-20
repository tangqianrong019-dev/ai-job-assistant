"""用户用量限制服务"""

from fastapi import HTTPException, Request
from ..core.supabase import supabase

FREE_LIMIT = 5


class UsageLimitError(HTTPException):
    def __init__(self, detail: str = "免费用户次数已用完，请升级至 Pro 版"):
        super().__init__(status_code=403, detail=detail)


async def get_user_profile(user_id: str) -> dict | None:
    """查询用户 profile"""
    return await supabase._get("user_profiles", {"id": user_id})


async def check_usage_limit(user_id: str) -> dict:
    """检查用户是否有剩余调用次数，通过则返回 profile。

    Raises:
        UsageLimitError: 免费用户已达到 3 次上限
    """
    profile = await get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在，请先注册")

    sub = profile.get("subscription_status", "free")
    count = profile.get("usage_count", 0)

    if sub == "free" and count >= FREE_LIMIT:
        raise UsageLimitError()

    return profile


async def increment_usage(user_id: str) -> dict:
    """调用次数 +1，返回更新后的 profile"""
    profile = await get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")

    new_count = profile.get("usage_count", 0) + 1
    return await supabase._patch(
        "user_profiles",
        {"id": user_id},
        {"usage_count": new_count},
    )


async def check_and_increment(user_id: str) -> dict:
    """组合操作：先检查限制，通过后递增 —— API 调用此函数"""
    await check_usage_limit(user_id)
    return await increment_usage(user_id)


# ---------------------------------------------------------------------------
# FastAPI 依赖 — 从 Header 提取 user_id 并校验
# ---------------------------------------------------------------------------

async def require_user(request: Request) -> str:
    """从 X-User-Id header 提取用户 ID，并检查用量限制"""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="缺少 X-User-Id header")
    await check_usage_limit(user_id)
    return user_id
