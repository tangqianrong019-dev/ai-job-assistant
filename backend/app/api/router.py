from fastapi import APIRouter

from . import auth, jobs, resume, interview, llm, project, offer, payment, files, user

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
api_router.include_router(offer.router, prefix="/offer", tags=["offer"])
api_router.include_router(payment.router, prefix="/payment", tags=["payment"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
