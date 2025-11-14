# Market Intelligence Frontend

AI-powered financial assistant with real-time stock analysis and market insights.

## Features

- 🎯 Real-time streaming responses (ChatGPT-style)
- 📊 Stock price queries and comparisons
- 📰 Market news and analysis
- 🎨 Dark finance-themed UI
- ⚡ Built with React + TypeScript + Vite + Tailwind CSS

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **React Router** - Routing
- **TanStack Query** - Data fetching

## API Integration

Connects to: `https://market-intelligence-chatbot-backend-production.up.railway.app`

The backend provides:
- Real-time stock prices (via yfinance)
- Market news (via NewsAPI)
- Stock history and comparisons
- Market summaries

## Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── ChatMessage.tsx
│   ├── ChatInput.tsx
│   └── TypingIndicator.tsx
├── hooks/           # Custom React hooks
│   └── useChatStream.ts
├── lib/             # Utility functions
│   └── utils.ts
├── pages/           # Page components
│   └── Index.tsx
├── types/           # TypeScript types
│   └── chat.ts
├── App.tsx          # Root component
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## Development

The app runs on `http://localhost:3000` in development mode.

Server-Sent Events (SSE) are used for streaming responses from the AI backend.

