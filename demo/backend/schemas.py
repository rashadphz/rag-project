from pydantic import BaseModel


class Source(BaseModel):
    filename: str
    heading: str


class SourceResponse(BaseModel):
    top_sources: list[Source]


class TextChunk(BaseModel):
    text: str | None  # None for the last chunk


class FollowUpQuestions(BaseModel):
    questions: list[str]
