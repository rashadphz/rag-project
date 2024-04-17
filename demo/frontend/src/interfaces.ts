export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface SendMessageRequest {
  message: string;
  history: ChatMessage[];
}

export interface Source {
  filename: string;
  heading: string;
}

export interface SourceResponse {
  top_sources: Source[];
}

export interface TextChunk {
  text: string | null;
}

export interface FollowUpQuestions {
  questions: string[];
}
export interface SQLEvent {
  event_type: "start" | "end";
}

