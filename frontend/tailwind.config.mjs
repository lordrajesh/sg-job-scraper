/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        hk: {
          red: '#dc2626',
          dark: '#991b1b',
        },
        slate: {
          850: '#172033',
          950: '#0f172a',
        },
      },
    },
  },
  plugins: [],
};
