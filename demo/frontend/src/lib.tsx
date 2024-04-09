import {
  SendMessageRequest,
  SourceResponse,
  TextChunk,
  FollowUpQuestions,
} from "@/interfaces";

type NonEmptyObject = { [k: string]: any };

export async function* handleStream<T extends NonEmptyObject>(
  streamingResponse: Response
): AsyncGenerator<T> {
  const reader = streamingResponse.body?.getReader();
  const decoder = new TextDecoder("utf-8");

  while (true) {
    const rawChunk = await reader?.read();
    if (!rawChunk) {
      throw new Error("Unable to process chunk");
    }
    const { done, value } = rawChunk;
    if (done) {
      break;
    }
    const chunk = decoder.decode(value, { stream: true });
    const json = JSON.parse(JSON.parse(chunk));
    yield json;
  }
}

export async function* sendMessage({ message }: SendMessageRequest) {
  const response = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const errorJson = await response.json();
    const errorMsg = errorJson.message || errorJson.detail || "";
    throw Error(`Failed to send message - ${errorMsg}`);
  }
  yield* handleStream<SourceResponse | TextChunk | FollowUpQuestions>(response);
}
