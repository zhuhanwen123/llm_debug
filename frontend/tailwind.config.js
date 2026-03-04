/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        skyglass: {
          50: '#f4fbff',
          100: '#e8f6ff',
          200: '#caebff',
          300: '#9fdcff',
          400: '#6fc7ff',
          500: '#39b0fa'
        }
      },
      boxShadow: {
        jelly: '0 12px 24px rgba(57, 176, 250, 0.18), inset 0 1px 0 rgba(255,255,255,0.55)'
      },
      keyframes: {
        jellyBounce: {
          '0%': { transform: 'scale(1)' },
          '35%': { transform: 'scale(0.92, 1.08)' },
          '70%': { transform: 'scale(1.04, 0.96)' },
          '100%': { transform: 'scale(1)' }
        },
        floatIn: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        }
      },
      animation: {
        jellyBounce: 'jellyBounce 420ms ease-out',
        floatIn: 'floatIn 420ms ease-out'
      }
    }
  },
  plugins: []
}
