"""认证 — JWT 本地 decode + Supabase API fallback"""
import os, httpx, jwt
from fastapi import HTTPException, Request


async def get_current_user(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Authorization: Bearer <token>")
    token = auth[7:]
    user_id = None

    # 方式1: 本地JWT
    try:
        payload = jwt.decode(token, os.environ.get("SUPABASE_JWT_SECRET", ""), algorithms=["HS256"], options={"verify_exp": True, "require": ["sub"]})
        user_id = payload["sub"]
    except Exception:
        # 方式2: Supabase API
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f'{os.environ.get("SUPABASE_URL")}/auth/v1/user',
                    headers={"Authorization": f"Bearer {token}", "apikey": os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")},
                )
            if resp.status_code == 200:
                user_id = resp.json()["id"]
        except Exception:
            pass

    if not user_id:
        raise HTTPException(status_code=401, detail="无效的 Token，请重新登录")
    return user_id


async def get_current_user_with_quota(request: Request) -> str:
    from .user_service import check_usage_limit
    user_id = await get_current_user(request)
    await check_usage_limit(user_id)
    return user_id
