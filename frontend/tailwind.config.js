/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'terminal-bg': '#0d1117',
        'terminal-card': '#1a1a2e',
        'terminal-border': '#30363d',
        'accent-yellow': '#ecad0a',
        'blue-primary': '#209dd7',
        'purple-secondary': '#753991',
        'green-up': '#00c853',
        'red-down': '#ff5252',
      },
      animation: {
        'price-flash-up': 'price-flash-up 500ms ease-out',
        'price-flash-down': 'price-flash-down 500ms ease-out',
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'price-flash-up': {
          '0%': { backgroundColor: '#00c853' },
          '100%': { backgroundColor: 'transparent' },
        },
        'price-flash-down': {
          '0%': { backgroundColor: '#ff5252' },
          '100%': { backgroundColor: 'transparent' },
        },
      },
    },
  },
  plugins: [],
}