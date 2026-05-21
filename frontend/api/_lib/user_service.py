"""用户用量限制"""
import os, httpx
from fastapi import HTTPException

FREE_LIMIT = 5


async def get_user_profile(user_id: str) -> dict | None:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{url}/rest/v1/user_profiles?select=*&id=eq.{user_id}",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
    rows = resp.json()
    return rows[0] if rows else None


async def check_usage_limit(user_id: str) -> dict:
    profile = await get_user_profile(user_id)
    if not profile:
        # 自动创建
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{url}/rest/v1/user_profiles",
                json={"id": user_id},
                headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "return=representation"},
            )
        profile = await get_user_profile(user_id) or {"subscription_status": "free", "usage_count": 0}

    if profile.get("subscription_status", "free") == "free" and profile.get("usage_count", 0) >= FREE_LIMIT:
        raise HTTPException(status_code=403, detail="免费次数已用完，请升级")
    return profile


async def increment_usage(user_id: str):
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    profile = await get_user_profile(user_id)
    if profile:
        new_count = profile.get("usage_count", 0) + 1
        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{url}/rest/v1/user_profiles?id=eq.{user_id}",
                json={"usage_count": new_count},
                headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "return=representation"},
            )
