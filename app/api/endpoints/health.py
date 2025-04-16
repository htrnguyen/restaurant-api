from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["Health"])
def check_health():
    return {"status": "healthy"}
