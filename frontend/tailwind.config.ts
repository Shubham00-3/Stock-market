import type { Config } from 'tailwindcss'

export default {
  darkMode: ["class"],
  content: [
    './index.html',
    './src/**/*.{ts,tsx,js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: 'hsl(var(--card))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: 'hsl(var(--secondary))',
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        border: 'hsl(var(--border))',
        'chat-user': 'hsl(var(--chat-user))',
        'chat-assistant': 'hsl(var(--chat-assistant))',
        'chat-input': 'hsl(var(--chat-input))',
      },
      boxShadow: {
        glow: 'var(--shadow-glow)',
        card: 'var(--shadow-card)',
      },
      transitionProperty: {
        smooth: 'var(--transition-smooth)',
      },
    },
  },
  plugins: [],
} satisfies Config

