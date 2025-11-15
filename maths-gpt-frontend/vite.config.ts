import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // enable the automatic JSX runtime (should match tsconfig jsx: "react-jsx")
      jsxRuntime: "automatic",
    }),
  ],
  resolve: {
    alias: {
      // allows `import X from '@/components/X'`
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    port: 5173,
    // Optional proxy: forward '/api' to a backend server running locally
    // change target to the actual host:port of your backend (e.g. FastAPI 8000, Flask 5000, Streamlit 8501)
    proxy: {
      // forwards /api/* => http://localhost:8000/api/*
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
        secure: false,
        // optional: rewrite path if needed
        // rewrite: (path) => path.replace(/^\/api/, "")
      },
    },
  },
  // build options (optional)
  build: {
    outDir: "dist",
  },
});
