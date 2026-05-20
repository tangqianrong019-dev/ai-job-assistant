from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"message": "auth — coming soon"}


@router.post("/register")
async def register():
    return {"message": "auth — coming soon"}
