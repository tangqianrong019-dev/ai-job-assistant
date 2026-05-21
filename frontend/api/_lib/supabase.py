"""Supabase REST 客户端（轻量版，无外部依赖）"""
import os, httpx


class SupabaseREST:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL", "")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    async def _get(self, table: str, query: dict) -> dict | None:
        params = "&".join(f"{k}=eq.{v}" for k, v in query.items())
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.url}/rest/v1/{table}?select=*&{params}",
                headers={"apikey": self.key, "Authorization": f"Bearer {self.key}", "Prefer": "return=representation"},
            )
        rows = resp.json()
        return rows[0] if rows else None

    async def _patch(self, table: str, query: dict, data: dict) -> dict:
        params = "&".join(f"{k}=eq.{v}" for k, v in query.items())
        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                f"{self.url}/rest/v1/{table}?{params}",
                json=data,
                headers={"apikey": self.key, "Authorization": f"Bearer {self.key}", "Prefer": "return=representation"},
            )
        rows = resp.json()
        return rows[0] if rows else {}


supabase = SupabaseREST()
