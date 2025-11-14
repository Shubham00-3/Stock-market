import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const MAX_CHARS = 2000;

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled && input.length <= MAX_CHARS) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const charCount = input.length;
  const isOverLimit = charCount > MAX_CHARS;

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative bg-chat-input rounded-2xl border border-border shadow-card transition-smooth focus-within:border-primary focus-within:shadow-glow">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about stocks, market news, or compare companies..."
          disabled={disabled}
          rows={1}
          className={cn(
            'w-full bg-transparent px-4 py-3 pr-24 text-foreground placeholder:text-muted-foreground resize-none outline-none max-h-32 overflow-y-auto',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        />

        <div className="absolute right-2 bottom-2 flex items-center gap-2">
          <span
            className={cn(
              'text-xs text-muted-foreground',
              isOverLimit && 'text-red-500 font-semibold'
            )}
          >
            {charCount}/{MAX_CHARS}
          </span>
          <button
            type="submit"
            disabled={disabled || !input.trim() || isOverLimit}
            className={cn(
              'p-2 rounded-lg bg-primary text-primary-foreground transition-smooth hover:shadow-glow disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:shadow-none',
              !disabled && input.trim() && !isOverLimit && 'hover:scale-105'
            )}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
      <p className="text-xs text-muted-foreground mt-2 px-1">
        Press <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">Enter</kbd> to send,{' '}
        <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">Shift + Enter</kbd> for new line
      </p>
    </form>
  );
}

