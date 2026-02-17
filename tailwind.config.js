/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
    "./templates/team/includes/**/*.html" // Add this to be safe
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          green: '#006837',
          hover: '#004d29',
        },
        text: {
          dark: '#1a1a1a',
          light: '#666666',
        },
        bgLight: '#f4f7f5',
      },
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
}