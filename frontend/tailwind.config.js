/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'part-1': '#9333ea', // purple for Organization Management
        'part-2': '#dc2626', // red for Hospital Systems
        'part-3': '#16a34a', // green for Patient Care
        'part-4': '#2563eb', // blue for Results
        'status-excellent': '#16a34a',
        'status-good': '#eab308',
        'status-needs-improvement': '#f97316',
        'status-critical': '#dc2626',
      },
    },
  },
  plugins: [],
}
