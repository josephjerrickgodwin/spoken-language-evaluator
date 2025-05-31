from typing import Optional
from pydantic import BaseModel, Field


class CandidateEvaluateRequest(BaseModel):
    """
    Request model for classifying the candidate English accent.
    """
    video_url: str = Field(..., description="Public URL of the video")

    class Config:
        json_schema_extra = {
            "example": {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }


class CandidateEvaluateResponse(BaseModel):
    """
    Represents the response for candidate accent evaluation, including classification, confidence score,
    and a summary of the video content (optional).
    """
    classification: str = Field(..., description="Classification of the accent")
    confidence: str = Field(..., description="Confidence score in English accent")
    summary: Optional[str] = Field(None, description="A short summary of the video content")

    class Config:
        json_schema_extra = {
            "example": {
                "classification": "Scotland",
                "confidence": "100%",
                "summary": "A short summary of the video"
            }
        }
