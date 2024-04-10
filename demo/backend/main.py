import asyncio
from typing import Iterator
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

import requests
from chat import stream_chat_message_objects

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_json_line(json_dict: dict) -> str:
    return json.dumps(json_dict) + "\n"


class SendMessageRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(request: SendMessageRequest) -> StreamingResponse:
    async def generator() -> Iterator[str]:
        async for obj in stream_chat_message_objects(request.message):
            yield get_json_line(obj.model_dump_json())
            await asyncio.sleep(0)

    return StreamingResponse(
        generator(),
        media_type="application/json",
    )


async def main():
    url = "http://127.0.0.1:8000/chat"
    message = "How do local balanced samplers in generative models compare in terms of sample quality and diversity?"

    async def get_event():
        with requests.post(
            url, data=SendMessageRequest(message=message).json(), stream=True
        ) as stream:
            for chunk in stream.iter_lines():
                yield chunk

    async for event in get_event():
        print(event)


if __name__ == "__main__":
    asyncio.run(main())
