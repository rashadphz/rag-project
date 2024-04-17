from pydantic import BaseModel

from pydantic import BaseModel, Field
from typing import List, Literal


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


class SQLEvent(BaseModel):
    event_type: Literal["start", "end"]


class RelatedSchema(BaseModel):
    """Related queries to the user's original query"""

    queries: List[RelatedQueryItem] = Field(..., min_items=3, max_items=3)
