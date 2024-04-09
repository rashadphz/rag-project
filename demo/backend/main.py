from typing import Iterator
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import time

import requests
from chat import stream_chat_message_objects

from schemas import FollowUpQuestions, Source, SourceResponse, TextChunk

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# sources = [
#     SourceResponse(
#         top_sources=[
#             Source(name="Source 1", url="http://source1.com"),
#             Source(name="Source 2", url="http://source2.com"),
#         ]
#     ),
# ]

full_text = """
Based on the search results, here is a concise answer to the question:
Local balanced samplers in generative models can improve the quality and diversity of generated samples compared to standard sampling approaches. The key findings are:
"""
text_chunks = [TextChunk(text=text) for text in full_text.split(" ")]
follow_up_questions = FollowUpQuestions(
    questions=[
        "What is X?",
        "How does Y work?",
        "Where can I find Z?",
    ]
)


def get_json_line(json_dict: dict) -> str:
    return json.dumps(json_dict) + "\n"


# def stream_chat_message_objects() -> (
#     Iterator[SourceResponse | TextChunk | FollowUpQuestions]
# ):
#     for source in sources:
#         yield source
#     time.sleep(0.5)
#     for chunk in text_chunks:
#         time.sleep(0.01)
#         yield chunk
#     time.sleep(0.5)
#     yield follow_up_questions


class SendMessageRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(request: SendMessageRequest) -> StreamingResponse:
    message = "How do local balanced samplers in generative models compare in terms of sample quality and diversity?"
    objects = stream_chat_message_objects(message)

    def generator() -> Iterator[str]:
        for obj in objects:
            yield get_json_line(obj.model_dump_json())

    return StreamingResponse(
        generator(),
        media_type="application/json",
    )


if __name__ == "__main__":

    url = "http://127.0.0.1:8000/chat"
    message = "How do local balanced samplers in generative models compare in terms of sample quality and diversity?"

    def get_event():
        with requests.post(
            url, data=SendMessageRequest(message=message).json(), stream=True
        ) as stream:
            for chunk in stream.iter_lines():
                print(chunk)
                yield chunk

    for event in get_event():
        print(event)
