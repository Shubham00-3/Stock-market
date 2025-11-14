export interface Message {
  role: 'user' | 'assistant';
  content: string;
  toolsUsed?: string[];
  isStreaming?: boolean;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface SSEEvent {
  event: 'session' | 'message' | 'done' | 'error';
  data: string;
}

export interface SessionData {
  session_id: string;
}

export interface MessageData {
  type: 'update';
  content: string;
}

export interface ErrorData {
  error: string;
}

