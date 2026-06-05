import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  cacheDir: "./node_modules/.vite",
  build: {
    sourcemap: true,
    target: "es2022",
  },
});
