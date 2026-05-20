"""支付接口 — Checkout 链接 + Webhook 处理"""

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from ..services.payment_service import get_checkout_url, verify_webhook_signature
from ..core.auth_deps import get_current_user
from ..services.user_service import supabase

router = APIRouter()

WEBHOOK_EVENTS = {
    "order_created": "订单创建",
    "subscription_created": "订阅开始",
    "subscription_updated": "订阅更新",
    "subscription_cancelled": "订阅取消",
    "subscription_expired": "订阅过期",
}


class CreateCheckoutRequest(BaseModel):
    annual: bool = Field(default=False, description="是否年付方案")


class CreateCheckoutResponse(BaseModel):
    checkout_url: str


@router.post("/create-checkout", response_model=CreateCheckoutResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    user_id: str = Depends(get_current_user),
):
    """获取 Lemon Squeezy 支付链接（带用户 ID）"""
    url = get_checkout_url(user_id=user_id, annual=request.annual)
    return CreateCheckoutResponse(checkout_url=url)


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------

@router.post("/webhook")
async def lemon_squeezy_webhook(request: Request):
    """接收 Lemon Squeezy 支付事件，自动更新 user_profiles"""
    raw_body = await request.body()
    signature = request.headers.get("X-Signature", "")

    if not verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = await request.json()
    event_name = event.get("meta", {}).get("event_name", "")
    label = WEBHOOK_EVENTS.get(event_name, event_name)

    print(f"[Webhook] 收到: {label}")

    data = event.get("data", {}).get("attributes", {})
    custom = data.get("custom_data", {}) or {}
    user_id = custom.get("user_id")

    if not user_id:
        return {"received": True, "note": "no user_id in custom data"}

    if event_name in ("subscription_created", "subscription_updated"):
        status = data.get("status", "")
        if status == "active":
            plan = data.get("variant_name", "pro")
            sub = "pro" if "pro" in plan.lower() else "enterprise"
            await supabase._patch(
                "user_profiles",
                {"id": user_id},
                {"subscription_status": sub, "usage_count": 0},
            )
            print(f"[Webhook] 用户 {user_id} → {sub}")

    elif event_name == "subscription_expired":
        await supabase._patch(
            "user_profiles",
            {"id": user_id},
            {"subscription_status": "free"},
        )
        print(f"[Webhook] 用户 {user_id} → free")

    return {"received": True, "event": label}
