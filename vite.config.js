import { resolve } from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import svgr from "vite-plugin-svgr";

// https://vitejs.dev/config/
export default defineConfig({
  root: './src/app',
  envDir: process.cwd(),
  publicDir: resolve(__dirname, 'public'),
  build: {
    watch: {},
    emptyOutDir: true,
    outDir: resolve(__dirname, 'dist'),
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/app/index.html'),
        lobbies: resolve(__dirname, 'src/app/lobbies/index.html'),
        game: resolve(__dirname, 'src/app/game/index.html'),
      },
    }
  },
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
    }
  },
  preview: {
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
    }
  },
  plugins: [svgr(), react()],
})
