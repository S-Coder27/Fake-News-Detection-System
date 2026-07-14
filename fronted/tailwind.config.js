/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      boxShadow: {
        glass: '0 8px 32px 0 rgba(31, 38, 135, 0.37)'
      },
      backdropBlur: {
        xs: '2px'
      }
    }
  },
  plugins: []
}