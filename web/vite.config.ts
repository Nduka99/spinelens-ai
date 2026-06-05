import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  cacheDir: "./node_modules/.vite",
  build: {
    sourcemap: true,
    target: "es2022",
    // Split heavy vendors into their own long-cacheable chunks. Route views are
    // additionally code-split via React.lazy in App.tsx, so Recharts (charts) and
    // the non-default views only download when first needed.
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return undefined;
          if (id.includes("maplibre-gl") || id.includes("react-map-gl")) return "maplibre";
          if (id.includes("recharts") || id.includes("/d3-") || id.includes("victory")) return "charts";
          if (id.includes("framer-motion") || id.includes("/motion") || id.includes("popmotion")) return "motion";
          if (id.includes("/react/") || id.includes("/react-dom/") || id.includes("/scheduler/")) return "react-vendor";
          return undefined;
        },
      },
    },
  },
});
