"""轻量 Supabase REST 客户端 — 基于 httpx，无额外 C 依赖"""

import httpx
from .config import settings


class SupabaseREST:
    """直接调用 Supabase REST API (PostgREST)"""

    def __init__(self):
        self.url = settings.supabase_url
        self.key = settings.supabase_service_role_key
        self._headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    async def _get(self, table: str, query: dict[str, str]) -> dict | None:
        """SELECT 单行"""
        params = "&".join(f"{k}=eq.{v}" for k, v in query.items())
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.url}/rest/v1/{table}?select=*&{params}",
                headers={**self._headers, "Prefer": "return=representation"},
            )
        rows = resp.json()
        return rows[0] if rows else None

    async def _patch(self, table: str, query: dict[str, str], data: dict) -> dict:
        """UPDATE 单行"""
        params = "&".join(f"{k}=eq.{v}" for k, v in query.items())
        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                f"{self.url}/rest/v1/{table}?{params}",
                json=data,
                headers={**self._headers, "Prefer": "return=representation"},
            )
        rows = resp.json()
        return rows[0] if rows else {}


# 单例
supabase = SupabaseREST()
