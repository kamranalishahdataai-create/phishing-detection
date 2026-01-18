/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f4fc',
          100: '#cce9f9',
          200: '#99d3f3',
          300: '#66bded',
          400: '#4AABDE',
          500: '#4A9FD4',
          600: '#3B7FAA',
          700: '#2C5F7F',
          800: '#1E4055',
          900: '#0F202A',
        },
        dark: {
          100: '#1a2332',
          200: '#151c28',
          300: '#111921',
          400: '#0d1117',
          500: '#090c10',
          600: '#050709',
        },
        accent: {
          blue: '#4A9FD4',
          cyan: '#5BC0DE',
          teal: '#38B2AC',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-gradient': 'linear-gradient(180deg, #0d1117 0%, #151c28 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
