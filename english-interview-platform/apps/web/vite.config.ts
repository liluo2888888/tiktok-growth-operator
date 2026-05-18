import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src")
    }
  },
  server: {
    port: Number(process.env.WEB_PORT) || 5174,
    strictPort: true,
    host: "127.0.0.1",
    proxy: {
      "/v1": {
        target: process.env.VITE_DEV_API ?? "http://127.0.0.1:8090",
        changeOrigin: true
      },
      "/healthz": {
        target: process.env.VITE_DEV_API ?? "http://127.0.0.1:8090",
        changeOrigin: true
      }
    }
  }
});
