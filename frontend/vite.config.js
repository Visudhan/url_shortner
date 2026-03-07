import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Listen on all network interfaces for Docker
    port: 5173,      // Default Vite port
    proxy: {
      // Send ANY request starting with /api to the Django backend
      '/api': {
        target: 'http://web:8000', // Matches the docker-compose service name
        changeOrigin: true,
      }
    }
  }
})
