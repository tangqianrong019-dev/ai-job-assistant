"""Lemon Squeezy 支付服务 — 生成支付链接 + Webhook 验证"""

import hashlib
import hmac
from ..core.config import settings


def get_checkout_url(user_id: str, annual: bool = False) -> str:
    """生成带用户 ID 的支付链接"""
    base = (
        settings.lemon_squeezy_checkout_url_yearly
        if annual
        else settings.lemon_squeezy_checkout_url
    )
    return f"{base}?checkout[custom][user_id]={user_id}"


def verify_webhook_signature(raw_body: bytes, signature: str) -> bool:
    """验证 Lemon Squeezy Webhook 签名"""
    secret = settings.lemon_squeezy_webhook_secret
    if not secret:
        return True
    digest = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)
