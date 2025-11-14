import { User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Message } from '@/types/chat';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex items-start gap-3 mb-6', isUser && 'flex-row-reverse')}>
      <div
        className={cn(
          'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
          isUser ? 'bg-chat-user' : 'bg-secondary'
        )}
      >
        {isUser ? (
          <User className="w-5 h-5 text-primary-foreground" />
        ) : (
          <Bot className="w-5 h-5 text-primary" />
        )}
      </div>

      <div className="flex-1 max-w-[80%]">
        <div
          className={cn(
            'rounded-2xl px-4 py-3 shadow-card transition-smooth',
            isUser
              ? 'bg-chat-user text-primary-foreground ml-auto'
              : 'bg-chat-assistant text-foreground'
          )}
        >
          <p className="whitespace-pre-wrap break-words">
            {message.content}
            {message.isStreaming && <span className="streaming-cursor inline-block w-0.5 h-5 bg-primary ml-1"></span>}
          </p>
        </div>

        {message.toolsUsed && message.toolsUsed.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {message.toolsUsed.map((tool, idx) => (
              <span
                key={idx}
                className="text-xs px-2 py-1 rounded-lg bg-secondary text-muted-foreground border border-border"
              >
                🔧 {tool}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

