import { Bot } from 'lucide-react';

export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 mb-6">
      <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0">
        <Bot className="w-5 h-5 text-primary" />
      </div>
      <div className="bg-chat-assistant rounded-2xl px-4 py-3 shadow-card">
        <div className="flex gap-1">
          <div className="w-2 h-2 rounded-full bg-muted-foreground typing-dot"></div>
          <div className="w-2 h-2 rounded-full bg-muted-foreground typing-dot"></div>
          <div className="w-2 h-2 rounded-full bg-muted-foreground typing-dot"></div>
        </div>
      </div>
    </div>
  );
}

