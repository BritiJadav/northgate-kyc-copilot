/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        northgate: {
          navy: '#0F172A',
          blue: '#1E3A8A',
          accent: '#2563EB',
          slate: '#334155',
          light: '#F8FAFC',
          card: '#FFFFFF',
          border: '#E2E8F0',
        }
      }
    },
  },
  plugins: [],
}
