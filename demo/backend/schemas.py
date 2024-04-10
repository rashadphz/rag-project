from pydantic import BaseModel

from pydantic import BaseModel, Field
from typing import List


class Source(BaseModel):
    filename: str
    heading: str


class SourceResponse(BaseModel):
    top_sources: list[Source]


class TextChunk(BaseModel):
    text: str | None  # None for the last chunk


class FollowUpQuestions(BaseModel):
    questions: list[str]


class RelatedQueryItem(BaseModel):
    query: str


class RelatedSchema(BaseModel):
    """Related queries to the user's original query"""

    queries: List[RelatedQueryItem] = Field(..., min_items=3, max_items=3)
