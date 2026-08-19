import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true, // bind to 0.0.0.0 so it's reachable from outside a Docker container
    allowedHosts: [
      'mayday-unscathed-spongy.ngrok-free.dev',
      '.ngrok-free.dev',   // any free ngrok host
      '.ngrok-free.app',
    ],
    proxy: {
      '/api': process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000',
    },
  },
})