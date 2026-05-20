"""FastAPI 认证依赖 — 双重验证：本地 JWT decode + Supabase API fallback"""

import jwt
import httpx
from fastapi import HTTPException, Request
from ..core.config import settings
from ..services.user_service import get_user_profile, check_usage_limit


async def get_current_user(request: Request) -> str:
    """解析 Authorization: Bearer <token>，返回 user_id。

    验证策略（双重保障）：
    1. 优先本地 JWT decode（快，无网络开销）
    2. 若本地验证失败，调用 Supabase /auth/v1/user（权威校验）
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Authorization: Bearer <token>")

    token = auth[7:]
    user_id: str | None = None

    # ---------- 方式 1：本地 JWT 解码 ----------
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_exp": True, "require": ["sub"]},
        )
        user_id = payload["sub"]
        print(f"[Auth] Local JWT decode ok, user_id={user_id}")
    except Exception as e:
        print(f"[Auth] Local JWT decode failed ({e}), trying Supabase API...")

        # ---------- 方式 2：Supabase API ----------
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{settings.supabase_url}/auth/v1/user",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": settings.supabase_service_role_key,
                    },
                )
            if resp.status_code == 200:
                user_id = resp.json()["id"]
                print(f"[Auth] Supabase API ok, user_id={user_id}")
            else:
                print(f"[Auth] Supabase API returned {resp.status_code}: {resp.text[:200]}")
        except Exception as e2:
            print(f"[Auth] Supabase API error: {e2}")

    if not user_id:
        raise HTTPException(status_code=401, detail="无效的 Token，请重新登录")

    # 确保 user_profiles 存在（不存在则自动创建）
    profile = await get_user_profile(user_id)
    if not profile:
        print(f"[Auth] Profile not found for {user_id}, creating...")
        # 用用户自己的 token 插入，满足 RLS 策略 auth.uid() = id
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.supabase_url}/rest/v1/user_profiles",
                json={"id": user_id},
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.supabase_service_role_key,
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
            )
        if resp.status_code in (200, 201):
            print(f"[Auth] Profile created for {user_id}")
        else:
            print(f"[Auth] Failed to create profile: {resp.status_code} {resp.text[:200]}")

    return user_id


async def get_current_user_with_quota(request: Request) -> str:
    """get_current_user + 用量检查（推荐在 AI 功能接口使用）"""
    user_id = await get_current_user(request)
    await check_usage_limit(user_id)
    return user_id
