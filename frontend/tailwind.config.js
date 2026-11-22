/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#FFFFFF',
          secondary: '#FFF9FA',
        },
        foreground: {
          DEFAULT: '#15151F',
          secondary: '#626273',
        },
        coral: {
          DEFAULT: '#F04464',
          hover: '#DB3556',
          light: '#FFF1F3',
        },
        pink: {
          surface: '#FCECEF',
          accent: '#FFF1F3',
        },
        border: {
          DEFAULT: '#ECE8EA',
        },
      },
      fontFamily: {
        sans: ['DM Sans', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Manrope', 'DM Sans', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'coral-sm': '0 2px 8px -2px rgba(240, 68, 100, 0.25)',
        'coral-md': '0 8px 24px -4px rgba(240, 68, 100, 0.20)',
        'soft': '0 4px 20px -2px rgba(21, 21, 31, 0.05)',
      },
    },
  },
  plugins: [],
}
