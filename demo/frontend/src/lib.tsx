// From : https://github.com/danswer-ai/danswer/blob/dac4be62e0fb223a4d13577cef7ff4ffc5277cd8/web/src/lib/search/streamingUtils.ts

import {
  SendMessageRequest,
  SourceResponse,
  TextChunk,
  FollowUpQuestions,
} from "@/interfaces";

type NonEmptyObject = { [k: string]: any };

const BASE_URL =
  process.env.NODE_ENV === "development"
    ? "http://127.0.0.1:8000"
    : "https://rag-project.onrender.com";

const processSingleChunk = <T extends NonEmptyObject>(
  chunk: string,
  partialChunk: string | null
): [T | null, string | null] => {
  const completeChunk = (partialChunk || "") + chunk;
  try {
    const chunkJson = JSON.parse(JSON.parse(completeChunk));
    return [chunkJson, null];
  } catch (err) {
    return [null, completeChunk];
  }
};

export const processRawChunkString = <T extends NonEmptyObject>(
  rawChunk: string,
  prevPartialChunk: string | null
): [T[], string | null] => {
  const chunkSections = rawChunk
    .split("\n")
    .filter((chunk) => chunk.length > 0);

  let parsedChunks: T[] = [];
  let partialChunk = prevPartialChunk;
  for (const chunk of chunkSections) {
    const [parsedChunk, newPartialChunk] = processSingleChunk<T>(
      chunk,
      partialChunk
    );
    if (parsedChunk) {
      parsedChunks.push(parsedChunk);
      partialChunk = null;
    } else {
      partialChunk = newPartialChunk;
    }
  }
  return [parsedChunks, partialChunk];
};

export async function* handleStream<T extends NonEmptyObject>(
  streamingResponse: Response
): AsyncGenerator<T> {
  const reader = streamingResponse.body?.getReader();
  const decoder = new TextDecoder("utf-8");

  let prevParitalChunk: string | null = null;
  while (true) {
    const rawChunk = await reader?.read();
    if (!rawChunk) {
      throw new Error("Unable to process chunk");
    }
    const { done, value } = rawChunk;
    if (done) {
      break;
    }
    //@ts-ignore
    const [completeChunks, partialChunk] = processRawChunkString<T>(
      decoder.decode(value, { stream: true }),
      prevParitalChunk
    );
    if (!completeChunks.length && !partialChunk) {
      break;
    }
    prevParitalChunk = partialChunk;
    for (const chunk of completeChunks) {
      yield chunk;
    }
  }
}

export async function* sendMessage({ message, history }: SendMessageRequest) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    const errorJson = await response.json();
    const errorMsg = errorJson.message || errorJson.detail || "";
    throw Error(`Failed to send message - ${errorMsg}`);
  }
  yield* handleStream<SourceResponse | TextChunk | FollowUpQuestions>(response);
}
