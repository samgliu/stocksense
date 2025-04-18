import { sentryVitePlugin } from '@sentry/vite-plugin';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  base: process.env.VITE_BASE_URL || '/',

  plugins: [
    react(),
    tailwindcss(),
    sentryVitePlugin({
      org: 'stocksense',
      project: 'stocksense-frontend',
      authToken: process.env.SENTRY_AUTH_TOKEN,
      uploadSourceMaps: true,
      sourcemaps: {
        filesToDeleteAfterUpload: ['dist/**/*.map'],
      },
    }),
  ],

  resolve: {
    alias: {
      '@': '/src',
    },
  },

  server: {
    port: 3000,
  },

  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
