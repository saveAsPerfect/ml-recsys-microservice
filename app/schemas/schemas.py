from pydantic import BaseModel, Field
from typing import List


class PostGet(BaseModel):
    id: int = Field(..., description="Post ID", example=123)
    text: str = Field(..., description="Post text content",
                      example="This is a sample post text")
    topic: str = Field(..., description="Post topic/category",
                       example="technology")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 123,
                "text": "This is a sample post about machine learning",
                "topic": "technology"
            }
        }


class Response(BaseModel):
    exp_group: str = Field(...,
                           description="Experiment group (control/test)", example="control")
    recommendations: List[PostGet] = Field(...,
                                           description="List of recommended posts")

    class Config:
        schema_extra = {
            "example": {
                "exp_group": "control",
                "recommendations": [
                    {
                        "id": 123,
                        "text": "Sample post 1",
                        "topic": "technology"
                    },
                    {
                        "id": 456,
                        "text": "Sample post 2",
                        "topic": "science"
                    }
                ]
            }
        }
