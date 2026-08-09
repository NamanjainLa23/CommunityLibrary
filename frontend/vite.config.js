import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    allowedHosts: [
      'mayday-unscathed-spongy.ngrok-free.dev',
      '.ngrok-free.dev',   // any free ngrok host
      '.ngrok-free.app',
    ],
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})