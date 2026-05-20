"""用户资料接口"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..core.auth_deps import get_current_user
from ..services.user_service import supabase

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    nickname: str = Field(default="", description="用户昵称")


class ProfileResponse(BaseModel):
    id: str
    email: str = ""
    nickname: str = ""
    subscription_status: str = "free"
    usage_count: int = 0


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user_id: str = Depends(get_current_user)):
    """获取当前用户 profile"""
    profile = await supabase._get("user_profiles", {"id": user_id})
    return ProfileResponse(
        id=user_id,
        email=profile.get("email", "") if profile else "",
        nickname=profile.get("nickname", "") if profile else "",
        subscription_status=profile.get("subscription_status", "free") if profile else "free",
        usage_count=profile.get("usage_count", 0) if profile else 0,
    )


@router.post("/profile", response_model=ProfileResponse)
async def update_profile(req: UpdateProfileRequest, user_id: str = Depends(get_current_user)):
    """更新用户昵称"""
    updated = await supabase._patch(
        "user_profiles",
        {"id": user_id},
        {"nickname": req.nickname},
    )
    return ProfileResponse(
        id=user_id,
        email=updated.get("email", ""),
        nickname=updated.get("nickname", ""),
        subscription_status=updated.get("subscription_status", "free"),
        usage_count=updated.get("usage_count", 0),
    )
