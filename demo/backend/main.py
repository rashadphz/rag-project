from typing import Iterator
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import time

import requests

app = FastAPI()


class Source(BaseModel):
    name: str
    url: str


class SourceResponse(BaseModel):
    top_sources: list[Source]


class TextChunk(BaseModel):
    text: str | None  # None for the last chunk


class FollowUpQuestion(BaseModel):
    question: str


sources = [
    SourceResponse(
        top_sources=[
            Source(name="Source 1", url="http://source1.com"),
            Source(name="Source 2", url="http://source2.com"),
        ]
    ),
]
text_chunks = [
    TextChunk(text="Here is a piece of text."),
    TextChunk(text="Here is another piece of text."),
]
follow_up_questions = [
    FollowUpQuestion(question="What is X?"),
    FollowUpQuestion(question="How does Y work?"),
    FollowUpQuestion(question="Where can I find Z?"),
]


def get_json_line(json_dict: dict) -> str:
    return json.dumps(json_dict) + "\n"


def stream_chat_message_objects() -> (
    Iterator[SourceResponse | TextChunk | FollowUpQuestion]
):
    for source in sources:
        yield source
    time.sleep(1)
    for chunk in text_chunks:
        time.sleep(0.1)
        yield chunk
    time.sleep(2)
    for question in follow_up_questions:
        yield question


@app.get("/chat")
async def root() -> StreamingResponse:
    objects = stream_chat_message_objects()

    def generator() -> Iterator[str]:
        for obj in objects:
            yield get_json_line(obj.model_dump_json())

    return StreamingResponse(
        generator(),
        media_type="application/json",
    )


if __name__ == "__main__":

    url = "http://127.0.0.1:8000/chat"

    def get_event():
        with requests.get(url, stream=True) as stream:
            for chunk in stream.iter_lines():
                print(chunk)
                yield chunk

    for event in get_event():
        print(event)
