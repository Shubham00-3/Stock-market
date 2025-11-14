import { useEffect, useRef } from 'react';
import { TrendingUp, Trash2, Sparkles } from 'lucide-react';
import { useChatStream } from '@/hooks/useChatStream';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { TypingIndicator } from '@/components/TypingIndicator';

const EXAMPLE_QUERIES = [
  'What is the current price of Apple stock?',
  'Compare Tesla and Microsoft stocks',
  'Show me market news about technology',
];

export default function Index() {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChatStream();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleExampleClick = (query: string) => {
    sendMessage(query);
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80 shadow-card">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">Market Intelligence</h1>
              <p className="text-xs text-muted-foreground">AI-Powered Financial Assistant</p>
            </div>
          </div>
          
          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-secondary text-muted-foreground hover:text-foreground hover:bg-muted transition-smooth"
            >
              <Trash2 className="w-4 h-4" />
              <span className="text-sm">Clear Chat</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {messages.length === 0 ? (
            /* Welcome Screen */
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
              <div className="w-20 h-20 rounded-2xl bg-primary/20 flex items-center justify-center mb-6 shadow-glow">
                <Sparkles className="w-10 h-10 text-primary" />
              </div>
              <h2 className="text-3xl font-bold text-foreground mb-3">
                Welcome to Market Intelligence
              </h2>
              <p className="text-muted-foreground text-lg mb-8 max-w-md">
                Your AI-powered assistant for real-time stock analysis, market news, and financial insights.
              </p>

              <div className="w-full max-w-2xl space-y-3">
                <p className="text-sm text-muted-foreground mb-4">Try asking:</p>
                <div className="grid gap-3">
                  {EXAMPLE_QUERIES.map((query, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleExampleClick(query)}
                      className="group text-left px-5 py-4 rounded-xl bg-card border border-border hover:border-primary hover:shadow-glow transition-smooth"
                    >
                      <p className="text-foreground group-hover:text-primary transition-smooth">
                        {query}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <div className="space-y-4">
              {messages.map((message, idx) => (
                <ChatMessage key={idx} message={message} />
              ))}
              
              {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
                <TypingIndicator />
              )}
              
              {error && (
                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400">
                  <p className="font-semibold mb-1">Error</p>
                  <p className="text-sm">{error}</p>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      {/* Input Area */}
      <div className="sticky bottom-0 border-t border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80 shadow-card">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}

