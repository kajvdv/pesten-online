import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  root: './src/app',
  server: {
    proxy: {
      '^/api/.*/connect': {
        target: "ws://127.0.0.1:8000",
        rewriteWsOrigin: true,
        changeOrigin: true,
        ws: true,
        rewrite: path => path.replace(/^\/api/, '')
      },
      '/api': {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '^/lobbies$': {
        target: "http://localhost:5173",
        rewrite: path => "/lobbies/index.html"
      },
      '/game?lobby_id=': {
        target: "http://localhost:5173",
        rewrite: path => "/game/index.html"
      }
    }
  },
  plugins: [react()],
})
