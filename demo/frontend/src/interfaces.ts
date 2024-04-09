export interface SendMessageRequest {
  message: string;
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
