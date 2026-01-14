import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        crew: {
          primary: '#4A423A',
          secondary: '#DEDBC0',
          accent: '#A0B09A',
          text: '#4A423A',
          'text-light': '#6B6B6B',
          'text-muted': '#9A9A9A',
          background: '#FFFBF5',
          surface: '#F5F2ED',
          'card-bg': '#FDFCFA',
          success: '#A0B09A',
          warning: '#D4A853',
          error: '#C85A54',
          border: '#E0DDD8',
        },
      },
    },
  },
  plugins: [],
};
export default config;
