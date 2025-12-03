from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class CaptionRequest(BaseModel):
    video_id: str
    mode: str = "template"  # "template" or "ai"


@router.post("/generate")
async def generate_caption(request: CaptionRequest):
    """Generate caption for a video"""
    # TODO: Implement with caption service
    return {
        "video_id": request.video_id,
        "mode": request.mode,
        "caption": "Caption placeholder"
    }
